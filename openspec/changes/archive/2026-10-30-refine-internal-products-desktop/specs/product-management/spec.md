## ADDED Requirements

### Requirement: Desktop product management has accessible hierarchy
The administrative desktop interface SHALL group product and variation forms separately from the product list, provide persistent field labels and named keyboard-accessible actions with visible focus, and render variations with semantic headers for their commercial attributes. It SHALL preserve existing event handlers, required-field rules, selected inactive associations, status and image-presence information, manual refresh, loading/disabled behavior and observable failures. An optional image upload SHALL NOT be presented as guaranteed operational or replaced with an unapproved service. Styles SHALL remain scoped to product management, with basic narrow-screen usability and table overflow contained within its region.

#### Scenario: Administrator prepares a product or variation
- **WHEN** an administrator opens product creation, product editing or variation maintenance
- **THEN** labeled fields and contextual actions expose the existing workflow without changing required data, validation or backend permissions

#### Scenario: Administrator reviews products
- **WHEN** products and variations are displayed
- **THEN** each product retains its information, associations and statuses, and its variations show SKU, price and available quantity with distinguishable maintenance actions

#### Scenario: Loading or failure remains visible
- **WHEN** a product operation is pending or fails
- **THEN** the existing disabled controls and feedback remain observable and the interface does not invent a successful persistence result
