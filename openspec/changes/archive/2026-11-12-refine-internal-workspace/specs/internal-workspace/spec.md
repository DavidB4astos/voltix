## MODIFIED Requirements

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

## ADDED Requirements

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
