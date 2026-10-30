## MODIFIED Requirements

### Requirement: Customers can access and update only their own profile
O sistema SHALL permitir que um Cliente autenticado consulte sua própria identidade e atualize nome completo, e-mail e telefone, mantendo CPF imutável após cadastro. O backend SHALL limitar toda leitura e atualização ao Cliente identificado pela sessão; nenhuma entrada de ID do cliente poderá ampliar esse escopo. Respostas SHALL omitir senha, hash e tokens.

#### Scenario: Customer reads own profile
- **WHEN** um Cliente autenticado consulta sua identidade
- **THEN** o sistema retorna somente os dados não sensíveis daquele Cliente

#### Scenario: Customer updates allowed profile fields
- **WHEN** um Cliente autenticado altera nome, e-mail ainda único entre Clientes ou telefone
- **THEN** o backend atualiza somente os campos permitidos do Cliente da sessão

#### Scenario: Customer cannot change CPF or another customer's profile
- **WHEN** o Cliente tenta alterar CPF, fornecer outro ID de Cliente ou acessar perfil de terceiro
- **THEN** o backend rejeita ou ignora qualquer campo não permitido e não retorna nem altera dados de outro Cliente

#### Scenario: Legacy customer routes enforce ownership and safe fields
- **WHEN** uma requisição usa uma rota legada de CLIENTE para listar, consultar, cadastrar, editar ou remover dados
- **THEN** ela preserva o caminho e método existentes; o cadastro público aceita somente os campos explícitos de registro, as demais operações exigem sessão de Cliente e escopo do próprio titular, nenhuma aceita escrita genérica e nenhuma expõe credenciais

#### Scenario: Customer account cannot be permanently deleted
- **WHEN** um Cliente tenta remover definitivamente a própria conta
- **THEN** o backend rejeita a operação e preserva o registro e seu histórico

#### Scenario: Published legacy aliases enforce the current customer contract
- **WHEN** requests reach the published GET /cliente or GET, PATCH, DELETE /cliente/{cliente_id} aliases
- **THEN** authentication is required before customer access, GET/PATCH enforce active customer ownership with explicit response fields, PATCH accepts only approved mutable profile fields, and permanent DELETE is rejected without a database deletion

#### Scenario: Restricted deployment preserves registration and unrelated APIs
- **WHEN** legacy protections are reconciled with the live backend
- **THEN** the reviewed package updates only these four query identities and preserves POST registration, current group identifiers, schemas and records
