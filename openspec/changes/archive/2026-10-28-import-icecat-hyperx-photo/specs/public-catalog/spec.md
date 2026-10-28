## ADDED Requirements

### Requirement: Additional image license notices remain visible
Approved local image credits SHALL preserve an optional license notice from the manifest and display it visibly alongside source and license links in catalog cards and selected product details. Required copyright/database-right and no-warranty notices SHALL not exist only in a tooltip. Existing complete credits without an additional notice SHALL remain valid. Account identifiers, credentials and tokens SHALL not be included in credit metadata or browser image URLs. Image imports SHALL preserve model/color correspondence and existing catalog and purchase behavior.

#### Scenario: Image provider requires an additional notice
- **WHEN** an approved photograph has a license notice in its curated metadata
- **THEN** cards and selected details display the notice and a link to the full license

#### Scenario: Existing photograph has no additional notice
- **WHEN** an approved photograph has complete original credit fields without a notice
- **THEN** its existing attribution remains available and no additional notice is invented
