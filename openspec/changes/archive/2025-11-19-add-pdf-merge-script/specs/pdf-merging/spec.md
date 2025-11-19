## ADDED Requirements
### Requirement: Command-line PDF merging
The tool MUST provide a command-line script that writes multiple input PDFs sequentially into a new PDF file.

#### Scenario: Merge succeeds
- **GIVEN** the user provides an output file path and at least two existing PDF files
- **WHEN** they run `python merge_pdfs.py --output merged.pdf 1.pdf 2.pdf`
- **THEN** the pages of each input file are written to `merged.pdf` in the same order

#### Scenario: Input validation fails
- **GIVEN** required parameters are missing or one of the input paths does not exist
- **WHEN** the script runs
- **THEN** it exits with a non-zero code and emits a clear error message
