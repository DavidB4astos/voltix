## 1. Paralelização de leituras independentes

- [x] 1.1 Paralelizar `details` e `_public_product_image(product_id)` com `asyncio.gather` em `load_public_product_details` (`voltix/voltix.py`)
- [x] 1.2 Paralelizar as 7 leituras `read(...)` com `asyncio.gather` em `load_internal_crm` (`voltix/voltix.py`) preservando `bounded_read` e tratamento de `401`/`403`

## 2. Verificação e encerramento

- [x] 2.1 Adicionar teste focado em `tests/` verificando execução concorrente de `load_public_product_details` e `load_internal_crm`
- [x] 2.2 Executar `python -m unittest discover -s tests -q`, `reflex compile` (restaurando `reflex.lock/*`), `git diff --check` e `openspec validate --all --strict`
- [x] 2.3 Registrar evidência em `evidence/verification.md`, arquivar com `openspec archive parallelize-xano-reads -y --skip-specs` e solicitar autorização antes de commit/push
