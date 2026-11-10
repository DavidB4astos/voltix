## Purpose

Definir a seção CRM do painel interno, que apresenta um retrato somente leitura do
relacionamento com os Clientes — Clientes ativos, Atendimentos por situação, Pedidos
registrados, últimos Atendimentos e o resumo de vendas do período padrão do backend —
usando exclusivamente endpoints já publicados e sem expor dados pessoais.

## ADDED Requirements

### Requirement: CRM dashboard is restricted to active internal users

A seção CRM SHALL ser apresentada somente dentro de uma sessão interna validada de
UsuarioInterno `ATIVO` com papel `FUNCIONARIO` ou `ADMINISTRADOR`. Visitantes, Clientes e
usuários internos `INATIVO` SHALL NOT visualizar nem operar a seção. O backend SHALL
permanecer a autoridade final. Uma resposta `401` ou `403` em qualquer leitura SHALL
encerrar a sessão e limpar os dados carregados.

#### Scenario: Active employee opens the CRM section

- **WHEN** um FUNCIONARIO `ATIVO` seleciona a seção CRM
- **THEN** a seção é apresentada e inicia a carga dos indicadores com o token interno

#### Scenario: Administrator opens the CRM section

- **WHEN** um ADMINISTRADOR `ATIVO` seleciona a seção CRM
- **THEN** a seção é apresentada com os mesmos indicadores e atalhos, sem controles adicionais

#### Scenario: Customer or inactive user is denied

- **WHEN** um Cliente ou UsuarioInterno `INATIVO` tenta selecionar a seção CRM
- **THEN** a seção não é apresentada e nenhuma leitura é emitida

#### Scenario: Unauthorized read ends the session

- **WHEN** qualquer leitura do CRM responde `401` ou `403`
- **THEN** a sessão interna é encerrada, os dados do CRM são descartados e a seleção volta a Clientes

### Requirement: Indicators are read from published endpoints with exact totals

A seção SHALL obter os indicadores exclusivamente dos endpoints já publicados, sem criar,
alterar ou publicar backend:

- Clientes ativos: `GET internal_customers` com `status=ATIVO` e `per_page=1`, usando
  `total_items`.
- Atendimentos abertos, em atendimento e finalizados: `GET atendimentos` com o respectivo
  `status` e `per_page=1`, usando `total_items`.
- Pedidos registrados: `GET internal_orders` com `status=TODOS` e `per_page=1`, usando
  `total_items`.
- Últimos Atendimentos: `GET atendimentos` com `status=TODOS`, `page=1` e `per_page=10`.
- Vendas: `GET reports/sales` sem `from` nem `to`, exibindo o período retornado pelo backend.

Os totais SHALL ser exatamente os `total_items` retornados, nunca a contagem de itens de uma
página. A seção SHALL NOT calcular datas, somas ou médias de vendas no navegador.

#### Scenario: Exact totals above one page

- **WHEN** um indicador tem mais registros do que cabem em uma página
- **THEN** o valor exibido é o `total_items` retornado pelo backend, não a quantidade de itens recebidos

#### Scenario: Recent attendances are bounded

- **WHEN** a seção carrega os últimos Atendimentos
- **THEN** no máximo 10 registros são solicitados, na ordem decrescente definida pelo backend

#### Scenario: Sales use the backend default window

- **WHEN** a seção carrega as vendas
- **THEN** nenhum limite de data é enviado e o período exibido é o retornado pelo backend

#### Scenario: No backend change is required

- **WHEN** a seção é implementada ou executada
- **THEN** nenhuma publicação, tabela, função ou permissão do Xano é criada ou alterada

### Requirement: CRM dashboard presents relationship and sales blocks

A seção SHALL apresentar, em blocos distintos:

- **Relacionamento**: Clientes ativos, Atendimentos abertos, Atendimentos em atendimento,
  Atendimentos finalizados e Pedidos registrados.
- **Vendas no período**: faturamento, Pedidos faturados, ticket médio e o período retornado
  pelo backend.
- **Últimos Atendimentos**: data, assunto, situação, responsável e identificação do Cliente
  por `cliente_id`.

Cada indicador SHALL ter rótulo textual e valor legível. Os blocos SHALL ser identificados
programaticamente. Quando não houver Atendimentos, a lista SHALL informar ausência de
registros sem ocultar os demais blocos. Quando não houver vendas no período, os valores
SHALL ser os zeros retornados pelo backend.

#### Scenario: Metrics are displayed

- **WHEN** todas as leituras respondem com sucesso
- **THEN** os cinco indicadores de relacionamento, os três de vendas e a lista de Atendimentos são exibidos

#### Scenario: No attendances

- **WHEN** a leitura de últimos Atendimentos retorna zero registros
- **THEN** a seção informa que não há Atendimentos e mantém os indicadores e as vendas visíveis

#### Scenario: No sales in the default period

- **WHEN** o backend retorna `pedidos=0` para o período padrão
- **THEN** faturamento, Pedidos faturados e ticket médio são exibidos conforme a resposta, sem inventar valores

#### Scenario: Status labels are explicit

- **WHEN** os indicadores de Atendimento são exibidos
- **THEN** cada valor tem rótulo próprio e não depende apenas de cor ou ícone

### Requirement: Dashboard load is all-or-nothing and discarded when stale

A carga SHALL ser disparada ao selecionar a seção CRM ou ao acionar a atualização manual.
Enquanto qualquer leitura estiver em andamento, a seção SHALL indicar carregamento e SHALL
NOT aceitar nova atualização. Se qualquer leitura falhar, a seção SHALL NOT renderizar
números parciais: apresenta mensagem de erro e permite nova tentativa. Respostas de uma
sessão ou geração anterior SHALL NOT substituir o estado atual.

#### Scenario: Partial failure shows no numbers

- **WHEN** uma das sete leituras falha por rede, resposta inválida ou erro do servidor
- **THEN** nenhum indicador é renderizado e a seção informa que a consulta está indisponível

#### Scenario: Retry after failure

- **WHEN** o usuário aciona a atualização após uma falha
- **THEN** todas as leituras são executadas novamente e os números só aparecem com sucesso completo

#### Scenario: Stale response is discarded

- **WHEN** uma resposta termina após o usuário encerrar a sessão ou trocar de seção
- **THEN** a resposta antiga não substitui os dados atuais

#### Scenario: Loading is explicit

- **WHEN** a carga está em andamento
- **THEN** a seção apresenta estado de carregamento em região anunciada e bloqueia a atualização

### Requirement: Shortcuts only navigate

A seção SHALL oferecer atalhos para as seções Clientes, Atendimentos e Pedidos. Acionar um
atalho SHALL apenas selecionar a seção autorizada correspondente, sem emitir escrita. O
atalho para uma seção não autorizada SHALL NOT ser oferecido.

#### Scenario: Shortcut opens customers

- **WHEN** o usuário aciona o atalho de Clientes
- **THEN** a seção Clientes é selecionada e nenhuma mutação é emitida

#### Scenario: Shortcut opens attendances

- **WHEN** o usuário aciona o atalho de Atendimentos
- **THEN** a seção Atendimentos é selecionada e sua carga de leitura existente é iniciada

#### Scenario: Shortcut opens orders

- **WHEN** o usuário aciona o atalho de Pedidos
- **THEN** a seção Pedidos é selecionada e sua carga de leitura existente é iniciada

### Requirement: CRM dashboard is read-only and private

A seção SHALL ser somente leitura: SHALL NOT criar, editar, inativar, excluir, cancelar,
pagar ou avançar status de Cliente, Atendimento, Pedido, Pagamento ou Produto. A seção
SHALL NOT exibir nome, e-mail, CPF, telefone, endereço, senha, hash, token ou URL privada.
A identificação de Cliente em Atendimentos SHALL permanecer por `cliente_id`.

#### Scenario: No write operation is offered

- **WHEN** o usuário navega pelo CRM
- **THEN** apenas a atualização da leitura e os atalhos de seção são oferecidos

#### Scenario: No sensitive data is rendered

- **WHEN** indicadores e Atendimentos são exibidos
- **THEN** apenas contagens, datas, situações, assuntos, responsável e `cliente_id` aparecem

#### Scenario: Token stays server-side

- **WHEN** a seção executa qualquer leitura
- **THEN** a requisição usa o token interno no servidor e o navegador recebe apenas dados sanitizados
