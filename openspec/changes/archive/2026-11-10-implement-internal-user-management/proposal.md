## Why

A área interna não possui gestão de usuários: novos `UsuarioInterno` só podem ser criados
manualmente no Xano, e não há como listar, corrigir nome/e-mail, trocar perfil ou inativar
um usuário pela aplicação. Também não existe perfil próprio: o usuário não consegue manter
seus dados nem trocar a própria senha com segurança. Os itens 7 e 14 da fila aprovada
cobrem exatamente essa lacuna, preservando o provisionamento administrativo e o histórico
de Atendimentos.

## What Changes

- Criar o grupo Xano `Voltix Internal Users` com endpoints de gestão exclusivos de
  `ADMINISTRADOR` ativo:
  - `GET users` para listar usuários internos com allowlist de campos.
  - `POST users` para criar usuário com nome, e-mail único, senha inicial, perfil e status
    `ATIVO`.
  - `PATCH users/{user_id}` para editar nome, e-mail, perfil e status, sem alterar senha e
    sem excluir o registro.
- Bloquear no backend: e-mail duplicado, perfil/status inválidos, alteração do próprio
  perfil ou status, remoção do último administrador ativo e acesso de não-administrador.
- Criar endpoints de perfil próprio para qualquer `UsuarioInterno` ativo:
  - `PATCH profile` para editar apenas nome e e-mail, com e-mail único.
  - `POST profile/password` para trocar a senha exigindo a senha atual e confirmação.
- Adicionar ao painel interno a seção "Usuários", visível apenas para `ADMINISTRADOR`, com
  lista, criação, edição e inativação/reativação com confirmação em dois passos.
- Adicionar acesso "Meu perfil" para ambos os perfis, com edição de nome/e-mail e formulário
  de troca de senha.
- Atualizar o texto de `internal-access` para permitir provisionamento por administrador,
  mantendo a ausência de cadastro público, e atualizar `internal-workspace` para reconhecer
  a seção administrativa de usuários.
- Não criar exclusão de usuário: a inativação preserva Atendimentos e demais históricos.

## Capabilities

### New Capabilities

- `internal-users`: gestão administrativa de usuários internos, perfil próprio e troca de
  senha com validação da senha atual.

### Modified Capabilities

- `internal-access`: o provisionamento deixa de ser exclusivamente manual no Xano e passa a
  admitir criação por `ADMINISTRADOR` ativo, sem cadastro público.
- `internal-workspace`: a navegação administrativa passa a incluir a seção "Usuários" e o
  acesso ao perfil próprio, preservando as permissões existentes.

## Impact

- Xano: novo grupo `xano/api/internal_users/api_group.xs` e cinco endpoints; publicação
  restrita, pendente de autorização explícita.
- Código: `voltix/voltix.py` (Estado, handlers, navegação, seção de usuários e perfil) e
  estilos internos em `assets/voltix-internal.css`.
- Testes: novo `tests/test_internal_user_management.py` e ajustes em testes de navegação e
  acesso interno.
- Specs: nova capability `internal-users`; deltas em `internal-access` e
  `internal-workspace`.
- Docs: `docs/roadmap-changes.md` e `docs/AI_AGENT_HANDOFF.md` após a verificação.
- Fora do escopo: recuperação de senha por e-mail (item 11), exclusão de usuário, verificação
  de e-mail, troca da senha de terceiros, revogação global de sessões, auditoria detalhada,
  multi-tenant/`account`, cadastro público e login social.
