## ADDED Requirements

### Requirement: Selected customer loads a read-only order history

Ao abrir o detalhe de um Cliente autorizado, o painel interno SHALL carregar
automaticamente a primeira página do histórico de Pedidos daquele Cliente, usando
exclusivamente o endpoint publicado `GET customers/{customer_id}/orders`. A seção SHALL
aparecer em largura total abaixo da lista/detalhe de Clientes e SHALL exibir código,
data, status, subtotal, frete, total e itens de cada Pedido. A seção SHALL ser somente
leitura e SHALL NOT criar, alterar, cancelar ou excluir Pedido, item, pagamento ou
Cliente. Fechar o detalhe, trocar o Cliente ou atualizar a lista SHALL remover o
histórico anterior.

#### Scenario: Opening a customer loads the history

- **WHEN** um FUNCIONARIO ou ADMINISTRADOR ativo seleciona um Cliente existente
- **THEN** o painel exibe a ficha do Cliente e inicia o carregamento da primeira página do histórico daquele Cliente

#### Scenario: Closing or changing the customer clears the history

- **WHEN** o usuário fecha o detalhe, seleciona outro Cliente ou executa a atualização da lista
- **THEN** o histórico do Cliente anterior deixa de ser exibido e respostas pendentes dele são descartadas

#### Scenario: History is read-only

- **WHEN** o histórico é carregado ou filtrado
- **THEN** nenhuma requisição de escrita é emitida e nenhum dado de Cliente ou Pedido é alterado

### Requirement: History uses bounded filters and pagination

A seção SHALL oferecer filtro de status com `TODOS` como padrão e os seis estados do
Pedido, além de período opcional `from`/`to` em `YYYY-MM-DD`, interpretado em UTC e
inclusivo. Sem filtros, SHALL exibir todo o histórico paginado. A paginação SHALL usar
20 Pedidos por página, com controles anterior/próxima limitados às páginas retornadas
pelo backend. Aplicar filtros SHALL voltar à página 1. Datas inválidas ou início
posterior ao fim SHALL ser rejeitados antes da requisição, com mensagem distinta.

#### Scenario: Default history shows everything

- **WHEN** o usuário abre o histórico sem alterar filtros
- **THEN** a consulta usa `status=TODOS` e nenhum período, exibindo a primeira página de 20 Pedidos

#### Scenario: Applying valid filters

- **WHEN** o usuário escolhe um status e/ou informa `from` e `to` válidos e aplica os filtros
- **THEN** a consulta reinicia na página 1 e exibe apenas os Pedidos que atendem aos critérios

#### Scenario: Invalid period is rejected locally

- **WHEN** uma data não está em `YYYY-MM-DD` ou o início é posterior ao fim
- **THEN** o painel informa o erro, não emite requisição e preserva os filtros anteriores

#### Scenario: Pagination is bounded by the response

- **WHEN** o histórico tem mais de uma página
- **THEN** os controles avançam ou voltam somente dentro de `1..total_pages` e atualizam os contadores exibidos

### Requirement: Order items are presented with persisted values

Cada Pedido SHALL exibir seus itens sempre expandidos, com SKU, descrição, quantidade,
preço unitário e subtotal. Os valores SHALL ser os persistidos no Pedido e no
ItemPedido, sem recalcular preços atuais de catálogo. Pedido sem itens SHALL exibir um
aviso local e preservar o resumo, sem falhar a seção. SKU ou descrição ausentes SHALL ser
apresentados como indisponíveis, sem interromper a renderização.

#### Scenario: Order with items

- **WHEN** um Pedido do histórico possui itens
- **THEN** a seção mostra a tabela de itens com os valores persistidos e o subtotal de cada linha

#### Scenario: Order without items

- **WHEN** um Pedido do histórico retorna `itens: []`
- **THEN** o resumo do Pedido continua visível e a seção informa que os itens não estão disponíveis

#### Scenario: Missing catalog description

- **WHEN** um item retorna SKU ou descrição nulos
- **THEN** a seção mostra um texto de indisponibilidade no lugar do valor, sem quebrar a página

### Requirement: History states are distinct and session-safe

A seção SHALL distinguir carregamento, lista vazia, erro de consulta e sessão não
autorizada. Falhas 401/403 SHALL encerrar a sessão interna e limpar os dados exibidos,
sem retry. Falhas de rede ou respostas inválidas SHALL manter uma mensagem de erro e
permitir nova tentativa manual, sem inventar Pedidos ou contadores. Respostas de uma
sessão, Cliente, filtro ou página anterior SHALL NOT sobrescrever o estado atual. A
consulta SHALL usar o token interno privado no servidor e SHALL NOT expor credenciais,
token de Cliente ou URLs privadas ao navegador.

#### Scenario: Loading and empty states

- **WHEN** a consulta está em andamento ou retorna zero Pedidos
- **THEN** o painel mostra, respectivamente, carregamento e vazio, sem listar Pedidos inexistentes

#### Scenario: Unauthorized response

- **WHEN** o backend responde 401 ou 403
- **THEN** o painel limpa histórico, ficha, lista e contadores e retorna ao estado não autenticado

#### Scenario: Obsolete response

- **WHEN** o usuário troca de Cliente ou filtro antes de uma resposta anterior chegar
- **THEN** a resposta antiga é descartada e não altera a seção atual

#### Scenario: No credentials in the browser

- **WHEN** a seção carrega o histórico
- **THEN** a requisição é feita server-side com o token interno e o navegador recebe apenas os dados sanitizados do contrato

#### Scenario: Keyboard and accessible controls

- **WHEN** o usuário navega por filtros, datas, paginação e conteúdo do histórico usando o teclado
- **THEN** os controles têm nomes acessíveis, foco visível e a seção é identificada programaticamente
