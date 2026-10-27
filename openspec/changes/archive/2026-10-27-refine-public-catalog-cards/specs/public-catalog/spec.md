## ADDED Requirements

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
