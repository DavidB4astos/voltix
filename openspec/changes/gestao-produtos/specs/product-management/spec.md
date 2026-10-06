## Purpose

Define the administrative behavior for maintaining Voltix products and their commercial variations, including the required category and brand relationships and the domain rules for price, SKU, stock, and status.

## ADDED Requirements

### Requirement: Administrators can list products
The system SHALL allow an authenticated, active `UsuarioInterno` with profile `ADMINISTRADOR` to list products and their variations, including product data, category and brand references, image presence, and current statuses.

#### Scenario: Administrator lists products
- **WHEN** an authorized administrator requests the product list
- **THEN** the system returns persisted products with their category, brand, variations, and statuses

#### Scenario: Non-administrator cannot list products
- **WHEN** a `FUNCIONARIO`, inactive user, or unauthenticated caller requests the product list
- **THEN** the backend rejects the request without returning product data

### Requirement: Administrators can create valid products
The system SHALL allow an authorized administrator to create a product with the attributes defined for Produto in the Domain Model, one optional main image, exactly one existing category, exactly one existing brand, and at least one variation. New products and variations SHALL start with status `ATIVO`. Technical specifications SHALL be maintained directly on the product; a variation SHALL have the Domain Model's name-or-description attribute, and SKU, price, and available quantity SHALL belong to variations. A category or brand SHALL be eligible for a new association only while `ATIVO`. This requirement does not establish additional mandatory-field rules for Product name, description, or technical specifications.

#### Scenario: Administrator creates a product with its first variation
- **WHEN** an authorized administrator submits a product with an active category and brand and at least one valid variation
- **THEN** the system persists the product and its variation(s), assigns status `ATIVO` to each, and returns the saved records

#### Scenario: Main image is optional
- **WHEN** an authorized administrator creates a valid product without an image
- **THEN** the system creates the product with no main image

#### Scenario: Inactive category or brand cannot be newly associated
- **WHEN** an authorized administrator creates or changes a product association to an inactive category or brand
- **THEN** the backend rejects the operation and preserves the existing product data

#### Scenario: Product creation is rejected when required relationships or variations are missing
- **WHEN** an authorized administrator submits a product without a category, brand, or at least one variation
- **THEN** the backend rejects the request and does not persist a product without its required variation

### Requirement: Product and variation data satisfy domain constraints
The system SHALL enforce the domain constraints for product and variation data in the backend, including required, globally unique SKU, price greater than zero, available quantity greater than or equal to zero, and statuses `ATIVO` or `INATIVO`. SKU uniqueness SHALL include inactive variations.

#### Scenario: Duplicate SKU is rejected
- **WHEN** an administrator creates or updates a variation with an SKU already assigned to another variation
- **THEN** the backend rejects the operation and preserves the existing records

#### Scenario: Invalid price or available quantity is rejected
- **WHEN** an administrator submits a variation with a price less than or equal to zero or an available quantity below zero
- **THEN** the backend rejects the operation without persisting invalid data

#### Scenario: Inactive variation still reserves its SKU
- **WHEN** an administrator attempts to reuse the SKU of an inactive variation
- **THEN** the backend rejects the duplicate SKU

### Requirement: Administrators can edit products and manage variations
The system SHALL allow authorized administrators to edit product information and maintain its variations without changing a product's status as a side effect. An existing product-to-category or product-to-brand relationship SHALL be preserved and displayed if that category or brand later becomes inactive; a new association or reassignment SHALL require an active category and brand. A product or variation associated with commercial history SHALL be preserved rather than permanently deleted. Every product SHALL retain at least one variation.

#### Scenario: Administrator edits product information
- **WHEN** an authorized administrator updates a product's name, description, technical specifications, associations, or main image
- **THEN** the system persists the submitted data while preserving the current product status and existing variations

#### Scenario: Existing association remains when category or brand becomes inactive
- **WHEN** a related category or brand is inactivated after being associated with a product
- **THEN** the product keeps the relationship and its management view displays the related record as inactive

#### Scenario: Administrator adds or edits a variation
- **WHEN** an authorized administrator submits valid variation data for an existing product
- **THEN** the system persists the variation under that product without changing unrelated product or variation data

#### Scenario: Administrator changes product or variation status
- **WHEN** an authorized administrator changes a product or variation status between `ATIVO` and `INATIVO`
- **THEN** the system persists the new status and retains the record and its relationships

#### Scenario: Product or variation with commercial history is preserved
- **WHEN** an administrator manages a product or variation associated with commercial history
- **THEN** the system preserves the record and its relationships, using inactivation where the record should no longer be active

### Requirement: Product management is protected and failures remain observable
The system SHALL authorize every product and variation operation in the backend for a valid session belonging to an active `ADMINISTRADOR`. The Reflex interface SHALL route user actions through State/Python logic, which SHALL make HTTP requests to Xano outside code executed directly in the browser. Failed operations SHALL not be reported as successful and SHALL preserve previously persisted data.

#### Scenario: Unauthorized mutation is rejected
- **WHEN** a `FUNCIONARIO`, inactive user, or unauthenticated caller attempts to create, edit, inactivate, or reactivate a product or variation
- **THEN** the backend rejects the operation without changing data

#### Scenario: Backend or network operation fails
- **WHEN** a product or variation operation fails validation, authorization, or backend communication
- **THEN** the interface shows an observable failure, does not show a success result, and retains the last confirmed persisted state
