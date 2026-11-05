## MODIFIED Requirements

### Requirement: Confirmed orders preserve required purchase history

Após confirmação válida, o sistema SHALL criar atomicamente um Pedido pertencente ao Cliente, associado ao Endereço escolhido, com código comercial único separado do identificador interno, data, status `AGUARDANDO_PAGAMENTO`, subtotal igual à soma dos ItemPedido, frete zero e total igual ao subtotal acrescido do frete. O Pedido SHALL possuir ao menos um ItemPedido e exatamente um Pagamento `PENDENTE` cujo valor seja igual ao total. O Cliente SHALL escolher um método permitido pelo Domain Model (`PIX`, `CARTAO` ou `BOLETO`); a Change SHALL apenas registrar essa escolha, sem iniciar, simular ou aprovar pagamento. Cada ItemPedido SHALL consolidar a variação, quantidade inteira positiva e preço unitário vigente no instante de confirmação, sem duplicar variações. Durante a mesma transação que cria o Pedido, o sistema SHALL baixar o estoque de cada VariaçãoProduto pela quantidade do ItemPedido, utilizando `db.increment` com guarda por condição (`id == variacao_id && quantidade_disponivel >= quantidade && status == "ATIVO"`) e `return = {type: "count"}`; se qualquer baixa afetar zero linhas, o sistema SHALL reverter integralmente o Pedido, os ItemPedido, o Pagamento, as baixas de estoque e a limpeza do Carrinho, respondendo HTTP 200 com `confirmado=false`. O estoque SHALL NUNCA ficar negativo e SHALL NUNCA ser reservado fora da confirmação (o Carrinho não reserva estoque).

#### Scenario: Successful confirmation creates order, items, and pending payment
- **WHEN** o Cliente confirma novamente a revisão atualizada e válida e todos os itens possuem estoque suficiente e estão ATIVO
- **THEN** o sistema cria um Pedido, um ItemPedido por VariaçãoProduto, um Pagamento pendente de valor igual ao total, baixa o estoque de cada variação por suas unidades e esvazia o Carrinho após o commit bem-sucedido

#### Scenario: Order snapshots preserve historical unit prices
- **WHEN** o preço de uma VariaçãoProduto muda depois da confirmação
- **THEN** o resumo do Pedido continua exibindo o preço unitário, subtotal e total registrados na compra

#### Scenario: Order confirmation fails partway through persistence
- **WHEN** a criação de qualquer dado obrigatório do Pedido falha ou o decremento guardado de algum item afeta zero linhas
- **THEN** Pedido, itens, Pagamento, baixas de estoque e limpeza do Carrinho não ficam parcialmente persistidos e o Carrinho permanece intacto

#### Scenario: Cart contents are not consumed before order commit
- **WHEN** uma confirmação é rejeitada ou falha antes da persistência atômica completa
- **THEN** nenhum ItemCarrinho é removido e nenhum estoque é alterado

#### Scenario: Checkout does not reduce or reserve stock
- **WHEN** o Cliente revisa o carrinho ou ainda não confirmou a compra
- **THEN** nenhuma unidade é baixada ou reservada; a baixa de estoque ocorre somente dentro da transação de confirmação do Pedido e atomicamente junto com a criação dos dados do Pedido

#### Scenario: Insufficient stock during confirmation rolls back everything
- **WHEN** no momento da confirmação algum item não possui estoque suficiente ou a Variação/Produto não está ATIVO
- **THEN** o sistema responde HTTP 200 com `confirmado=false`, nenhum Pedido, ItemPedido ou Pagamento é criado, nenhum estoque é alterado e o Carrinho permanece intacto

#### Scenario: Stock cannot go negative or be double-sold
- **WHEN** dois Clientes confirmam, simultaneamente, pedidos da última unidade do mesmo SKU
- **THEN** no máximo uma venda é confirmada; a outra responde HTTP 200 com `confirmado=false`; o estoque final é zero

### Requirement: Checkout item reads share the same explicit order

Checkout review, the preliminary confirmation read and the confirmation read inside the existing transaction SHALL order returned ItemCarrinho records by ItemCarrinho id ascending before building review items and snapshots. Ordering SHALL preserve ownership checks, address validation, availability, prices, quantities, totals, stale-review comparison and existing atomic persistence. The stock decrements introduced by the confirmation SHALL use the same ordering and the same transaction, and SHALL NOT reservation outside the confirmation.

#### Scenario: Customer reviews multiple cart items
- **WHEN** o Cliente revisa o carrinho com múltiplos itens
- **THEN** both the review items and the snapshot follow ascending ItemCarrinho id order without changing their values

#### Scenario: Confirmation rebuilds a review
- **WHEN** a confirmação relê os itens antes e dentro da transação
- **THEN** both queries explicitly use ascending ItemCarrinho id order before the existing snapshot comparison

#### Scenario: Commercial data changed after review
- **WHEN** a revisão corrente difere da enviada porque dados comerciais mudaram
- **THEN** a rejeição de revisão obsoleta e a revisão atualizada continuam em vigor sem confirmar silenciosamente valores diferentes
