## MODIFIED Requirements

### Requirement: Navigation respects existing roles
The workspace SHALL provide Dashboard, CRM, Customers, Attendances and Orders to active employees and administrators; Products, Categories and brands, Bulk import and Users only to administrators; and a self-profile view to both approved profiles. Selecting a section SHALL accept only known authorized values and SHALL NOT add permissions or trigger a data mutation. Selecting Dashboard, CRM, Attendances, Orders, Users or the profile MAY initiate a read-only load; selecting the other sections SHALL preserve their existing behavior.

#### Scenario: Employee navigation
- **WHEN** a validated FUNCIONARIO opens the workspace or attempts to select an administrative section
- **THEN** only Dashboard, CRM, Customers, Attendances, Orders and the self-profile view are available, and administrative selections including Products, Categories, Bulk import and Users are rejected without rendering administrative content

#### Scenario: Administrator navigation
- **WHEN** a validated ADMINISTRADOR selects an authorized section
- **THEN** only that section's existing content is presented, with its original handlers and guards, and selecting Users presents the administrative user list

#### Scenario: Profile remains available to both roles
- **WHEN** an active employee or administrator opens the self-profile view
- **THEN** the workspace presents their own identity and profile actions without exposing administrative user management

#### Scenario: Unknown or unauthorized section is rejected
- **WHEN** a session submits a section value that is unknown or not permitted for its role
- **THEN** the workspace keeps the current section and does not load data for the rejected value
