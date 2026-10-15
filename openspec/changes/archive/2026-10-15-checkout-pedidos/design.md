## Context

See [proposal.md](./proposal.md) and [specs/checkout-orders/spec.md](./specs/checkout-orders/spec.md). Cliente uses its own Xano auth scope and server-side Reflex State requests. Existing tables provide `CLIENTE`, `endereco`, `carrinho`, `item_carrinho`, `produto`, and `variacao_produto`; cart lines store quantity only, while variation prices and stock are decimals. The Domain Model requires historical order-item prices and a one-to-one Payment but does not define the technical stock-decrement moment. The approved behavior for this Change is to validate stock at confirmation without decreasing or reserving it.

The selected delivery address remains editable, so the approved order history also stores a copy of its delivery fields on Pedido alongside the required Endereco reference.

## Goals / Non-Goals

**Goals:**

- Keep checkout ownership and commercial validation on Xano, not in the browser or only in Python.
- Persist Pedido, ItemPedido and its required pending Pagamento together, and clear the existing cart only after that transaction succeeds.
- Preserve the purchase-time unit prices, totals and delivery-address contents.

**Non-Goals:**

- Define cancellation transitions, stock restoration, shipment tracking, payment approval or administrative order management.
- Reduce or reserve stock, calculate freight, or add a real payment or freight integration.
- Change existing Cliente, Endereco, Produto, VariaçãoProduto or Carrinho schemas beyond consuming their existing data and removing cart items after successful order creation.

## Decisions

### Use one customer-scoped order API boundary

Create authenticated review, confirmation, order-list and order-detail endpoints in the existing Cliente API group. Every operation derives its owner from `$auth.id`, confirms the Cliente is active and scopes Pedido, Carrinho and Endereco lookups to that identity. A client-provided address or order ID is only a selector; it never supplies ownership.

Alternative considered: accept an owner ID or trusted order totals from Reflex. Rejected because both can be modified by the caller and would weaken backend authorization and pricing integrity.

### Persist the Domain Model entities and only the approved history snapshots

Add Pedido, ItemPedido and Pagamento tables with their required relationships and uniqueness rules. Pedido stores a unique commercial code distinct from its internal ID, current order status, date, subtotal, freight and total; freight is zero in this Change. ItemPedido stores a positive integer quantity and the decimal unit price from confirmation, with a unique `(pedido_id, variacao_produto_id)` pair. Pagamento is created with the Pedido, stores the selected allowed method, the order total and status `PENDENTE`; this records the mandatory one-to-one domain relationship but does not start a payment attempt.

Preserve the selected Endereco relationship and copy its delivery fields (CEP, logradouro, número, complemento, bairro, cidade, estado and identificação) into Pedido at confirmation, per the approved history decision. This avoids later address edits changing the order summary. Do not add product-name, SKU, tax, discount or payment-attempt snapshots not required by the Domain Model or approved scope.

Alternative considered: keep only the mutable Endereco reference. Rejected because later edits would change historical delivery information. A separate address entity or full address table copy was also rejected as unnecessary; the approved field snapshot is stored on Pedido.

### Recompute a reviewed checkout before committing

The review endpoint returns current cart lines, address summary, prices and calculated totals. Confirmation receives the selected address, allowed payment method and the reviewed commercial values as comparison data, then reloads the authenticated customer's cart and current Product/Variation/stock/price/address records. The backend recalculates all amounts from persisted data. If the reviewed contents, statuses, stock or prices no longer match, it returns a refreshed review and does not create an order; the Customer must explicitly confirm that new review.

On a valid confirmation, a Xano transaction creates Pedido, consolidated ItemPedido rows and its PENDENTE Pagamento, then removes only that customer's cart lines. Failures roll back the transaction and preserve the cart. The application does not send or accept authoritative prices, subtotals, freight or totals from the client.

Alternative considered: create a durable checkout entity for every review. Rejected to avoid adding a lifecycle/table not present in the Domain Model for a single confirmation flow. The confirmation request's reviewed values are comparison-only; persisted data remains authoritative.

### Do not alter stock at checkout in this Change

Revalidate each current variation as active and its available stock as sufficient for the cart quantity immediately before order persistence. Do not decrement or reserve stock because the Domain Model explicitly leaves the technical moment undefined and the approved Change decision is validation only. Orders start at `AGUARDANDO_PAGAMENTO`; the mandatory related Payment starts at `PENDENTE` using a method selected from `PIX`, `CARTAO` or `BOLETO`, with value equal to the Pedido total. There is no charge, approval, gateway or real freight calculation. Freight and its contribution to total are zero.

Alternative considered: decrement stock on order creation. Rejected because it would define the unresolved stock lifecycle and cancellation/restoration behavior without project approval.

### Keep Reflex as a server-side client

Extend the existing Cliente State and page flow: request a review, let the Customer choose an active own address and payment method, submit explicit confirmation, then show the returned order summary. Add owner-scoped order history/detail views. All HTTP requests use the existing server-side Xano helper and the separate Cliente token; failures retain the last confirmed state and never produce success-shaped fallbacks.

## Risks / Trade-offs

- [Stock is not reserved or reduced, so concurrent orders can each pass a point-in-time availability check] -> Revalidate in the confirmation transaction, clearly treat availability as a check rather than reservation, and do not claim stock has been allocated. A future approved Change must define when stock is decremented and how cancellation restores it.
- [A variation's price or stock can change between review and confirmation] -> Re-read all commercial values and compare with the reviewed values in Xano; require a fresh explicit confirmation on mismatch.
- [Xano publication may be blocked or required dependencies may not exist in the environment] -> Perform read-only dependency audit first; do not alter unrelated tables or bypass `allow_push`; document and stop remote validation if blocked.
- [Address data may be edited after an order] -> Keep the required relation and use the approved delivery-field snapshot for historical display.

## Migration Plan

1. Audit Xano read-only for the active Cliente, address, cart, product and variation schemas/APIs; do not publish if dependencies are missing or environment permissions disallow it.
2. Add Pedido, ItemPedido and Pagamento schemas and validate their relationships and unique indexes without modifying existing schemas.
3. Add review, confirmation and owner-scoped order query endpoints; exercise transactional rollback, repeated variation consolidation and boundary authorization locally or with authorized tests.
4. Add State/Python and Reflex checkout/order-summary flows using the Customer token and a new environment URL; keep `reflex.lock` unchanged.
5. Run local tests, Reflex compilation, XanoScript and strict OpenSpec validation. Run remote E2E only if the authorized Xano environment permits it; do not create unnecessary QA records.
6. Roll back by disabling the new routes/endpoints, not by deleting persisted order history. Do not modify stock or existing customer/product/cart schemas during rollback.

## Open Questions

None. Stock timing, zero freight for this Change, pending-payment record behavior and historical delivery snapshots are resolved in the proposal/spec from the user's instructions and approvals.
