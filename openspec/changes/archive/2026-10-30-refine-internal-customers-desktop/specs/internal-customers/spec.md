## MODIFIED Requirements

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