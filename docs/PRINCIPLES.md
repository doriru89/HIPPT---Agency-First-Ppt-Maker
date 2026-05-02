# Agency-First Principles

These principles emerged from 12 build sessions. They define what makes this pipeline different from "ask AI to make slides."

## 1. Content First
Vision lock, context gathering, and audience interview BEFORE any design. The ghost deck must read as an essay before any pixel is placed.

## 2. Test with Real Examples
Every rule validated against actual deck output. No theoretical quality standards — if it doesn't produce measurably better decks, it's removed.

## 3. Prevent, Don't Just Capture
Process rules prevent mistakes at build time (F1-F10 prevention table). Errata records what slipped through despite prevention. Prevention > detection > correction.

## 4. One Bottleneck Per Round
TOC (Theory of Constraints) convergence: fix ONE weakest dimension per iteration. Multiple simultaneous fixes prevent causal attribution and cause oscillation.

## 5. DOM Feeds Semantic
Playwright positions + native editability = best of both engines. DOM extraction for WHERE, semantic understanding for WHAT.

## 6. Evidence Proves, Not Decorates
Images must contain data that proves assertions. A homepage screenshot shows a site exists; a metric chart proves market size. Decorative evidence wastes slide real estate.

## 7. Screenshot Before Score
Never score from metadata alone (E-PRES-017). Always render at 960x540 via Playwright and VIEW the actual output before assigning Q1-Q10 scores.

## 8. Ghost Deck Reads as Essay
Assertive titles alone tell the complete story. If you read only the slide titles in order, the narrative arc should be clear without any body text.

## 9. So-What Gate
Every slide answers "so what?" with a position, not a label. "Market Overview" fails. "The healthcare transparency market will reach $4.2B by 2028" passes.

## 10. Fixed 960x540
No clamp(), no vw/vh. Match PPTX 96 DPI native. This single decision eliminates an entire category of coordinate-system bugs.
