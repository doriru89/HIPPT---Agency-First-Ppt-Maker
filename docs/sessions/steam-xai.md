# Steam XAI Presentation — Session Learnings

3 sessions (2026-04-30 to 2026-05-02). Academic presentation on AI explainability in Steam game recommendations.

## Key Pipeline Rules

- **960x540 viewport is law** — slide-native DPI (E-PRES-036). No rendering at 1920x1080 without 2x font overflow penalty
- **Edit HTML directly after manual improvements** — regenerating via build scripts overwrites hand-tuned changes
- **Story-first workflow** — ghost deck (structure) → research → content enrichment → visual build
- **CSS-only animations** — no GSAP CDN for lightweight loads on professor's laptop
- **Yale Blue + academic framing** — `#00356B` primary palette, avoid "NFT" terminology

## Failure Patterns

- Plotly charts in `display:none` slides have zero dimensions — must call `Plotly.relayout()` on show
- Base64 PNGs (500KB+) bloat HTML — remove after final PPTX export
- Static image replacements scored low before tabbed interactive redesign
- Title centering + subtitle + meta stacking creates visual awkwardness on close slides

## Process Improvements

- Design rubric scoring → iterate → re-score cycle (target 80/90, achieved 75/90 in 2 iterations)
- External evidence required for all claims (not just "our model says so")
- Reference PPTX analysis established canvas fill baseline (91% avg)
