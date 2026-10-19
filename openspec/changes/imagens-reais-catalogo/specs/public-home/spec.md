## ADDED Requirements

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
