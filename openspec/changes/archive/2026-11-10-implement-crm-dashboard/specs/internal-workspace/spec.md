## MODIFIED Requirements

### Requirement: Navigation respects existing roles
The workspace SHALL provide Dashboard, CRM, Customers, Attendances and Orders to active employees and administrators, and Products, Categories and brands, and Bulk import only to administrators. Selecting a section SHALL accept only known authorized values and SHALL NOT add permissions or trigger a data mutation. Selecting Dashboard, CRM, Attendances or Orders MAY initiate a read-only load; selecting the other sections SHALL preserve their existing behavior.

#### Scenario: Employee navigation
- **WHEN** a validated FUNCIONARIO opens the workspace or attempts to select an administrative section
- **THEN** only Dashboard, CRM, Customers, Attendances and Orders are available and an administrative selection is rejected without rendering product management

#### Scenario: Administrator navigation
- **WHEN** a validated ADMINISTRADOR selects one of the eight sections
- **THEN** only that section's existing content is presented, with its original handlers and guards

### Requirement: Desktop workspace has clear hierarchy and keyboard access
The desktop workspace SHALL use a restrained navy and cyan sidebar, a coherent main heading, descriptive section text, clear selected navigation, visible keyboard focus, and accessible named controls. Identity, sign out and a link to the public store SHALL be available. It SHALL present only implemented sections and SHALL NOT link to unimplemented features. Styles SHALL be scoped to the workspace and preserve basic usability on narrow screens.

#### Scenario: Desktop user works in a section
- **WHEN** the workspace is viewed at a desktop width
- **THEN** navigation remains separate from the main content and the current section is clearly identified without stacking all modules in a single long page

#### Scenario: Keyboard navigation
- **WHEN** a user tabs through navigation and activates an authorized item
- **THEN** its focus is visible and its selected state is conveyed programmatically
