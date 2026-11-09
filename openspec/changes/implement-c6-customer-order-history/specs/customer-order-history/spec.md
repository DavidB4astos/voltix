## ADDED Requirements

### Requirement: Active internal users can read a customer's order history

Um UsuarioInterno autenticado, `ATIVO` e com papel `FUNCIONARIO` ou `ADMINISTRADOR` SHALL
poder consultar o histórico de Pedidos de um Cliente em `GET customers/{customer_id}/orders`.
O backend SHALL validar que o Cliente existe e responder `notfound` quando não existir.
A resposta SHALL ser paginada, com 20 Pedidos por página por padrão e máximo de 50, e
SHALL conter `cliente_id`, `items`, `page`, `per_page`, `total_items` e `total_pages`.
Os Pedidos SHALL ser ordenados por `data_pedido` decrescente e, em empate, por `id`
decrescente. Cliente, visitante e UsuarioInterno `INATIVO` SHALL ser negados no backend.

#### Scenario: Funcionario reads a customer history

- **WHEN** um FUNCIONARIO ativo chama `GET customers/42/orders`
- **THEN** o backend responde a primeira página de Pedidos do Cliente 42, do mais recente para o mais antigo

#### Scenario: Administrator applies pagination

- **WHEN** um ADMINISTRADOR ativo informa `page=2` e `per_page=50`
- **THEN** o backend responde a segunda página com até 50 Pedidos e os totais de itens e páginas

#### Scenario: Customer does not exist

- **WHEN** o `customer_id` informado não corresponde a um Cliente
- **THEN** o backend responde `notfound` e não executa a consulta de Pedidos

#### Scenario: Invalid pagination is rejected

- **WHEN** `page` é menor que 1 ou `per_page` está fora de 1–50
- **THEN** o backend responde `inputerror` e não executa a consulta

#### Scenario: Inactive internal user is denied

- **WHEN** um UsuarioInterno `INATIVO` tenta consultar o histórico
- **THEN** o backend nega com `accessdenied` e nada é retornado

#### Scenario: Customer and visitor are denied

- **WHEN** um Cliente autenticado ou um visitante sem sessão chama o endpoint interno
- **THEN** o backend nega o acesso antes de qualquer leitura

### Requirement: Each order includes its summary and item lines

Cada Pedido retornado SHALL conter `id`, `codigo`, `data_pedido`, `status`, `subtotal`,
`valor_frete`, `valor_total` e `itens`. Cada item SHALL conter `variacao_id`, `sku`,
`nome_ou_descricao`, `quantidade`, `preco_unitario` e `subtotal`, calculado como
`preco_unitario * quantidade`. Os valores SHALL ser os persistidos no Pedido e no
ItemPedido, sem recalcular preços atuais de catálogo. Pedido sem item persistido SHALL
retornar `itens` vazio, sem falhar.

#### Scenario: Order with items

- **WHEN** o histórico retorna um Pedido com itens persistidos
- **THEN** cada item traz SKU, nome da variação, quantidade, preço unitário e subtotal, preservando os valores da compra

#### Scenario: Order without persisted items

- **WHEN** um Pedido do histórico não possui ItemPedido
- **THEN** o Pedido é retornado com `itens: []` e os demais campos preservados

#### Scenario: Items belong to the correct order

- **WHEN** há vários Pedidos na página
- **THEN** cada lista `itens` contém apenas os itens do respectivo Pedido, sem misturar Pedidos

### Requirement: Filters and empty results are deterministic

O filtro `status` SHALL aceitar `TODOS` (padrão) ou um dos seis estados do Pedido. Os
filtros `from` e `to` SHALL ser opcionais, no formato `YYYY-MM-DD`, interpretados como
dias inteiros em UTC e inclusivos nas duas pontas. O backend SHALL validar o formato e
que o início não é posterior ao fim; caso contrário, responder `inputerror` sem executar
a consulta. Sem filtros de período, SHALL retornar todo o histórico paginado. Quando não
houver Pedidos, SHALL responder sucesso com `items=[]`, totais de itens zerados e página
válida. A consulta SHALL ser somente leitura.

#### Scenario: Status filter

- **WHEN** o usuário informa `status=ENTREGUE`
- **THEN** somente Pedidos `ENTREGUE` do Cliente entram na página e nos totais

#### Scenario: Inclusive period filter

- **WHEN** o usuário informa `from=2026-10-01` e `to=2026-10-31`
- **THEN** entram apenas Pedidos com `data_pedido` entre 01/10/2026 00:00:00 e 31/10/2026 23:59:59 UTC

#### Scenario: Invalid period is rejected

- **WHEN** uma data não está em `YYYY-MM-DD` ou o início é posterior ao fim
- **THEN** o backend responde `inputerror` e não executa a consulta

#### Scenario: Empty history returns an empty page

- **WHEN** o Cliente não possui Pedidos ou nenhum Pedido atende aos filtros
- **THEN** a resposta é sucesso com `items=[]` e `total_items=0`

### Requirement: History is read-only and exposes no sensitive customer data

O endpoint SHALL ser somente leitura e SHALL NOT alterar Pedido, ItemPedido, Pagamento,
Cliente, estoque ou qualquer outro dado. A resposta SHALL NOT conter nome, e-mail, CPF,
telefone, endereço, senha, token ou qualquer identificador de autenticação do Cliente;
somente `cliente_id` SHALL identificar o Cliente.

#### Scenario: Query is read-only

- **WHEN** o histórico é consultado
- **THEN** nenhum Pedido, ItemPedido, Pagamento, Cliente ou estoque é criado, alterado ou excluído

#### Scenario: No sensitive customer data is exposed

- **WHEN** o histórico é retornado
- **THEN** a resposta não contém nome, e-mail, CPF, telefone, endereço, senha ou token do Cliente, apenas `cliente_id`
