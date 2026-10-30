## ADDED Requirements

### Requirement: Desktop category and brand management has labeled forms and readable lists
The administrator catalog panel SHALL present categories and brands in distinct labeled sections with persistent labels for required name and optional description. Create and edit modes SHALL be explicit, and existing save/cancel/refresh/edit/status events and name/description payloads SHALL be preserved. Records SHALL appear in semantic tables with full names/descriptions, textual status and record-specific accessible action names. Inactive records SHALL remain visible. Controls SHALL be disabled during the existing loading state, feedback SHALL remain observable and empty-list guidance SHALL NOT appear simultaneously with loading. Styles SHALL remain scoped and preserve the administrator-only guard. At desktop widths of 1024px and above, content SHALL remain readable without horizontal page overflow; the form and list MAY stack when useful space is insufficient.

#### Scenario: Administrator scans category and brand records
- **WHEN** an administrator opens the catalog panel with active and inactive records
- **THEN** each entity has its own section, complete record text, textual status and clearly identified actions

#### Scenario: Administrator edits a record
- **WHEN** an existing edit action is activated
- **THEN** the labeled form shows edit mode with existing values and preserves save and cancel behavior

#### Scenario: Loading or failed refresh remains observable
- **WHEN** a section is loading or reports a backend failure
- **THEN** loading disables its controls without simultaneous empty guidance, and the existing failure message remains visible for a new attempt

#### Scenario: Current list is empty
- **WHEN** a section is not loading and its current list has no records
- **THEN** it offers discrete empty guidance and the existing refresh action without claiming remote deletion or successful synchronization

#### Scenario: Employee cannot access catalog management
- **WHEN** a Funcionário uses the internal panel
- **THEN** administrator category and brand forms and actions remain unavailable
