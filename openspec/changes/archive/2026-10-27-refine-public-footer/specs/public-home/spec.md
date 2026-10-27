## MODIFIED Requirements

### Requirement: Home visual layer is scoped to the public home
The home visual refinement SHALL be implemented with styles scoped to the public home and SHALL NOT change the content presentation or business behavior of the catalog, product detail, customer account, cart, checkout, orders or internal administrative surfaces, except for the explicitly approved shared public desktop footer defined by Institutional footer. Home-specific classes SHALL use a dedicated prefix, and global link, button and focus selectors SHALL NOT be introduced. The refinement SHALL preserve the existing public header and internal footer, every existing route, handler, data contract and business behavior; it SHALL NOT add, remove or rename routes.

#### Scenario: Visitor navigates to another surface
- **WHEN** a visitor moves from the home to the catalog, cart, checkout, account, orders or internal access
- **THEN** those pages keep their existing content presentation, routes, data and business behavior, while public desktop pages use the Institutional footer

#### Scenario: Shared chrome and routes are preserved
- **WHEN** the refined home is compared with the previous home
- **THEN** the existing header, internal footer, route map, handlers and data contracts are unchanged; the public desktop footer follows Institutional footer

### Requirement: Institutional footer
The public home and existing public storefront pages SHALL end with a Voltix institutional footer. At widths of at least 1024px it SHALL show the brand and grouped links to existing Home, catalog, account, cart, orders and internal access routes, with the academic-project and simulated-prices/payments notice visible. It SHALL NOT invent contacts, policies or commercial services. Links SHALL have visible keyboard focus and targets at least 44px high. Narrower viewports and internal pages SHALL retain the legacy footer. Shared public pages SHALL explicitly opt into the desktop variant.

#### Scenario: Visitor scrolls to the footer
- **WHEN** the public home footer is displayed
- **THEN** it presents the Voltix institutional content consistently on desktop and mobile

#### Scenario: Desktop visitor follows footer links
- **WHEN** a desktop visitor chooses a footer navigation link
- **THEN** it opens the existing destination without changing access rules or submitting a form

#### Scenario: Visitor uses footer keyboard navigation
- **WHEN** a visitor tabs through the desktop footer
- **THEN** each link exposes a visible focus indicator in reading order

#### Scenario: Legacy footer remains available
- **WHEN** a visitor uses a viewport below 1024px or an internal page
- **THEN** only the legacy footer appears
