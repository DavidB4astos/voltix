# Evidência — Cache curto e tratamento de HTTP 429 no Dashboard e CRM

Data: 21/11/2026  
Worktree: `.worktrees/cache-internal-dashboards` (branch `cache-internal-dashboards`)

## 1. Alterações aplicadas

- [voltix.py](file:///c:/Users/David%20Bastos/Downloads/PROJETO%20VOLTIX/PROJETO%20VOLTIX/voltix/.worktrees/cache-internal-dashboards/voltix/voltix.py):
  - Adicionados `_internal_dashboard_loaded_at` e `_internal_crm_loaded_at` (limpos em `_clear_internal_dashboard` e `_clear_internal_crm`).
  - `select_internal_section`: evita recarregar `Dashboard` ou `CRM` na troca de aba quando o snapshot ainda está dentro da janela de 20 s (mantendo o botão manual de atualização).
  - `load_internal_crm`: reaproveita `self.internal_dashboard[0]` quando carregado sem filtros nos últimos 20 s, economizando 1 chamada a `reports/sales`.
  - Tratamento explícito de `HTTP 429` em `load_internal_dashboard` e `load_internal_crm`.
- [test_cache_internal_dashboards.py](file:///c:/Users/David%20Bastos/Downloads/PROJETO%20VOLTIX/PROJETO%20VOLTIX/voltix/.worktrees/cache-internal-dashboards/tests/test_cache_internal_dashboards.py): teste unitário cobrindo o reaproveitamento da janela de 20 s na troca de abas.

## 2. Gates executados

- `python -m unittest discover -s tests -q`: `456/456` OK.
- `python -m reflex compile` + `git restore reflex.lock`: compilado sem erros.
- `git diff --check` e `openspec validate --all --strict`: limpos após arquivamento com `--skip-specs`.
