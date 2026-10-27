## ADDED Requirements

### Requirement: Admin can consult customers list

O painel administrativo SHALL permitir a consulta listagem de clientes cadastrados, com filtros opcionais por nome (parcial, case-insensitive) e status (ATIVO/INATIVO). A resposta SHALL omitir dados sensíveis (senhas, tokens) e apresentar e-mail mascarado (apenas os 3 primeiros caracteres seguidos de "*****"). O endpoint SHALL ser de leitura somente e exigir perfil `ADMINISTRADOR` ativo. A busca SHALL ser aplicada em `nome` e `e-mail` do cliente. Quando nenhum filtro for fornecido, SHALL retornar apenas clientes `ATIVO`. O endpoint SHALL respeitar limites de requisições do Xano Free e tratar HTTP 429 com retry via `Retry-After`.

#### Scenario: Anonymous admin lists active customers
- **WHEN** o administrador logado acessa a listagem de clientes sem filtros
- **THEN** s�o retornados apenas clientes com status ATIVO, em ordem alfab�tica por nome

#### Scenario: Admin filters by status
- **WHEN** o administrador seleciona status "INATIVO"
- **THEN** s�o retornados apenas clientes com status INATIVO

#### Scenario: Admin searches by name
- **WHEN** o administrador pesquisa pelo termo "Maria" no campo de busca
- **THEN** s�o retornados clientes cujo nome ou e-mail contenha "Maria", sem distin��o entre maiúsculas e minúsculas

#### Scenario: Admin search returns masked email
- **WHEN** a listagem inclui o cliente com e-mail "maria.silva@email.com"
- **THEN** a interface apresenta o e-mail como "Mar*****"

#### Scenario: Empty search returns full active list
- **WHEN** o termo de busca estiver vazio ou em branco
- **THEN** o filtro por nome � ignorado e a listagem retorna todos os clientes ATIVO

#### Scenario: Rate limit retry succeeds
- **WHEN** o Xano responder HTTP 429 com cabeçalho `Retry-After`
- **THEN** o sistema aguarda o intervalo especificado e realiza nova tentativa, sem apresentar falha ao admin