## ADDED Requirements

### Requirement: Active internal users can read sales metrics for a period

Um UsuarioInterno autenticado, `ATIVO` e com papel `FUNCIONARIO` ou `ADMINISTRADOR` SHALL
poder consultar métricas de vendas por período em `GET reports/sales`. Sem parâmetros, o
período SHALL ser os últimos 30 dias, inclusive hoje, em UTC. O cliente SHALL poder
informar `from` e/ou `to` no formato `YYYY-MM-DD`, interpretados como dias inteiros em UTC
e inclusivos nas duas pontas. A resposta SHALL conter `faturamento`, `pedidos`,
`ticket_medio`, `periodo`, `status_incluidos` e `serie_diaria`. Cliente, visitante e
UsuarioInterno `INATIVO` SHALL ser negados no backend.

#### Scenario: Funcionario reads the default period

- **WHEN** um FUNCIONARIO ativo chama `GET reports/sales` sem `from` nem `to`
- **THEN** o backend responde os últimos 30 dias inclusivos em UTC, com faturamento, quantidade de Pedidos, ticket médio e série diária

#### Scenario: Administrator reads an explicit range

- **WHEN** um ADMINISTRADOR ativo informa `from=2026-10-01` e `to=2026-10-31`
- **THEN** o backend considera apenas Pedidos com `data_pedido` entre 01/10/2026 00:00:00 e 31/10/2026 23:59:59 UTC

#### Scenario: A single boundary falls back to the 30-day window

- **WHEN** o usuário informa apenas `to`, sem `from`
- **THEN** o início é `to - 29 dias`, mantendo 30 dias inclusivos

#### Scenario: A single start boundary ends today

- **WHEN** o usuário informa apenas `from`, sem `to`
- **THEN** o fim é o dia atual em UTC

#### Scenario: Invalid or excessive periods are rejected

- **WHEN** a data não está em `YYYY-MM-DD`, o início é posterior ao fim, ou o intervalo passa de 366 dias inclusivos
- **THEN** o backend responde erro de entrada e não executa a consulta

#### Scenario: No sensitive data is exposed

- **WHEN** qualquer métrica é retornada
- **THEN** a resposta contém apenas agregados e datas, nunca nome, e-mail, CPF, telefone, senha, token ou identificador de Cliente

#### Scenario: Inactive internal user is denied

- **WHEN** um UsuarioInterno `INATIVO` tenta consultar as métricas
- **THEN** o backend nega com `accessdenied` e nada é retornado

### Requirement: Revenue and order count follow the approved status set

O faturamento SHALL ser a soma de `valor_total` dos Pedidos cujo status atual esteja em
`PAGAMENTO_CONFIRMADO`, `EM_PREPARACAO`, `ENVIADO` ou `ENTREGUE`. A quantidade SHALL ser a
contagem desses mesmos Pedidos. Pedidos em `AGUARDANDO_PAGAMENTO` e `CANCELADO` SHALL NOT
entrar em nenhuma das métricas. Cada Pedido SHALL contar uma única vez. O endpoint SHALL
ser somente leitura e SHALL NOT alterar Pedido, ItemPedido, Pagamento, estoque ou qualquer
outro dado.

#### Scenario: Confirmed and operational orders count

- **WHEN** existem Pedidos nos quatro status incluídos dentro do período
- **THEN** todos entram no faturamento e na quantidade, somando `valor_total` uma vez por Pedido

#### Scenario: Awaiting payment is excluded

- **WHEN** um Pedido está em `AGUARDANDO_PAGAMENTO` dentro do período
- **THEN** ele não entra no faturamento nem na quantidade

#### Scenario: Cancelled orders are excluded

- **WHEN** um Pedido foi cancelado, mesmo que já tenha estado pago no passado
- **THEN** ele não entra no faturamento nem na quantidade

#### Scenario: The approved status set is explicit in the response

- **WHEN** o backend responde as métricas
- **THEN** `status_incluidos` lista exatamente os quatro status usados na agregação

#### Scenario: Query is read-only

- **WHEN** a consulta é executada
- **THEN** nenhum registro é criado, alterado ou excluído

### Requirement: Period boundaries and empty results are deterministic

Os limites do período SHALL ser inclusivos nas duas pontas e calculados em UTC. A
`serie_diaria` SHALL conter apenas dias com Pedidos contabilizados, em ordem crescente de
data, com `data`, `faturamento` e `pedidos` por dia. Quando não houver Pedidos no período,
o backend SHALL responder sucesso com `faturamento=0`, `pedidos=0`, `ticket_medio=0` e
`serie_diaria=[]`. O `ticket_medio` SHALL ser zero quando não houver Pedidos e SHALL ser
arredondado para duas casas decimais.

#### Scenario: Empty period returns zeros

- **WHEN** nenhum Pedido incluído existe no período
- **THEN** a resposta é sucesso com totais zerados e série diária vazia

#### Scenario: Daily series is ascending and consolidated

- **WHEN** existem Pedidos em dias distintos do período
- **THEN** a série traz um item por dia com vendas, em ordem crescente, somando corretamente faturamento e quantidade

#### Scenario: Inclusive boundaries

- **WHEN** um Pedido tem `data_pedido` exatamente no início ou no fim do período
- **THEN** ele é incluído nas métricas

#### Scenario: Monetary values are rounded at the response boundary

- **WHEN** a soma dos valores resulta em mais de duas casas decimais
- **THEN** o faturamento, o ticket médio e os valores da série são arredondados para duas casas
