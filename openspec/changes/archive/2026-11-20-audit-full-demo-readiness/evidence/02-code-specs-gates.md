# Evidência 02 — Código, specs e gates (20/11/2026)

## Objetivo

Conferir coerência entre documentação, OpenSpec, testes, compile, diff e estado do Git, sem alterar
código, specs consolidadas ou configuração.

## Resultados

| Gate | Comando / fonte | Resultado |
| --- | --- | --- |
| Suíte completa | `python.exe -m unittest discover -s tests -q` (venv `.venv-novo-pc`, CWD no worktree) | **Ran 445 tests ... OK** em 3,835 s |
| Compile | `reflex.exe compile` | `Success: App compiled successfully in 23.584 seconds` |
| Whitespace | `git diff --check` | limpo |
| OpenSpec | `openspec validate --all --strict` | **29 passed, 0 failed (29 items)** — 28 specs + a change ativa; apenas avisos informativos de requisitos com mais de 500 caracteres |
| Worktree | `git status --short --branch` | `HEAD (no branch)`; único item não rastreado é a própria change; `main` em `origin/main` permanece limpo |

### Observações sobre a execução

- O wrapper PowerShell reportou `exit code 1` para a suíte porque redirecionou para stderr três
  `ResourceWarning: Implicitly cleaning up <HTTPError 429/403/401>` originados de objetos de erro
  simulados nos testes (`tempfile.py`). O resultado do `unittest` foi `OK` com 445 testes; não houve
  chamada real ao Xano (duração de 3,8 s e mocks explícitos nos testes).
- `reflex compile` atualizou `reflex.lock/bun.lock` e `reflex.lock/package.json`; ambos foram
  restaurados com `git restore --worktree`, antes do `git diff --check`.
- O compile emitiu aviso informativo de que a versão instalada do Reflex (0.9.12) está desatualizada
  em relação à 0.11.0 disponível. Não há change aprovada para atualização de dependências; registrado
  como informação, sem ação nesta auditoria.

## Conferência de documentação (tarefa 3.5)

Fontes: `docs/AI_AGENT_HANDOFF.md` e `docs/roadmap-changes.md`, comparadas ao commit `79f57a5`.

- **Changes ativas:** consistente. O handoff orienta consultar `openspec list` em vez de presumir
  change ativa (linha 135); as seções históricas citam `audit-runtime-screens-and-flows` e
  `fix-demo-blockers` como arquivadas em 20/11 (linhas 98–103 e 698–710). O roadmap descreve ambas
  como concluídas (linhas 300–329). Nenhuma afirmação de change ativa concorrente.
- **Testes:** inconsistência pontual em `docs/AI_AGENT_HANDOFF.md:631` — "A suíte mais recente
  registrada teve **435 testes aprovados**". O próprio arquivo registra 445 testes em duas passagens
  posteriores (linhas 99 e 708) e a execução atual confirmou 445. Classificação: **pós-entrega**
  (documentação desatualizada, sem impacto na demo); correção reservada para a tarefa 6.5.
  As demais contagens (435 em linha 94) são registros datados de 13/11 e estão corretamente
  contextualizados como históricos.
- **Xano:** consistente. Handoff e roadmap mantêm E6 (compra E2E bloqueada até ambiente isolado),
  a decisão de verificação remota somente leitura, o upload com 403 histórico no plano Free, o limite
  de 10 requisições/20 s e os joins de carrinho/checkout como pendências de prova isolada. Nenhuma
  afirmação de publicação ou escrita nova nesta auditoria.
- **Caminhos de ambiente:** `.venv-windows`, `.venv-novo-pc` e `.venv` existem no repositório
  principal; o comando do handoff é executável. Nenhuma correção necessária.

## Limitações

- A conferência documental cobriu apenas os dois arquivos definidos na tarefa 3.5; documentos de
  `docs/ap2/` e `docs/deferred-changes/` são registros históricos/datados e não foram revalidados.
- O `exit code 1` do wrapper PowerShell não indica falha de teste; o veredito do `unittest` foi `OK`.
- A suíte foi executada com o Python do repositório principal apontando para o CWD do worktree, pois
  o worktree não contém virtualenv versionado (dependências não fazem parte do escopo da change).
