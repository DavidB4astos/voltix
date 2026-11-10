## ADDED Requirements

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
