# internal-workspace Specification

## Purpose
Provide an authenticated internal workspace with clear desktop hierarchy, keyboard-accessible section navigation and presentation limited to each existing internal role, while preserving backend authorization and the current management workflows.

## Requirements

### Requirement: Authenticated workspace is separate from sign in
The internal route SHALL show sign-in controls only outside a successfully validated active internal session, and SHALL show the workspace only inside that session. Existing authentication and backend authorization SHALL remain authoritative.

#### Scenario: Successful internal access
- **WHEN** an active internal user completes the existing session validation
- **THEN** the workspace replaces the sign-in form, without duplicate storefront navigation or an additional login form above it

#### Scenario: Session ends
- **WHEN** the user logs out or authorization is cleared
- **THEN** the sign-in surface is shown, the workspace is removed and the section selection resets to customers

### Requirement: Navigation respects existing roles
The workspace SHALL provide Customers, Attendances and Orders to active employees and administrators, and Products, Categories and brands, and Bulk import only to administrators. Selecting a section SHALL accept only known authorized values and SHALL NOT add permissions or trigger a data mutation. Selecting Attendances or Orders MAY initiate a read-only list load; selecting the other sections SHALL preserve their existing behavior.

#### Scenario: Employee navigation
- **WHEN** a validated FUNCIONARIO opens the workspace or attempts to select an administrative section
- **THEN** only Customers, Attendances and Orders are available and an administrative selection is rejected without rendering product management

#### Scenario: Administrator navigation
- **WHEN** a validated ADMINISTRADOR selects one of the six sections
- **THEN** only that section's existing content is presented, with its original handlers and guards

### Requirement: Desktop workspace has clear hierarchy and keyboard access
The desktop workspace SHALL use a restrained navy and cyan sidebar, a coherent main heading, descriptive section text, clear selected navigation, visible keyboard focus, and accessible named controls. Identity, sign out and a link to the public store SHALL be available. It SHALL NOT invent dashboards, metrics or links to unimplemented CRM features. Styles SHALL be scoped to the workspace and preserve basic usability on narrow screens.

#### Scenario: Desktop user works in a section
- **WHEN** the workspace is viewed at a desktop width
- **THEN** navigation remains separate from the main content and the current section is clearly identified without stacking all modules in a single long page

#### Scenario: Keyboard navigation
- **WHEN** a user tabs through navigation and activates an authorized item
- **THEN** its focus is visible and its selected state is conveyed programmatically
