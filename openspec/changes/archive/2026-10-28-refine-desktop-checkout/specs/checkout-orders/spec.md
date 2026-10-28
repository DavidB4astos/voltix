## ADDED Requirements

### Requirement: Clear desktop checkout review and confirmation
The checkout SHALL preserve its customer session guard and existing review/confirmation events and payloads. At widths of at least 1024px, delivery/review and the summary/confirmation SHALL use two columns. The address and payment selectors SHALL have explicit associated labels, disabled states during loading, and preserve their current event bindings and form names. Only ATIVO addresses SHALL be selectable; a list with no active address SHALL show account navigation and keep review disabled. Before review is ready, the UI SHALL explain how to review without inventing totals or delivery details. Ready reviews SHALL display actual item names or SKU fallback, variation when present, quantity, unit price, subtotal, availability and the returned delivery snapshot, subtotal, freight and total. Monetary values SHALL reuse the cart's text-based formatting without recalculation. Confirmation SHALL be disabled during loading, without ready items or when any item is unavailable, reflecting existing server-side rejection. Only PIX, CARTAO and BOLETO SHALL be offered, with the existing pending-payment/no-charge explanation. Existing feedback and new-confirmation-after-review-change behavior SHALL be retained. The page SHALL NOT initiate a charge or create data merely for visual tests. Narrow widths SHALL stack safely and styles SHALL be checkout-scoped.

#### Scenario: Customer has not reviewed yet
- **WHEN** the checkout opens without a ready review
- **THEN** it shows address selection and review guidance, without fabricated totals or an enabled confirmation

#### Scenario: No active address is available
- **WHEN** the available address list is empty or contains only inactive addresses
- **THEN** the page offers account/address management and disables review

#### Scenario: Customer reviews an eligible cart
- **WHEN** an existing review succeeds
- **THEN** the UI shows its actual items, address snapshot and returned amounts alongside the existing payment-method/confirmation form

#### Scenario: Review contains unavailable items
- **WHEN** any reviewed item is unavailable
- **THEN** the UI keeps it visible with a correction link to the cart and disables confirmation

#### Scenario: Request is in progress or fails
- **WHEN** review or confirmation is loading or returns feedback
- **THEN** loading disables the controls and existing feedback remains observable without claiming success

#### Scenario: Customer navigates with a keyboard
- **WHEN** the customer reaches selectors and actions with a keyboard
- **THEN** labels, focus and enabled/disabled conditions are perceivable, with no nested interactive controls
