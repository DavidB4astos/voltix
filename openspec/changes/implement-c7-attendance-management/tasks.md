## 1. Preparação

- [x] 1.1 Confirmar o escopo com o usuário (backend + spec, sem tela; grupo `Voltix Internal CRM`; 5 endpoints; responsável/ADMIN finaliza) — verificação: decisão registrada
- [x] 1.2 Conferir `CLIENTE`, `pedido`, `user` e os padrões de auth/transação de C3/C4/C6 — verificação: leitura dos `*.xs` coerente com a delta

## 2. Implementação

- [x] 2.1 Criar `xano/table/atendimento.xs` com FKs, enum de status, timestamps privados e índices — verificação: language server oficial sem erros
- [x] 2.2 Criar `api_group "Voltix Internal CRM"` com canonical `voltix-internal-crm` — verificação: grupo reconhecido pelo language server
- [x] 2.3 Criar `POST atendimentos` com validação de Cliente/Pedido do mesmo Cliente, responsável = `$auth.id` e status `ABERTO` em transação — verificação: preconditions explícitas
- [x] 2.4 Criar `GET atendimentos` com filtros `cliente_id`/`status`, paginação 20/50 e ordenação `data_atendimento desc, id desc` — verificação: `db.query` com paging/totals
- [x] 2.5 Criar `GET atendimentos/{attendance_id}` com `notfound` para ausente e resposta sem dados pessoais — verificação: `output` restrito
- [x] 2.6 Criar `PATCH atendimentos/{attendance_id}` editando apenas conteúdo de `ABERTO`/`EM_ATENDIMENTO` e atualizando `updated_at` — verificação: teste de imutabilidade
- [x] 2.7 Criar `POST atendimentos/{attendance_id}/status` com regras de responsável/ADMIN, transições válidas, imutabilidade e no-op idempotente — verificação: matriz de transições revisada
- [x] 2.8 Garantir autorização `FUNCIONARIO`/`ADMINISTRADOR` `ATIVO` em todos os endpoints — verificação: preconditions em todos os arquivos
- [x] 2.9 Garantir que nenhuma resposta exponha dados pessoais do Cliente — verificação: revisão dos contratos

## 3. Verificação local

- [x] 3.1 `openspec validate implement-c7-attendance-management --strict` — verificação: válido
- [x] 3.2 Validar os `*.xs` com o language server oficial (`%TEMP%\xs-lsp\validate.mjs`) — verificação: sem erros
- [x] 3.3 Suíte `python -m unittest discover -s tests -q` preservada — verificação: sem regressões
- [x] 3.4 `openspec validate --all --strict` — verificação: todas as specs válidas
- [x] 3.5 `git diff --check` limpo e `reflex.lock/*` restaurado — verificação: sem whitespace/conflitos
- [x] 3.6 Commit focado com a implementação — verificação: `git log --oneline -1`

## 4. Medição E5 e publicação restrita

- [ ] 4.1 Medir plano/consumo atual no dashboard Xano e registrar a evidência — verificação: dados do dashboard anexados
- [ ] 4.2 Apresentar impacto estimado da C7 e **GATE** — aguardar autorização explícita antes de publicar — verificação: OK registrado
- [x] 4.3 Dry-run restrito à tabela e aos endpoints novos — verificação: preview anexado à evidência
- [ ] 4.4 Publicar somente após o gate — verificação: saída da CLI registrada
- [ ] 4.5 Pull independente pós-publicação — verificação: diff confere com o local

## 5. Verificação remota mínima

- [ ] 5.1 Checagem somente leitura (rota sem sessão → 401), sem executar consulta autenticada — verificação: evidência em `evidence/`

## 6. Encerramento

- [ ] 6.1 Arquivar a change e consolidar a capability `attendance-management` — verificação: `openspec validate --all --strict`
- [ ] 6.2 Atualizar `docs/roadmap-changes.md` (C7 concluída, matriz de autorização) e `docs/AI_AGENT_HANDOFF.md` — verificação: consistente com a evidência
- [ ] 6.3 `git status --short --branch` limpo — verificação: nada pendente
- [ ] 6.4 Commit focado + push somente com autorização explícita — verificação: `git log --oneline -1`
