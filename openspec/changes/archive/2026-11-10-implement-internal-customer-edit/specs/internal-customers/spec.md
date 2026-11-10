## MODIFIED Requirements

### Requirement: Active internal users can read customer records
The system SHALL authorize customer list and detail reads only with a valid internal user session whose user record exists, status is ATIVO, and role is FUNCIONARIO or ADMINISTRADOR. Both endpoints SHALL enforce this in Xano before querying customers. Visitor and customer sessions SHALL be rejected even when identifiers overlap. Customer records SHALL NOT be mutated by these reads. Customer updates SHALL require a valid internal user session whose user record exists, status is ATIVO and role is ADMINISTRADOR, and SHALL be enforced by the update endpoint before reading or changing any customer.

#### Scenario: Both approved internal roles can consult customers
- **WHEN** an active FUNCIONARIO or ADMINISTRADOR requests the list or detail using an internal session
- **THEN** the backend permits the authorized read without changing customer data

#### Scenario: Unauthorized sessions are rejected
- **WHEN** either read endpoint receives no session, a Cliente token, an unsupported role, an inactive internal user, or a user no longer present
- **THEN** it denies access before returning any customer data or existence information

#### Scenario: Employees cannot update customers
- **WHEN** an active FUNCIONARIO, a Cliente session, a visitor or an inactive internal user sends a customer update
- **THEN** the backend denies the request before changing any customer record

### Requirement: Responses minimize and mask customer data in the backend
The list SHALL expose only id, nome_completo, email_masked, telefone_masked, status and created_at. Detail SHALL add only cpf_masked. The update response SHALL expose the same fields as detail for the updated customer. Email SHALL expose at most three local-part characters while hiding at least one, followed by five asterisks and no domain; one-character local parts SHALL be fully masked. Phone SHALL expose only its last four digits when longer than four. CPF SHALL expose only its last two digits in ***.***.***-NN format when valid-length. Missing or malformed values SHALL NOT leak raw input. All responses SHALL exclude credentials, hashes, tokens, addresses, orders, USER_ID and unapproved fields, and SHALL NOT log search terms or payloads containing customer data.

#### Scenario: List and detail use sanitized fields
- **WHEN** an authorized read returns a customer
- **THEN** email maria@example.test becomes mar*****, phone 11999991234 becomes *****1234 and detail CPF 12345678909 becomes ***.***.***-09, with only whitelisted fields in the response

#### Scenario: Update returns the sanitized detail contract
- **WHEN** an authorized administrator updates a customer
- **THEN** the response carries the same masked contact fields as detail and excludes credentials, hashes, tokens, addresses, orders, USER_ID and raw values

#### Scenario: Short or malformed contact values
- **WHEN** local-part lengths are two or one, or a contact/CPF is missing or malformed
- **THEN** masking does not expose the whole local part, a raw value or an unapproved fallback field

### Requirement: Desktop consultation handles feedback and session changes safely

The internal surface SHALL provide submitted search, status selection, clear filters,
bounded pagination and a closable accessible detail panel for both authorized roles.
Loading, empty, error and unauthorized states SHALL be distinct. A 429 MAY be retried at
most once when Retry-After is valid and no greater than 30 seconds; otherwise the
interface SHALL show manual retry without blocking or inventing success. Unauthorized
failures SHALL NOT retry. Obsolete responses SHALL NOT overwrite newer filters or
selections. Logout or invalid session SHALL clear customer list, detail, counts, order
history and related feedback. This capability SHALL NOT add reveal, export or support
actions; customer order history SHALL be presented only by the `customer-history-panel`
capability, through its own read-only section. Editing SHALL be offered only to active
administrators, SHALL keep raw contact values out of browser state and SHALL require an
explicit confirmation before inactivating a customer. Desktop presentation SHALL group
submitted filters and refresh controls, expose protected contact fields in a legible table
with named detail actions, show accurate pagination when pages exist, and present selected
customer details in a named, closable region. Initial, loading, no-results and failure
feedback SHALL be visually distinct without initiating extra reads or inventing customer
counts. Styles SHALL remain scoped to customer consultation.

#### Scenario: Failed request or rate limit

- **WHEN** a request fails or returns 429
- **THEN** feedback remains visible, any allowed retry is bounded, and the interface never presents stale data as a newly successful query

#### Scenario: Filter or session changes during a request

- **WHEN** a filter or selection changes, or the user logs out or loses authorization before an older response returns
- **THEN** outdated responses are discarded and no customer detail or history persists across session loss

#### Scenario: Existing internal product management remains restricted

- **WHEN** a FUNCIONARIO uses customer consultation
- **THEN** customer read access does not grant product administration, customer editing or other sensitive mutations

#### Scenario: Desktop consultation before and after a read

- **WHEN** an authorized user opens customer consultation, submits filters or selects a customer
- **THEN** the initial surface invites a read, request feedback remains distinct, returned counts and masked contacts are legible, and a selected detail can be closed without changing customer data

#### Scenario: Desktop keyboard consultation

- **WHEN** the user tabs through search, status, query actions, pagination, detail and administrator edit controls
- **THEN** controls have accessible names and visible focus, the table retains semantic headers, and no reveal or export action is offered

## ADDED Requirements

### Requirement: Administrators can update customer identity data and status

PATCH customers/{customer_id} SHALL accept only a positive integer id and require the
update authorization defined for active administrators. It SHALL accept optional
nome_completo, email, telefone and status, require at least one of them, and reject CPF,
password, USER_ID, addresses, orders, attendances or arbitrary fields as update inputs.
An absent field SHALL preserve the current value. Nome_completo SHALL be trimmed to 1-300
characters, email SHALL be trimmed, lowercased, valid and at most 254 characters,
telefone SHALL be trimmed to at most 30 characters, and status SHALL be ATIVO or INATIVO.
Email SHALL remain unique among customers, allowing the current customer's own address.
The backend SHALL update updated_at, keep CPF unchanged, preserve the record for inactive
customers and respond with the sanitized detail contract. A missing customer SHALL return
not found only after authorization, invalid or conflicting input SHALL return a bad
request, and the operation SHALL NOT reveal or persist raw contact values outside the
customer record.

#### Scenario: Administrator updates contact data
- **WHEN** an active administrator submits a new name, email or phone and the values are valid and unique
- **THEN** only the supplied fields change, CPF stays identical, updated_at advances and the response contains masked contacts in the detail shape

#### Scenario: CPF and credentials remain immutable
- **WHEN** a request attempts to change CPF, password, USER_ID or an unsupported field
- **THEN** the backend does not accept the field as an update input and no credential or CPF change is persisted

#### Scenario: Duplicate email is rejected
- **WHEN** an administrator submits an email already used by another customer
- **THEN** the backend returns a bad request and leaves the target customer unchanged

#### Scenario: Inactivate and reactivate a customer
- **WHEN** an administrator submits status INATIVO for an active customer or ATIVO for an inactive customer
- **THEN** the status changes idempotently, the record and its history remain present, and an inactive customer can no longer start a new login session

#### Scenario: Employee or missing customer is rejected
- **WHEN** a FUNCIONARIO submits an update or an administrator targets a missing positive id
- **THEN** access is denied before mutation or the missing record returns not found without exposing customer data
