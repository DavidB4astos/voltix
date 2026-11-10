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

### Requirement: Desktop workspace has clear hierarchy and keyboard access
The desktop workspace SHALL use a restrained navy and cyan sidebar, a coherent main heading, descriptive section text, clear selected navigation, visible keyboard focus, and accessible named controls. Identity, sign out and a link to the public store SHALL be available. It SHALL present only implemented sections and SHALL NOT link to unimplemented features. Styles SHALL be scoped to the workspace and preserve basic usability on narrow screens.

#### Scenario: Desktop user works in a section
- **WHEN** the workspace is viewed at a desktop width
- **THEN** navigation remains separate from the main content and the current section is clearly identified without stacking all modules in a single long page

#### Scenario: Keyboard navigation
- **WHEN** a user tabs through navigation and activates an authorized item
- **THEN** its focus is visible and its selected state is conveyed programmatically
