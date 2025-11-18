## Implementation Plan
- [ ] Review the current rows/cols derivation for pages-per-sheet that keeps portrait layouts side by side
- [ ] Enforce rows >= cols whenever orientation=portrait and confirm page order remains left-to-right, top-to-bottom
- [ ] Guard landscape layouts so column-first logic is unchanged for legacy users
- [ ] Update README or CLI help to clarify that portrait mode stacks pages vertically
- [ ] Generate sample 2-up/4-up PDFs to visually confirm the new stacking behavior
