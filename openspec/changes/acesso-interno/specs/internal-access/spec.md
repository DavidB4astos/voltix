## Purpose

Estabelecer o acesso autenticado e autorizado de UsuarioInterno à área interna da Voltix, preservando a separação entre usuários internos e clientes e limitando a capability ao fluxo mínimo de entrada e saída.

## ADDED Requirements

### Requirement: Internal users can authenticate

O sistema SHALL permitir o login somente de um `UsuarioInterno` previamente provisionado no Xano, usando e-mail e senha válidos, sem oferecer cadastro público de usuários internos.

#### Scenario: Active provisioned user logs in

- **WHEN** um `UsuarioInterno` com status `ATIVO` envia credenciais válidas
- **THEN** o backend autentica o usuário, cria uma sessão autenticada e retorna sua identidade interna sem expor a senha

#### Scenario: Invalid credentials are rejected

- **WHEN** são enviadas credenciais inválidas ou de um usuário não provisionado
- **THEN** o backend rejeita o login, não cria sessão e a interface informa uma falha de autenticação

#### Scenario: Public internal signup is unavailable

- **WHEN** alguém tenta criar um usuário interno por um fluxo público de cadastro
- **THEN** o sistema rejeita a criação e mantém o provisionamento sob controle manual no Xano

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
