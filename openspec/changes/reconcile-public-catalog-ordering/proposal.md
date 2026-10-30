## Why
O novo pull confirmou ausência de ordenação nas categorias públicas e nas variações do detalhe, embora a fonte local já defina name asc e sku asc. A navegação pode apresentar ordem diferente da prevista.
## What Changes
Publicar somente a ordenação das duas consultas existentes. Tornar explícito esse contrato na spec. Conferir a listagem pública sem alterar seus filtros, campos ou URLs assinadas.
## Capabilities
### Modified Capabilities
- public-catalog: ordenar categorias por nome e variações por SKU.
## Impact
Somente GET categories e GET products/{product_id}. Sem dados, tabelas, autenticação, endpoints novos, frontend, estoque, preços ou operações de escrita. A listagem de produtos e o endpoint de imagem ficam fora do pacote.
