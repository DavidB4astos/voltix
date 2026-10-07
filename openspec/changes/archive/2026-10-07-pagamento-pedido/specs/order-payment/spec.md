## Purpose

Define the simulated payment flow that completes a Voltix order without connecting to a financial institution or payment gateway. The flow uses the payment method and amount already recorded at checkout.

## ADDED Requirements

### Requirement: Active customers can simulate approval of their own pending order
The system SHALL allow an authenticated active Customer to request the simulated payment of their own order when its payment is `PENDENTE` and order status is `AGUARDANDO_PAGAMENTO`. The simulation SHALL approve the payment, update the same Payment to `APROVADO`, and move the Order to `PAGAMENTO_CONFIRMADO`.

#### Scenario: Customer simulates payment for an eligible order
- **WHEN** an active authenticated Customer requests payment simulation for their own pending order
- **THEN** the system sets the existing Payment to `APROVADO`, sets the Order to `PAGAMENTO_CONFIRMADO`, and returns the updated status without creating another Payment

#### Scenario: Customer attempts to pay another customer's order
- **WHEN** a Customer requests simulation for an order they do not own
- **THEN** the backend rejects the request without revealing the order, payment, or customer data and performs no mutation

#### Scenario: Unauthenticated or inactive customer requests payment
- **WHEN** a request does not have a valid session for an active Customer
- **THEN** the backend rejects it and performs no mutation

#### Scenario: Order or payment is not awaiting payment
- **WHEN** payment simulation is requested for an order whose payment or order status is not eligible
- **THEN** the system does not change either record and reports that payment cannot be simulated in the current state

### Requirement: Simulated payment preserves the existing payment contract
The system SHALL use the single Payment created with the Order, preserve its selected method (`PIX`, `CARTAO` or `BOLETO`) and value equal to the Order total, and SHALL NOT create partial payments or attempt-history records. The simulation SHALL NOT represent a real financial transaction.

#### Scenario: Eligible payment is approved without a real financial integration
- **WHEN** an eligible payment is simulated
- **THEN** the existing method and amount remain unchanged, the payment becomes `APROVADO`, and no gateway, bank, real PIX/boleto charge, or card details are used

#### Scenario: Stored payment value does not match order total
- **WHEN** simulation finds that the Payment value differs from the Order total
- **THEN** it rejects the operation and leaves both records unchanged

#### Scenario: Repeated request after approval
- **WHEN** the same Customer repeats a simulation request after that Order is already confirmed as paid
- **THEN** the system returns the current approved state without creating a Payment or changing the purchase total

### Requirement: Payment approval does not alter inventory
The simulated payment flow SHALL NOT decrement, reserve, or restore product inventory.

#### Scenario: Customer completes simulated payment
- **WHEN** a Payment is simulated as approved
- **THEN** the payment and order statuses change as specified while every variation's available quantity remains unchanged

### Requirement: Customer sees confirmed payment status through Reflex State
The order-details interface SHALL send the simulation request through Reflex State/Python, which SHALL call Xano server-side using the Customer session. The interface SHALL show the updated order/payment state only after a valid backend response and SHALL report failures without claiming approval.

#### Scenario: Customer requests simulation from own order details
- **WHEN** a Customer activates the payment simulation in their order summary
- **THEN** Reflex State calls the Xano payment operation with the Customer session and displays the confirmed status returned by Xano

#### Scenario: Payment request fails or returns an invalid response
- **WHEN** the backend request fails, is unauthorized, or returns an invalid response
- **THEN** the interface reports that payment was not confirmed and does not display a success state
