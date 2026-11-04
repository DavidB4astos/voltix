## ADDED Requirements

### Requirement: Internal login fields have associated visible labels

The internal login form SHALL provide a visible HTML label programmatically associated with each email and password input. The association SHALL preserve existing input names, types, required validation, submission handler, and authentication behavior.

#### Scenario: Assistive technology identifies internal login fields
- **WHEN** the internal login form is rendered
- **THEN** each email and password input has a visible label whose `for` value matches that input's unique `id`
- **AND** the form preserves its existing names, types, required validation, and submit handler
