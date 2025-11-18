## MODIFIED Requirements
### Requirement: Command-line PDF merging
The CLI MUST provide an option to render N original pages onto a single output page (N-up layout) while keeping the default behavior (1 page per sheet).

#### Scenario: N-up layout succeeds
- **GIVEN** the user runs `python merge_pdfs.py --input-dir ./docs --output merged.pdf --pages-per-sheet 4`
- **WHEN** the directory contains at least four pages total
- **THEN** each output page contains up to four scaled sub-pages arranged in a grid, in reading order, until all pages are consumed

#### Scenario: Invalid N-up parameter
- **GIVEN** the user sets `--pages-per-sheet` to zero or a negative number
- **WHEN** the script starts
- **THEN** it MUST exit with a non-zero status and explain that the value must be a positive integer
