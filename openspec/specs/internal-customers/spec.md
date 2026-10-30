# internal-customers Specification

## Purpose
Provide read-only customer consultation for active employees and administrators, with backend authorization, masked contact data, combined filters, bounded pagination and safe session handling. Customer sessions, inactive internal users and visitors cannot access this internal capability.

## Requirements

### Requirement: Active internal users can read customer records
The system SHALL authorize customer list and detail reads only with a valid internal user session whose user record exists, status is ATIVO, and role is FUNCIONARIO or ADMINISTRADOR. Both endpoints SHALL enforce this in Xano before querying customers. Visitor and customer sessions SHALL be rejected even when identifiers overlap. Customer records SHALL NOT be mutated by these reads.

#### Scenario: Both approved internal roles can consult customers
- **WHEN** an active FUNCIONARIO or ADMINISTRADOR requests the list or detail using an internal session
- **THEN** the backend permits the authorized read without changing customer data

#### Scenario: Unauthorized sessions are rejected
- **WHEN** either endpoint receives no session, a Cliente token, an unsupported role, an inactive internal user, or a user no longer present
- **THEN** it denies access before returning any customer data or existence information

### Requirement: Customer lists support combined filters and bounded pagination
GET customers SHALL accept q trimmed to at most 100 characters, status ATIVO by default or INATIVO/TODOS, page default 1 and per_page default 20 capped at 50. Invalid values SHALL be rejected. The backend SHALL combine partial case-insensitive name/email search with status, ignore blank q, sort by nome_completo then id ascending and paginate before responding. The response SHALL contain items, page, per_page, total_items and total_pages; no-match total_pages SHALL be zero. Changing filters SHALL reset page to 1 and clear the selected detail.

#### Scenario: Default and combined filters
- **WHEN** an authorized user opens the list without filters or submits q with a selected status
- **THEN** default results contain only ATIVO customers, or results match both the status and the name/email condition respectively

#### Scenario: Stable pages and invalid inputs
- **WHEN** customers have identical names or the user requests an invalid page, size, status or overlong term
- **THEN** valid pages retain deterministic id tie-breaking and invalid inputs are rejected instead of silently expanding access

#### Scenario: No results or page beyond the end
- **WHEN** no customer matches or a positive page exceeds the available pages
- **THEN** items is empty with accurate counts, and a no-match list reports total_items and total_pages as zero

### Requirement: Responses minimize and mask customer data in the backend
The list SHALL expose only id, nome_completo, email_masked, telefone_masked, status and created_at. Detail SHALL add only cpf_masked. Email SHALL expose at most three local-part characters while hiding at least one, followed by five asterisks and no domain; one-character local parts SHALL be fully masked. Phone SHALL expose only its last four digits when longer than four. CPF SHALL expose only its last two digits in ***.***.***-NN format when valid-length. Missing or malformed values SHALL NOT leak raw input. Both responses SHALL exclude credentials, hashes, tokens, addresses, orders, USER_ID and unapproved fields, and SHALL NOT log search terms or payloads containing customer data.

#### Scenario: List and detail use sanitized fields
- **WHEN** an authorized read returns a customer
- **THEN** email maria@example.test becomes mar*****, phone 11999991234 becomes *****1234 and detail CPF 12345678909 becomes ***.***.***-09, with only whitelisted fields in the response

#### Scenario: Short or malformed contact values
- **WHEN** local-part lengths are two or one, or a contact/CPF is missing or malformed
- **THEN** masking does not expose the whole local part, a raw value or an unapproved fallback field

### Requirement: Customer details preserve read scope and ownership separation
GET customers/{customer_id} SHALL accept only a positive integer id and apply the same internal authorization as listing. Authorized users SHALL be able to consult active or inactive customer records without accessing addresses or order history. A missing customer SHALL return not found only after authorization. The Reflex integration SHALL use server-side GETs with the private internal token, never the customer token or a browser-exposed credential.

#### Scenario: Consult inactive or missing customer
- **WHEN** an authorized internal user selects an inactive customer or requests a missing positive id
- **THEN** an inactive customer's sanitized detail is available or the missing record returns not found, without mutation or additional data domains

#### Scenario: Browser does not receive backend credentials
- **WHEN** the internal interface loads a list or detail
- **THEN** State performs the request using the internal private session and only sanitized data reaches browser state

### Requirement: Desktop consultation handles feedback and session changes safely
The internal surface SHALL provide submitted search, status selection, clear filters, bounded pagination and a closable accessible detail panel for both authorized roles. Loading, empty, error and unauthorized states SHALL be distinct. A 429 MAY be retried at most once when Retry-After is valid and no greater than 30 seconds; otherwise the interface SHALL show manual retry without blocking or inventing success. Unauthorized failures SHALL NOT retry. Obsolete responses SHALL NOT overwrite newer filters or selections. Logout or invalid session SHALL clear customer list, detail, counts and related feedback. This capability SHALL NOT add edit, reveal, export, order-history or support actions. Desktop presentation SHALL group submitted filters and refresh controls, expose protected contact fields in a legible table with named detail actions, show accurate pagination when pages exist, and present selected customer details in a named, closable read-only region. Initial, loading, no-results and failure feedback SHALL be visually distinct without initiating extra reads or inventing customer counts. Styles SHALL remain scoped to customer consultation.

#### Scenario: Failed request or rate limit
- **WHEN** a request fails or returns 429
- **THEN** feedback remains visible, any allowed retry is bounded, and the interface never presents stale data as a newly successful query

#### Scenario: Filter or session changes during a request
- **WHEN** a filter or selection changes, or the user logs out or loses authorization before an older response returns
- **THEN** outdated responses are discarded and no customer detail persists across session loss

#### Scenario: Existing internal product management remains restricted
- **WHEN** a FUNCIONARIO uses customer consultation
- **THEN** customer read access does not grant product administration or other sensitive mutations

#### Scenario: Desktop consultation before and after a read
- **WHEN** an authorized user opens customer consultation, submits filters or selects a customer
- **THEN** the initial surface invites a read, request feedback remains distinct, returned counts and masked contacts are legible, and a selected detail can be closed without changing customer data

#### Scenario: Desktop keyboard consultation
- **WHEN** the user tabs through search, status, query actions, pagination and detail controls
- **THEN** controls have accessible names and visible focus, the table retains semantic headers, and no edit, reveal or export action is offered
