## 1. Backend Xano

- [x] 1.1 Em `xano/api/internal_users/users_POST.xs`, trocar
      `text password filters=min:8|minAlpha:1|minDigit:1` por
      `text password filters=min:8` e adicionar precondition com
      `regex_test:"[A-Za-z]"` e `regex_test:"[0-9]"` (antes do `db.add`, depois
      do guard de administrador) — verificação: ausência dos filtros inválidos e
      presença do regex no arquivo
- [x] 1.2 Em `xano/api/internal_users/profile/password_POST.xs`, aplicar a mesma
      correção a `new_password`, antes do `db.edit` e depois do guard de sessão —
      verificação: ausência dos filtros inválidos e presença do regex no arquivo
- [x] 1.3 Confirmar que a tabela `user` (`xano/table/user.xs`) não foi alterada e
      que a coluna `password` mantém `minAlpha`/`minDigit` (tipo `password`) —
      verificação: `git diff -- xano/table/user.xs` vazio

## 2. Testes

- [x] 2.1 Adicionar asserções em `tests/test_internal_user_management.py`
      (`InternalUserScriptTests`): nenhuma ocorrência de `minAlpha`/`minDigit` nos
      dois endpoints, presença do `regex_test` e da precondition de letra e dígito,
      ordem autorização → validação → escrita — verificação: asserções verdes
- [x] 2.2 Executar a suíte completa — verificação:
      `python -m unittest discover -s tests -q` sem falhas (430 testes OK)

## 3. Verificação e publicação

- [x] 3.1 `openspec validate fix-internal-users-password-filters --strict` —
      verificação: válido
- [x] 3.2 `git diff --check` — verificação: sem whitespace/conflito
- [x] 3.3 Dry-run restrito dos dois endpoints —
      verificação: preview com apenas os dois `UPDATE` (users e profile/password)
- [x] 3.4 **GATE** — autorização explícita recebida em 13/11/2026 antes de publicar no Xano —
      verificação: push restrito OK, 2 documentos
- [x] 3.5 Pull independente pós-publicação — verificação: local e remoto coincidem
      (somente a normalização do importador `regex_test` → `regex_matches`, como no
      passo query-quote)
- [x] 3.6 Verificação remota somente leitura — verificação: `POST /users` sem sessão
      responde `400 min 8` para `password` curta e `400 Missing param` para corpo vazio,
      sem escrita; `POST /profile/password` idem para `new_password`. A verificação
      autenticada com sessão descartável (esperado: 400 genérico do precondition sem
      escrita) não foi executada — limitação registrada na evidência

## 4. Encerramento

- [x] 4.1 Registrar evidência em `evidence/` da change — verificação: `verification.md` presente
- [x] 4.2 Atualizar `docs/roadmap-changes.md` e `docs/AI_AGENT_HANDOFF.md` —
      verificação: consistente com a evidência e sem dados pessoais
- [x] 4.3 Arquivar a change e validar globalmente — verificação:
      `openspec validate --all --strict` (28 itens após arquivamento) e diretório em
      `openspec/changes/archive/`
- [ ] 4.4 Commit — verificação: somente com autorização explícita; `git status`
      limpo ou limitações explicadas
