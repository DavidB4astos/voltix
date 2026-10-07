## Context

See [proposal.md](./proposal.md) and [specs/order-payment/spec.md](./specs/order-payment/spec.md). Checkout already creates one pending Payment for each Order with the selected method and total amount; the Customer order detail already retrieves both records. The Domain Model defines simulated payment and the payment/order statuses. The approved demo behavior is that the explicit “Simular pagamento” action approves the pending payment.

## Goals / Non-Goals

**Goals:**

- Reuse the existing Payment and Order records to complete the pending-to-confirmed transition.
- Keep ownership validation and authoritative status changes in Xano.
- Keep payment communication outside browser-executed code through Reflex State/Python.

**Non-Goals:**

- Add payment tables, payment-attempt history, new payment methods, or changes to checkout's payment creation.
- Integrate a bank, gateway, or real PIX, card, or boleto collection.
- Simulate payment refusal, partial payment, refund, order cancellation, or stock movement.

## Decisions

### Expose one owner-scoped Xano payment operation

Add a Customer-authenticated operation keyed by Order ID. Xano derives the Customer from `$auth.id`, verifies the Customer is active, scopes the Order to that Customer, and reads its single Payment. An Order ID is only a selector and never supplies owner identity.

Alternative considered: update the Order or Payment directly from the browser/Reflex without a dedicated authenticated backend operation. Rejected because the browser must not be authoritative for ownership or financial state.

### Update the existing Payment and Order atomically

For an eligible `AGUARDANDO_PAGAMENTO` Order with one `PENDENTE` Payment whose value equals the Order total, update that Payment to `APROVADO` and the Order to `PAGAMENTO_CONFIRMADO` in one Xano transaction. Preserve method and value, and do not create a second Payment or attempt history. An already-approved Order returns its current state without repeating mutations; inconsistent or ineligible records produce an explicit error.

Alternative considered: create another Payment record for the simulation. Rejected because the Domain Model requires exactly one Payment per Order and no attempt history.

### Make approval a transparent deterministic demo

The Customer explicitly activates “Simular pagamento”; the simulation approves the eligible pending Payment. The UI must identify it as a simulation and must not imply that money was transferred or card/PIX/boleto was actually processed.

Alternative considered: random outcomes, user-selected approval/refusal, or method-specific processing. Rejected because the agreed school-project flow is an approval action and the Domain Model requires no real financial integration.

### Call Xano from Reflex State/Python

Add a server-side Customer State request using the separate Customer token and an environment-configured endpoint. On a valid response, refresh the order summary; on communication, authorization, or response errors, retain the last confirmed order data and show a failure rather than success.

Alternative considered: browser-to-Xano payment requests or embedding endpoint secrets in the page. Rejected to preserve the project's established Reflex-to-State-to-Xano architecture.

## Risks / Trade-offs

- [A repeated network request could otherwise apply a transition twice] -> Treat an already-approved Order as idempotent and do not create further records.
- [Payment and Order statuses could become inconsistent if only one write succeeds] -> Update both records in the same Xano transaction.
- [The environment may block publishing or remote E2E] -> Do not bypass Xano permissions; validate locally and document remote validation as blocked.
- [A simulated approval could be mistaken for a real charge] -> Label the action and resulting flow as simulated and collect no payment credentials.

## Migration Plan

1. Add the owner-scoped Customer payment operation without changing existing tables or checkout endpoints.
2. Add the server-side Reflex State request and a simulation action to own pending Order details.
3. Test ownership, eligible/ineligible statuses, amount consistency, repeat requests, error handling, and that inventory is unchanged.
4. Run local tests, Reflex compilation, XanoScript validation, and strict OpenSpec validation. Run remote E2E only if the authorized Xano environment permits it.
5. Roll back by disabling the new endpoint/action; do not delete Order or Payment history.
