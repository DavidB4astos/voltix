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

### Requirement: Clear desktop account and address workspace
The customer account page SHALL preserve its customer-session guard, registration/login fields, profile fields, immutable CPF, existing handlers and address action conditions. At desktop widths of at least 1024px, profile and address management SHALL use separate columns with semantic section headings. Address inputs SHALL have persistent visible labels and accessible names. Account actions SHALL have visible keyboard focus. Loading or errors SHALL not be described as a confirmed empty address book. Narrow layouts SHALL stack without horizontal overflow. Styling SHALL remain account-scoped, without backend or session changes.

#### Scenario: Customer manages their account
- **WHEN** an authenticated customer opens the desktop account page
- **THEN** profile and address management appear in distinct columns with the existing actions and values

#### Scenario: Customer fills an address
- **WHEN** an address input contains a value
- **THEN** its label remains visible and its accessible name identifies the field

#### Scenario: Address request is pending or fails
- **WHEN** address loading or failure feedback is present
- **THEN** feedback remains visible without claiming the address book is confirmed empty

#### Scenario: Visitor signs in or registers
- **WHEN** no customer session is authenticated
- **THEN** registration and login retain their existing fields and submission events

### Requirement: Consistent signed-out customer entry points
The signed-out customer account page SHALL expose one visible primary heading identifying Minha conta before the existing registration and login forms. Signed-out checkout and orders pages SHALL present their existing account link as a clearly visible blue action with at least 48px height and visible keyboard focus, consistent with the cart access action. Account links SHALL preserve the /cliente destination. Session guards, form submissions and authenticated branches SHALL remain unchanged.

#### Scenario: Visitor opens the account page
- **WHEN** a signed-out visitor opens /cliente
- **THEN** one visible H1 identifies Minha conta and existing registration/login fields and submissions remain available

#### Scenario: Visitor needs to authenticate before purchase or history
- **WHEN** a signed-out visitor opens checkout or orders
- **THEN** the account action has a clear accessible name, visible keyboard focus, minimum 48px height and leads to /cliente without creating data
