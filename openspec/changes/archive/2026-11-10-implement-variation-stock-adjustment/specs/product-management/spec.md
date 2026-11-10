## ADDED Requirements

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
