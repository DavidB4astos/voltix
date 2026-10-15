## Why

O catálogo público da Voltix não carrega dados reais: as variáveis de ambiente dos endpoints públicos não estão definidas no ambiente de execução, e o frontend constrói a URL da imagem apontando para o endpoint de detalhes em vez do endpoint dedicado de imagem, de modo que as imagens nunca são exibidas e a falha é silenciosa. É necessário conectar o frontend Reflex, de forma verificável, aos endpoints públicos já publicados no Xano.

## What Changes

- Configurar no ambiente (`.env`, não versionado) os quatro destinos públicos: categorias, produtos, detalhes de produto e imagem de produto, com a base `https://x8ki-letl-twmt.n7.xano.io/api:cVn4Vybh`.
- Ajustar a montagem de URL no frontend para que a imagem do produto seja solicitada em `/products/{product_id}/image`, mantendo categorias (`/categories`), produtos com filtro opcional (`/products?category_id=`), e detalhes (`/products/{product_id}`) em seus caminhos atuais.
- Alinhar o teste de contrato dos XanoScripts públicos ao conteúdo atual de `products_GET.xs`, sem remover validações e sem alterar a lógica de associações (não usar `join`).
- Manter as requisições públicas anônimas e somente de leitura.

Ficam fora desta Change: alterações nos XanoScripts e na lógica de joins, alteração de dados no Xano, novas rotas, autenticação, regras de negócio, carrinho, checkout, pedidos, pagamentos e CRM.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `public-catalog`: o cliente do catálogo público passa a resolver seus endpoints por configuração de ambiente e a obter a imagem do produto pelo endpoint dedicado de imagem, sem expor o caminho privado.

## Impact

- `voltix/voltix.py`: ajuste de `_public_catalog_request` (suporte a sufixo de caminho) e de `_public_product_image`.
- `.env` local (ignorado pelo Git) passa a conter as quatro URLs públicas; `.env.example` já lista as chaves como template.
- `tests/test_public_catalog.py`: assertivas do contrato read-only dos XanoScripts públicos passam a refletir o `products_GET.xs` atual.
- Sem novas dependências e sem alteração de rotas, sessão, autorização, State de negócio ou dados/XanoScript.
