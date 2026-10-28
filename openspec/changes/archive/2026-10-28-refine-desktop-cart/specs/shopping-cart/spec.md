## ADDED Requirements

### Requirement: Clear desktop cart review and accessible controls
The cart SHALL preserve its customer-authenticated guard and use the existing server-side events and confirmed commercial values. At desktop widths of at least 1024px, confirmed items and the summary SHALL appear in two columns. Each item SHALL expose a name or SKU fallback as H2, variation when present, SKU, availability, current unit price, confirmed quantity and subtotal. The quantity input SHALL have a visible, explicitly associated label and integer step, allowing zero removal through the existing handler. Update and remove controls SHALL have item-specific accessible names and visible focus. Monetary presentation SHALL use R$, a decimal comma and at least two fractional digits without float conversion, recalculation or loss of extra precision. All mutation/refresh controls and checkout continuation SHALL be disabled during loading, while prior confirmed data and an updating message remain observable. Empty, loading and feedback SHALL remain distinct; an initial failure SHALL NOT be presented as a confirmed empty cart. The summary and checkout link SHALL be offered only when items exist and SHALL NOT nest an interactive button inside a link. No shipping cost, discount, stock reservation or product image SHALL be invented. Narrow layouts SHALL stack without horizontal overflow. Isolated fixtures SHALL NOT introduce a route or authentication bypass in the product.

#### Scenario: Customer reviews confirmed items
- **WHEN** an authenticated customer has confirmed cart items on desktop
- **THEN** item information and values are legible beside a summary using the unchanged backend total

#### Scenario: Customer edits quantity
- **WHEN** a customer edits a labeled quantity input
- **THEN** the confirmed quantity remains explicit until the existing update event confirms the operation, and zero remains supported for removal

#### Scenario: Unavailable item remains visible
- **WHEN** a confirmed item is unavailable
- **THEN** its real quantity, availability and values remain visible, with existing correction/removal actions preserved

#### Scenario: Cart is updating
- **WHEN** a cart request is in progress
- **THEN** controls and checkout continuation are disabled and existing values are identified as last confirmed values

#### Scenario: Empty cart or initial error
- **WHEN** no items exist and the cart is not loading
- **THEN** an empty message with catalog navigation appears if there is no feedback; otherwise the existing feedback remains visible without claiming the empty result was confirmed

#### Scenario: Visitor has no customer session
- **WHEN** a visitor without a customer session opens the cart
- **THEN** the customer sign-in invitation appears and no authenticated cart controls or values are exposed
