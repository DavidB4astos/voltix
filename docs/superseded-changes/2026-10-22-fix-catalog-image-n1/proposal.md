## Why

O carregamento do catálogo público faz uma requisição HTTP de imagem por produto, em paralelo. Com 20 produtos ativos, uma única carga fria emite ~22 requisições e excede o limite do Xano Free (10 requisições por 20 segundos), resultando em HTTP 429 em `public_catalog.product_image`. Isso impede a verificação de `/catalogo`, bloqueia o smoke test da change `refine-storefront-home` e mantém o archive impedido.

## What Changes

- **Backend (Xano)**: `products_GET.xs` passa a retornar, para cada produto `ATIVO`, um campo `image_url` com URL assinada temporária quando houver imagem principal, ou `null` quando não houver. O caminho privado (`imagem_principal`) continua omitido da resposta. A mesma regra vale para a listagem completa e para a listagem filtrada por categoria. O endpoint dedicado `products/{id}/image` permanece disponível para o detalhe do produto.
- **Frontend (Reflex)**: `_public_catalog_products` aceita e valida o novo campo `image_url`; `_fetch_public_products` passa a usar a imagem retornada pela listagem e deixa de executar `_public_product_image` para cada produto. `resolve_demo_image_named` continua substituindo a URL por ativo local aprovado quando aplicável. O detalhe do produto mantém a consulta pontual ao endpoint de imagem.
- **Contrato**: a carga do catálogo passa a emitir 2 requisições HTTP (categorias + produtos), independentemente da quantidade de produtos, em vez de 2 + N. O campo novo é aditivo; nenhum campo existente é removido.
- **Testes**: atualizar mocks e contagens de chamadas afetadas; adicionar teste de regressão que confirma que uma carga do catálogo não dispara requisições de imagem por produto e que a imagem da listagem é utilizada.
- **Evidência**: após a implementação, registrar a nova medição de requisições e o resultado do smoke de `/catalogo` em `docs/ap2/07-evidencias-catalogo-429.md` e atualizar `docs/roadmap-changes.md`.

**Fora do escopo:** alterar o layout ou o comportamento visual da Home/catálogo; baixar ou completar imagens demo; recomprimir imagens; mudar o TTL do cache; adicionar paginação; alterar o fluxo de detalhe do produto; autenticação/autorização; outras rotas; plano do Xano; dependências, versão do Reflex ou lockfiles; qualquer alteração de preço, estoque ou elegibilidade.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `public-catalog`: a entrega de imagens passa a ocorrer na própria listagem de produtos por meio de URL assinada temporária, sem uma requisição HTTP por produto; o endpoint dedicado de imagem permanece para o detalhe. O carregamento passa a ter quantidade limitada de requisições, independente do número de produtos.

## Impact

- **Backend**: `xano/api/public_catalog/products_GET.xs` (projeção interna de `imagem_principal`, assinatura por produto e campo `image_url` na resposta).
- **Frontend**: `voltix/voltix/voltix.py` (`_public_catalog_products` e `_fetch_public_products`); `product_id_image_GET.xs` e o fluxo de detalhe permanecem inalterados.
- **Testes**: `tests/test_public_catalog.py` (payloads, mocks e contagens de requisições) e novo teste de regressão para o limite de requisições.
- **Documentação**: `docs/ap2/07-evidencias-catalogo-429.md` e `docs/roadmap-changes.md`.
- **Dependências**: nenhuma nova.
- **Segurança**: a resposta pública continua sem o caminho privado; a URL assinada é temporária (TTL 3600 s) e somente de leitura.
