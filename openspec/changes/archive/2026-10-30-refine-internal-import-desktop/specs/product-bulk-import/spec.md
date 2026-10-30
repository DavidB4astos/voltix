## ADDED Requirements

### Requirement: Desktop bulk import clearly separates file review and persistence
The administrator import panel SHALL distinguish file selection, preview and final results through labeled sections and persistent guidance. It SHALL display the existing CSV/XLSX formats and limits of 200 rows, 50 products and 2 MB, plus required and optional column names. It SHALL display selected filenames from the existing upload control. Preview and results SHALL use semantic tables with complete product names, textual statuses and reasons/details. Existing upload ID, event bindings, valid-row confirmation conditions, loading disables, cancellation and reset behavior SHALL remain unchanged. Feedback and real progress text SHALL remain observable; no invented success or percentage SHALL appear. Styles SHALL be scoped, preserve the administrator guard and avoid horizontal page overflow at desktop widths of at least 1024px.

#### Scenario: Administrator prepares a file
- **WHEN** the administrator opens the import section and selects a supported file
- **THEN** file guidance and selected name are visible and preview remains separate from confirmation of persistence

#### Scenario: Administrator reviews mixed rows
- **WHEN** preview contains valid, rejected or duplicate rows
- **THEN** a labeled table displays each line, product, textual status and full reason, preserving the existing confirmation condition

#### Scenario: Import is processing
- **WHEN** the existing loading state is active
- **THEN** existing file/preview/reset/confirmation controls remain disabled as before and real progress and the existing cancellation control are observable when applicable

#### Scenario: Import reports partial results
- **WHEN** the existing report contains created, skipped or failed groups
- **THEN** the result table preserves each outcome and complete detail without turning failures into success

#### Scenario: Employee opens the internal panel
- **WHEN** a Funcionário uses the internal interface
- **THEN** import controls remain unavailable
