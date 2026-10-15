# customer-access Specification

## Purpose
Define independent registration, authentication, session, and self-service access for Voltix Customers, including protection of Customer identity data from other customers and from internal-user access flows.

## Requirements

### Requirement: Customers can register an account
O sistema SHALL permitir cadastro público de Cliente com nome completo, CPF, e-mail, telefone e senha. CPF e e-mail SHALL ser obrigatórios e únicos entre Clientes; e-mail SHALL permanecer independente da unicidade entre Clientes e `UsuarioInterno`. A senha SHALL ser armazenada somente como credencial protegida pelo backend, nunca retornada em respostas. Novos Clientes SHALL iniciar com status `ATIVO`.

#### Scenario: Customer registers with unused identity values
- **WHEN** uma pessoa informa os dados obrigatórios com CPF e e-mail ainda não utilizados por outro Cliente
- **THEN** o backend cria um Cliente `ATIVO` e retorna sua identidade não sensível sem expor senha, hash ou token

#### Scenario: Duplicate CPF or customer email is rejected
- **WHEN** o cadastro usa CPF ou e-mail já pertencente a outro Cliente
- **THEN** o backend rejeita o cadastro e não cria nem altera registros

#### Scenario: Customer email may match an internal user's email
- **WHEN** uma pessoa se cadastra com e-mail já usado por `UsuarioInterno`, mas ainda não usado por Cliente
- **THEN** o cadastro de Cliente é avaliado somente contra outros Clientes e não altera nem autoriza a identidade interna

#### Scenario: Invalid registration is rejected
- **WHEN** faltam dados obrigatórios ou a senha não pode ser processada pelo mecanismo de credencial protegido do backend
- **THEN** o cadastro falha sem criar Cliente e a interface informa falha sem expor credenciais

### Requirement: Customers can authenticate and maintain an independent session
O sistema SHALL permitir que Clientes efetuem login com e-mail e senha, criar sessão pertencente à entidade `Cliente` e permitir logout. Cada acesso autenticado SHALL revalidar a existência e o status `ATIVO` do Cliente. Esta sessão SHALL permanecer distinta da sessão e dos perfis de `UsuarioInterno`.

#### Scenario: Active customer logs in
- **WHEN** um Cliente `ATIVO` envia e-mail e senha válidos
- **THEN** o backend autentica o Cliente e retorna sessão e identidade sem senha ou hash

#### Scenario: Invalid credentials do not create a session
- **WHEN** o e-mail não existe, a senha é inválida ou a conta está `INATIVO`
- **THEN** o backend rejeita o login e não cria sessão autenticada

#### Scenario: Inactive customer session is rejected
- **WHEN** um Cliente autenticado passa a estar `INATIVO` e usa a sessão existente
- **THEN** o backend rejeita as operações autenticadas do Cliente

#### Scenario: Customer credentials cannot grant internal access
- **WHEN** uma sessão emitida para Cliente é usada em uma operação protegida para `UsuarioInterno`
- **THEN** o backend rejeita o acesso interno

#### Scenario: Customer logs out
- **WHEN** o Cliente aciona logout
- **THEN** a sessão local da aplicação é removida e ações posteriores não enviam a sessão anterior

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

### Requirement: Customer authentication uses the Reflex State and server-side Xano flow
A interface SHALL encaminhar cadastro, login, consultas de sessão, alterações de perfil e logout ao State/lógica Python da aplicação; essa camada SHALL executar as chamadas HTTP ao Xano. Credenciais e tokens SHALL permanecer fora do código executado diretamente no navegador e fora das respostas destinadas à interface.

#### Scenario: Customer flow uses server-side requests
- **WHEN** a pessoa interage com cadastro, login ou sessão de Cliente na interface Reflex
- **THEN** a ação é processada no State/Python e a comunicação HTTP com Xano ocorre nessa camada

#### Scenario: Customer backend is unavailable
- **WHEN** há erro HTTP, falha de rede, configuração ausente ou resposta incompatível
- **THEN** a interface apresenta estado de erro sem simular sucesso nem expor credenciais ou tokens
