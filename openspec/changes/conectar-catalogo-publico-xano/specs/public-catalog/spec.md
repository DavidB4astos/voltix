## ADDED Requirements

### Requirement: Public catalog client resolves endpoints from environment configuration
O cliente do catálogo público SHALL resolver, a partir de configuração de ambiente, os destinos de categorias, produtos, detalhes de produto e imagem de produto, sem embutir endereços fixos no código versionado nem expor credenciais ou informações sensíveis. As requisições ao catálogo público SHALL permanecer somente de leitura e anônimas.

#### Scenario: Configured endpoints are used
- **WHEN** o catálogo público é carregado em um ambiente com os quatro destinos configurados
- **THEN** o cliente consulta categorias, produtos (com filtro opcional por categoria), detalhes do produto e imagem do produto usando esses destinos configurados, sem depender de um endereço fixo no código

#### Scenario: Missing configuration fails explicitly
- **WHEN** uma configuração obrigatória de destino do catálogo público está ausente
- **THEN** o carregamento apresenta uma falha de configuração observável e não tenta uma chamada para um destino implícito

## MODIFIED Requirements

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
