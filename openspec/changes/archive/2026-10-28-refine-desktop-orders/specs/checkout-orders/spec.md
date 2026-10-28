## ADDED Requirements

### Requirement: Clear desktop customer order history and summaries
The orders page SHALL preserve its customer-session guard and existing order lookup and payment-simulation events. At desktop widths of at least 1024px, history and the selected summary or selection guidance SHALL appear in two columns. History entries SHALL expose the returned commercial code, registered date, readable status, line-item count and historical total, with item-specific summary actions and visible focus. A selected summary SHALL retain the persisted delivery snapshot, variation name or SKU fallback, SKU, quantity, historical unit price, subtotal, freight, total and payment information. Formatting SHALL reuse decimal text without recalculation. Loading and feedback SHALL remain observable, preserving confirmed data and avoiding a false empty result during loading/failure. Simulation SHALL be offered only for AGUARDANDO_PAGAMENTO with PENDENTE payment, remain disabled while simulating/loading and retain the explicit no-charge notice. No tracking, promised date, cancellation flow or missing product information SHALL be invented. Narrow widths SHALL stack without overflow and styles SHALL remain orders-scoped.

#### Scenario: Customer reviews history
- **WHEN** confirmed orders exist on desktop
- **THEN** their commercial code, registered date, status and historical total are readable beside summary selection guidance

#### Scenario: Customer opens a summary
- **WHEN** the existing summary event returns an order
- **THEN** persisted items, delivery and payment values are presented with semantic headings and no current-price recalculation

#### Scenario: Payment simulation is eligible or complete
- **WHEN** an order awaits payment with a pending payment or is already paid
- **THEN** the existing simulation action is offered only in the eligible case and never implies a real charge

#### Scenario: Request, empty result or error
- **WHEN** history/detail is loading, history is empty or feedback exists
- **THEN** the page identifies the relevant state without claiming failed requests are a confirmed empty history

#### Scenario: Keyboard navigation
- **WHEN** the customer reaches summary, refresh or simulation actions by keyboard
- **THEN** actions have clear accessible names and visible focus, preserving their existing identifiers and handlers
