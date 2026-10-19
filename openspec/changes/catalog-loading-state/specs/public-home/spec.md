## MODIFIED Requirements

### Requirement: Product showcase grid with real data
The public home SHALL present a responsive grid of products using real Xano data from the existing public catalog flow, showing each product's name, image when present, and stock availability as displayed in the catalog. Product eligibility rules SHALL remain unchanged. Até a primeira carga de dados da sessão ser concluída, a Home SHALL apresentar o estado de carregamento e SHALL NOT apresentar o estado de lista vazia; o estado de lista vazia SHALL ser apresentado somente quando a carga estiver concluída sem produtos disponíveis.

#### Scenario: Visitor views the product showcase
- **WHEN** the public home renders the product grid at desktop, tablet, or mobile width
- **THEN** products appear in a readable responsive layout without horizontal overflow and without altering their existing eligibility or data rules

#### Scenario: Home is loading or empty
- **WHEN** the product data is loading, or no public products are available
- **THEN** the home presents existing loading and empty treatments distinct from normal content

#### Scenario: Home initial load does not show empty state prematurely
- **WHEN** the home renders before the first product data load of the session has completed
- **THEN** the home presents the loading treatment and does not present the empty product list treatment
