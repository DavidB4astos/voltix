# public-catalog Specification

## Purpose
Permitir que qualquer visitante consulte produtos ativos da Voltix, navegue por categorias ativas e veja detalhes comerciais sem autenticação ou acesso às operações administrativas.

## Requirements

### Requirement: Visitors can browse the public product catalog

O cat�logo p�blico SHALL permitir filtrar produtos ATIVO por categoria, quando fornecido o par�metro `category_id` v�lido e correspondente a uma categoria ATIVA. Al�m do filtro por categoria, o cat�logo p�blico SHALL permitir filtrar por nome do produto quando fornecido o par�metro opcional `q`. A busca por nome SHALL ser por correspond�ncia parcial, case-insensitive, aplicada apenas ao campo `nome` dos produtos. O par�metro `q` SHALL ser combinado com `category_id` quando ambos forem fornecidos (condi��o AND). Quando `q` for vazio ou composto apenas por espa�os em branco, ele SHALL ser ignorado. A busca SHALL respeitar que apenas produtos ATIVO sejam considerados. O formato da resposta, os endpoints p�blicos existentes e as demais regras do cat�logo p�blico SHALL permanecer inalterados.

#### Scenario: Anonymous visitor lists active products
- **WHEN** o visitante an�nimo acessa a listagem p�blica sem par�metros
- **THEN** s�o retornados apenas produtos ATIVO

#### Scenario: Product has an inactive category or brand association
- **WHEN** um produto ATIVO est� associado a uma categoria INATIVA ou marca INATIVA
- **THEN** o cat�logo p�blico omite o nome da categoria/marca, sem excluir o produto

#### Scenario: Catalog read endpoint is called without authentication
- **WHEN** o endpoint p�blico de leitura do cat�logo � chamado sem autentica��o
- **THEN** a resposta � obtida normalmente para produtos ATIVO

#### Scenario: Visitor filters products by name
- **WHEN** o visitante fornece o par�metro `q` com parte do nome de um produto ATIVO
- **THEN** a listagem retorna apenas os produtos ATIVO cujo `nome` contenha o termo informado, sem distin��o entre mai�sculas e min�sculas

#### Scenario: Visitor combines name search and category filter
- **WHEN** o visitante fornece `q` e `category_id` v�lido para uma categoria ATIVA
- **THEN** a listagem retorna apenas produtos ATIVO que atendam ao filtro por nome e perten�am � categoria selecionada

#### Scenario: Name search returns no results
- **WHEN** o par�metro `q` n�o corresponde a nenhum produto ATIVO
- **THEN** a listagem retorna vazia e a interface apresenta o estado vazio

#### Scenario: Empty search term is ignored
- **WHEN** o par�metro `q` � vazio ou cont�m apenas espa�os em branco
- **THEN** o filtro por nome � ignorado e o comportamento � o mesmo da listagem sem busca

### Requirement: Visitors can navigate by active category
O catálogo SHALL apresentar e permitir a seleção de Categorias `ATIVO`. A seleção SHALL limitar os resultados a produtos `ATIVO` associados à Categoria selecionada; Categorias `INATIVO` não SHALL ser oferecidas como filtro.

#### Scenario: Visitor filters products by active category
- **WHEN** o visitante seleciona uma Categoria `ATIVO`
- **THEN** o catálogo apresenta somente produtos `ATIVO` associados à Categoria selecionada

#### Scenario: Inactive category is not available for navigation
- **WHEN** uma Categoria está `INATIVO`
- **THEN** ela não aparece na navegação/filtro público e não pode ser usada para obter resultados de uma categoria ativa

### Requirement: Visitors can view product details and active variations
O sistema SHALL permitir que visitantes consultem os detalhes de um produto `ATIVO`, incluindo suas variações `ATIVO`, preço e quantidade disponível. Variações `INATIVO` não SHALL ser apresentadas. Estoque zero SHALL permanecer distinto do status da variação e ser indicado como indisponível para compra; esta indicação não SHALL oferecer fluxo de compra.

#### Scenario: Visitor opens active product details
- **WHEN** o visitante solicita detalhes de um produto `ATIVO`
- **THEN** o sistema apresenta as informações do produto, associações públicas ativas e somente variações `ATIVO`, com preço e quantidade disponível

#### Scenario: Inactive product or variation is requested
- **WHEN** o visitante solicita detalhes de um produto `INATIVO` ou tenta obter uma variação `INATIVO`
- **THEN** o backend não disponibiliza os dados inativos e responde como recurso não encontrado

#### Scenario: Active variation has zero stock
- **WHEN** uma variação `ATIVO` tem quantidade disponível igual a zero
- **THEN** o catálogo apresenta a variação como ativa com quantidade zero e indica que está indisponível para compra, sem alterar seu status

#### Scenario: Active product has no active variations
- **WHEN** um produto `ATIVO` não possui variações `ATIVO`
- **THEN** seus dados gerais permanecem consultáveis, sem apresentar variações inativas nem controles de compra

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

### Requirement: Public catalog reuses recently loaded data

O carregamento do catálogo público SHALL reutilizar, por um curto período de expiração, os dados já obtidos (categorias e produtos com a respectiva imagem resolvida). Dentro desse período, navegar entre a Home e o Catálogo SHALL NOT emitir novas requisições ao Xano. Após a expiração, o próximo carregamento SHALL consultar o Xano novamente. A reutilização SHALL respeitar a seleção de categoria vigente e SHALL NOT alterar o formato das requisições nem os contratos dos endpoints públicos.

#### Scenario: Navigation within the reuse period reuses data
- **WHEN** o visitante carrega a Home ou o Catálogo e, dentro do período de expiração, navega para a outra página
- **THEN** o catálogo apresenta os mesmos dados sem emitir novas requisições ao Xano

#### Scenario: Data is refreshed after expiration
- **WHEN** o período de expiração termina e o catálogo é carregado novamente
- **THEN** o sistema consulta o Xano novamente e apresenta os dados atualizados

#### Scenario: Reuse respects the selected category
- **WHEN** o visitante seleciona uma categoria diferente da anterior
- **THEN** o sistema obtém os produtos correspondentes à categoria selecionada, sem reutilizar dados de uma seleção diferente

### Requirement: Public catalog prevents concurrent duplicate loads

Enquanto um carregamento do catálogo público estiver em andamento, novas solicitações de carregamento SHALL NOT disparar consultas duplicadas ao Xano; as solicitações concorrentes SHALL aguardar ou reutilizar o resultado do carregamento em andamento.

#### Scenario: Concurrent loads issue a single set of requests
- **WHEN** dois carregamentos do catálogo público são solicitados simultaneamente
- **THEN** apenas um conjunto de requisições é enviado ao Xano e ambos os carregamentos recebem o mesmo resultado

### Requirement: Public catalog respects Xano rate limiting

Ao receber HTTP 429 do Xano, o sistema SHALL aguardar conforme o cabeçalho `Retry-After` (ou um intervalo padrão quando ausente) e SHALL repetir a requisição por um número limitado de tentativas. Esgotadas as tentativas, a falha SHALL permanecer observável e nova tentativa SHALL ser possível. O sistema SHALL respeitar o limite do plano gratuito do Xano sem exigir mudança de plano e SHALL NOT simular sucesso.

#### Scenario: Transient rate limit is retried and succeeds
- **WHEN** o Xano responde HTTP 429 com `Retry-After` e uma tentativa seguinte retorna sucesso
- **THEN** o catálogo carrega os dados normalmente, sem apresentar falha ao visitante

#### Scenario: Retry-After interval is respected
- **WHEN** o Xano responde HTTP 429 informando um intervalo em `Retry-After`
- **THEN** o sistema aguarda aproximadamente esse intervalo antes de repetir a requisição

#### Scenario: Persistent rate limit remains observable
- **WHEN** o Xano continua respondendo HTTP 429 após o número máximo de tentativas
- **THEN** a interface informa que o catálogo não pôde ser carregado e permite nova tentativa

### Requirement: Public catalog failures are logged without exposing sensitive data

Falhas de carregamento do catálogo público SHALL ser registradas no backend com informação suficiente para diagnóstico (por exemplo, o endpoint lógico e o status HTTP). Os registros SHALL NOT conter credenciais, tokens, URLs completas com parâmetros sensíveis nem o caminho privado de armazenamento da imagem.

#### Scenario: Failure is recorded for diagnosis
- **WHEN** uma consulta do catálogo público falha após o tratamento de erros
- **THEN** o backend produz um registro de log identificando a causa/status e o endpoint lógico da falha

#### Scenario: Sensitive data is not logged
- **WHEN** um registro de falha é produzido
- **THEN** ele não contém credenciais, tokens, o caminho privado da imagem nem URLs completas com parâmetros sensíveis

### Requirement: Public catalog failures remain observable
Uma falha de rede, erro HTTP ou resposta inválida SHALL ser apresentada como falha de carregamento, sem dados ou sucesso simulados, e SHALL permitir nova tentativa quando aplicável. Falhas transitórias de limite de taxa (HTTP 429) SHALL ser tratadas com nova tentativa limitada, respeitando `Retry-After`, antes de reportar a falha ao visitante.

#### Scenario: Catalog request fails
- **WHEN** a consulta pública falha por indisponibilidade, erro HTTP ou resposta inválida
- **THEN** a interface informa que o catálogo não pôde ser carregado e não apresenta os dados da tentativa como resultado confirmado

#### Scenario: Transient rate limit is retried before reporting failure
- **WHEN** o Xano responde HTTP 429 de forma transitória
- **THEN** o sistema repete a requisição respeitando `Retry-After` e só reporta a falha se as tentativas se esgotarem

### Requirement: Public catalog client resolves endpoints from environment configuration
O cliente do catálogo público SHALL resolver, a partir de configuração de ambiente, os destinos de categorias, produtos, detalhes de produto e imagem de produto, sem embutir endereços fixos no código versionado nem expor credenciais ou informações sensíveis. As requisições ao catálogo público SHALL permanecer somente de leitura e anônimas.

#### Scenario: Configured endpoints are used
- **WHEN** o catálogo público é carregado em um ambiente com os quatro destinos configurados
- **THEN** o cliente consulta categorias, produtos (com filtro opcional por categoria), detalhes do produto e imagem do produto usando esses destinos configurados, sem depender de um endereço fixo no código

#### Scenario: Missing configuration fails explicitly
- **WHEN** uma configuração obrigatória de destino do catálogo público está ausente
- **THEN** o carregamento apresenta uma falha de configuração observável e não tenta uma chamada para um destino implícito

### Requirement: Public catalog distinguishes initial loading, empty, and populated states

O catálogo público SHALL apresentar estados visuais distintos e mutuamente exclusivos para a primeira carga da sessão: carregamento enquanto a consulta inicial ao backend não tiver sido concluída, lista vazia somente quando a carga inicial estiver concluída sem produtos disponíveis, e grade de produtos quando houver produtos. Antes da conclusão da primeira carga, o sistema SHALL NOT apresentar o estado de lista vazia como se o catálogo não tivesse produtos.

#### Scenario: Initial load in progress shows loading state
- **WHEN** um visitante abre o catálogo público antes de a primeira carga de dados da sessão ser concluída
- **THEN** a interface apresenta o estado de carregamento e não apresenta o estado de lista vazia nem a grade de produtos

#### Scenario: Completed load with no products shows empty state
- **WHEN** a primeira carga é concluída e não há produtos públicos disponíveis
- **THEN** a interface apresenta o estado de lista vazia

#### Scenario: Completed load with products shows the product list
- **WHEN** a primeira carga é concluída e há produtos públicos disponíveis
- **THEN** a interface apresenta a grade de produtos e não apresenta os estados de carregamento nem de lista vazia

#### Scenario: Failed initial load remains observable
- **WHEN** a primeira carga termina em falha após o tratamento de erros
- **THEN** a interface apresenta o estado de falha com nova tentativa e não apresenta o estado de lista vazia como resultado

### Requirement: Demo products display real images from local assets when available
The public catalog SHALL resolve images for demo products by matching the product SKU against a curated mapping of local static image assets. For SKUs matching `VTX-DEMO-*`, when a corresponding local image exists, the catalog SHALL present that local image instead of relying solely on Xano-provided image URLs. When no local image is available for a demo SKU, the catalog SHALL fall back to the existing image resolution behavior (Xano image endpoint or placeholder). This behavior applies to product cards, list/grid rendering, and product detail view. Non-demo products SHALL NOT be affected by this mapping.

#### Scenario: Catalog displays local image for demo SKU
- **WHEN** the catalog lists a product with SKU `VTX-DEMO-001` and a local image is mapped for that SKU
- **THEN** the rendered product card uses the local static image

#### Scenario: Catalog falls back to existing image for unmapped demo SKU
- **WHEN** the catalog lists a product with SKU `VTX-DEMO-XXX` with no local image mapping
- **THEN** the catalog uses the existing image resolution behavior (Xano `image_url` or placeholder)

#### Scenario: Non-demo product image resolution unchanged
- **WHEN** the catalog lists a non-demo product
- **THEN** image resolution follows the existing behavior with no reference to the demo SKU mapping

### Requirement: Public catalog search form and URL state
The catalog SHALL offer an explicitly labeled product-name search form submitted by Enter or Buscar. Typing alone SHALL NOT request the catalog. Applied queries SHALL use the existing anonymous q parameter combined with category_id, with URL encoding and no changes to public API access rules. The search field and incoming q SHALL be trimmed and limited to 100 characters. Applied search and editable draft SHALL be separate. Category changes SHALL preserve the applied term. Limpar filtros SHALL remove category, term and selected product details. Loading SHALL disable the controls and SHALL NOT show stale results as confirmed. Errors SHALL remain observable with retry. A successful search SHALL expose the applied term, count and a distinct no-results message. Reopening the catalog URL SHALL restore the applied filters. Home entry SHALL clear the draft as well as prior filters. Existing product_id entry SHALL still open product details.

#### Scenario: Visitor submits a search
- **WHEN** a visitor types a product name and submits by Enter or Buscar
- **THEN** the catalog URL encodes q and displays the real public results for that name

#### Scenario: Typing does not fetch results
- **WHEN** a visitor edits the search field without submitting
- **THEN** no catalog request is sent and the applied result set remains unchanged

#### Scenario: Visitor combines search with category
- **WHEN** a visitor changes the category after applying a search
- **THEN** the URL and results combine category_id with the applied q

#### Scenario: Visitor clears filters
- **WHEN** a visitor activates Limpar filtros
- **THEN** search, category and selected details are cleared and the unfiltered catalog loads

#### Scenario: Search finds no product
- **WHEN** the public query succeeds with no matching product
- **THEN** a no-results message appears and no stale grid is displayed

#### Scenario: Search fails and retries
- **WHEN** a public search request fails
- **THEN** the error is shown and retry uses the same applied search and category

#### Scenario: Visitor reopens a filtered URL
- **WHEN** the catalog opens with q and category_id
- **THEN** the input, category and loader use the normalized applied filters

#### Scenario: Visitor repeats the same search
- **WHEN** a visitor submits the filters already represented by the current URL
- **THEN** the existing loader runs and loading can finish without requiring a different route

### Requirement: Consistent public catalog product cards
The public catalog SHALL present each real product as an article with an H2 name, secondary brand/category when present, its complete available description, and an accessible Ver detalhes action preserving the existing product-details event. Cards SHALL reserve a consistent image area, contain photos without cropping/distortion, and show Imagem não disponível when the image URL is empty. They SHALL NOT substitute another model or invent a photograph, price, promotion, rating or availability. Approved local photos SHALL expose author, source and license from the manifest, with full original attribution available on the source link and in metadata. Only complete credits for existing local files with safe filenames SHALL be exposed; callers SHALL NOT mutate the credit cache. Styles SHALL remain catalog-scoped and SHALL preserve existing filters, search, result states and purchase behavior.

#### Scenario: Visitor compares product cards
- **WHEN** the catalog lists products with different image proportions or missing images
- **THEN** the cards reserve consistent visual space, preserve photo proportions and display the honest placeholder for absent URLs

#### Scenario: Visitor reads product information
- **WHEN** a product card appears
- **THEN** its name is an H2 and its real name/description remain readable without truncation, with brand/category omitted when absent

#### Scenario: Visitor opens details
- **WHEN** a visitor activates Ver detalhes for a card
- **THEN** the existing details event receives that product identifier and no purchase is submitted

#### Scenario: Approved photograph has attribution
- **WHEN** a card uses an approved local photo with complete credit metadata
- **THEN** its author, source and license are visible and the full attribution is retained without assigning it to another photo

#### Scenario: Incomplete or unsafe credit metadata
- **WHEN** credit metadata is incomplete, references a missing file or uses an unsafe filename
- **THEN** it is not offered as an approved credit mapping and callers cannot mutate the underlying cache

### Requirement: Clear desktop product detail presentation
The catalog SHALL present selected product details in a labeled section, with an H2 product name, secondary brand/category when available, complete available description and technical specifications. At desktop widths of at least 1024px, the main image and commercial information SHALL use two columns. Photos SHALL be contained without cropping or distortion, approved local photos SHALL expose the matching author/source/license, and missing image URLs SHALL show an honest placeholder. Prices SHALL use R$ with two decimal places and a decimal comma, without changing the underlying amount. Each active variation SHALL retain its real SKU, name, price and available quantity. Existing add-to-cart events SHALL remain unchanged and add one unit per activation; this quantity SHALL be explained. Out-of-stock variations SHALL keep disabled purchase controls and no-active-variation products SHALL have no purchase control. The close action, loading, error/retry, cart feedback and account/cart links SHALL preserve their behavior. Buttons SHALL have visible focus, readable labels and variation-specific accessible names. Styles SHALL remain detail-scoped and stack safely below desktop widths.

#### Scenario: Visitor inspects a photographed product
- **WHEN** a visitor opens a product with an approved local photo on desktop
- **THEN** the intact photo and matching credit appear alongside the real information, with the name as H2 and price in Brazilian decimal notation

#### Scenario: Visitor inspects a product without an image
- **WHEN** the selected product has an empty image URL
- **THEN** the detail shows Imagem não disponível and retains the available product information

#### Scenario: Visitor compares active variations
- **WHEN** a selected product has active variations
- **THEN** each variation displays its name or SKU fallback, real SKU, price, availability and distinctly named existing add-to-cart action explaining that one unit is added

#### Scenario: Purchase is unavailable
- **WHEN** a variation has zero stock or a cart mutation is in progress
- **THEN** its purchase action is disabled while the real stock indication remains visible

#### Scenario: No active variation exists
- **WHEN** the selected product has no active variations
- **THEN** an informative empty state appears without purchase controls

#### Scenario: Existing navigation and feedback remain usable
- **WHEN** the visitor closes the details or attempts to add a variation without a customer session
- **THEN** the existing close behavior or login feedback remains available, preserving catalog filters and existing events
