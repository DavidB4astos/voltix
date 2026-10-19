# public-catalog Specification

## Purpose
Permitir que qualquer visitante consulte produtos ativos da Voltix, navegue por categorias ativas e veja detalhes comerciais sem autenticação ou acesso às operações administrativas.

## Requirements

### Requirement: Visitors can browse the public product catalog
O sistema SHALL permitir que visitantes sem sessão consultem produtos com status `ATIVO` e suas informações gerais disponíveis: nome, descrição, especificações técnicas, imagem principal quando existente e associações a categoria e marca somente quando essas entidades estiverem `ATIVO`. A consulta pública SHALL ser somente de leitura e SHALL retornar apenas os campos necessários à apresentação do catálogo.

#### Scenario: Anonymous visitor lists active products
- **WHEN** um visitante sem sessão abre o catálogo público
- **THEN** o sistema apresenta produtos `ATIVO` e não apresenta produtos `INATIVO`, sem exigir login

#### Scenario: Product has an inactive category or brand association
- **WHEN** um produto `ATIVO` possui associação existente com Categoria ou Marca `INATIVO`
- **THEN** o produto permanece consultável conforme seu próprio status, o nome da entidade inativa não é apresentado como opção ou classificação pública, e nenhuma associação é alterada

#### Scenario: Catalog read endpoint is called without authentication
- **WHEN** um visitante consulta os dados do catálogo sem credenciais
- **THEN** o backend retorna somente os dados públicos previstos e não permite criar, editar ou alterar dados

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
Quando houver imagem principal privada, o sistema SHALL disponibilizá-la ao visitante por uma URL assinada e temporária compatível com o armazenamento nativo do Xano. A resposta pública SHALL omitir o caminho privado original do arquivo. Produto sem imagem SHALL continuar consultável. A imagem do produto SHALL ser obtida por um endpoint público dedicado de imagem do produto, distinto do endpoint de detalhes.

#### Scenario: Product has a private main image
- **WHEN** o catálogo retorna um produto com imagem principal privada
- **THEN** o visitante recebe uma URL assinada temporária para exibir a imagem, sem receber o caminho privado original

#### Scenario: Product has no main image
- **WHEN** o catálogo retorna um produto sem imagem principal
- **THEN** o sistema apresenta os demais dados normalmente e não exige imagem

#### Scenario: Client requests the dedicated image endpoint
- **WHEN** o catálogo público precisa exibir a imagem de um produto
- **THEN** o cliente solicita a imagem ao endpoint dedicado de imagem do produto e não ao endpoint de detalhes, usando a URL assinada retornada quando existir

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
