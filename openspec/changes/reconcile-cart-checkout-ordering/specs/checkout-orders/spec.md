## ADDED Requirements

### Requirement: Checkout item reads share the same explicit order
Checkout review, the preliminary confirmation read and the confirmation read inside the existing transaction SHALL order returned ItemCarrinho records by ItemCarrinho id ascending before building review items and snapshots. Ordering SHALL preserve ownership checks, address validation, availability, prices, quantities, totals, stale-review comparison and existing atomic persistence. It SHALL NOT introduce stock reduction or reservation.

#### Scenario: Customer reviews multiple cart items
- **WHEN** checkout review builds its item list and snapshot for a valid cart
- **THEN** both follow ascending ItemCarrinho id order without changing their values

#### Scenario: Confirmation rebuilds a review
- **WHEN** confirmation reads items before and inside its existing transaction
- **THEN** both queries explicitly use ascending ItemCarrinho id order before the existing snapshot comparison

#### Scenario: Commercial data changed after review
- **WHEN** the ordered current review differs from the submitted review because commercial data changed
- **THEN** the existing stale-review rejection and refreshed review remain in effect without silently confirming different values
