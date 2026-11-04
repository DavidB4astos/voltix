## ADDED Requirements

### Requirement: Internal variation prices use Brazilian currency display

The internal product variation table SHALL display each price with the `R$` prefix, a comma decimal separator, and two decimal places. The column header SHALL NOT redundantly repeat the currency unit. Formatting SHALL NOT change the underlying price value, calculations, or form submissions.

#### Scenario: Administrator reviews a variation price
- **WHEN** a variation with price `119.9` is displayed in the internal product table
- **THEN** its price is shown as `R$ 119,90`
- **AND** the column header does not repeat the currency unit
- **AND** the price value used by forms and backend requests remains unchanged
