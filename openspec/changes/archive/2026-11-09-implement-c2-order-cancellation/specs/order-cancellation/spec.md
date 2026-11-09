## ADDED Requirements

### Requirement: Customers can cancel their own order while it awaits payment

Um Cliente autenticado e `ATIVO` SHALL poder cancelar um Pedido próprio somente quando o
Pedido estiver em `AGUARDANDO_PAGAMENTO` e pertencer a ele. O backend SHALL derivar o
proprietário do Pedido a partir da sessão do Cliente; qualquer requisição em nome de
outra conta SHALL ser rejeitada. Cancelamentos fora dessa janela (ex.: `PAGAMENTO_CONFIRMADO`,
`EM_PREPARACAO`, `ENVIADO`, `ENTREGUE`, `CANCELADO` já aplicado) SHALL ser rejeitados sem
efeito colateral.

#### Scenario: Customer cancels own awaiting-payment order
- **WHEN** um Cliente `ATIVO` cancela um Pedido próprio em `AGUARDANDO_PAGAMENTO`
- **THEN** o pedido vira `CANCELADO`, o pagamento vira `CANCELADO`, o estoque é devolvido e a operação retorna sucesso, sem novas tentativas de pagamento simulado

#### Scenario: Customer cannot cancel someone else's order
- **WHEN** um Cliente solicita cancelamento informando um `order_id` pertencente a outro Cliente
- **THEN** o backend rejeita o pedido sem vazar a existência nem revelar dados do Pedido, e nada é alterado

#### Scenario: Customer cannot cancel confirmed or terminal orders
- **WHEN** um Cliente solicita cancelamento de um Pedido em `PAGAMENTO_CONFIRMADO`, `EM_PREPARACAO`, `ENVIADO` ou `ENTREGUE`
- **THEN** o backend rejeita sem efeito colateral e o Pedido permanece no estado anterior

### Requirement: Administrators can cancel orders beyond the client window

Um UsuarioInterno `ATIVO` com papel `ADMINISTRADOR` SHALL poder cancelar Pedidos em
`AGUARDANDO_PAGAMENTO` ou `PAGAMENTO_CONFIRMADO`, respeitados os mesmos efeitos de
cancelamento. O papel `FUNCIONARIO` SHALL NOT cancelar pedidos; o backend SHALL verificar
autorização no backend independente e não confiar no frontend.

#### Scenario: Administrator cancels a PAGAMENTO_CONFIRMADO order
- **WHEN** um ADMIN cancela um Pedido `PAGAMENTO_CONFIRMADO`
- **THEN** o Pedido vira `CANCELADO`, o pagamento vira `CANCELADO`, o estoque é devolvido, e a operação é idempotente (repetir retorna a mesma situação sem novo acréscimo de estoque)

#### Scenario: Funcionario cannot cancel orders
- **WHEN** um UsuarioInterno `FUNCIONARIO` tenta cancelar um Pedido
- **THEN** o backend nega com `accessdenied` e nada é alterado

#### Scenario: Administrator cannot cancel shipped or delivered orders
- **WHEN** um ADMIN tenta cancelar um Pedido em `ENVIADO` ou `ENTREGUE`
- **THEN** a operação é rejeitada sem efeito colateral

### Requirement: Cancellation is transactional and idempotent

A operação SHALL devolver a quantidade de cada ItemPedido ao estoque da VariaçãoProduto
correspondente (via `db.increment` com `id` e quantidade devolvida), marcar o Pedido como
`CANCELADO` e o Pagamento como `CANCELADO`, tudo em uma única transação. Se o Pedido já
estiver em `CANCELADO`, a operação SHALL retornar o estado atual sem alterar nada (nem
estoque). Cancelamentos em série SHALL NOT duplicar devolução. O Carrinho da sessão não
é afetado; o histórico do Pedido permanece acessível com o estado `CANCELADO`.

#### Scenario: Cancellation returns stock for each item
- **WHEN** um cancelamento é aplicado a um Pedido com múltiplos ItemPedido
- **THEN** cada VariaçãoProduto recebe de volta exatamente a quantidade registrada naquele ItemPedido, e nenhuma variação fora do pedido é alterada

#### Scenario: Repeating a cancellation does not double-return stock
- **WHEN** um pedido já cancelado é cancelado novamente
- **THEN** a operação retorna sucesso com o Pedido em `CANCELADO`, sem alterar o estoque

#### Scenario: Cancellation failure rolls back entirely
- **WHEN** qualquer passo da devolução de estoque falha no meio do caminho
- **THEN** nenhum estoque, Pedido ou Pagamento fica parcialmente persistido
