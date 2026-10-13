# public-home Specification

## Purpose
Provide the Voltix public homepage: a premium, responsive landing that presents the store's identity, benefits, categories and real Xano catalog data, guiding visitors to the public catalog while keeping the internal access separate and existing business behavior intact.

## Requirements

### Requirement: Public home on root with premium header navigation
The system SHALL serve a public homepage at the root route `/`, with a premium header composed of a navy top bar containing the Voltix logo, a horizontal menu of existing public routes, an account link and a cart link. The header SHALL preserve the current route access behavior and SHALL NOT expose internal links beyond the existing "Acesso interno" entry.

#### Scenario: Visitor opens the public home
- **WHEN** a visitor opens `/` without an internal session
- **THEN** the system presents the public home, and the internal login screen is no longer the landing content

#### Scenario: Visitor opens the header menu
- **WHEN** a visitor uses the public header navigation at any supported width
- **THEN** the existing public route links (catalog, account, cart) and the internal access entry remain identifiable and lead to the same destinations as before

### Requirement: Hero promoting the catalog
The public home SHALL present a wide hero on a light background with a heading on the left, an electronics imagery container on the right, and a call-to-action button labeled "Explorar produtos". The button SHALL lead to the existing public catalog and keep its current route and access behavior.

#### Scenario: Visitor interacts with the hero
- **WHEN** a visitor clicks "Explorar produtos" in the hero
- **THEN** the system navigates to the existing public catalog page

#### Scenario: Home renders on a narrow viewport
- **WHEN** the home is viewed at mobile width
- **THEN** the hero reflows without horizontal overflow, keeping heading, imagery and call-to-action reachable and readable

### Requirement: Benefits strip below the hero
The public home SHALL show a horizontal benefits strip below the hero summarizing store advantages, presented consistently across breakpoints and without introducing business rules.

#### Scenario: Visitor views benefits
- **WHEN** the home displays the benefits strip at desktop or mobile width
- **THEN** the benefit items remain legible and within the viewport

### Requirement: Category cards with images and names
The public home SHALL display categories as cards containing an image and the category name. Categories SHALL come from the existing public Xano data used by the storefront and SHALL respect the same availability rules as the catalog (only active public categories).

#### Scenario: Visitor views category cards
- **WHEN** the public home renders category cards
- **THEN** each card shows the category name and image, and the set reflects the active public categories available in the catalog

### Requirement: Product showcase grid with real data
The public home SHALL present a responsive grid of products using real Xano data from the existing public catalog flow, showing each product's name, image when present, and stock availability as displayed in the catalog. Product eligibility rules SHALL remain unchanged.

#### Scenario: Visitor views the product showcase
- **WHEN** the public home renders the product grid at desktop, tablet, or mobile width
- **THEN** products appear in a readable responsive layout without horizontal overflow and without altering their existing eligibility or data rules

#### Scenario: Home is loading or empty
- **WHEN** the product data is loading, or no public products are available
- **THEN** the home presents existing loading and empty treatments distinct from normal content

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
