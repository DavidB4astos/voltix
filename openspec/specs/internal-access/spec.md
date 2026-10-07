## Purpose

Estabelecer o acesso autenticado e autorizado de UsuarioInterno Ã  Ã¡rea interna da Voltix, preservando a separaÃ§Ã£o entre usuÃ¡rios internos e clientes e limitando a capability ao fluxo mÃ­nimo de entrada e saÃ­da.

## Requirements

### Requirement: Internal users can authenticate

O sistema SHALL permitir o login somente de um `UsuarioInterno` previamente provisionado no Xano, usando e-mail e senha vÃ¡lidos, sem oferecer cadastro pÃºblico de usuÃ¡rios internos.

#### Scenario: Active provisioned user logs in

- **WHEN** um `UsuarioInterno` com status `ATIVO` envia credenciais vÃ¡lidas
- **THEN** o backend autentica o usuÃ¡rio, cria uma sessÃ£o autenticada e retorna sua identidade interna sem expor a senha

#### Scenario: Invalid credentials are rejected

- **WHEN** sÃ£o enviadas credenciais invÃ¡lidas ou de um usuÃ¡rio nÃ£o provisionado
- **THEN** o backend rejeita o login, nÃ£o cria sessÃ£o e a interface informa uma falha de autenticaÃ§Ã£o

#### Scenario: Public internal signup is unavailable

- **WHEN** alguÃ©m tenta criar um usuÃ¡rio interno por um fluxo pÃºblico de cadastro
- **THEN** o sistema rejeita a criaÃ§Ã£o e mantÃ©m o provisionamento sob controle manual no Xano

### Requirement: Internal identity uses approved profiles and statuses

O sistema SHALL representar `UsuarioInterno` na tabela Xano `user`, usando exclusivamente os perfis `FUNCIONARIO` e `ADMINISTRADOR` e os status `ATIVO` e `INATIVO`.

#### Scenario: Authenticated identity is returned

- **WHEN** uma sessÃ£o vÃ¡lida consulta a identidade do usuÃ¡rio interno
- **THEN** o backend retorna nome, e-mail, perfil e status permitidos para a interface, sem retornar senha, token ou outros dados de credencial

#### Scenario: Invalid profile or status cannot authorize access

- **WHEN** um registro possui perfil ou status diferente dos valores aprovados
- **THEN** o backend nÃ£o o considera um `UsuarioInterno` autorizado para a Ã¡rea interna

### Requirement: Active internal users can access the protected area

O sistema SHALL permitir o acesso Ã  Ã¡rea interna somente para uma sessÃ£o vÃ¡lida de `UsuarioInterno` com status `ATIVO`, e SHALL aplicar essa autorizaÃ§Ã£o no backend.

#### Scenario: Active employee accesses the protected area

- **WHEN** um `UsuarioInterno` `ATIVO` com perfil `FUNCIONARIO` acessa a Ã¡rea interna com sessÃ£o vÃ¡lida
- **THEN** o backend autoriza o acesso e a interface apresenta a Ã¡rea interna mÃ­nima

#### Scenario: Active administrator accesses the protected area

- **WHEN** um `UsuarioInterno` `ATIVO` com perfil `ADMINISTRADOR` acessa a Ã¡rea interna com sessÃ£o vÃ¡lida
- **THEN** o backend autoriza o acesso e a interface apresenta a Ã¡rea interna mÃ­nima

#### Scenario: Unauthenticated request is denied

- **WHEN** uma requisiÃ§Ã£o Ã  Ã¡rea interna nÃ£o apresenta uma sessÃ£o vÃ¡lida
- **THEN** o backend rejeita a requisiÃ§Ã£o e a interface nÃ£o apresenta a Ã¡rea protegida como autenticada

#### Scenario: Inactive internal user is denied

- **WHEN** um `UsuarioInterno` `INATIVO` tenta acessar a Ã¡rea interna, mesmo possuindo credenciais ou token
- **THEN** o backend rejeita o acesso e a interface informa que o acesso interno nÃ£o estÃ¡ disponÃ­vel

### Requirement: Authenticated internal users can end their session

O sistema SHALL permitir que o usuÃ¡rio interno encerre a sessÃ£o pela interface e SHALL remover a sessÃ£o local utilizada pela aplicaÃ§Ã£o.

#### Scenario: User logs out

- **WHEN** um usuÃ¡rio interno autenticado aciona o logout
- **THEN** a sessÃ£o local Ã© removida, a Ã¡rea protegida deixa de ser apresentada e a aplicaÃ§Ã£o retorna ao estado nÃ£o autenticado

#### Scenario: Protected access after logout

- **WHEN** uma tentativa de acessar a Ã¡rea interna ocorre depois do logout sem uma nova autenticaÃ§Ã£o
- **THEN** o backend rejeita a requisiÃ§Ã£o por ausÃªncia de sessÃ£o vÃ¡lida

### Requirement: Internal access remains separate from customer access

A autenticaÃ§Ã£o desta capability MUST permanecer restrita a `UsuarioInterno` e SHALL manter `Cliente` como conceito separado, sem transformar credenciais de cliente em perfil interno.

#### Scenario: Customer records do not grant internal access

- **WHEN** um registro ou credencial pertencente ao conceito `Cliente` Ã© apresentado ao fluxo de acesso interno
- **THEN** ele nÃ£o Ã© tratado como `FUNCIONARIO` ou `ADMINISTRADOR` e nÃ£o recebe acesso Ã  Ã¡rea interna


