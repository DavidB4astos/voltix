## ADDED Requirements

### Requirement: Clear desktop product detail presentation
The catalog SHALL present selected product details in a labeled section, with an H2 product name, secondary brand/category when available, complete available description and technical specifications. At desktop widths of at least 1024px, the main image and commercial information SHALL use two columns. Photos SHALL be contained without cropping or distortion, approved local photos SHALL expose the matching author/source/license, and missing image URLs SHALL show an honest placeholder. Prices SHALL use R$ with two decimal places and a decimal comma, without changing the underlying amount. Each active variation SHALL retain its real SKU, name, price and available quantity. Existing add-to-cart events SHALL remain unchanged and add one unit per activation; this quantity SHALL be explained. Out-of-stock variations SHALL keep disabled purchase controls and no-active-variation products SHALL have no purchase control. The close action, loading, error/retry, cart feedback and account/cart links SHALL preserve their behavior. Buttons SHALL have visible focus, readable labels and variation-specific accessible names. Styles SHALL remain detail-scoped and stack safely below desktop widths.

#### Scenario: Visitor inspects a photographed product
- **WHEN** a visitor opens a product with an approved local photo on desktop
- **THEN** the intact photo and matching credit appear alongside the real information, with the name as H2 and price in Brazilian decimal notation

#### Scenario: Visitor inspects a product without an image
- **WHEN** the selected product has an empty image URL
- **THEN** the detail shows Imagem não disponível and retains the available product information

#### Scenario: Visitor compares active variations
- **WHEN** a selected product has active variations
- **THEN** each variation displays its name or SKU fallback, real SKU, price, availability and distinctly named existing add-to-cart action explaining that one unit is added

#### Scenario: Purchase is unavailable
- **WHEN** a variation has zero stock or a cart mutation is in progress
- **THEN** its purchase action is disabled while the real stock indication remains visible

#### Scenario: No active variation exists
- **WHEN** the selected product has no active variations
- **THEN** an informative empty state appears without purchase controls

#### Scenario: Existing navigation and feedback remain usable
- **WHEN** the visitor closes the details or attempts to add a variation without a customer session
- **THEN** the existing close behavior or login feedback remains available, preserving catalog filters and existing events
