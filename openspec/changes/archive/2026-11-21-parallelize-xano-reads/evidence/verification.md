# Evidência — Paralelização de leituras independentes ao Xano

Data: 21/11/2026  
Worktree: `.worktrees/parallelize-xano-reads` (branch `parallelize-xano-reads`)

## 1. Alterações aplicadas

- [voltix.py](file:///c:/Users/David%20Bastos/Downloads/PROJETO%20VOLTIX/PROJETO%20VOLTIX/voltix/.worktrees/parallelize-xano-reads/voltix/voltix.py):
  - `load_public_product_details`: `details` e `_public_product_image(product_id)` agora executam em paralelo via `asyncio.gather`.
  - `load_internal_crm`: as 7 leituras independentes agora executam via `asyncio.gather` (mantendo `bounded_read`, `current()` e tratamento de `401`/`403`).
- [test_parallel_xano_reads.py](file:///c:/Users/David%20Bastos/Downloads/PROJETO%20VOLTIX/PROJETO%20VOLTIX/voltix/.worktrees/parallelize-xano-reads/tests/test_parallel_xano_reads.py): teste verificando execução concorrente de detalhes e imagem.

## 2. Gates executados

- `python -m unittest discover -s tests -q`: `455/455` OK.
- `python -m reflex compile` + `git restore reflex.lock`: compilado sem erros.
- `git diff --check` e `openspec validate --all --strict`: limpos após arquivamento com `--skip-specs`.
