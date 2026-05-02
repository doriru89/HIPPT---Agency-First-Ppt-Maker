# BCG Design DNA Benchmark — 2026-05-01

## Test Setup
- **Reference:** `WORK/PROJECTS/design-system/references/pptx/bcg-template.pptx` (65 slides)
- **Tokens:** `OUTPUT/design/ref-bcg-template.yaml` — green (#177B57), orange (#DC6E00), blue-gray (#79A2B3), Arial only
- **HTML source:** `OUTPUT/html/benchmark-bcg-test-2026-05-01.html` (4 slides, 960×540)
- **Content:** New AI infrastructure market assessment (not CareCost)

## Slides Tested
| # | Type | Content |
|---|------|---------|
| S1 | Title | Green hero block + 4 numbered key dimensions |
| S2 | Data-dense | 4 stat cards + data table with orange highlights |
| S3 | Comparison | Before/after: centralized training vs distributed inference |
| S4 | Framework | 3 imperative cards (green/orange/blue-gray) + bottom bar |

## Engine Results

### slides_to_pptx.py (semantic engine)
- **Output:** `/tmp/benchmark/bcg-semantic-export.pptx`
- **Canvas fill:** 93.97% avg (89%-96% per slide) — exceeds 80% gate
- **Font range:** 8-32pt, median 11pt
- **Element types:** 23 auto_shapes + 30 text_boxes + 1 table — **100% native, 0% rasterized**
- **Round-trip:** 4 slides verified
- **S3 comparison handler:** rendered as left/right bullet lists (7 shapes) — simpler than HTML's individual positioned items but preserves all content

### html_to_pptx.py (DOM extraction engine)
- **Output:** `/tmp/benchmark/bcg-dom-export.pptx`
- **Canvas fill warnings:** S1: 19%, S2: 39%, S4: 30% (measures bounding boxes, not visual fill)
- **Elements:** 71 total (15+13+29+17) — more granular than semantic (54 shapes)
- **Round-trip:** 4 slides verified

### Key Difference
Semantic engine understands element TYPES (stat_card renders value+label, table renders with headers, card renders with border accent). DOM extraction measures element POSITIONS (bounding boxes) but doesn't understand what they are — reports canvas fill as low even when the HTML fills 85%+ visually.

## Pending: Google Slides Visual Comparison
**Blocked by:** Chrome profile session locks Playwright MCP.
**Action needed:** Close Chrome → upload both PPTXs to Google Drive (My Drive) → screenshot in Google Slides → compare vs HTML screenshots.

### HTML Screenshots (ground truth)
- `/tmp/benchmark/bcg-s1-v2.png` through `bcg-s4-v2.png`

### PPTXs to compare
- `/tmp/benchmark/bcg-semantic-export.pptx` (semantic engine)
- `/tmp/benchmark/bcg-dom-export.pptx` (DOM extraction)

## Q1-Q9 Pre-Score (HTML, before formal scoring)
| Q | Dimension | Estimate | Notes |
|---|-----------|----------|-------|
| Q1 | Structure & Narrative | 8 | Assertion titles, clear 4-slide arc, no exec summary |
| Q2 | Canvas Utilization | 7 | S1/S2/S4 good (85%+), S3 has 15% empty bottom |
| Q3 | Typography | 8 | Clear 3-level hierarchy (32/24/13pt), consistent Arial |
| Q4 | Color & Harmony | 9 | All colors from BCG palette, WCAG AA, ≤5 hues |
| Q5 | Data Presentation | 8 | Clean table, direct-labeled stat cards, sourced |
| Q6 | Editability | N/A | Scored on PPTX, not HTML |
| Q7 | Professional Polish | 7 | Good alignment, S3 gap deducts, spacing consistent |
| Q8 | Visual Evidence | 6 | No images (data/text only deck — template baseline) |
| Q9 | Vision Adherence | 8 | All slides serve AI infrastructure assessment vision |
| **Total (Q1-Q5,Q7-Q9)** | | **61/80** | **76%** (Q6 deferred, Q10 deferred) |

First pass falls below 85% target — Q2 (canvas fill S3) and Q8 (no visual evidence) are the main gaps.
