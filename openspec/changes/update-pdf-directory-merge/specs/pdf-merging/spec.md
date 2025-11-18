## MODIFIED Requirements
### Requirement: Command-line PDF merging
The CLI MUST support merging every PDF file located within a user-provided directory.

#### Scenario: Merge entire directory
- **GIVEN** the user provides `--input-dir ./docs` pointing to an existing folder containing PDF files
- **WHEN** they run `python merge_pdfs.py --input-dir ./docs --output merged.pdf`
- **THEN** the tool MUST detect every `.pdf` (case-insensitive) directly inside that folder, sort them lexicographically by filename, and merge them into `merged.pdf`

#### Scenario: Directory contains no PDFs
- **GIVEN** the user passes `--input-dir ./empty`
- **WHEN** the folder has no PDF files
- **THEN** the tool MUST exit with a non-zero status and explain that no PDF files were found
