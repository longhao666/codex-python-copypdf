## MODIFIED Requirements
### Requirement: Orientation Control for N-up Output
N-up pages MUST respect the requested reading orientation and layout expectations.

#### Scenario: Portrait pages stack vertically
- **GIVEN** the user omits --orientation or passes portrait
- **AND** --pages-per-sheet is greater than 1
- **WHEN** the tool places consecutive source pages on a single sheet
- **THEN** each column MUST fill from top to bottom before moving right, so the second page in a 2-up layout appears below the first

#### Scenario: Portrait grids prefer rows over columns
- **GIVEN** the CLI derives an automatic N-up grid for pages-per-sheet > 1
- **AND** --orientation portrait is in effect
- **WHEN** rows and columns are computed
- **THEN** the row count MUST be greater than or equal to the column count to keep the canvas taller than it is wide
