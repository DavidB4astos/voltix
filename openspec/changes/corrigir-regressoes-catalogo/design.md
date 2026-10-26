## Context

Os testes do catálogo público (`tests/test_public_catalog.py`) falhavam porque `_fetch_public_products` não aceitava o parâmetro de busca, a listagem não mapeava `image_url` do payload e executava erroneamente requisições individuais (`_public_product_image`) para cada produto.

## Goals / Non-Goals

**Goals:**
- Permitir que `_fetch_public_products` receba `category_id` e `search` e envie `q` ao Xano.
- Mapear corretamente `image_url` da resposta da listagem pública em `_public_product_entry`.
- Eliminar o uso de `_public_product_image` na listagem de produtos.
- Atualizar a cache key para incluir o termo de busca.

**Non-Goals:**
- Alterar tabelas, banco de dados ou endpoints do Xano.
- Modificar os arquivos de teste unitário para mascarar falhas da implementação.

## Decisions

### 1) Mapeamento de Image URL
- Extrair `image_url` de `payload.get("image_url")`, validando URL HTTPS se presente.

### 2) Assinatura de `_fetch_public_products`
- Assinatura: `async def _fetch_public_products(self, category_id: str = "", search: str = "") -> list[PublicProductEntry]:`
- Enviar `q: search.strip()` em `query_params` quando não vazio.

### 3) Cache Key
- Incluir `search.strip()` na chave de cache junto com `category_id`.
