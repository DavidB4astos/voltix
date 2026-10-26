## Why

Durante a finalização da AP2, testes do catálogo público apresentaram falhas e erros relacionados à assinatura de `_fetch_public_products` (que não aceitava o parâmetro de busca `search`/`q`), ao mapeamento incorreto de `product.image_url` (fazendo com que ficasse vazio apesar da resposta conter a URL assinada) e ao uso indevido de requisições individuais de imagem por produto (`_public_product_image`), desrespeitando o contrato que prevê URLs na própria listagem.

## What Changes

- Atualizar `_fetch_public_products` em `voltix/voltix.py` para aceitar `category_id` e `search` (parâmetro `q` enviado ao Xano).
- Corrigir `_public_product_entry` e `_public_catalog_products` para extrair e validar `image_url` diretamente do payload retornado pela listagem.
- Remover chamadas individuais a `_public_product_image` na listagem pública de produtos, preservando-as apenas para detalhes do produto.
- Atualizar chave de cache do catálogo para incluir o termo de busca (`search`/`q`), garantindo o isolamento correto dos resultados cacheados.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `public-catalog`: Correção do suporte a busca textual por `q`, mapeamento correto de `image_url` na listagem sem requisições HTTP individuais por produto, e isolamento de cache por termo de busca.

## Impact

- **Frontend (`voltix/voltix.py`)**: Ajuste na assinatura e lógica de `_fetch_public_products`, `_public_product_entry`, `_load_public_catalog_data` e chave de cache.
- **Testes**: Adequação da execução dos testes do catálogo sem alterar os testes em si.
