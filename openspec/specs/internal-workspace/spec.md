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
The desktop workspace SHALL use a restrained navy and cyan sidebar, a coherent main heading, descriptive section text, clear selected navigation, visible keyboard focus, and accessible named controls. Identity, sign out and a link to the public store SHALL be available. Navigation items SHALL be compact rows with clear selected state and SHALL be reachable by keyboard. The header area next to the section title SHALL NOT repeat a redundant global "Acesso interno" pill; if a top-right indicator remains, it SHALL communicate session state unobtrusively. It SHALL present only implemented sections and SHALL NOT link to unimplemented features. Styles SHALL be scoped to the workspace and preserve basic usability on narrow screens, stacking the sidebar above the content without horizontal overflow.

#### Scenario: Desktop user works in a section
- **WHEN** the workspace is viewed at a desktop width
- **THEN** navigation remains separate from the main content and the current section is clearly identified without stacking all modules in a single long page

#### Scenario: Keyboard navigation
- **WHEN** a user tabs through navigation and activates an authorized item
- **THEN** its focus is visible and its selected state is conveyed programmatically

#### Scenario: Compact sidebar navigation
- **WHEN** the workspace is viewed at a desktop width
- **THEN** navigation items render as compact rows with icon, label and a distinct selected state, all reachable by keyboard, and the current section is identified without additional redundant global indicators in the header

#### Scenario: Narrow screen preserves usability
- **WHEN** the workspace is viewed at 375 or 768 px
- **THEN** the sidebar stacks above the content, navigation remains horizontally scrollable or wrapped accessibly and the main content shows no horizontal overflow

### Requirement: Workspace surfaces use consistent actions and density
The workspace SHALL present data-load and refresh actions (for example "carregar/atualizar", "buscar", "aplicar filtros") as solid buttons consistent with other primary actions, and destructive actions with the existing destructive treatment, preserving their labels, handlers, permissions and confirmation flows. Informational, error and empty states SHALL be visually distinct but compact, without removing messages, roles or actions, and tables SHALL remain readable at desktop and tablet widths.

#### Scenario: Refresh action uses a button
- **WHEN** a section offers a data-load or refresh action
- **THEN** the action renders as a solid button consistent with the other primary actions and triggers the same handler and authorization guard as before

#### Scenario: Error and empty states remain visible but compact
- **WHEN** a section displays an error, informational or empty state
- **THEN** the state remains clearly readable and distinguishable, in a more compact presentation, and the existing message and actions are preserved

#### Scenario: Tables remain readable
- **WHEN** a section displays tabular data at desktop or tablet width
- **THEN** rows, headers and action cells remain aligned and readable, actions stay identifiable and the table does not require horizontal scrolling at those widths
