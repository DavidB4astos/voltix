## Context

Ver `proposal.md - Why`. O frontend Reflex já possui todo o fluxo de catálogo público (`load_public_catalog`, `_fetch_public_products`, `load_public_product_details`, `_public_product_image`) e os XanoScripts públicos já estão publicados e respondem nos caminhos `/categories`, `/products`, `/products/{product_id}` e `/products/{product_id}/image`. As causas do não-carregamento são de configuração e de montagem de URL no cliente, não de backend.

## Goals / Non-Goals

**Goals:**

- Fazer o catálogo público carregar dados reais usando os quatro destinos configurados por ambiente.
- Corrigir a montagem da URL da imagem para atingir o endpoint dedicado de imagem do produto.
- Manter os testes verdes sem enfraquecer as validações de contrato existentes.

**Non-Goals:**

- Não alterar XanoScripts, a lógica de associações (joins) do `products_GET.xs`, nem dados no Xano.
- Não alterar rotas, sessão, autorização, regras de negócio, carrinho, checkout, pedidos ou CRM.
- Não introduzir dependências novas.

## Decisions

- **Configuração por ambiente.** Os quatro destinos públicos passam a ser definidos no `.env` (ignorado pelo Git), reutilizando as chaves já declaradas em `.env.example` (`XANO_PUBLIC_CATEGORIES_URL`, `XANO_PUBLIC_PRODUCTS_URL`, `XANO_PUBLIC_PRODUCT_DETAILS_URL`, `XANO_PUBLIC_PRODUCT_IMAGE_URL`). Alternativa considerada: embutir a base no código — rejeitada por versionar endereços e violar `reflex-xano-integration`.
- **Detalhes e imagem compartilham a base de produtos.** O código anexa `/{id}` ao destino; por isso o destino de detalhes é `.../products` (resulta em `/products/{id}`). Para a imagem, adiciona-se um parâmetro opcional `path_suffix` a `_public_catalog_request`, usado por `_public_product_image` com `path_suffix="/image"`, resultando em `/products/{id}/image`. Alternativa considerada: montar a URL da imagem fora do helper — rejeitada por duplicar a lógica de normalização/consulta. Alternativa considerada: alterar o caminho no Xano — rejeitada porque os endpoints já estão publicados e não devem ser alterados.
- **Teste de contrato alinhado ao XanoScript atual.** As assertivas que esperam `$db.categoria.status`/`$db.marca.status` passam a esperar `$category_record.status`/`$brand_record.status`, refletindo o `products_GET.xs` atual, que resolve nomes via `db.get` no `foreach` (sem `join`). As demais validações (somente leitura, sem `db.add`/`db.patch`/`db.del`, ausência de `imagem_principal` na listagem/detalhes, `storage.sign_private_url` na imagem) permanecem.

## Risks / Trade-offs

- [Destino de imagem mal configurado apontaria para o endpoint de detalhes e retornaria `""` silenciosamente] → o destino dedicado e o teste de contrato cobrem a montagem correta do caminho.
- [Ausência de dados de `variacao_produto`/`imagem_principal` no Xano faz o produto aparecer sem variações/de imagem] → fora de escopo (dados), sem alteração de código; documentado no proposal.
- [`.env` é sensível] → permanece ignorado pelo Git; nenhum valor é versionado.

## Migration Plan

1. Definir as quatro variáveis públicas no `.env` local.
2. Aplicar a correção de montagem de URL no `voltix/voltix.py`.
3. Ajustar o teste de contrato e executar a suíte de testes.
