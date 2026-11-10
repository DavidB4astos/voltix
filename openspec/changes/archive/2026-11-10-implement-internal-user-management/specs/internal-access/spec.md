## MODIFIED Requirements

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
