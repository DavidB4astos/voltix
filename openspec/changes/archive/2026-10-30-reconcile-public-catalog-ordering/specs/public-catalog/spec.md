## MODIFIED Requirements

### Requirement: Visitors can navigate by active category
O catálogo SHALL apresentar e permitir a seleção de Categorias `ATIVO`. A seleção SHALL limitar os resultados a produtos `ATIVO` associados à Categoria selecionada; A resposta de categorias SHALL ser ordenada por `name` ascendente, sem garantia de desempate entre nomes iguais. Categorias `INATIVO` não SHALL ser oferecidas como filtro.

#### Scenario: Visitor filters products by active category
- **WHEN** o visitante seleciona uma Categoria `ATIVO`
- **THEN** o catálogo apresenta somente produtos `ATIVO` associados à Categoria selecionada

#### Scenario: Inactive category is not available for navigation
- **WHEN** uma Categoria está `INATIVO`
- **THEN** ela não aparece na navegação/filtro público e não pode ser usada para obter resultados de uma categoria ativa

#### Scenario: Public categories are ordered by name
- **WHEN** um visitante consulta categorias públicas
- **THEN** somente categorias ATIVO são retornadas em ordem ascendente de name, preservando os campos existentes


### Requirement: Visitors can view product details and active variations
O sistema SHALL permitir que visitantes consultem os detalhes de um produto `ATIVO`, incluindo suas variações `ATIVO`, preço e quantidade disponível. As variações retornadas SHALL ser ordenadas por `sku` ascendente, sem garantia de desempate entre SKUs iguais. Variações `INATIVO` não SHALL ser apresentadas. Estoque zero SHALL permanecer distinto do status da variação e ser indicado como indisponível para compra; esta indicação não SHALL oferecer fluxo de compra.

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

#### Scenario: Active variations are ordered by SKU
- **WHEN** um visitante consulta o detalhe de um produto ATIVO
- **THEN** suas variações ATIVO aparecem em ordem ascendente de sku, preservando preço e quantidade, inclusive estoque zero

