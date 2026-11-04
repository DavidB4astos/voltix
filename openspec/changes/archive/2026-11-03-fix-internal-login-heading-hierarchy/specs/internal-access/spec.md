## ADDED Requirements

### Requirement: Internal login has one primary heading

The internal login page SHALL expose exactly one level-one heading identifying the page. Repeated brand marks in its header and footer SHALL NOT be rendered as level-one headings. Their text and visual presentation SHALL remain unchanged.

#### Scenario: Internal login heading hierarchy
- **WHEN** the unauthenticated internal login page is rendered
- **THEN** “Acesso interno” is the page's single level-one heading
- **AND** repeated Voltix brand marks are not level-one headings
- **AND** existing brand text and visual presentation remain unchanged
