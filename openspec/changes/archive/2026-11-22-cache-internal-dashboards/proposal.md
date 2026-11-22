## Why

Durante a navegação no `/interno`, alternar entre `Clientes`, `Dashboard` e `CRM` dispara leituras repetidas ao Xano Free (limite de 10 requisições / 20 s). Além disso:
- `load_internal_dashboard` e `load_internal_crm` limpam os dados já carregados antes de consultar o backend; se ocorrer `HTTP 429`, a tela perde os dados e exibe a mensagem genérica `"Verifique o acesso e tente novamente."`.
- `load_internal_crm` consulta `reports/sales` mesmo quando o `Dashboard` acabou de consultá-lo sem filtros.

## What Changes

- **Cache curto (20 s) na troca de aba (`select_internal_section`):**
  - Ao abrir `Dashboard` ou `CRM` pela troca de aba, se já houver snapshot carregado há menos de 20 s (para o mesmo usuário/filtros), reutilizar o estado atual sem nova chamada ao Xano. O botão manual `Carregar / atualizar` continua forçando leitura fresca.
- **Reaproveitamento de `reports/sales` no `CRM`:**
  - Quando o `Dashboard` já tiver carregado `reports/sales` sem filtro de datas nos últimos 20 s para o mesmo usuário, `load_internal_crm` reutiliza esse resultado sem gastar 1 requisição extra.
- **Tratamento explícito de `HTTP 429`:**
  - Exibir mensagem específica de limite temporário (`"Limite temporário de requisições do plano gratuito (10 req/20 s). Aguarde ~20 segundos e tente novamente."`) em `load_internal_dashboard` e `load_internal_crm`.
- **Fora do escopo:** alterações em Xano, endpoints, regras de autorização (`401`/`403` continuam encerrando a sessão) ou specs consolidadas.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- Nenhuma (`skip_specs: true` em `.openspec.yaml`).

## Impact

- **Worktree:** `.worktrees/cache-internal-dashboards` (branch `cache-internal-dashboards`).
- **Arquivos:** `voltix/voltix.py` e teste focado em `tests/`.
- **Gates:** `python -m unittest discover -s tests -q`, `reflex compile` (com restauração de `reflex.lock/*`), `git diff --check` e `openspec validate --all --strict`.
