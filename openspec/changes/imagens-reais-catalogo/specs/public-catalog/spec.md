## ADDED Requirements

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
