## ADDED Requirements

### Requirement: Cart reads use explicit item order
The cart read SHALL return its existing joined ItemCarrinho records in ascending ItemCarrinho id order. It SHALL preserve customer ownership, active-session authorization, current price calculations, availability indication and the existing response fields. Ordering SHALL NOT reserve or reduce stock or mutate cart records.

#### Scenario: Customer reads multiple cart items
- **WHEN** an active customer reads their own cart with multiple returned items
- **THEN** those items are ordered by ItemCarrinho id ascending and retain their existing quantities and commercial information

#### Scenario: Customer reads an empty cart
- **WHEN** the customer has no returned cart items
- **THEN** the existing empty response remains unchanged and no item or order is created
