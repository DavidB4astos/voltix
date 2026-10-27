## Purpose

Definir o comportamento de baixa de estoque durante a confirmação do Pedido: a confirmação válida baixa atomicamente a quantidade disponível das variações do Carrinho, garante que o estoque nunca se torne negativo e serializa a disputa pela última unidade, preservando o contrato de resposta atual e o comportamento do Carrinho sem reserva.

## REMOVED Requirements

### Requirement: Confirmed orders preserve required purchase history
Substituído por "Confirmed orders preserve purchase history and reduce stock", que mantém o histórico de compra exigido e passa a baixar estoque atomicamente na confirmação. O cenário anterior que afirmava que o checkout não reduz estoque deixa de valer.

## ADDED Requirements

### Requirement: Confirmed orders preserve purchase history and reduce stock
Após confirmação válida, o sistema SHALL criar atomicamente um Pedido pertencente ao Cliente, associado ao Endereço escolhido, com código comercial único separado do identificador interno, data, status `AGUARDANDO_PAGAMENTO`, subtotal igual à soma dos ItemPedido, frete zero e total igual ao subtotal acrescido do frete. O Pedido SHALL possuir ao menos um ItemPedido e exatamente um Pagamento `PENDENTE` cujo valor seja igual ao total. O Cliente SHALL escolher um método permitido pelo Domain Model (`PIX`, `CARTAO` ou `BOLETO`); esta Change SHALL apenas registrar essa escolha, sem iniciar, simular ou aprovar pagamento. Cada ItemPedido SHALL consolidar a variação, quantidade inteira positiva e preço unitário vigente no instante de confirmação, sem duplicar variações. Na mesma transação de confirmação, o sistema SHALL baixar de cada VariaçãoProduto a quantidade correspondente ao ItemPedido, de modo que estoque e Pedido sejam persistidos ou revertidos juntos.

#### Scenario: Successful confirmation creates order, items, and pending payment
- **WHEN** o Cliente confirma novamente a revisão atualizada e válida
- **THEN** o sistema cria um Pedido, um ItemPedido por VariaçãoProduto, um Pagamento pendente de valor igual ao total, baixa o estoque correspondente e esvazia o Carrinho após o commit bem-sucedido

#### Scenario: Order snapshots preserve historical unit prices
- **WHEN** o preço de uma VariaçãoProduto muda depois da confirmação
- **THEN** o resumo do Pedido continua exibindo o preço unitário, subtotal e total registrados na compra

#### Scenario: Order confirmation fails partway through persistence
- **WHEN** a criação de qualquer dado obrigatório do Pedido ou a baixa de estoque falha
- **THEN** Pedido, itens, Pagamento e baixa de estoque não ficam parcialmente persistidos e o Carrinho permanece intacto

#### Scenario: Cart contents are not consumed before order commit
- **WHEN** uma confirmação é rejeitada ou falha antes da persistência atômica completa
- **THEN** nenhum ItemCarrinho é removido e nenhum estoque é alterado

#### Scenario: Cart does not reserve stock
- **WHEN** uma VariaçãoProduto é adicionada ou mantida no Carrinho
- **THEN** a quantidade disponível permanece inalterada; o estoque é baixado somente em uma confirmação de Pedido bem-sucedida

### Requirement: Stock decrements are atomic and never negative
A baixa de estoque SHALL ocorrer somente dentro da transação de confirmação, condicionada à disponibilidade vigente, e SHALL impedir valores negativos e a venda concorrente da última unidade. Quando o estoque for insuficiente ou a VariaçãoProduto/Produto não estiver `ATIVO`, o sistema SHALL manter o comportamento de resposta HTTP 200 com `confirmado=false`, sem criar Pedido, ItemPedido ou Pagamento e sem alterar o estoque. A baixa nunca SHALL deixar Pedido persistido sem baixa correspondente, nem baixa persistida sem Pedido correspondente.

#### Scenario: Insufficient stock rejects the whole order
- **WHEN** o Cliente confirma uma revisão válida cujo item não possui estoque suficiente, ou a VariaçãoProduto/Produto não está `ATIVO`
- **THEN** o backend retorna HTTP 200 com `confirmado=false`, não cria Pedido, ItemPedido ou Pagamento, mantém o Carrinho intacto e não altera o estoque

#### Scenario: Concurrent purchases of the last unit are serialized
- **WHEN** duas confirmações concorrentes disputam a última unidade disponível de uma VariaçãoProduto
- **THEN** exatamente uma confirmação conclui o Pedido com a baixa exata, a outra retorna `confirmado=false`, e o estoque final é `0`, nunca negativo

#### Scenario: Failure after decrement rolls back order and stock together
- **WHEN** qualquer passo da persistência falha após a baixa de estoque
- **THEN** a baixa e o Pedido, itens e Pagamento são revertidos conjuntamente, sem baixa órfã e sem Pedido parcial

#### Scenario: Zero stock keeps the variation active
- **WHEN** a baixa reduz a quantidade disponível de uma VariaçãoProduto a `0`
- **THEN** a VariaçãoProduto permanece `ATIVO`, apenas indisponível para novas compras
