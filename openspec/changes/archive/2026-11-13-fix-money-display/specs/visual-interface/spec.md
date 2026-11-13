## ADDED Requirements

### Requirement: Money values render in the Voltix currency format
All monetary values presented to the user — prices, unit prices, subtotals, freight, totals, history amounts, sales and dashboard metrics, fixtures and internal summaries — SHALL be displayed in the form `R$ <integer>,<fraction>` where the integer part is the backend decimal text as registered and the fraction is exactly two digits. The presentation SHALL NOT add or render literal escape characters, JSON delimiters or quoting around the value, and SHALL NOT alter the amount sent by the backend or require a recalculation.

#### Scenario: Standard two-decimal value
- **WHEN** the interface presents a monetary value of `119.90`
- **THEN** it renders `R$ 119,90` with no literal quotes or escapes

#### Scenario: Zero-padded and short fractions
- **WHEN** the interface presents `119` or `119.5`
- **THEN** it renders `R$ 119,00` and `R$ 119,50` respectively, always with two fraction digits

#### Scenario: Amounts required elsewhere stay unchanged
- **WHEN** the interface presents the same amount in multiple locations (cart, checkout, orders, product variations, dashboard)
- **THEN** every location renders the identical two-decimal format without recalculation of the backend amount
