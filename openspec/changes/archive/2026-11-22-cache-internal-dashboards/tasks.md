## 1. Cache curto e reaproveitamento entre Dashboard e CRM

- [x] 1.1 Adicionar timestamps privados `_internal_dashboard_loaded_at` e `_internal_crm_loaded_at` (limpos em `_clear_internal_dashboard`, `_clear_internal_crm` e troca de sessão) em `voltix/voltix.py`
- [x] 1.2 Evitar recarga automática na troca de aba em `select_internal_section` quando o snapshot ainda estiver dentro de 20 s, mantendo atualização manual nos botões
- [x] 1.3 Reaproveitar `self.internal_dashboard[0]` em `load_internal_crm` quando carregado sem filtros nos últimos 20 s

## 2. Tratamento claro de HTTP 429

- [x] 2.1 Exibir mensagem clara de rate limit (`HTTP 429`) em `load_internal_dashboard` e `load_internal_crm` sem mascarar como erro de acesso

## 3. Verificação e encerramento

- [x] 3.1 Adicionar testes unitários focados em `tests/` cobrindo cache de troca de aba, reaproveitamento de `reports/sales` e mensagem `HTTP 429`
- [x] 3.2 Executar `python -m unittest discover -s tests -q`, `reflex compile` (restaurando `reflex.lock/*`), `git diff --check` e `openspec validate --all --strict`
- [x] 3.3 Registrar evidência em `evidence/verification.md`, arquivar com `openspec archive cache-internal-dashboards -y --skip-specs` e solicitar autorização antes de commit/push
