## ADDED Requirements

### Requirement: Demo images are served as local static assets with fallback
The visual interface SHALL support serving demo product images from local static assets (in Reflex assets) identified by SKU mapping, with consistent responsive sizing, appropriate loading behavior, and graceful fallback to placeholder on load/error. The implementation SHALL preserve existing image components’ behavior for non-demo SKUs and SHALL NOT require modifying Xano data.

#### Scenario: Image component renders local demo asset responsively
- **WHEN** a demo product image is rendered from local assets
- **THEN** the image is responsive and maintains aspect ratio appropriate for card/grid/detail layouts

#### Scenario: Fallback to placeholder on missing local asset
- **WHEN** no local asset exists for a mapped/demo case
- **THEN** the component displays the existing placeholder behavior

#### Scenario: Non-demo images unchanged
- **WHEN** rendering a non-demo product image
- **THEN** visual presentation and behavior remain unchanged
