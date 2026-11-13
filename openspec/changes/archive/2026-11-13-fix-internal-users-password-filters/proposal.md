## Why

Os endpoints de gestão de usuários internos do Xano declaram `minAlpha:1|minDigit:1`
em inputs do tipo `text`, filtro que o XanoScript não oferece para esse tipo (apenas
para colunas/inputs `password`). O mesmo defeito foi encontrado e corrigido na change
`implement-internal-password-recovery` (`confirm` usa `text filters=min:8` com a regra
de letra e dígito aplicada via `regex_test` na stack). Os endpoints afetados são:

- `xano/api/internal_users/users_POST.xs` (`POST /users`, criação por ADMINISTRADOR);
- `xano/api/internal_users/profile/password_POST.xs` (`POST /profile/password`,
  troca da própria senha).

Sem a correção, a validação do backend não aplica a regra de senha anunciada pelo
contrato (8+ caracteres com letra e dígito), divergindo do comportamento já
especificado em `openspec/specs/internal-users/spec.md` e do frontend, que valida a
mesma regra antes de enviar.

## What Changes

- `users_POST.xs`: input `password` passa a `text filters=min:8`; a regra de ao menos
  uma letra e um dígito passa a ser imposta por precondition com `regex_test`, na
  mesma linha do `confirm_POST.xs` já publicado.
- `profile/password_POST.xs`: input `new_password` recebe a mesma correção.
- Mensagem de erro de validação explícita para senha fraca, sem revelar dados de
  conta ou credenciais.
- Xano: publicação restrita aos dois endpoints, somente após dry-run e autorização
  explícita; verificação remota somente leitura.
- Sem alteração de frontend, rotas, contratos de resposta, dados, tabelas,
  permissões ou da tabela `user` (a coluna `password` mantém `minAlpha`/`minDigit`,
  válidos para tipo `password`).

## Capabilities

### New Capabilities

<!-- Nenhuma capability nova. -->

### Modified Capabilities

<!-- Nenhuma requirement muda: a spec internal-users já exige 8+ caracteres com
     letra e dígito. Esta change apenas torna o backend publicável capaz de aplicar
     a regra existente. Por isso o change declara skip_specs: true. -->

## Impact

- Xano: somente `users_POST.xs` e `profile/password_POST.xs` no grupo
  `Voltix Internal Users` (`voltix-internal-users`); publicação mínima e pendente de
  autorização explícita; dry-run antes e pull posterior.
- Frontend: nenhum. O contrato em `voltix/internal_users.py` já valida a mesma regra.
- Testes: asserções estáticas sobre os dois XanoScripts (sem filtros inválidos, com
  precondition `regex_test`), alinhadas a `tests/test_internal_users.py` existente.
- Documentação: evidências da change, `docs/roadmap-changes.md`,
  `docs/AI_AGENT_HANDOFF.md` e `.env.example` se necessário (nenhuma variável nova é
  esperada).
- Fora do escopo: recuperação de senha de `Cliente`, rate limiting, revogação de
  tokens, alteração da coluna `password` da tabela `user`, mudança de contratos
  HTTP, qualquer mudança no frontend e qualquer escrita em dados reais.
