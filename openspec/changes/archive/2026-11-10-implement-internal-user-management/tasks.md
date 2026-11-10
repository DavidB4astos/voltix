## 1. Preparação

- [x] 1.1 Conferir a tabela `user`, o login interno, as specs `internal-access` e
      `internal-workspace` e a navegação atual — verificação: leitura dos arquivos sem
      alteração
- [x] 1.2 Confirmar que a tabela `user` aceita criação com senha hasheada pelo Xano e que
      os endpoints do template `Members & Accounts` não serão reutilizados — verificação:
      decisão registrada no design
- [x] 1.3 Confirmar que exclusão de usuário permanece fora do escopo e que a inativação
      preserva Atendimentos — verificação: regra de domínio §4.3 conferida

## 2. Backend Xano

- [x] 2.1 Criar `xano/api/internal_users/api_group.xs` para o grupo
      `Voltix Internal Users` — verificação: grupo com canonical, tags e sem segredo
- [x] 2.2 Criar `users_GET.xs` com `auth = "user"`, guarda de ADMINISTRADOR ativo antes da
      consulta, ordenação por nome e allowlist de campos — verificação: sem senha,
      `password_reset` ou `account_id`
- [x] 2.3 Criar `users_POST.xs` com nome, e-mail único, senha inicial válida, perfil
      aprovado e status `ATIVO` — verificação: e-mail duplicado responde `400` e nenhuma
      credencial é retornada
- [x] 2.4 Criar `user/user_id_PATCH.xs` com edição parcial de nome, e-mail, perfil e status,
      `404` para ausente e `400` para e-mail duplicado — verificação: nenhum campo de senha
      aceito
- [x] 2.5 Bloquear no PATCH administrativo alteração do próprio perfil/status e remoção do
      último administrador ativo — verificação: precondições antes da escrita
- [x] 2.6 Criar `profile_PATCH.xs` para o próprio nome/e-mail, sem aceitar perfil, status,
      senha ou `account_id` — verificação: apenas o usuário autenticado é alterado
- [x] 2.7 Criar `profile/password_POST.xs` com senha atual, nova senha e confirmação —
      verificação: `security.check_password`, regras de senha e resposta sem credenciais
- [x] 2.8 Validar os arquivos com dry-run/importação do Xano — verificação: apenas os
      `CREATE` esperados no preview

## 3. Frontend

- [x] 3.1 Adicionar Estado, contrato e handlers de listagem, criação, edição e
      inativação/reativação de usuários internos — verificação: sessão ADMINISTRADOR
      exigida pelo request server-side
- [x] 3.2 Adicionar a seção "Usuários" à navegação apenas para ADMINISTRADOR e atualizar a
      allowlist de `select_internal_section` — verificação: FUNCIONARIO não renderiza a
      seção
- [x] 3.3 Renderizar lista, formulários e confirmação em dois passos, com controles de
      perfil/status desabilitados para o próprio administrador — verificação: rótulos e
      mensagens observáveis
- [x] 3.4 Tornar o bloco de identidade acionável e renderizar "Meu perfil" para ambos os
      perfis, com edição de nome/e-mail — verificação: identidade local atualizada apenas
      após resposta confirmada
- [x] 3.5 Renderizar o formulário de troca de senha e limpar os campos somente após sucesso —
      verificação: falhas preservam os valores e não inventam sucesso
- [x] 3.6 Mapear falhas `400` de e-mail/proteção, `401`, `403`, `404` e rede para mensagens
      distintas — verificação: dados confirmados preservados

## 4. Testes

- [x] 4.1 Cobrir listagem, criação, edição, inativação/reativação e permissões em
      `tests/test_internal_user_management.py` — verificação: handlers e requests cobertos
- [x] 4.2 Cobrir perfil próprio e troca de senha, incluindo senha atual incorreta,
      confirmação divergente, senha fraca e e-mail duplicado — verificação: nenhuma escrita
      inventada em falha
- [x] 4.3 Cobrir o XanoScript: autorização antes do negócio, allowlists, ausência de
      exclusão, proteção do último administrador e ausência de segredos nas respostas —
      verificação: asserções estáticas dos arquivos
- [x] 4.4 Ajustar testes de navegação/acesso para a nova seção e para o perfil — verificação:
      suíte existente preservada
- [x] 4.5 Executar a suíte completa — verificação: `python -m unittest discover -s tests -q`
      (389 testes OK)

## 5. Verificação e publicação

- [x] 5.1 `openspec validate implement-internal-user-management --strict` — verificação:
      válido
- [x] 5.2 `reflex compile` e restauração de `reflex.lock/*` não relacionado — verificação:
      `git status` sem migração acidental de dependências
- [x] 5.3 `git diff --check` — verificação: sem whitespace/conflito
- [x] 5.4 Dry-run restrito dos cinco endpoints e do grupo — verificação: preview com apenas
      os `CREATE` esperados
- [x] 5.5 **GATE** — autorização explícita antes de publicar no Xano — verificação:
      aprovação registrada do usuário
- [x] 5.6 Pull independente pós-publicação — verificação: guards, allowlists, group e GUIDs
      preservados
- [x] 5.7 Verificação remota somente leitura — verificação: `GET /users`, `PATCH /users/{id}`,
      `PATCH /profile` responderam `401` sem sessão; `POST /users` e
      `POST /profile/password` responderam `400` por campos obrigatórios ausentes, sem
      escrita real
- [ ] 5.8 **GATE opcional** — teste autenticado positivo com usuário sintético somente com
      autorização explícita para escrita real — verificação: evidência registrada ou
      limitação documentada. **Não executado**: exige criação de usuário sintético e
      autorização separada para escrita real; permanece como limitação documentada.

## 6. Encerramento

- [x] 6.1 Sincronizar as deltas com `openspec/specs/` e confirmar
      `openspec validate --all --strict` — verificação: validação global
- [x] 6.2 Atualizar `docs/roadmap-changes.md` e `docs/AI_AGENT_HANDOFF.md` — verificação:
      consistente com a evidência
- [x] 6.3 Arquivar a change — verificação: diretório em `openspec/changes/archive/`
- [ ] 6.4 Commit/push somente com autorização explícita — verificação:
      `git status --short --branch` limpo e sincronizado
