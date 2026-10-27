## ADDED Requirements

### Requirement: Public catalog search form and URL state
The catalog SHALL offer an explicitly labeled product-name search form submitted by Enter or Buscar. Typing alone SHALL NOT request the catalog. Applied queries SHALL use the existing anonymous q parameter combined with category_id, with URL encoding and no changes to public API access rules. The search field and incoming q SHALL be trimmed and limited to 100 characters. Applied search and editable draft SHALL be separate. Category changes SHALL preserve the applied term. Limpar filtros SHALL remove category, term and selected product details. Loading SHALL disable the controls and SHALL NOT show stale results as confirmed. Errors SHALL remain observable with retry. A successful search SHALL expose the applied term, count and a distinct no-results message. Reopening the catalog URL SHALL restore the applied filters. Home entry SHALL clear the draft as well as prior filters. Existing product_id entry SHALL still open product details.

#### Scenario: Visitor submits a search
- **WHEN** a visitor types a product name and submits by Enter or Buscar
- **THEN** the catalog URL encodes q and displays the real public results for that name

#### Scenario: Typing does not fetch results
- **WHEN** a visitor edits the search field without submitting
- **THEN** no catalog request is sent and the applied result set remains unchanged

#### Scenario: Visitor combines search with category
- **WHEN** a visitor changes the category after applying a search
- **THEN** the URL and results combine category_id with the applied q

#### Scenario: Visitor clears filters
- **WHEN** a visitor activates Limpar filtros
- **THEN** search, category and selected details are cleared and the unfiltered catalog loads

#### Scenario: Search finds no product
- **WHEN** the public query succeeds with no matching product
- **THEN** a no-results message appears and no stale grid is displayed

#### Scenario: Search fails and retries
- **WHEN** a public search request fails
- **THEN** the error is shown and retry uses the same applied search and category

#### Scenario: Visitor reopens a filtered URL
- **WHEN** the catalog opens with q and category_id
- **THEN** the input, category and loader use the normalized applied filters

#### Scenario: Visitor repeats the same search
- **WHEN** a visitor submits the filters already represented by the current URL
- **THEN** the existing loader runs and loading can finish without requiring a different route
