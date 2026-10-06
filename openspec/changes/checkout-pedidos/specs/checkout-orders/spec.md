## Purpose

Permitir que um Cliente autenticado confirme uma compra a partir do próprio Carrinho e consulte o Pedido criado, mantendo os valores comerciais e itens registrados para preservar o histórico da compra.

## ADDED Requirements

### Requirement: Customers can review and confirm their own cart as an order
O sistema SHALL permitir que um Cliente `ATIVO` autenticado revise o próprio Carrinho e selecione um Endereço `ATIVO` pertencente a esse Cliente. O backend SHALL rejeitar Carrinho vazio, endereço inexistente, inativo ou de outro Cliente, e SHALL validar novamente na confirmação a existência, status `ATIVO`, preço atual e estoque disponível de cada Produto e VariaçãoProduto.

#### Scenario: Customer reviews a valid cart and address
- **WHEN** um Cliente consulta a revisão do próprio Carrinho e escolhe um Endereço ativo próprio
- **THEN** o sistema apresenta itens, quantidades, preços atuais, subtotais por item, subtotal do Pedido, frete zero e total antes da confirmação

#### Scenario: Empty cart cannot be checked out
- **WHEN** o Cliente tenta revisar ou confirmar um Carrinho sem itens
- **THEN** o sistema rejeita a operação e não cria Pedido, ItemPedido ou Pagamento

#### Scenario: Customer selects an address owned by another customer
- **WHEN** o Cliente seleciona um Endereço inexistente ou pertencente a outro Cliente
- **THEN** o backend rejeita a operação sem revelar dados do endereço nem criar um Pedido

#### Scenario: Inactive address cannot be used
- **WHEN** o Cliente tenta confirmar com um Endereço próprio inativo
- **THEN** o backend rejeita a confirmação e preserva o Carrinho

#### Scenario: Product or variation became inactive or unavailable
- **WHEN** um Produto ou VariaçãoProduto do Carrinho não está ativo ou o estoque atual é inferior à quantidade solicitada
- **THEN** o backend rejeita a confirmação, informa quais itens precisam ser revistos e preserva o Carrinho sem criar Pedido

#### Scenario: Price or cart contents changed after review
- **WHEN** preço, quantidade, status, estoque ou conteúdo do Carrinho difere dos dados apresentados na revisão quando o Cliente confirma
- **THEN** o sistema não confirma silenciosamente valores diferentes, retorna uma revisão atualizada e exige nova confirmação do Cliente

#### Scenario: Checkout requires an active customer session
- **WHEN** uma requisição de revisão ou confirmação não possui sessão válida de Cliente ativo
- **THEN** o backend rejeita a operação sem retornar ou alterar dados comerciais

### Requirement: Confirmed orders preserve required purchase history
Após confirmação válida, o sistema SHALL criar atomicamente um Pedido pertencente ao Cliente, associado ao Endereço escolhido, com código comercial único separado do identificador interno, data, status `AGUARDANDO_PAGAMENTO`, subtotal igual à soma dos ItemPedido, frete zero e total igual ao subtotal acrescido do frete. O Pedido SHALL possuir ao menos um ItemPedido e exatamente um Pagamento `PENDENTE` cujo valor seja igual ao total. O Cliente SHALL escolher um método permitido pelo Domain Model (`PIX`, `CARTAO` ou `BOLETO`); esta Change SHALL apenas registrar essa escolha, sem iniciar, simular ou aprovar pagamento. Cada ItemPedido SHALL consolidar a variação, quantidade inteira positiva e preço unitário vigente no instante de confirmação, sem duplicar variações.

#### Scenario: Successful confirmation creates order, items, and pending payment
- **WHEN** o Cliente confirma novamente a revisão atualizada e válida
- **THEN** o sistema cria um Pedido, um ItemPedido por VariaçãoProduto, um Pagamento pendente de valor igual ao total e esvazia o Carrinho após o commit bem-sucedido

#### Scenario: Order snapshots preserve historical unit prices
- **WHEN** o preço de uma VariaçãoProduto muda depois da confirmação
- **THEN** o resumo do Pedido continua exibindo o preço unitário, subtotal e total registrados na compra

#### Scenario: Order confirmation fails partway through persistence
- **WHEN** a criação de qualquer dado obrigatório do Pedido falha
- **THEN** Pedido, itens e Pagamento não ficam parcialmente persistidos e o Carrinho permanece intacto

#### Scenario: Cart contents are not consumed before order commit
- **WHEN** uma confirmação é rejeitada ou falha antes da persistência atômica completa
- **THEN** nenhum ItemCarrinho é removido e nenhum estoque é alterado

#### Scenario: Checkout does not reduce or reserve stock
- **WHEN** um Pedido é confirmado nesta Change
- **THEN** a disponibilidade de estoque é apenas validada no momento da confirmação e nenhuma quantidade é baixada ou reservada

### Requirement: Customers can view only their own order history and summaries
O sistema SHALL permitir que um Cliente autenticado liste e consulte os resumos dos próprios Pedidos, incluindo código, data, status, snapshot do endereço de entrega e itens/valores históricos. O backend SHALL derivar o proprietário da sessão Cliente e rejeitar acesso a Pedidos de terceiros. Todo Pedido SHALL conservar a referência ao Endereço e um snapshot dos dados de entrega selecionados, além dos ItemPedido associados como histórico.

#### Scenario: Customer views own order history
- **WHEN** um Cliente autenticado consulta seu histórico
- **THEN** o sistema retorna somente Pedidos pertencentes àquele Cliente e seus resumos históricos

#### Scenario: Customer views an own order confirmation
- **WHEN** o Cliente consulta um Pedido criado por si
- **THEN** o sistema apresenta código, status, dados de entrega copiados na confirmação, itens, quantidades, preços unitários, subtotais, frete e total persistidos

#### Scenario: Later address edits do not alter an existing order
- **WHEN** o Cliente edita ou inativa o Endereço após confirmar um Pedido
- **THEN** o resumo do Pedido mantém os dados de entrega capturados no instante da confirmação

#### Scenario: Customer cannot access another customer's order
- **WHEN** um Cliente tenta consultar um Pedido de terceiro por identificador
- **THEN** o backend rejeita o acesso sem revelar conteúdo nem valores do Pedido

#### Scenario: Unauthenticated user cannot view orders
- **WHEN** uma requisição de histórico ou resumo não possui sessão válida de Cliente ativo
- **THEN** o backend rejeita a operação sem retornar Pedidos

### Requirement: Checkout uses Reflex State and reports failures without false success
A interface SHALL encaminhar revisão, confirmação e consulta de Pedidos ao State/lógica Python Reflex, que SHALL realizar chamadas HTTP server-side ao Xano utilizando somente a sessão de Cliente. Falhas e revisões expiradas SHALL ser apresentadas sem indicar confirmação falsa e SHALL preservar os dados previamente confirmados.

#### Scenario: Checkout request uses the customer session through State
- **WHEN** o Cliente revisa ou confirma o Carrinho pela interface
- **THEN** o State/Python chama o Xano usando o token de Cliente e nenhum segredo ou chamada autenticada direta é exposto ao navegador

#### Scenario: Confirmation failure remains visible
- **WHEN** validação, autorização ou comunicação falha durante a confirmação
- **THEN** a interface apresenta a falha e não anuncia um Pedido como criado

#### Scenario: Order flow does not process payment or freight
- **WHEN** o Cliente confirma um Pedido nesta Change
- **THEN** nenhum pagamento real/aprovação, gateway, cotação ou integração de frete é executado
