## ADDED Requirements

### Requirement: Consistent signed-out customer entry points
The signed-out customer account page SHALL expose one visible primary heading identifying Minha conta before the existing registration and login forms. Signed-out checkout and orders pages SHALL present their existing account link as a clearly visible blue action with at least 48px height and visible keyboard focus, consistent with the cart access action. Account links SHALL preserve the /cliente destination. Session guards, form submissions and authenticated branches SHALL remain unchanged.

#### Scenario: Visitor opens the account page
- **WHEN** a signed-out visitor opens /cliente
- **THEN** one visible H1 identifies Minha conta and existing registration/login fields and submissions remain available

#### Scenario: Visitor needs to authenticate before purchase or history
- **WHEN** a signed-out visitor opens checkout or orders
- **THEN** the account action has a clear accessible name, visible keyboard focus, minimum 48px height and leads to /cliente without creating data
