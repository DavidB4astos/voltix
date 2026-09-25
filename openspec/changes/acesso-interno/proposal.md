## Why

A Voltix já possui a integração técnica entre Reflex e Xano, além de artefatos genéricos de autenticação no backend, mas ainda não oferece acesso controlado à área interna. Esta Change estabelece o primeiro fluxo autenticado para `UsuarioInterno`, aplicando no backend os perfis e o status definidos no domínio antes da criação de funcionalidades administrativas ou de CRM.

## What Changes

- Reaproveitar a tabela Xano `user` como representação oficial de `UsuarioInterno`.
- Formalizar os perfis `FUNCIONARIO` e `ADMINISTRADOR` e os status `ATIVO` e `INATIVO`.
- Permitir login somente de usuários internos provisionados manualmente no Xano, sem cadastro público.
- Implementar o fluxo mínimo `login → sessão autenticada → página interna protegida → logout`.
- Impedir o acesso de `UsuarioInterno` com status `INATIVO`.
- Validar autenticação e autorização no backend Xano, mantendo o State/lógica Python do Reflex como intermediário da interface.
- Manter `Cliente` e `UsuarioInterno` como conceitos e fluxos independentes.

## Capabilities

### New Capabilities

- `internal-access`: Autenticação, sessão, proteção da área interna e autorização mínima por perfil para `UsuarioInterno`.

### Modified Capabilities

Nenhuma.

## Impact

- Afeta a tabela e os endpoints Xano relacionados ao usuário autenticado, adaptando a semântica genérica `admin/member` aos perfis Voltix `ADMINISTRADOR/FUNCIONARIO` e adicionando a regra de status `ATIVO/INATIVO`.
- Afeta o State/lógica Python e a interface Reflex para login, sessão, página interna protegida, logout e estados de erro.
- Reaproveita mecanismos Xano existentes de verificação de senha, criação de token e recuperação do usuário autenticado, sem reutilizar cadastro público ou autorização genérica sem adaptação.
- Depende de usuários internos provisionados manualmente no Xano e de configuração segura do ambiente, sem credenciais versionadas.
- Não altera nem implementa funcionalidades de clientes, catálogo, carrinho, pedidos, pagamentos, CRM ou CRUD de usuários internos.
