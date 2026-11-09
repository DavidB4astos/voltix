## Purpose

Definir a seção desktop de Pedidos do painel interno, que permite a usuários internos ativos
consultar Pedidos, inspecionar Cliente, itens, entrega e Pagamento e, quando administradores,
avançar o status operacional em sequência estrita, sem alterar dados do Pedido nem expor
informações sensíveis.

## ADDED Requirements

### Requirement: Order panel is restricted to active internal users

A seção Pedidos SHALL ser apresentada somente dentro de uma sessão interna validada de
UsuarioInterno `ATIVO` com papel `FUNCIONARIO` ou `ADMINISTRADOR`. Visitantes, Clientes e
usuários internos `INATIVO` SHALL NOT visualizar ou operar a seção. O backend SHALL
permanecer a autoridade final. Uma resposta `401` SHALL encerrar a sessão e limpar os dados
carregados; uma resposta `403` em leitura SHALL ter o mesmo efeito. Em avanço de status,
`403` representa operação negada e SHALL manter a sessão e o Pedido apresentado, apenas
informando a negativa.

#### Scenario: Active employee opens the panel

- **WHEN** um FUNCIONARIO ativo seleciona a seção Pedidos
- **THEN** a seção é apresentada com a listagem pronta para consulta e sem controles de status

#### Scenario: Unauthorized read loses the panel

- **WHEN** uma leitura de Pedidos responde `401` ou `403`
- **THEN** a tela limpa listagem, detalhe, filtros e mensagens e retorna à superfície de acesso interno

#### Scenario: Status operation denied keeps the session

- **WHEN** o backend responde `403` a uma tentativa de avanço de status
- **THEN** a tela mantém a sessão, o status anterior e mostra que a operação não é permitida

### Requirement: Order listing supports search, status filter and pagination

A seção SHALL listar Pedidos com busca textual opcional `q` de até 100 caracteres (código do
Pedido ou nome do Cliente), filtro por `status` (`TODOS`, `AGUARDANDO_PAGAMENTO`,
`PAGAMENTO_CONFIRMADO`, `EM_PREPARACAO`, `ENVIADO`, `ENTREGUE` ou `CANCELADO`) e paginação de
20 itens, com navegação anterior/próxima. A resposta SHALL conter exatamente `items`, `page`,
`per_page`, `items_total` e `page_total`, e cada item SHALL conter exatamente `id`, `codigo`,
`data_pedido`, `status`, `cliente`, `itens_count`, `subtotal`, `valor_frete` e `valor_total`,
com `cliente` contendo exatamente `id` e `nome_completo`. A tela SHALL exibir total e página
atual, aplicar filtros válidos reiniciando na página 1 e rejeitar filtros inválidos com
mensagem local, sem enviar requisição. Respostas com campos extras, tipos inválidos, status
desconhecido, totais inconsistentes ou datas inválidas SHALL ser rejeitadas com mensagem de
erro.

#### Scenario: Search by order code or customer name

- **WHEN** o usuário informa um termo de busca e aplica os filtros
- **THEN** a tela carrega a primeira página dos Pedidos correspondentes e atualiza o total

#### Scenario: Combine status and search

- **WHEN** o usuário seleciona `ENVIADO` e informa um termo de busca
- **THEN** a consulta combina os dois critérios sem descartar nenhum deles

#### Scenario: Invalid filter is not sent

- **WHEN** o termo excede 100 caracteres ou o status está fora do conjunto aceito
- **THEN** a tela mostra uma mensagem de filtros inválidos e não executa a consulta

#### Scenario: Empty listing

- **WHEN** a consulta retorna `items=[]` e `items_total=0`
- **THEN** a tela mostra um estado vazio com a opção de ajustar os filtros, sem erro genérico

#### Scenario: Pagination metadata

- **WHEN** a resposta indica `page=2` e `page_total=3`
- **THEN** a tela mostra "Página 2 de 3" e habilita apenas a navegação permitida

### Requirement: Order detail exposes only allowed customer and order data

A seção SHALL abrir o detalhe de um Pedido consultando o endpoint publicado e exibir `id`,
`codigo`, `data_pedido`, `status`, Cliente com `id`, `nome_completo` e `email_masked`,
`entrega` com `cep`, `logradouro`, `numero`, `complemento`, `bairro`, `cidade`, `estado` e
`identificacao`, `itens` com `variacao_id`, `sku`, `nome_ou_descricao`, `quantidade`,
`preco_unitario` e `subtotal`, `subtotal`, `valor_frete`, `valor_total` e `pagamento` com
`metodo`, `valor` e `status`. A tela SHALL NOT exibir CPF, telefone, senha, hash, token ou
qualquer campo não previsto nesse contrato. Valores ausentes ou nulos SHALL ser apresentados
como "Indisponível" sem quebrar a tela. Em `notfound`, a tela SHALL remover o detalhe e
informar que o Pedido não existe.

#### Scenario: Inspect an order

- **WHEN** o usuário abre um Pedido existente
- **THEN** a tela mostra Cliente, itens, endereço, Pagamento e valores persistidos, sem dados sensíveis

#### Scenario: Missing order

- **WHEN** o detalhe responde `notfound`
- **THEN** a tela fecha o detalhe e mostra a mensagem de Pedido não encontrado

#### Scenario: Sensitive field is never rendered

- **WHEN** qualquer Pedido é listado ou detalhado
- **THEN** CPF, telefone, senha, hash e token não aparecem na tela nem são inventados

### Requirement: Only administrators advance order status within the published sequence

A seção SHALL oferecer avanço de status somente a `ADMINISTRADOR`, um passo por requisição,
na sequência `PAGAMENTO_CONFIRMADO → EM_PREPARACAO → ENVIADO → ENTREGUE`. `FUNCIONARIO` SHALL
NOT ver nem acionar controles de status. A tela SHALL oferecer apenas o próximo alvo válido;
`AGUARDANDO_PAGAMENTO`, `CANCELADO` e `ENTREGUE` SHALL NOT oferecer avanço. Repetir o status
atual SHALL ser tratado como operação idempotente sem escrita. A resposta SHALL conter
exatamente `pedido_id`, `codigo`, `status_anterior`, `status_atual` e `alterado`. Em sucesso,
a tela SHALL atualizar o detalhe e a listagem; em `badrequest` ou `accessdenied`, SHALL
manter o status anterior e mostrar a mensagem correspondente.

#### Scenario: Administrator advances one step

- **WHEN** um ADMINISTRADOR aciona o avanço de `PAGAMENTO_CONFIRMADO` para `EM_PREPARACAO`
- **THEN** a tela envia o alvo e apresenta o Pedido em `EM_PREPARACAO`

#### Scenario: Full sequence

- **WHEN** um ADMINISTRADOR avança sucessivamente até `ENTREGUE`
- **THEN** cada ação aplica um passo e o Pedido passa a não oferecer novos avanços

#### Scenario: Employee has no status control

- **WHEN** um FUNCIONARIO abre um Pedido em qualquer status
- **THEN** a tela não oferece controle de avanço e mantém a consulta disponível

#### Scenario: Invalid transition is rejected

- **WHEN** o backend responde `badrequest` a uma tentativa de avanço
- **THEN** a tela mantém o status anterior e informa que a transição não é permitida

#### Scenario: Repeated target is idempotent

- **WHEN** o alvo enviado é igual ao status atual
- **THEN** a tela apresenta sucesso com `alterado=false` e não duplica a escrita

### Requirement: Panel handles loading, stale responses and errors safely

A seção SHALL apresentar estados distintos de carregamento, vazio, erro e sessão não
autorizada, com mensagens em português e sem expor payload bruto, tokens ou credenciais ao
navegador. Requisições SHALL ocorrer no servidor com o token interno. A tela SHALL descartar
respostas cuja sessão, filtros, página ou Pedido selecionado não sejam mais os atuais. Falhas
de rede, `429`, `500` ou respostas inválidas SHALL mostrar mensagem genérica e permitir nova
tentativa, mantendo o backend como fonte de verdade.

#### Scenario: Stale response is discarded

- **WHEN** uma resposta de listagem chega após o usuário trocar o filtro ou a página
- **THEN** a tela ignora a resposta obsoleta e mantém o estado do filtro atual

#### Scenario: Loading and retry

- **WHEN** uma consulta está em andamento ou falha temporariamente
- **THEN** a tela mostra carregamento ou mensagem genérica e permite nova tentativa

### Requirement: Panel is accessible and reuses the internal workspace language

A seção SHALL usar rótulos associados aos campos, nome acessível nos controles, foco visível,
status comunicado programaticamente e mensagens em `role=status`. A navegação SHALL exibir
Pedidos ao lado de Clientes e Atendimentos para os dois papéis internos, mantendo a seção
claramente identificada e sem empilhar todos os módulos na mesma página.

#### Scenario: Keyboard and assistive access

- **WHEN** o usuário navega por teclado ou leitor de tela pela seção
- **THEN** campos, botões, estados de carregamento e mensagens são anunciados corretamente

#### Scenario: Employee navigation includes orders

- **WHEN** um FUNCIONARIO validado abre o painel
- **THEN** Clientes, Atendimentos e Pedidos estão disponíveis, sem seções administrativas
