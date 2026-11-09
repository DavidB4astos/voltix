## MODIFIED Requirements

### Requirement: Navigation respects existing roles
The workspace SHALL provide Customers, Attendances and Orders to active employees and administrators, and Products, Categories and brands, and Bulk import only to administrators. Selecting a section SHALL accept only known authorized values and SHALL NOT add permissions or trigger a data mutation. Selecting Attendances or Orders MAY initiate a read-only list load; selecting the other sections SHALL preserve their existing behavior.

#### Scenario: Employee navigation
- **WHEN** a validated FUNCIONARIO opens the workspace or attempts to select an administrative section
- **THEN** only Customers, Attendances and Orders are available and an administrative selection is rejected without rendering product management

#### Scenario: Administrator navigation
- **WHEN** a validated ADMINISTRADOR selects one of the six sections
- **THEN** only that section's existing content is presented, with its original handlers and guards
