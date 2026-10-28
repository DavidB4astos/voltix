## ADDED Requirements

### Requirement: Clear desktop account and address workspace
The customer account page SHALL preserve its customer-session guard, registration/login fields, profile fields, immutable CPF, existing handlers and address action conditions. At desktop widths of at least 1024px, profile and address management SHALL use separate columns with semantic section headings. Address inputs SHALL have persistent visible labels and accessible names. Account actions SHALL have visible keyboard focus. Loading or errors SHALL not be described as a confirmed empty address book. Narrow layouts SHALL stack without horizontal overflow. Styling SHALL remain account-scoped, without backend or session changes.

#### Scenario: Customer manages their account
- **WHEN** an authenticated customer opens the desktop account page
- **THEN** profile and address management appear in distinct columns with the existing actions and values

#### Scenario: Customer fills an address
- **WHEN** an address input contains a value
- **THEN** its label remains visible and its accessible name identifies the field

#### Scenario: Address request is pending or fails
- **WHEN** address loading or failure feedback is present
- **THEN** feedback remains visible without claiming the address book is confirmed empty

#### Scenario: Visitor signs in or registers
- **WHEN** no customer session is authenticated
- **THEN** registration and login retain their existing fields and submission events
