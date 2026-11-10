## Purpose

Estabelecer o acesso autenticado e autorizado de UsuarioInterno à área interna da Voltix, preservando a separação entre usuários internos e clientes e limitando a capability ao fluxo mínimo de entrada e saída.

## Requirements

### Requirement: Internal users can authenticate

O sistema SHALL permitir o login somente de um `UsuarioInterno` provisionado no Xano ou
criado por um `ADMINISTRADOR` ativo pela área interna, usando e-mail e senha válidos, sem
oferecer cadastro público de usuários internos.

#### Scenario: Active provisioned user logs in

- **WHEN** um `UsuarioInterno` com status `ATIVO` envia credenciais válidas
- **THEN** o backend autentica o usuário, cria uma sessão autenticada e retorna sua identidade interna sem expor a senha

#### Scenario: Administrator-provisioned user logs in

- **WHEN** um usuário criado por um `ADMINISTRADOR` ativo, com perfil aprovado e status `ATIVO`, envia credenciais válidas
- **THEN** o backend autentica o usuário normalmente, sem exigir provisionamento manual adicional no Xano

#### Scenario: Invalid credentials are rejected

- **WHEN** são enviadas credenciais inválidas ou de um usuário não provisionado
- **THEN** o backend rejeita o login, não cria sessão e a interface informa uma falha de autenticação

#### Scenario: Public internal signup is unavailable

- **WHEN** alguém tenta criar um usuário interno por um fluxo público de cadastro
- **THEN** o sistema rejeita a criação e mantém o provisionamento sob controle administrativo

### Requirement: Internal identity uses approved profiles and statuses

O sistema SHALL representar `UsuarioInterno` na tabela Xano `user`, usando exclusivamente os perfis `FUNCIONARIO` e `ADMINISTRADOR` e os status `ATIVO` e `INATIVO`.

#### Scenario: Authenticated identity is returned

- **WHEN** uma sessão válida consulta a identidade do usuário interno
- **THEN** o backend retorna nome, e-mail, perfil e status permitidos para a interface, sem retornar senha, token ou outros dados de credencial

#### Scenario: Invalid profile or status cannot authorize access

- **WHEN** um registro possui perfil ou status diferente dos valores aprovados
- **THEN** o backend não o considera um `UsuarioInterno` autorizado para a área interna

### Requirement: Active internal users can access the protected area

O sistema SHALL permitir o acesso à área interna somente para uma sessão válida de `UsuarioInterno` com status `ATIVO`, e SHALL aplicar essa autorização no backend.

#### Scenario: Active employee accesses the protected area

- **WHEN** um `UsuarioInterno` `ATIVO` com perfil `FUNCIONARIO` acessa a área interna com sessão válida
- **THEN** o backend autoriza o acesso e a interface apresenta a área interna mínima

#### Scenario: Active administrator accesses the protected area

- **WHEN** um `UsuarioInterno` `ATIVO` com perfil `ADMINISTRADOR` acessa a área interna com sessão válida
- **THEN** o backend autoriza o acesso e a interface apresenta a área interna mínima

#### Scenario: Unauthenticated request is denied

- **WHEN** uma requisição à área interna não apresenta uma sessão válida
- **THEN** o backend rejeita a requisição e a interface não apresenta a área protegida como autenticada

#### Scenario: Inactive internal user is denied

- **WHEN** um `UsuarioInterno` `INATIVO` tenta acessar a área interna, mesmo possuindo credenciais ou token
- **THEN** o backend rejeita o acesso e a interface informa que o acesso interno não está disponível

### Requirement: Authenticated internal users can end their session

O sistema SHALL permitir que o usuário interno encerre a sessão pela interface e SHALL remover a sessão local utilizada pela aplicação.

#### Scenario: User logs out

- **WHEN** um usuário interno autenticado aciona o logout
- **THEN** a sessão local é removida, a área protegida deixa de ser apresentada e a aplicação retorna ao estado não autenticado

#### Scenario: Protected access after logout

- **WHEN** uma tentativa de acessar a área interna ocorre depois do logout sem uma nova autenticação
- **THEN** o backend rejeita a requisição por ausência de sessão válida

### Requirement: Internal access remains separate from customer access

A autenticação desta capability MUST permanecer restrita a `UsuarioInterno` e SHALL manter `Cliente` como conceito separado, sem transformar credenciais de cliente em perfil interno.

#### Scenario: Customer records do not grant internal access

- **WHEN** um registro ou credencial pertencente ao conceito `Cliente` é apresentado ao fluxo de acesso interno
- **THEN** ele não é tratado como `FUNCIONARIO` ou `ADMINISTRADOR` e não recebe acesso à área interna

### Requirement: Internal login has one primary heading

The internal login page SHALL expose exactly one level-one heading identifying the page. Repeated brand marks in its header and footer SHALL NOT be rendered as level-one headings. Their text and visual presentation SHALL remain unchanged.

#### Scenario: Internal login heading hierarchy
- **WHEN** the unauthenticated internal login page is rendered
- **THEN** “Acesso interno” is the page's single level-one heading
- **AND** repeated Voltix brand marks are not level-one headings
- **AND** existing brand text and visual presentation remain unchanged

### Requirement: Internal login fields have associated visible labels

The internal login form SHALL provide a visible HTML label programmatically associated with each email and password input. The association SHALL preserve existing input names, types, required validation, submission handler, and authentication behavior.

#### Scenario: Assistive technology identifies internal login fields
- **WHEN** the internal login form is rendered
- **THEN** each email and password input has a visible label whose `for` value matches that input's unique `id`
- **AND** the form preserves its existing names, types, required validation, and submit handler

### Requirement: Internal access behavior is covered by automated tests

The project SHALL maintain automated tests that exercise the internal authentication and authorization contract without contacting Xano, using isolated fixtures and no real customer or internal-user records. The tests SHALL cover successful login, rejected credentials, identity validation, protected-area authorization, logout and separation between Cliente and UsuarioInterno.

#### Scenario: Successful login is verified

- **WHEN** the automated suite exercises login with valid credentials and a well-formed backend response
- **THEN** the test confirms that a non-empty token and the returned internal user identifier are stored, the local session is marked authenticated and no password or token is exposed in the presentation payload

#### Scenario: Invalid credentials and malformed responses are verified

- **WHEN** the automated suite exercises login with rejected credentials, a malformed response, a missing token, a non-numeric identifier or a transport failure
- **THEN** the test confirms that no authenticated session is created and the local authentication fields remain empty

#### Scenario: Identity validation is verified

- **WHEN** the automated suite exercises session validation with an approved active profile, an unapproved profile, an inactive status, a missing token or a rejected protected-area check
- **THEN** the test confirms that only the approved active identity keeps the session authenticated and that every other case clears the local session

#### Scenario: Logout is verified

- **WHEN** an authenticated internal user triggers logout in the automated suite
- **THEN** the test confirms that the token, identity, internal data and protected-area access are removed and the workspace returns to the unauthenticated state

#### Scenario: Customer separation is verified

- **WHEN** the automated suite presents client credentials or a client profile to the internal access flow
- **THEN** the test confirms that the record is not accepted as FUNCIONARIO or ADMINISTRADOR and does not receive internal access

#### Scenario: Backend guards remain enforced

- **WHEN** the automated suite inspects the internal authentication and access definitions
- **THEN** it confirms that login, identity and protected access accept only the approved profiles and `ATIVO` status, return `accessdenied` otherwise, and do not expose password or token in identity responses

### Requirement: Internal access tests remain isolated from external services

The automated tests for internal access SHALL use stubs or fakes for backend calls and SHALL NOT perform network requests, create sessions in Xano or read real records.

#### Scenario: Suite runs without Xano availability

- **WHEN** the internal-access test suite runs in an environment where Xano is unreachable or unconfigured
- **THEN** every test still completes deterministically using controlled responses and no external call is attempted beyond the test stub
