# pdf-merging Specification

## Purpose
TBD - created by archiving change add-pdf-merge-script. Update Purpose after archive.
## Requirements
### Requirement: Command-line PDF merging
The CLI MUST allow users to configure explicit N-up grid parameters (rows and columns) in addition to the number of pages per sheet, mimicking “one sheet, multiple pages” print behavior.

#### Scenario: Custom grid layout
- **GIVEN** the user runs `python merge_pdfs.py --input-dir ./docs --output merged.pdf --nup-rows 2 --nup-cols 1`
- **WHEN** there are multiple pages to merge
- **THEN** each output page contains two original pages arranged vertically (2 rows x 1 column) in reading order

#### Scenario: Invalid grid parameters
- **GIVEN** the user supplies `--nup-rows 0` or specifies rows without columns (or vice versa)
- **WHEN** the script runs
- **THEN** it MUST exit with a non-zero status and explain the parameter requirements

