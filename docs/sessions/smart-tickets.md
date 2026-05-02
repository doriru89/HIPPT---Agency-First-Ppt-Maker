# Smart Tickets Deck — Session Learnings

6 sessions (2026-04-28 to 2026-05-01). 12-slide pitch deck.

## Key Pipeline Rules Established

- **HTML is SSOT** — PPTX is a one-shot export after HTML approval (Step 4.9)
- **Content enrichment is mandatory** (Step 3.7) — ghost deck → 65+ sources → enriched content → build
- **3-lens expert critique** (Step 3.8) — industry insider, technical skeptic, strategy professor stress-test thesis before build
- **Image audit with VIEW** (Step 3.9) — 3 of 7 images failed (CNN cookie popup, wrong LN page, GET redirect)
- **One bottleneck per convergence round** — fix ONE Q dimension, re-score all, check if avg >= 80%
- **Base64 conversion is FINAL step** — iterate with file paths, convert only after PPTX complete
- **Sidecar JSON re-sync** after convergence rounds modify HTML (E-PRES-028)

## Failure Patterns

- **E-PRES-006 is #1 failure** — AI defaults to content-sized (width: auto) instead of canvas-filled. R1 scored Q2:5 → Q2:7 after fixes.
- Sidecar JSON staleness after convergence — modifications don't sync back to JSON
- S5 evidence panel hidden by `overflow: hidden` despite insertion
- Duplicate insertion via string-matching is fragile — use line-number-based insertion
- S9 numbers bolted on below radial hub instead of integrated into spoke nodes

## Process Improvements

- Step 3.9 Image Audit — VIEW each image to verify content, readability, coherence
- Step 4.9 HTML Approval Gate — no PPTX work until HTML locked
- Step 5.0 Sidecar JSON Sync — re-extract after HTML >= 80, not at initial build
- Step 5c Context Review — top-down (ghost deck vision) + bottom-up (source evidence) per slide < 7
