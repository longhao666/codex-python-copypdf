## Why
- The previous orientation change only swapped canvas width/height, so portrait 2-up/4-up pages still appear side by side
- Portrait output should stack pages vertically to match reader expectations and avoid horizontal cropping

## What Changes
- Update the N-up grid derivation so portrait mode enforces row-first stacking (rows >= cols)
- Keep the existing landscape behavior when users explicitly request it
- Refresh README/help examples to explain portrait outputs stack top-to-bottom

## Impact
- pages-per-sheet > 1 combined with the default portrait orientation will now render differently, requiring updated screenshots
- CLI options remain unchanged, but behavior better reflects what "portrait" implies
