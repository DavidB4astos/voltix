# product-management Specification

## Purpose
Define the administrative behavior for maintaining Voltix products and their commercial variations, including the required category and brand relationships and the domain rules for price, SKU, stock, and status.

## Requirements

### Requirement: Administrators can list products
The system SHALL allow an authenticated, active `UsuarioInterno` with profile `ADMINISTRADOR` to list products and their variations, including product data, category and brand references, image presence, and current statuses. Published GET products and GET variations SHALL enforce user-table authentication and active ADMINISTRADOR authorization before querying business records. User lookup SHALL expose only id, role and status. Products SHALL be ordered by nome ascending and return only id, nome, descricao, especificacoes_tecnicas, imagem_principal, categoria_id, marca_id, status, created_at and updated_at. Variations SHALL be ordered by sku ascending and return only id, produto_id, nome_ou_descricao, sku, preco, quantidade_disponivel, status, created_at and updated_at. These reads SHALL preserve inactive records for administrative maintenance, remain non-mutating and report access denial explicitly.

#### Scenario: Administrator lists products
- **WHEN** an authorized administrator requests the product list
- **THEN** the system returns persisted products with their category, brand, variations, and statuses

#### Scenario: Non-administrator cannot list products
- **WHEN** a `FUNCIONARIO`, inactive user, or unauthenticated caller requests the product list
- **THEN** the backend rejects the request without returning product data

#### Scenario: Administrative read fields remain bounded
- **WHEN** an authorized administrator requests products or variations
- **THEN** the response remains a list of the approved fields, in the specified ascending order, without exposing unrelated user fields or silently hiding inactive catalog records

#### Scenario: Read denial precedes catalog access
- **WHEN** authentication is missing or invalid, or the user is not an active administrator
- **THEN** access is denied before reading product or variation business data and no record is modified

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

### Requirement: Internal variation prices use Brazilian currency display

The internal product variation table SHALL display each price with the `R$` prefix, a comma decimal separator, and two decimal places. The column header SHALL NOT redundantly repeat the currency unit. Formatting SHALL NOT change the underlying price value, calculations, or form submissions.

#### Scenario: Administrator reviews a variation price
- **WHEN** a variation with price `119.9` is displayed in the internal product table
- **THEN** its price is shown as `R$ 119,90`
- **AND** the column header does not repeat the currency unit
- **AND** the price value used by forms and backend requests remains unchanged

### Requirement: Administrators adjust variation stock atomically

The system SHALL allow an authenticated `UsuarioInterno` with role `ADMINISTRADOR` and
status `ATIVO` to adjust the available quantity of an existing variation through a dedicated
backend operation that receives a non-zero signed decimal delta and applies it atomically.
The backend SHALL authorize the session before reading or changing any variation. A positive
delta SHALL add units and a negative delta SHALL remove units. The operation SHALL NEVER
produce a negative available quantity: a negative delta SHALL be applied only when the
current available quantity is sufficient, using a guarded atomic increment in a single
statement, so that concurrent checkouts or adjustments cannot be overwritten. The operation
SHALL reject a zero delta, an unknown variation and insufficient stock without changing the
stored quantity, and SHALL NOT modify variation metadata, price, SKU, status or product data,
and SHALL NOT create a stock movement record or require a reason. The response SHALL return
the updated variation using the existing administrative variation fields and SHALL NOT expose
internal or sensitive data.

#### Scenario: Administrator adds stock

- **WHEN** an authorized administrator sends a positive delta to an existing variation
- **THEN** the backend increases the available quantity by that delta and the stored quantity becomes the new confirmed value

#### Scenario: Administrator removes stock

- **WHEN** an authorized administrator sends a negative delta no greater than the current available quantity
- **THEN** the backend decreases the available quantity by that delta without changing the variation status, price, SKU or product data

#### Scenario: Insufficient stock is rejected without change

- **WHEN** an authorized administrator sends a negative delta greater than the current available quantity
- **THEN** the backend rejects the operation with a client error, the stored quantity remains unchanged, and no partial write occurs

#### Scenario: Zero delta is rejected

- **WHEN** an authorized administrator sends a zero delta
- **THEN** the backend rejects the operation and no quantity is changed

#### Scenario: Unknown variation is rejected

- **WHEN** an authorized administrator targets a variation that does not exist
- **THEN** the backend responds with a not-found error before changing any record

#### Scenario: Adjustment never makes stock negative under concurrency

- **WHEN** a checkout consumes the last unit of a variation while an administrator requests a removal for the same variation at the same time
- **THEN** the guarded atomic operations compose without overwriting, the available quantity is never negative, and the adjustment that fails the guard reports failure without writing

#### Scenario: Unauthorized callers cannot adjust stock

- **WHEN** a `FUNCIONARIO`, an inactive internal user, a `Cliente` session, a visitor or an unauthenticated caller requests a stock adjustment
- **THEN** the backend denies access before reading the variation or changing any quantity

#### Scenario: Adjustment does not create a stock movement record

- **WHEN** an authorized administrator adjusts stock, in any direction
- **THEN** only the variation's available quantity changes, with no movement history, reason or table introduced

### Requirement: Product panel offers a dedicated stock adjustment action

The administrative product panel SHALL offer, per variation, a stock adjustment action
alongside the existing variation maintenance actions, visible only to active
`ADMINISTRADOR`. The action SHALL open a dedicated form showing the variation identification,
the current available quantity, an entry/exit direction and a positive quantity. Client-side
validation SHALL require a quantity greater than zero and SHALL advise when an exit exceeds
the current quantity, while the backend remains authoritative. Controls SHALL be disabled
while an adjustment is pending. Success SHALL be shown only after a confirmed response and a
list reload, using the backend-confirmed quantity. Failures SHALL keep the submitted values,
show observable feedback and SHALL NOT display an unconfirmed quantity as persisted. Styles
SHALL remain scoped to product management.

#### Scenario: Administrator opens the stock adjustment form

- **WHEN** an active administrator selects the stock adjustment action for a variation
- **THEN** the dedicated form shows the variation, its current quantity, the direction and a positive quantity field with labeled controls

#### Scenario: Successful adjustment reflects backend state

- **WHEN** an adjustment is accepted by the backend
- **THEN** the interface reloads the variations and displays the backend-confirmed quantity with a success message

#### Scenario: Failed adjustment stays observable

- **WHEN** an adjustment fails validation, authorization, stock guard or communication
- **THEN** the interface keeps the submitted values, shows an observable failure and does not present a successful persistence result

### Requirement: Administrators can delete products without commercial history

The system SHALL allow an authenticated `UsuarioInterno` with role `ADMINISTRADOR` and
status `ATIVO` to permanently delete an existing product only when none of its variations
is referenced by an `ItemPedido` or an `ItemCarrinho`. The backend SHALL authorize the
session before reading or changing any product record. The reference check and the
deletions SHALL run in a single transaction so that a product with commercial history is
never partially deleted. When any variation is referenced, the backend SHALL reject the
operation with a client error, SHALL leave the product and all variations unchanged, and
SHALL communicate that inactivation is the supported path. When no reference exists, the
backend SHALL delete every variation of the product, active or inactive, and then the
product itself. The operation SHALL NOT delete or modify orders, payments, carts, cart
items, categories, brands, other products or stored image files, and SHALL NOT expose
internal or sensitive data. A product that does not exist SHALL produce a not-found error
before any deletion. A product without variations and an inactive product without
references SHALL remain eligible for deletion.

#### Scenario: Administrator deletes an unused product
- **WHEN** an authorized administrator deletes an existing product whose variations are not referenced by any order item or cart item
- **THEN** the backend deletes all of that product's variations and the product in one transaction and confirms the deletion

#### Scenario: Product with commercial history is preserved
- **WHEN** an authorized administrator deletes a product that has at least one variation referenced by an order item or a cart item
- **THEN** the backend rejects the operation with a client error, no variation or product is deleted, and the response indicates that the product has commercial history and should be inactivated instead

#### Scenario: Unknown product is rejected
- **WHEN** an authorized administrator deletes a product identifier that does not exist
- **THEN** the backend responds with a not-found error without deleting any record

#### Scenario: Unauthorized callers cannot delete products
- **WHEN** a `FUNCIONARIO`, an inactive internal user, a `Cliente` session, a visitor or an unauthenticated caller requests product deletion
- **THEN** the backend denies access before reading the product or deleting any record

#### Scenario: Deletion remains all-or-nothing
- **WHEN** the reference check or any deletion fails during a product deletion
- **THEN** the transaction leaves the product and all of its variations unchanged, with no orphaned or partially removed record

### Requirement: Product panel offers a confirmed product deletion action

The administrative product panel SHALL offer a product deletion action alongside the
existing product maintenance actions, visible only to active `ADMINISTRADOR`. The action
SHALL require explicit two-step confirmation that names the product and explains that the
deletion is permanent and only allowed without commercial history. Controls SHALL be
disabled while a deletion is pending. Success SHALL be shown only after a confirmed
response and a list reload; if the deleted product was being edited, the edit form and its
selected identifier SHALL be cleared. Failures SHALL keep the last confirmed list and any
submitted form state, show observable feedback, and SHALL NOT present the deletion as
successful. A rejection caused by commercial history SHALL be distinguishable in the
feedback and SHALL direct the administrator to inactivation. Styles SHALL remain scoped to
product management.

#### Scenario: Administrator confirms deletion in two steps
- **WHEN** an active administrator selects the product deletion action and then confirms it
- **THEN** the interface shows a confirmation block naming the product before any request is sent, and sends the deletion only after the second action

#### Scenario: Successful deletion reflects the persisted list
- **WHEN** the backend confirms the deletion
- **THEN** the interface reloads the products, removes the product from the list, shows a success message and clears the edit form when that product was being edited

#### Scenario: Deletion failure stays observable
- **WHEN** a deletion fails because of commercial history, authorization, a missing product or communication
- **THEN** the interface keeps the last confirmed list, shows an observable failure, does not report success, and a commercial-history rejection directs the administrator to inactivation
