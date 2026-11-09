## Purpose

Definir a seção desktop de Dashboard do painel interno, que permite a usuários internos ativos
consultar métricas agregadas de vendas por período — faturamento, quantidade de Pedidos,
ticket médio e série diária — sem alterar dados e sem expor informações pessoais ou
identificadores de Cliente.

## ADDED Requirements

### Requirement: Dashboard is restricted to active internal users

A seção Dashboard SHALL ser apresentada somente dentro de uma sessão interna validada de
UsuarioInterno `ATIVO` com papel `FUNCIONARIO` ou `ADMINISTRADOR`. Visitantes, Clientes e
usuários internos `INATIVO` SHALL NOT visualizar nem operar a seção. O backend SHALL
permanecer a autoridade final. Uma resposta `401` ou `403` na leitura SHALL encerrar a sessão
e limpar os dados carregados.

#### Scenario: Active employee opens the dashboard

- **WHEN** um FUNCIONARIO `ATIVO` seleciona a seção Dashboard
- **THEN** a seção é apresentada com o período e as métricas consultadas usando o token interno

#### Scenario: Administrator opens the dashboard

- **WHEN** um ADMINISTRADOR `ATIVO` seleciona a seção Dashboard
- **THEN** a seção é apresentada com os mesmos filtros e métricas, sem controles adicionais

#### Scenario: Customer or inactive user is denied

- **WHEN** um Cliente ou UsuarioInterno `INATIVO` tenta acessar as métricas
- **THEN** o backend nega o acesso e a seção não renderiza dados

#### Scenario: Unauthorized read ends the session

- **WHEN** a consulta de métricas responde `401` ou `403`
- **THEN** a sessão interna é encerrada e os dados do Dashboard são descartados

### Requirement: Period filter is validated locally and defaults to the backend window

A seção SHALL oferecer filtros opcionais `from` e `to` no formato `YYYY-MM-DD`, interpretados
como dias inteiros em UTC e inclusivos. Quando ambos estiverem vazios, a consulta SHALL usar
o período padrão de 30 dias do backend. Quando apenas um limite for informado, o backend SHALL
completar a janela. A seção SHALL rejeitar localmente data malformada, início posterior ao fim
ou intervalo acima de 366 dias, sem enviar requisição. O período efetivamente aplicado SHALL
ser o retornado pelo backend, não um cálculo do navegador.

#### Scenario: Default period without filters

- **WHEN** o usuário carrega o Dashboard sem informar `from` nem `to`
- **THEN** a requisição não envia limites e o período exibido é o retornado pelo backend

#### Scenario: Explicit inclusive range

- **WHEN** o usuário informa `from=2026-10-01` e `to=2026-10-31`
- **THEN** a requisição envia exatamente esses valores e exibe o período retornado

#### Scenario: Invalid date or inverted range

- **WHEN** a data não está em `YYYY-MM-DD` ou o início é posterior ao fim
- **THEN** a seção informa o erro, descarta resultados anteriores inconsistentes e não envia requisição

#### Scenario: Excessive range is rejected locally

- **WHEN** o intervalo informado passa de 366 dias inclusivos
- **THEN** a seção informa o erro e não envia requisição

#### Scenario: Backend rejects the period

- **WHEN** o backend responde `400` para o período informado
- **THEN** a seção informa que o período é inválido e mantém a sessão

### Requirement: Dashboard presents aggregated sales metrics and daily series

A seção SHALL apresentar `faturamento`, `pedidos`, `ticket_medio`, o período aplicado e os
`status_incluidos` retornados pelo backend. A série diária SHALL ser exibida em tabela com
`data`, `faturamento` e `pedidos`, em ordem crescente. Os valores monetários SHALL ser
apresentados com duas casas decimais sem recálculo aritmético no navegador. Quando não houver
Pedidos no período, a seção SHALL apresentar totais zerados e ausência de série. A seção SHALL
NOT exibir nome, e-mail, CPF, telefone, senha, hash, token ou identificador de Cliente.

#### Scenario: Metrics are displayed

- **WHEN** o backend responde métricas no período
- **THEN** faturamento, quantidade de Pedidos, ticket médio, período e status incluídos são exibidos

#### Scenario: Empty period shows zeros

- **WHEN** o backend responde `pedidos=0`
- **THEN** a seção exibe faturamento e ticket médio zerados e informa que não houve vendas no período

#### Scenario: Daily series is presented in ascending order

- **WHEN** a resposta contém `serie_diaria`
- **THEN** cada dia é exibido com data, faturamento e quantidade, na ordem recebida

#### Scenario: Approved status set is explicit

- **WHEN** as métricas são exibidas
- **THEN** a seção mostra os quatro status incluídos na agregação

#### Scenario: No sensitive data is rendered

- **WHEN** qualquer métrica ou série é exibida
- **THEN** apenas agregados, datas e status são apresentados, sem dados pessoais ou identificadores de Cliente

### Requirement: Dashboard validates the response before rendering

A seção SHALL validar a resposta antes de apresentá-la: chaves exatas, tipos numéricos,
período em UTC, `status_incluidos` exatamente com os quatro status aprovados, série diária
sem datas duplicadas e em ordem crescente, e coerência entre os totais e a série. Respostas
malformadas SHALL NOT ser renderizadas e SHALL produzir mensagem de erro sem alterar a sessão.
Respostas obsoletas SHALL ser descartadas por geração, token e usuário.

#### Scenario: Extra or missing fields are rejected

- **WHEN** a resposta contém campo extra, ausente ou tipo inválido
- **THEN** a seção não renderiza os dados e informa erro de consulta

#### Scenario: Inconsistent totals are rejected

- **WHEN** a soma da série não corresponde a `pedidos` ou `ticket_medio` é incompatível com os totais
- **THEN** a seção não renderiza os dados e informa erro de consulta

#### Scenario: Duplicate or descending dates are rejected

- **WHEN** a série repete uma data ou não está em ordem crescente
- **THEN** a seção não renderiza os dados e informa erro de consulta

#### Scenario: Stale response is discarded

- **WHEN** uma consulta anterior termina após o usuário trocar o período ou encerrar a sessão
- **THEN** a resposta obsoleta não substitui os dados atuais

### Requirement: Dashboard is read-only

A seção SHALL ser somente leitura. Ela SHALL NOT oferecer criação, edição, cancelamento,
avanço de status de Pedido, alteração de Pagamento ou qualquer operação de escrita.

#### Scenario: No write operation is offered

- **WHEN** o usuário navega pelo Dashboard
- **THEN** apenas filtros de período e recarga são oferecidos, sem comandos que alterem dados
