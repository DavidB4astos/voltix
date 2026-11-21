## Why

Atualmente duas operações muito usadas na demonstração executam leituras HTTP independentes de forma sequencial em `voltix/voltix.py`:
1. `load_public_product_details(product_id)` aguarda o retorno de `details` para só então chamar `_public_product_image(product_id)` (2 idas sequenciais de rede).
2. `load_internal_crm()` executa 7 leituras independentes em série (`customers`, 3 contagens de `atendimentos`, `orders`, `recentes` e `sales`), somando a latência de todas em sequência.

## What Changes

- **Paralelizar `load_public_product_details` (`voltix/voltix.py`):**
  - Executar a busca de detalhes e `_public_product_image(product_id)` em paralelo com `asyncio.gather`.
- **Paralelizar `load_internal_crm` (`voltix/voltix.py`):**
  - Executar as 7 leituras `read(...)` independentes com `asyncio.gather`, mantendo `bounded_read`, checagem `current()` e tratamento de `401`/`403` e demais erros.
- **Fora do escopo:** alterações em Xano, endpoints, regras de negócio, cache ou specs consolidadas.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- Nenhuma (`skip_specs: true` em `.openspec.yaml`).

## Impact

- **Worktree:** `.worktrees/parallelize-xano-reads` (branch `parallelize-xano-reads`).
- **Arquivos:** `voltix/voltix.py` e teste focado em `tests/`.
- **Gates:** `python -m unittest discover -s tests -q`, `reflex compile` (com restauração de `reflex.lock/*`), `git diff --check` e `openspec validate --all --strict`.
