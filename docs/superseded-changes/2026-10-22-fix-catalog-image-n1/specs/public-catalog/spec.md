## MODIFIED Requirements

### Requirement: Public product images are delivered without exposing private storage paths

Quando houver imagem principal privada, o sistema SHALL disponibilizá-la ao visitante por uma URL assinada e temporária compatível com o armazenamento nativo do Xano. A resposta pública SHALL omitir o caminho privado original do arquivo. Produto sem imagem SHALL continuar consultável. A listagem pública de produtos SHALL incluir, para cada produto `ATIVO`, a URL assinada temporária da imagem principal quando existente, ou a indicação de ausência de imagem. O endpoint público dedicado de imagem SHALL permanecer disponível e SHALL ser usado pelo detalhe do produto. A listagem SHALL NOT exigir uma requisição HTTP de imagem por produto.

#### Scenario: Product has a private main image
- **WHEN** o catálogo lista um produto com imagem principal privada
- **THEN** a listagem retorna uma URL assinada temporária no campo de imagem do produto, sem retornar o caminho privado original

#### Scenario: Product has no main image
- **WHEN** o catálogo lista um produto sem imagem principal
- **THEN** a listagem indica a ausência de imagem e o sistema apresenta os demais dados normalmente, sem exigir imagem

#### Scenario: Catalog listing includes image references for all products
- **WHEN** o catálogo lista múltiplos produtos `ATIVO`
- **THEN** a resposta da listagem inclui a referência de imagem de cada produto e o cliente não emite uma requisição de imagem por produto

#### Scenario: Client requests the dedicated image endpoint
- **WHEN** o visitante abre o detalhe de um produto
- **THEN** o cliente solicita a imagem ao endpoint dedicado de imagem do produto, usando a URL assinada retornada quando existir

### Requirement: Demo products display real images from local assets when available

The public catalog SHALL resolve images for demo products by matching the product SKU against a curated mapping of local static image assets. For SKUs matching `VTX-DEMO-*`, when a corresponding local image exists, the catalog SHALL present that local image instead of relying solely on Xano-provided image URLs. When no local image is available for a demo SKU, the catalog SHALL fall back to the existing image resolution behavior (the Xano-provided image URL returned with the product listing or a placeholder). This behavior applies to product cards, list/grid rendering, and product detail view. Non-demo products SHALL NOT be affected by this mapping.

#### Scenario: Catalog displays local image for demo SKU
- **WHEN** o catálogo lista um produto com SKU `VTX-DEMO-001` e existe uma imagem local mapeada para esse SKU
- **THEN** o card renderizado usa a imagem estática local

#### Scenario: Catalog falls back to existing image for unmapped demo SKU
- **WHEN** o catálogo lista um produto com SKU `VTX-DEMO-XXX` sem imagem local mapeada
- **THEN** o catálogo usa a URL de imagem fornecida pelo Xano na listagem ou o placeholder quando ela não existir

#### Scenario: Non-demo product image resolution unchanged
- **WHEN** o catálogo lista um produto que não é demo
- **THEN** a resolução de imagem segue o comportamento existente, sem referência ao mapeamento de SKUs demo

## ADDED Requirements

### Requirement: Public catalog loads images without per-product HTTP requests

A carga da listagem pública SHALL obter as referências de imagem de todos os produtos na mesma resposta de produtos, sem emitir uma requisição HTTP de imagem por produto. Uma carga fria SHALL emitir no máximo uma requisição de categorias e uma requisição de produtos, independentemente da quantidade de produtos `ATIVO`. O endpoint dedicado de imagem SHALL permanecer disponível e SHALL ser usado pelo detalhe do produto.

#### Scenario: Cold catalog load has bounded requests
- **WHEN** o cache do catálogo está expirado e a listagem pública é carregada com N produtos `ATIVO`
- **THEN** o cliente envia uma requisição de categorias e uma requisição de produtos, sem requisições de imagem por produto

#### Scenario: Many products do not multiply image requests
- **WHEN** a quantidade de produtos `ATIVO` aumenta
- **THEN** o número de requisições HTTP da listagem permanece limitado a duas (categorias e produtos)

#### Scenario: Product detail uses the dedicated image endpoint
- **WHEN** um visitante abre o detalhe de um produto `ATIVO`
- **THEN** o sistema solicita a imagem desse produto ao endpoint dedicado de imagem, sem alterar o limite de requisições da listagem
