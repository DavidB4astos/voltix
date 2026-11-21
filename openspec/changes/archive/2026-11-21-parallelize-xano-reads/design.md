## Context

Todas as requisições HTTP ao Xano já usam `asyncio.to_thread(_request_xano_json, ...)`, portanto são não-bloqueantes e podem ser disparadas em paralelo via `asyncio.gather` sem alterar contratos ou semântica de erro.

## Goals / Non-Goals

- **Goals:**
  - Reduzir pela metade a latência de abertura de `Ver detalhes` no catálogo.
  - Reduzir a latência de carregamento do painel `CRM` substituindo 7 esperas sequenciais por `asyncio.gather` (ainda respeitando `bounded_read`).
- **Non-Goals:**
  - Remover chamadas exigidas por specs (ex.: `_public_product_image` no detalhe) ou alterar o plano Xano Free.

## Decisions

1. **`asyncio.gather` em `load_public_product_details`:** dispara `_public_catalog_request(XANO_PUBLIC_PRODUCT_DETAILS_URL_ENV, record_id=product_id)` e `_public_product_image(product_id)` juntos. Se `details` falhar, o `except` existente trata normalmente.
2. **`asyncio.gather` em `load_internal_crm`:** dispara as 7 chamadas `read(...)` juntas; `bounded_read` continua controlando a concorrência e erros `401`/`403` continuam limpando a sessão.
