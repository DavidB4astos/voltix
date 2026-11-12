## MODIFIED Requirements

### Requirement: Storefront product surfaces remain clear and consistent
The catalog, product cards, product details, and variation presentation SHALL use a consistent responsive hierarchy for existing product imagery, descriptions, category/brand labels, variation availability, prices, and existing actions. Visual changes SHALL NOT alter product eligibility, displayed data rules, stock handling, or cart behavior. The catalog SHALL present products in two columns between 768 and 1023 px, and in at least three columns from 1280 px, without horizontal overflow. Product-image credit/license lines SHALL remain visible and accurate while using a compact typographic treatment that does not dominate the card.

#### Scenario: Customer browses the catalog

- **WHEN** the catalog displays products at desktop, tablet, or mobile width
- **THEN** product cards form a readable responsive layout, preserve the existing product information, and provide consistently styled detail actions

#### Scenario: Catalog at tablet width uses two columns

- **WHEN** the catalog is displayed at a width between 768 and 1023 px
- **THEN** product cards are arranged in two columns, each card keeps its existing content fully readable and the page does not scroll horizontally

#### Scenario: Credit and license lines stay legible but compact

- **WHEN** a product image displays its Icecat credit or license line
- **THEN** the credit/license information and its link to the source remain visible, accurate and keyboard-reachable, in a more compact style than the product description

#### Scenario: Customer views product details and variations

- **WHEN** the customer opens existing product details
- **THEN** available product information, image when present, variation price, stock availability, and existing add-to-cart action remain clear and usable without changing their behavior

### Requirement: Shared navigation and page endings are responsive
Customer-facing pages SHALL use a consistent header/navigation treatment and a consistent footer presentation. At mobile widths (below 1024 px), navigation SHALL present a compact header that keeps the Voltix identity, the primary routes and the cart/account actions visible with short labels and icons, without wrapping into multiple large rows; category shortcuts offered alongside the home header SHALL scroll horizontally with a visible affordance instead of clipping labels. Navigation links SHALL lead only to existing routes and preserve their existing access behavior.

#### Scenario: Customer navigates using desktop or mobile header

- **WHEN** a customer uses navigation at desktop or mobile width
- **THEN** existing route links remain identifiable and usable without changing access requirements

#### Scenario: Mobile header remains compact and fully visible

- **WHEN** the storefront header renders below 1024 px
- **THEN** the primary routes (Início, Produtos) and the account/cart destinations remain accessible in a compact single-row-or-wrapped header that does not dominate the first viewport, and no route label is clipped

#### Scenario: Home category shortcuts show that more items exist

- **WHEN** the home page offers horizontal scrolling category shortcuts on a small screen
- **THEN** the row scrolls smoothly and a visible cue (for example a fade, edge hint or scrollbar) indicates that more categories are available off-screen

### Requirement: Storefront and purchase surfaces align content across breakpoints
Os cards do catálogo e as superfícies de carrinho, checkout e pedidos SHALL manter alinhamento consistente de imagem, preço, status e ações em 375, 768 e 1280 px, sem rolagem horizontal e sem remover campos, ações ou mensagens existentes. Card media areas SHALL keep a stable aspect ratio so mixed product images produce even card heights within a row.

#### Scenario: Catalog cards at multiple widths

- **WHEN** o catálogo é exibido em larguras mobile, tablet ou desktop
- **THEN** os cards alinham imagem, preço e ação de forma legível, formando uma grade responsiva sem overflow

#### Scenario: Card media areas keep a stable height

- **WHEN** o catálogo renderiza produtos com imagens de proporções diferentes
- **THEN** a área de mídia de cada card mantém proporção estável e os cards de uma mesma linha mantêm altura consistente

#### Scenario: Purchase summary on a narrow viewport

- **WHEN** o cliente visualiza carrinho, checkout ou pedido em tela estreita
- **THEN** resumo, totais, status e ações permanecem visíveis e legíveis sem rolagem horizontal
