# public-home Specification

## Purpose
Provide the Voltix public homepage: a premium, responsive landing that presents the store's identity, benefits, categories and real Xano catalog data, guiding visitors to the public catalog while keeping the internal access separate and existing business behavior intact.

## Requirements

### Requirement: Public home on root with premium header navigation
The system SHALL serve a public homepage at the root route `/`, with a premium navy header containing the Voltix logo and access to the existing catalog, account, cart and internal access routes. On desktop viewports at least 1024 CSS pixels wide, the public storefront SHALL present Início and Produtos as primary text navigation, account and cart as labeled actions, and Acesso interno as a secondary entry. Produtos SHALL lead to `/catalogo`; the desktop logo SHALL lead to `/`. The current route SHALL be indicated accessibly. The desktop Home SHALL omit the redundant secondary category bar while retaining the category section in its body. Narrower viewports and the internal area SHALL retain their existing header and navigation behavior. The header SHALL NOT introduce new internal links or change authentication, authorization or backend behavior.

#### Scenario: Visitor opens the public home
- **WHEN** a visitor opens `/` without an internal session
- **THEN** the system presents the public home, and the internal login screen is no longer the landing content

#### Scenario: Visitor opens the header menu
- **WHEN** a visitor uses the public header navigation at any supported width
- **THEN** the existing catalog, account, cart and internal access destinations remain available and identifiable

#### Scenario: Desktop visitor opens the catalog
- **WHEN** a desktop visitor activates Produtos in the public header
- **THEN** the catalog route `/catalogo` opens and its navigation item indicates the current page

#### Scenario: Desktop visitor returns home
- **WHEN** a desktop visitor activates the Voltix logo on a public storefront page
- **THEN** the Home route `/` opens

#### Scenario: Narrow viewport preserves the existing header
- **WHEN** the public storefront is viewed below 1024 CSS pixels
- **THEN** only the existing header variant is visible, preserving its labels and destinations

### Requirement: Hero promoting the catalog

The public home SHALL present a premium editorial hero on the store's dark navy surface, without an eyebrow or kicker label above the heading, with a single page-level heading, a short supporting sentence, exactly one primary call-to-action labeled "Explorar produtos" leading to the existing public catalog, and a media panel. The hero media SHALL be composed only from an approved local asset from the store's assets — either a licensed photograph or a store-owned generated image — or, when that asset does not suit the composition, a store-owned graphic panel built from the store's visual tokens. The hero SHALL NOT reference external image URLs, SHALL NOT introduce promotions, prices, ratings, or commercial claims that do not exist in the store, and SHALL keep the call-to-action's current route and access behavior.

**Implementation:** The hero SHALL prioritize displaying a store-owned generated editorial image (`vtx-home-workspace-v2.webp`) with its provenance statement ("Cenário ilustrativo gerado por IA; os equipamentos não representam produtos específicos."). The store-owned graphic panel SHALL be used only as fallback when the photograph is unavailable or unsuitable for the composition.

#### Scenario: Visitor interacts with the hero
- **WHEN** a visitor activates "Explorar produtos" in the hero
- **THEN** the system navigates to the existing public catalog page

#### Scenario: Home renders on a narrow viewport
- **WHEN** the home is viewed at mobile width
- **THEN** the hero stacks heading, supporting sentence, call-to-action and media without horizontal overflow, keeping all of them reachable and readable

#### Scenario: Hero media uses only local approved assets
- **WHEN** the hero renders its media panel
- **THEN** the media is an approved local asset (a licensed photograph or a store-owned generated image) or a store-owned graphic panel, and no external image URL is requested

#### Scenario: Local hero asset does not suit the composition
- **WHEN** the approved local asset cannot be used without cropping or distortion that misrepresents it
- **THEN** the hero renders the store-owned graphic panel instead of an external or fabricated image

#### Scenario: Hero is rendered without an eyebrow
- **WHEN** the hero renders its heading
- **THEN** no eyebrow, kicker or pill label is displayed above the level-one heading

#### Scenario: Hero displays editorial photograph with provenance
- **WHEN** the hero renders with the local generated editorial image
- **THEN** the generated editorial scenery is displayed without representing catalog SKUs
- **AND** a visible provenance statement "Cenário ilustrativo gerado por IA; os equipamentos não representam produtos específicos." is shown without requiring interaction
- **AND** no fabricated author, license or source is displayed

---

### Requirement: Benefits strip below the hero

The public home SHALL show a benefits strip below the hero summarizing store advantages as a single linear band presented consistently across breakpoints, using only benefit statements already present in the store and without introducing business rules. The benefits SHALL be presented without card boxes or shadows, using top and bottom border separators.

#### Scenario: Visitor views benefits
- **WHEN** the home displays the benefits strip at desktop or mobile width
- **THEN** the benefit items remain legible, in reading order, and within the viewport
- **AND** each benefit displays its approved text without alteration: "Explore por categoria / Encontre o que seu setup precisa.", "Conheça os detalhes / Consulte informações e variações.", "Sua conta, seus pedidos / Acompanhe seu histórico de compras."

---

### Requirement: Typographic category cards

The public home SHALL display categories as a premium editorial typographic list with continuous presentation, containing the category name and its supporting description when present below 1024px; desktop MAY omit the supporting description for compact rows, without photographs or fabricated imagery. Categories SHALL be presented with sequential numbering (01, 02, 03...) generated by CSS counter, separated by horizontal dividers, with an arrow indicator on hover. Categories SHALL come from the existing public data used by the storefront and SHALL respect the same availability rules as the catalog (only active public categories). Each category entry SHALL lead to the existing catalog with its category_id applied, as defined by Contextual storefront entry.

#### Scenario: Visitor views category cards
- **WHEN** the public home renders category cards
- **THEN** each card shows the category name and reflects the active public categories available in the catalog, with no image rendered
- **AND** categories are numbered sequentially (01, 02, 03...) via CSS counter
- **AND** categories are separated by horizontal divider lines

#### Scenario: Visitor opens a category
- **WHEN** a visitor activates a category card
- **THEN** the system navigates to the existing catalog destination for that category
- **AND** the category_id of the selected category is applied to the existing public filter

#### Scenario: Category list preserves empty state
- **WHEN** no categories are available
- **THEN** the system displays "Nenhuma categoria disponível no momento."
- **AND** no category list or placeholder cards are rendered

---

### Requirement: Product showcase grid with real data

The public home SHALL present a short curated showcase of at most four products using real data from the existing public catalog flow. Selection SHALL be based only on verifiable correspondence between a product and an approved local image asset resolved from that product's own identity. The home SHALL NOT select products by list position and SHALL NOT reuse another product's image or fall back to an unverified order. The showcase SHALL render fewer cards when fewer products are eligible and SHALL be omitted when no product is eligible, without substituting other products. Each showcased product SHALL show its real name, brand and category when present, its image when available, and SHALL NOT show price, availability or discount information. Every showcased photograph SHALL display its credit. Product eligibility rules SHALL remain unchanged.

**Loading treatment:** While product data is loading (`State.public_catalog_loading == True` or `State.public_catalog_loaded == False`), the home SHALL display skeleton placeholder cards instead of text. Skeleton cards SHALL be discrete, without excessive animation, and SHALL respect the user's `prefers-reduced-motion` preference by suppressing non-essential movement.

**State distinction:** The home SHALL distinguish between loading (data fetch in progress), error with retry (fetch failed with message and retry action), empty catalog (successful fetch but zero products available), and showcase omission (successful fetch but zero products eligible for showcase due to image correspondence rules).

#### Scenario: Visitor views the product showcase
- **WHEN** the public home renders the product grid at desktop, tablet, or mobile width
- **THEN** at most four curated products appear in a readable responsive layout without horizontal overflow and without altering their existing eligibility or data rules

#### Scenario: Showcase renders only verifiable matches
- **WHEN** the public catalog data contains products whose own identity resolves to an approved local image
- **THEN** only those products are showcased, and no product is selected by list position or paired with another product's image

#### Scenario: Fewer products are eligible
- **WHEN** fewer than four products have a verifiable approved image
- **THEN** the showcase renders only the eligible products and does not fill the remaining slots with unverified products

#### Scenario: No product is eligible
- **WHEN** no product in the current public catalog data has a verifiable approved local image
- **THEN** the showcase list is omitted and no substitute products or reused images are shown

#### Scenario: Showcased image requires attribution
- **WHEN** a showcased product image is licensed with an attribution requirement
- **THEN** the product card displays the author and license credit for that image

#### Scenario: Home is loading or empty
- **WHEN** the product data is loading, or no public products are available
- **THEN** the home presents existing loading and empty treatments distinct from normal content

#### Scenario: Product showcase displays skeleton during loading
- **WHEN** product data is loading (`State.public_catalog_loading == True` or `State.public_catalog_loaded == False`)
- **THEN** the home presents skeleton placeholder cards
- **AND** no loading text is displayed
- **AND** skeleton cards respect the user's `prefers-reduced-motion` preference

#### Scenario: Product showcase displays error with retry
- **WHEN** product loading fails with an error message (`State.public_catalog_message != ""`)
- **THEN** the home displays an error panel with the message
- **AND** a "Tentar novamente" action is available
- **AND** activating the action triggers the same retry behavior as before

#### Scenario: Product showcase displays empty catalog state
- **WHEN** product data loaded successfully (`State.public_catalog_loaded == True`) but zero products are available (`State.public_products.length() == 0`)
- **THEN** the home displays "Nenhum produto disponível para exibição."
- **AND** no skeleton or product cards are rendered

#### Scenario: Home initial load does not show empty state prematurely
- **WHEN** the home renders before the first product data load of the session has completed
- **THEN** the home presents the loading treatment (skeleton cards)
- **AND** does not present the empty product list treatment

---

### Requirement: Editorial context section with approved photography

The public home SHALL include one editorial section that presents an approved local photograph from the store's assets, a short heading, a short supporting sentence, and at most one call-to-action leading to an existing public route. The accompanying copy SHALL describe the photograph truthfully and SHALL NOT attribute a product, offer, setup or service to the image that it does not show. The section SHALL display the image credit. If no approved photograph is available, the section SHALL be omitted entirely.

**Implementation:** The editorial section SHALL use `vtx-editorial-mx-master-3s.jpg` (Mouse Logitech MX Master 3S) with the heading "Precisão em cada detalhe", supporting copy describing the premium equipment, and visible credit "Logitech MX Master 3S HS17.jpg by Hayden Schiff, CC BY 4.0, via Wikimedia Commons" without requiring interaction.

#### Scenario: Visitor views the editorial section
- **WHEN** the public home renders the editorial section
- **THEN** it shows an approved local photograph (`vtx-editorial-mx-master-3s.jpg`)
- **AND** its credit (author: Hayden Schiff, license: CC BY 4.0, source: Wikimedia Commons) is visible without interaction
- **AND** a short heading "Precisão em cada detalhe" describes the content
- **AND** a supporting sentence describes the premium equipment truthfully
- **AND** at most one call-to-action leads to `/catalogo`

#### Scenario: No approved editorial photograph is available
- **WHEN** the store has no approved local photograph for the editorial section
- **THEN** the home omits the section instead of rendering a placeholder or an unlicensed image

### Requirement: Image provenance and credits on the public home
Images displayed on the public home SHALL declare provenance appropriate to their origin. A third-party licensed photograph SHALL display a visible credit with its author, license and source, read from the existing local image manifest. A store-owned or generated image without third-party photographic authorship SHALL display a visible provenance statement identifying its origin and nature, consistent with the origin recorded in the local image manifest, and the home SHALL NOT fabricate an author, license or source for it. Credits and provenance statements SHALL be shown without requiring interaction, SHALL NOT load third-party resources, and SHALL NOT rely on hover-only content. An image whose required credit or provenance cannot be resolved SHALL NOT be displayed on the home.

#### Scenario: Visitor sees a credited third-party photograph
- **WHEN** the home renders a third-party licensed photograph
- **THEN** its author, license and source are visible in the section where the photograph appears

#### Scenario: Visitor sees provenance for a store-owned or generated image
- **WHEN** the home renders a store-owned or generated image without third-party photographic authorship
- **THEN** a visible provenance statement identifies its origin and nature, and no author, license or source is fabricated

#### Scenario: Required credit or provenance cannot be resolved
- **WHEN** the home cannot resolve the credit or provenance required for an image
- **THEN** that image is not displayed

### Requirement: Home visual layer is scoped to the public home
The home visual refinement SHALL be implemented with styles scoped to the public home and SHALL NOT change the presentation or behavior of the catalog, product detail, customer account, cart, checkout, orders or internal administrative surfaces. Home-specific classes SHALL use a dedicated prefix, and global link, button and focus selectors SHALL NOT be introduced. The refinement SHALL preserve the shared header and footer, every existing route, handler, data contract and business behavior; it SHALL NOT add, remove or rename routes.

#### Scenario: Visitor navigates to another surface
- **WHEN** a visitor moves from the home to the catalog, cart, checkout, account, orders or internal access
- **THEN** those pages keep their existing presentation, routes, data and behavior

#### Scenario: Shared chrome and routes are preserved
- **WHEN** the refined home is compared with the previous home
- **THEN** the shared header and footer, the route map, the handlers and the data contracts are unchanged

### Requirement: Home accessibility and responsive behavior
The public home SHALL expose one level-one heading, headings in semantic order, visible keyboard focus on every interactive element, descriptive alternative text for informative images, and touch targets of at least 44 pixels for primary controls. The home SHALL reflow from 360 to 1440 pixels without horizontal overflow and SHALL honor the user's reduced-motion preference by removing non-essential movement while keeping content visible.

#### Scenario: Visitor navigates the home by keyboard
- **WHEN** a visitor moves through home links and controls using the keyboard
- **THEN** the focus indicator is visible on each control and the reading order matches the visual order

#### Scenario: Visitor prefers reduced motion
- **WHEN** the user agent reports `prefers-reduced-motion: reduce`
- **THEN** non-essential transitions and transforms are suppressed and all content remains visible

#### Scenario: Home is viewed on a narrow viewport
- **WHEN** the home is rendered at 360 or 390 pixels wide
- **THEN** no horizontal scrolling is required and no content is clipped

#### Scenario: Informative image is rendered
- **WHEN** the home renders an informative image (product, editorial or hero)
- **THEN** the image has alternative text describing its content, or an empty alternative when it is purely decorative

### Requirement: Institutional footer
The public home SHALL end with an institutional footer consistent with the Voltix identity, without changing existing footer content rules.

#### Scenario: Visitor scrolls to the footer
- **WHEN** the public home footer is displayed
- **THEN** it presents the Voltix institutional content consistently on desktop and mobile

### Requirement: Internal access relocated without behavior change
The internal access screen SHALL move from the root route to `/interno`, preserving login, session validation, authorization and administrative visibility exactly as before.

#### Scenario: Internal user authenticates from the new route
- **WHEN** an internal user opens `/interno` and authenticates successfully
- **THEN** the same session, role-based visibility and administrative actions apply as before the route change

#### Scenario: Existing internal entry points
- **WHEN** a user reaches the internal area from the public header
- **THEN** the "Acesso interno" entry leads to `/interno` and requires the same valid internal session as before

### Requirement: Visual refresh does not change business behavior
The public home SHALL preserve existing routes, data, business rules, API interactions, authentication/authorization behavior, and State events for catalog, cart, checkout, orders, accounts and administration. It SHALL NOT introduce new business capabilities or backend changes.

#### Scenario: Storefront actions remain unchanged
- **WHEN** a visitor moves from the home to any existing storefront action
- **THEN** the same State/backend flow and business result apply as before the home introduction

### Requirement: Home displays real images for demo SKUs from local assets
The public home SHALL resolve images for demo products by matching SKU against the same local static asset mapping used by the public catalog. For SKUs matching `VTX-DEMO-*`, when a local image exists, the home SHALL display that image in product/category-related cards; otherwise it SHALL fall back to existing behavior (Xano image or placeholder). Non-demo products SHALL remain unaffected.

#### Scenario: Home shows local image for mapped demo SKU
- **WHEN** the home displays a product card for SKU `VTX-DEMO-001` with a local image mapped
- **THEN** the card displays the local static image

#### Scenario: Home falls back when no local image exists
- **WHEN** the home displays a demo SKU with no local image mapping
- **THEN** the home uses the existing image resolution behavior

#### Scenario: Non-demo products unchanged on home
- **WHEN** the home displays a non-demo product
- **THEN** image resolution is unchanged

### Requirement: Contextual storefront entry
The Home SHALL link each category to the catalog with its category_id and each showcased product with its product_id. Catalog entry SHALL validate query parameters before loading the existing filter or product detail. Home entry SHALL reset prior filters. Desktop styling SHALL use a centered hero, compact category rows, rounded primary CTA and neutral product surfaces inspired by Apple while retaining Voltix assets, credits and navy/cyan identity. Below 1024px the visual layout SHALL remain unchanged.

#### Scenario: Visitor chooses a category
- **WHEN** a visitor follows a Home category link
- **THEN** the catalog opens with that existing category selected

#### Scenario: Visitor chooses a product
- **WHEN** a visitor follows a showcased product link
- **THEN** the catalog opens the existing details for that product

#### Scenario: Invalid query parameter
- **WHEN** a catalog parameter is malformed or a category does not exist
- **THEN** the catalog safely falls back to all categories, and malformed product identifiers do not request a detail

#### Scenario: Visitor returns home after filtering
- **WHEN** a visitor returns Home from a filtered catalog
- **THEN** Home reloads the unfiltered public catalog
