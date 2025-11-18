## ADDED Requirements
### Requirement: Orientation Control for N-up Output
N-up mode (pages-per-sheet > 1) MUST produce portrait pages by default and MUST offer a landscape override option.

#### Scenario: Default portrait orientation
- **GIVEN** the user omits `--orientation` or passes `portrait`
- **WHEN** the tool generates any N-up page
- **THEN** the resulting page height MUST be greater than or equal to its width

#### Scenario: Configurable landscape orientation
- **GIVEN** the user runs the CLI with `--orientation landscape`
- **WHEN** the tool generates any N-up page
- **THEN** the resulting page width MUST be greater than or equal to its height