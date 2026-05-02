# Presentation Design Errata

## Prevention Mapping (F-table → Errata)

| F | Failure Mode | Primary Errata | Related |
|---|-------------|----------------|---------|
| F1 | Content-sized elements | E-PRES-006 | E-PRES-003 |
| F2 | Web-sized text | E-PRES-001 | — |
| F3 | Arbitrary spacing | E-PRES-016 | — |
| F4 | Rectangles for diagrams | E-PRES-039 | — |
| F5 | Gray placeholder blocks | E-PRES-040 | — |
| F6 | Mixed letter-spacing | E-PRES-041 | E-PRES-013 |
| F7 | Image reuse | E-PRES-033 | — |
| F8 | Decorative evidence | E-PRES-032 | E-PRES-020 |
| F9 | Missing so-what | E-PRES-048 | Ghost deck |
| F10 | Inconsistent line-heights | E-PRES-013 | — |

## E-PRES-001: Text-to-canvas ratio too low
**Pattern:** AI generates text at web-appropriate sizes (0.85rem body, 1.2rem titles) but presentations are viewed at distance. Text appears tiny relative to full-viewport slides.
**Fix:** titles ≥ 48px (keynote) / ≥ 16px (dense), body ≥ 18px (keynote) / ≥ 11px (dense), labels ≥ 14px / ≥ 9px, source ≥ 10px / ≥ 8px
**Source:** 2026-04-23 Artopath v1 review

## E-PRES-002: Green-on-green unreadable
**Pattern:** Monospace code/skill text using `var(--glow)` (#5d8a6b) on dark green background (#0f1f14) has insufficient contrast ratio (~2.5:1, needs 4.5:1).
**Fix:** Use `#a8d4b8` (light mint) for code text on dark green. Or use gold/cream for emphasis.
**Source:** 2026-04-23 slide 12 expert-review text

## E-PRES-003: Empty space = missing support
**Pattern:** Slides have large unused areas because content lacks supporting evidence (pictures, data, diagrams). Every assertion needs visual proof.
**Rule:** Each slide must pass the "3-support check": Is every statement supported by either words, pictures, or data? Can someone understand the slide without narration?
**Source:** 2026-04-23 slides 12, 9 review

## E-PRES-004: CSS position override in slide classes
**Pattern:** Individual slide classes (`.s-stat`, `.s-synthesis`) used `position: relative` which overrode `.slide`'s `position: fixed`, making slides invisible.
**Fix:** Never put `position: relative` on slide-level classes. Use `!important` on `.slide { position: fixed !important; }`. Add child wrappers for relative positioning context.
**Source:** 2026-04-23 slides 6-8 invisible bug

## E-PRES-005: Platform cards stacking
**Pattern:** Absolutely-positioned elements using `translate()` percentages stack on top of each other because translate % is relative to element size, not parent.
**Fix:** Use `top/left/right/bottom` percentages for positioning within parent container, not `translate()`.
**Source:** 2026-04-23 slide 2 platform cards overlapping

## E-PRES-006: Content-sized vs canvas-sized (ROOT CAUSE)
**Pattern:** AI generates elements sized to their text content, then floats them in empty space. Cards are 160-220px on a 1920px viewport = 8-11% coverage. Professional templates fill 80%+ of the canvas. The result looks like Post-it notes on a whiteboard.
**Root cause:** AI defaults to `width: auto` (shrink-to-content) instead of `width: 100%` (fill-the-frame). This is the most common AI presentation failure mode and the root of E-PRES-001 and E-PRES-003.
**Fix — Design Process Gate:** Add a "Canvas Fill Audit" step to the presentation pipeline between Build and Critique:
  1. For each slide, measure: what % of viewport width and height is occupied by content?
  2. **Detail slides** (content, storyboard, before-after): content must fill ≥ 80% of viewport area (per pptx-quality.yaml Q2 scoring bands)
  3. **Breathing slides** (title, section-break, quote): empty space must be INTENTIONAL — centered, symmetric, atmospheric
  4. **No accidental margins** — if padding > 8% on any side, it must serve a purpose (image bleed, asymmetric layout)
  5. Cards/elements should be sized relative to viewport (vw/vh), not content (auto/fit-content)
**Prompt to add to /presentation SKILL.md:**
  "Before finalizing each slide, check: would a designer look at this and say 'why is there so much empty space?' If yes, either fill it with supporting content (image, data, diagram) or make the emptiness intentional (center content, add atmospheric gradient, increase element size to 80%+ of canvas)."
**Source:** 2026-04-23 systematic review — slides 2, 3, 6, 9, 12 all had unintentional empty space

## E-PRES-007: Reference PPTX analysis ~~pending~~ RESOLVED
**Pattern:** Three reference PPTXs (`mid-model.pptx`, `agency.pptx`, `produce-review.pptx`) were provided as gold-standard examples but never analyzed for space utilization patterns.
**Resolution:** Analyzed via `hippt-analyze` on 2026-04-23. Key findings: 91% avg canvas fill across 107 slides, body text 8-14pt, display type up to 499pt, minimal padding (1-4%). Results populated into `config/philosophies/editorial.yaml` → `learned_patterns` (4 entries: 3 per-file + 1 aggregate).
**Files:** Your reference PPTX files in `input/`
**Source:** 2026-04-23 Austin feedback → resolved 2026-04-23 S3

## E-PRES-008: Content swap doesn't fix geometry
**Pattern:** Replacing text content with richer content (screenshots, images, diagrams) makes undersized containers WORSE, not better. A 300px-wide screenshot of a full web page is an unreadable thumbnail. Rich content needs MORE space to be legible — the opposite of intuition.
**Root cause:** The instinct to "make it look real" by swapping in images skips the prerequisite: the container must be large enough for the new content type. This is a corollary of E-PRES-006 (content-sized vs canvas-sized).
**Fix:** Always fix container geometry (width, height, flex ratios) BEFORE swapping content type. Minimum container widths by content type:
  - Screenshots/web captures: ≥ 400px
  - Icons/logos: ≥ 200px
  - Embedded charts/diagrams: ≥ 600px
  - Text-only cards: ≥ 160px (current default, often too small)
**Source:** 2026-04-23 S3 design-lead review of Slide 2 platform cards

## E-PRES-009: Uniform sizing = order, varied sizing = chaos
**Pattern:** AI defaults to uniform card sizes (all items same `width: clamp(X, Y, Z)`). But visual hierarchy requires intentional sizing variation that maps to narrative intent. Uniform sizing communicates order, comparison, equality. Varied sizing communicates chaos, hierarchy, fragmentation.
**Fix:** Before generating a card layout, ask: does this slide communicate order or chaos?
  - **Order** (comparison, features, timeline): uniform sizing, aligned grid, equal gaps
  - **Chaos** (overload, fragmentation, before-state): 2-3 size tiers, z-index depth layering, shadow depth differentials (light shadows = back layer, heavy shadows = front layer), overlapping positions
  - **Hierarchy** (primary vs secondary): primary item 40-60% wider than secondary items
**Source:** 2026-04-23 S3 design-lead review — overlapping cascade technique for Slide 2

## E-PRES-010: Decorative panels waste canvas on content slides
**Pattern:** AI adds decorative accent panels (gradient fills, radial glows) as flex siblings on content slides. These occupy 30-45% of viewport width but carry zero information. Example: `.stat-accent { flex: 0.45; background: var(--forest); }` — a solid green rectangle taking 45% of S6.
**Fix:** Decorative panels are only acceptable on breathing slides (title, section-break, quote). On content slides, replace with: (a) a real product screenshot or photo, (b) a supporting diagram, or (c) remove and give the content side full width. Every pixel should either inform or intentionally breathe.
**Source:** 2026-04-23 S3 Austin feedback — S6 "just empty green, might as well be art"

## E-PRES-011: Milestone/challenge cards lack detail density
**Pattern:** AI generates cards with only 1 line of impact text. Professional deck cards have 3 rows: what was done, how it was measured, what it proved. Single-line cards look unfinished and waste vertical space inside the card frame.
**Fix:** Each milestone/challenge card should have a minimum of 3 content rows:
  - Row 1: What was done (the deliverable)
  - Row 2: How it was measured (the metric or test)
  - Row 3: What it proved (the outcome or learning)
  If genuinely nothing to show for a row, collapse to 1 row minimum. Never 2 rows — either sparse (1) or detailed (3).
**Source:** 2026-04-23 S3 Austin feedback — "milestone text tiny, no details on what we did"

## E-PRES-012: Green-on-dark-green in card detail text
**Pattern:** Card detail/fix text using `var(--glow)` (#5d8a6b) is unreadable on dark cards. This is E-PRES-002 recurring in a different context — challenge card `.ch-fix` and milestone `.ms-chain` use glow color which fails contrast on dark green backgrounds.
**Fix:** All text on dark backgrounds must use `#a8d4b8` (light mint), `var(--cream)`, or `var(--gold)`. Never `var(--glow)` for text. Apply this to `.ch-fix`, `.ms-chain`, `.ms-impact`, and any card detail/mono text.
**Source:** 2026-04-23 S3 Austin feedback — "green font for docker hard to read"

## E-PRES-013: Typographic rhythm inconsistency
**Pattern:** AI mixes line-height ratios across slides (1.2, 1.5, 1.8) within the same deck. Subliminal discomfort — each slide "feels" different even with same fonts/colors.
**Fix:** One line-height per text role deck-wide. Body: 1.5, headings: 1.2, captions: 1.4. Validate at build time — grep all line-height values, flag if >1 unique value per role.
**Source:** 2026-04-27 creative-director gap analysis

## E-PRES-014: Rogue color introduction
**Pattern:** AI introduces "helpful" colors (blue for links, green for success, red for errors) that weren't in the extracted design tokens. Each rogue hue breaks palette coherence.
**Fix:** No more than 5 distinct hues per deck (excluding photographs). Every hue must trace to the extracted token palette. Any color not in `ref-<slug>.yaml` palette is a violation. Validate: extract all hex colors from CSS, diff against token palette.
**Source:** 2026-04-27 creative-director gap analysis

## E-PRES-015: Visual weight imbalance across slides
**Pattern:** Content "center of mass" jumps randomly — slide 3 left-heavy, slide 4 right-heavy, slide 5 centered. Creates visual seasickness in rapid presentation.
**Fix:** Measure weighted average of element positions per slide. Sequential slides should either maintain consistent weight distribution OR shift intentionally (left→center→right = cinematic pan). Random jumps are bugs.
**Source:** 2026-04-27 creative-director gap analysis

## E-PRES-016: Spacing inconsistency between slides
**Pattern:** Section gaps are 48px on slide 3 but 32px on slide 7. Padding varies per slide despite same layout type. Each inconsistency signals "assembled, not designed."
**Fix:** Extract spacing token from first content slide, enforce deck-wide. If `spacing.rhythm` is 8px, all gaps must be multiples of 8px. Validate: grep margin/padding values, flag non-multiples of rhythm base.
**Source:** 2026-04-27 creative-director gap analysis

## E-PRES-020: Visual reasoning layer before build
**Pattern:** AI builds HTML slides immediately after ghost deck (text structure), selecting images reactively during build. This produces generic image placement — wrong images, wrong sizes, wrong context. The AI doesn't reason about what image BEST proves each slide's assertion.
**Fix:** Add a **Visual Plan** step between Ghost Deck and Build. For each slide:
1. **Context review** — read the whole deck's narrative arc. What is this slide's role in the story?
2. **Image reasoning** — what visual BEST proves this assertion? Candidates from:
   - Project files or web search (e.g., relevant product screenshots, data visualizations)
   - Product screenshots (Playwright captures from `.playwright-mcp/`)
   - Online sources (platform screenshots, reference images)
   - Data outputs (Python-generated charts, research paper figures)
   - Animations/diagrams (SVG, CSS animation)
3. **Space allocation** — how much slide space should the image occupy? (50%? 70%? full-bleed?)
4. **Human gate** — present the visual plan (image descriptions + space allocation + candidate ideas) BEFORE building. Grid layout should be shown at this stage.
5. **Coherence check** — does the image tell the same story as the text? "Cultural knowledge scatters" → show DNA graph (unified) not random stock photo.
**Example failure:** Slide 1 used Artopath hero page (generic) instead of DNA graph (which visually PROVES unification). IMDb card had no visual showing WHY "no cultural lineage" is a problem — a screenshot of IMDb's cast-only page would demonstrate the gap.
**Severity:** quality-defining — image selection is 50%+ of slide impact
**Source:** 2026-04-28 convergence R3-R4 — Austin's feedback on image reasoning

## E-PRES-021: Data output reasoning step
**Pattern:** AI doesn't consider whether a slide needs a generated data visualization (chart, graph, metric). Consulting slides often need Python-generated charts from research data, course assignments, or project metrics.
**Fix:** During the Visual Plan step (E-PRES-020), explicitly ask: "Does this slide need a data output?" If yes:
1. What data source? (research paper, project metrics, course assignment output)
2. What chart type? (bar, line, scatter, table, metric callout)
3. Generate via Python (matplotlib, plotly) or inline SVG
4. Store in `output/assets/<slug>/`
**Source:** 2026-04-28 — Austin referenced HW3 AI for Business Decisions as example of data-driven slides

## E-PRES-017: Screenshot-before-score hard gate
**Pattern:** AI scores presentation quality (Q1-Q7) from structural data (JSON metadata, token YAML, bounding-box metrics) without viewing actual rendered output. Structural metrics undercount organic shapes (Agency Q2: 69% structural vs ~85% visual), miss alignment issues, and cannot assess gestalt polish.
**Fix:** HARD GATE — any step that compares, scores, or enhances PPT/HTML layout MUST:
1. Render screenshots first (PPTX→LibreOffice→PDF→PNG, or HTML→Playwright)
2. Store screenshots in a persistent, named directory (e.g., `/tmp/pptx-calibration/{slug}/` or `output/screenshots/{slug}/`)
3. View the screenshots before scoring (Read tool for AI, `open <folder>` for human review)
4. FAIL LOUDLY if screenshots don't exist — never proceed with scoring from metadata alone
5. Show Austin the folder (`open <path>`) so he can grade visually alongside AI scores
**Severity:** blocking — no score without screenshot
**Source:** 2026-04-28 calibration round — Agency Q2 was 1 point off, structural-only Mid Model Q7 was 1 point off

## E-PRES-019: Font-substituted screenshots mask real flaws
**Pattern:** When PPTX files have embedded/custom fonts and are rendered via LibreOffice with font stripping (E-PRES-018 workaround), the substituted fonts have different metrics (width, kerning, line-height). Text that OVERLAPS or CLIPS in the real PPTX may render cleanly with substituted fonts, producing false-positive "looks good" scores. Mid Model scored Q7:9 from stripped screenshots but Q7:4 from Austin viewing in Keynote — a 5-point gap caused by font substitution masking text overlap.
**Fix:** For calibration scoring, ALWAYS verify against native rendering (Keynote/PowerPoint), not just LibreOffice screenshots. AI screenshots are necessary (E-PRES-017) but not sufficient — human review in native app is the ground truth. When scoring from stripped-font screenshots, add caveat: "font metrics may differ from native rendering."
**Severity:** scoring-invalidating — can produce 5-point errors on Q7
**Source:** 2026-04-28 calibration round — Mid Model Q7 gap (AI:9 vs human:4)

## E-PRES-018: Embedded fonts crash LibreOffice
**Pattern:** PPTX files with embedded fonts (in `ppt/fonts/*.fntdata`) cause LibreOffice headless to crash with `Signal 6` in `EmbeddedFontsManager::addEmbeddedFont`. Stale LibreOffice processes from earlier crashes block subsequent conversions.
**Fix:** Before LibreOffice conversion:
1. Kill stale processes: `pkill -9 soffice`
2. Strip embedded fonts: unzip PPTX, `rm -rf ppt/fonts/`, remove `<p:embeddedFontLst>` from `ppt/presentation.xml`, remove fntdata entries from `[Content_Types].xml`, re-zip
3. Convert the stripped copy: `soffice --headless --norestore --convert-to pdf <stripped.pptx>`
4. Then: `pdftoppm -png -r 150 <output.pdf> <slide-prefix>`
**Source:** 2026-04-28 calibration round — all 3 non-BCG PPTXs crashed

## E-PPTX-001: Hex color format mismatch
**Pattern:** python-pptx `RGBColor` expects 3 integers (0-255), not hex strings. PptxGenJS uses hex strings without '#'. Mixing conventions causes silent color corruption — wrong colors render without errors.
**Fix:** Always construct colors via `RGBColor(0xRR, 0xGG, 0xBB)`. Never pass hex strings. When reading from token YAML, parse: `int(hex_str[1:3], 16)` etc. Validate: grep for `RGBColor("` — any string argument is a bug.
**Source:** 2026-04-27 CTO gap analysis + build_pitch_v6.py pattern

## E-PPTX-002: EMU math precision errors
**Pattern:** python-pptx uses EMU (English Metric Units, 914400 per inch) internally. Mixing `Inches()`, `Pt()`, and raw EMU values causes cumulative positioning drift — elements misaligned by 1-3px after multiple calculations.
**Fix:** Choose one unit system per script. Prefer `Inches()` for positions/sizes, `Pt()` for font sizes. Never do arithmetic on EMU values directly. Use helper functions that encapsulate conversion.
**Source:** 2026-04-27 CTO gap analysis

## E-PPTX-003: Font embedding and fallback
**Pattern:** PPTX files reference fonts by name. If the font isn't installed on the viewing machine, PowerPoint silently substitutes — layout shifts, character widths change, text overflows boxes.
**Fix:** Maintain a font fallback mapping table. Before export, check each font family against system fonts. Map non-system fonts to safe alternatives with adjusted letter-spacing. Log substitutions. Recommended safe fonts: Calibri, Arial, Segoe UI, Georgia, Consolas.
**Source:** 2026-04-27 creative-director gap analysis

## E-PPTX-004: Gradient and border-radius degradation
**Pattern:** CSS `border-radius` has no PPTX equivalent (ROUNDED_RECTANGLE is the closest, but with fixed corner radius). CSS gradients with >2 stops or radial/conic types have no python-pptx support. Silent degradation produces flat fills where gradients were expected.
**Fix:** Classify each CSS effect during HTML build as "PPTX-safe" or "rasterize-fallback". Safe: solid fills, linear 2-stop gradients, drop shadows. Rasterize: border-radius on non-rectangles, radial gradients, backdrop-filter, clip-path. For rasterize cases, render element to PNG at 2x resolution and insert as image.
**Source:** 2026-04-27 creative-director gap analysis + feedback_slide_export_workflow.md

## E-PRES-026: Image readability gate
**Pattern:** Evidence images rendered as thumbnail strips (≤130px) are unreadable at presentation distance. They fill space but prove nothing — decoration masquerading as evidence.
**Fix:** All evidence images must be ≥200px rendered height. Use 2-column `evidence-proof` grid layout (not 4-thumb strips). Position each image directly under the claim it supports. Test: can you read the key headline in the image at 1080p?
**Severity:** content-invalidating — images that can't be read don't count as evidence
**Source:** 2026-04-29 R3 convergence — S7/S10 thumbnail strips redesigned to proof panels

## E-PRES-027: space-between on slides with fewer than 3 grid rows
**Pattern:** `justify-content: space-between` on `.slide-body` distributes content sections evenly. Works well for slides with 3+ sections (title, content, footer). On slides with only 2 content rows (e.g., S2), it creates a massive gap in the middle — worse than the empty space it was meant to fix.
**Fix:** Apply `.fill` class (which adds `justify-content: space-between`) per-slide, not globally. Only use on slides with ≥3 content sections. For 2-section slides, use default `flex-start` or add padding.
**Severity:** layout-breaking on affected slides
**Source:** 2026-04-29 R3 convergence — S2 gap bug

## E-PRES-028: Sidecar JSON staleness after convergence rounds
**Pattern:** HTML convergence rounds (R1→R2→R3) modify content, add images, change layouts — but the sidecar JSON is only generated once at initial build. After 3+ rounds, the JSON diverges significantly: missing images, wrong text, outdated element types. PPTX export from stale JSON produces a deck that doesn't match the approved HTML.
**Fix:** Add Step 4.7 (Sidecar JSON Sync) to the pipeline. After convergence ≥80, re-extract all slide content from HTML into JSON before any PPTX export. Treat JSON staleness as a blocking issue.
**Severity:** export-invalidating — stale JSON = wrong PPTX
**Source:** 2026-04-29 R3→R4 transition — JSON had R2 content while HTML was at R3

## E-PRES-029: Font role names vs family names in sidecar JSON
**Pattern:** Sidecar JSON uses semantic role names ("display", "body", "label") for fonts. The PPTX engine needs actual font family names ("Playfair Display", "Source Serif 4", "Inter"). The `TokenResolver.resolve_font()` maps roles→families only if a tokens YAML is provided. Without tokens, everything falls back to Calibri — losing the typographic hierarchy.
**Fix:** Always provide `--tokens` flag when running `slides_to_pptx.py`. If no tokens YAML exists, create a minimal one mapping at least display/body/label to safe font families. Validate: grep for `Calibri` in PPTX text — if >50% of text uses Calibri, the resolver likely failed.
**Severity:** typography-degrading — all text becomes Calibri
**Source:** 2026-04-29 PPTX fidelity audit

## E-PRES-030: Image audit before build — verify what you captured
**Pattern:** AI captures screenshots via Playwright and assigns them to slides based on filename/URL — without viewing the actual image content. Failed captures (cookie walls, paywalls, redirect pages, generic homepages) get embedded as "evidence" and nobody notices until human review. In S5 session: `cnn-verdict.png` was a cookie consent popup, `ln-earnings-home.png` was a generic PR page (not earnings), `get-protocol-hero.png` was a redirect page with only a logo.
**Fix:** Add Step 3.9 (Image Audit) to pipeline. After capturing images, the AI must VIEW each image and verify:
1. Does the image show the claimed content? (not a paywall/redirect/generic page)
2. Can you read the key headline at 1080p? (readability gate)
3. Does the image prove the specific assertion on the slide? (coherence)
4. Is the source credible for this claim? (not just any page from the domain)
Failed images must be re-captured or replaced before build. Base64 conversion happens after audit passes.
**Severity:** content-invalidating — wrong images undermine the entire evidence chain
**Source:** 2026-04-29 S5 — 3 of 7 unused images were failed captures or wrong content

## AP11: Thumbnail strips as "evidence"
**Pattern:** Placing 4+ tiny screenshots in a horizontal strip to "show evidence." At 130px height, text is illegible. The images fill canvas space (solving AP9) but prove nothing — they're decoration, not evidence.
**Fix:** Use 2-column `evidence-proof` layout at ≥200px height. Each image sits under the specific claim it supports. Fewer, larger, readable images > many tiny unreadable ones.
**Source:** 2026-04-29 R3 — image readability gate formalized

### E-PRES-031 — Breathing slide exemption must be earned
**Pattern:** AI labels a content-rich slide as "breathing/vision" to avoid flagging low canvas fill. Result: empty space goes unfixed.
**Rule:** Only title slides (S1, S12) and intentional section dividers qualify as "breathing." Any slide with data elements (numbers, charts, market sizes, comparison tables) is a detail slide — Q2 ≥80% fill required. No judgment calls.
**Root cause:** Convergence pass optimized for speed over rigor; applied Q2 leniently.

### E-PRES-032 — Evidence images must prove, not decorate
**Pattern:** Screenshot of a website homepage used as "evidence" for a slide assertion. The image shows the site exists but doesn't prove the claim. Example: NBA Top Shot homepage screenshot on a slide about digital collectibles — the homepage doesn't show $1B revenue or 20M users.
**Rule:** Evidence images must contain the DATA that proves the assertion — a chart, a headline with the number, a report excerpt. If the image can be replaced by a logo + metric without information loss, use the logo + metric instead. Article screenshots are acceptable only if the headline IS the evidence.
**Root cause:** Image selection was keyword-matched (slide mentions X → screenshot X's website) instead of assertion-matched (slide claims Y → find image that shows Y).

### E-PRES-033 — No image reuse across slides
**Pattern:** Same base64 image embedded in multiple slides. Reduces impact, signals lazy evidence, and wastes viewport space that could carry new information.
**Rule:** Each evidence image may appear on exactly one slide. If two slides need to reference the same source, the second slide uses a different format: logo + key metric, pull quote with source attribution, or a different screenshot from the same source showing different data.
**Root cause:** Image assignment was source-driven (this image is from X, X is mentioned here too) instead of claim-driven (what specific claim does this slide make, and what image proves THAT claim?).

### E-PRES-034 — Base64 embedding is the final step, after PPTX export
**Pattern:** Images converted to base64 data URIs during or before convergence. Result: 7MB HTML file, slow edits, slow browser reloads, painful iteration.
**Rule:** During design iteration, reference images by file path (`/images/smart-tickets/foo.png`). Convert to base64 only as the very last step after PPTX is generated and all iteration is complete. The base64 version is for sharing/archival only.
**Root cause:** Base64 was applied early to make the file "self-contained" for review, but review happens locally where file paths work fine.

### E-PRES-035 — PPTX review in native renderer, not PDF conversion
**Pattern:** AI generates PPTX, converts to PDF via LibreOffice, reviews PDF screenshots, declares success. LibreOffice rendering differs from PowerPoint/Keynote — font substitution, layout shifts, spacing errors are invisible in the PDF.
**Rule:** Review PPTX in PowerPoint, Keynote, or LibreOffice Impress. Never declare PPTX done without visual inspection in a native renderer. Never review via PDF.
**Pipeline:** Generate PPTX → open in PowerPoint/Keynote/LibreOffice Impress → screenshot each slide → compare vs HTML → fix handlers → repeat until delta is acceptable.

### E-PRES-036 — Render at slide-native DPI to avoid coordinate system split
**Pattern:** HTML→PPTX conversion renders at 1920×1080 but a 10"×5.625" PPTX at 96 DPI is only 960×540 pixels. This creates a 2x mismatch: positions scale at 0.5x (1920→960) but CSS font px→pt (×0.75) stays at 1x. Result: fonts are 2x too large for their boxes and overflow into neighbors.
**Root cause:** Rendering at 2x the slide's native DPI. A 78px title at 1920px maps to a 2.625" box (78/1920×10), but 78px×0.75=58.5pt needs 0.81" height — double the 0.43" box.
**Fix:** Render HTML at 960×540 (matching the slide's 96 DPI native resolution). Then 1 CSS px = 1/96" exactly matches PPTX coordinates. `font_px × 0.75` gives correct pt sizes. CSS `clamp()` naturally produces PPTX-appropriate sizes (Title ~40pt, Body ~11pt, Caption ~8pt). Using 0.375 as a font scale (the proportional approach) preserves layout but makes text unreadably small.
**Applies to:** Any system that maps browser pixels to PPTX coordinates. The layout library stores positions in percentages (safe). The viewport resolution must match the slide's physical DPI.
**Severity:** layout-breaking — text either overflows (at 1920) or is unreadable (at 0.375 scale)
**Source:** 2026-04-29 html_to_pptx.py. Took 6 iterations (r7→r13) to find the correct approach.

### E-PRES-037 — Prefer leaf elements over parent containers in DOM extraction
**Pattern:** DOM walker extracts both a parent container (e.g., `.newspaper` div, h=318px with all child text) AND its child elements (heading at h=36px, body text at h=80px). Both get text boxes at the same x,y position — the parent's text box contains ALL the text, overlapping with the child's text box that contains a SUBSET. Dense layouts (newspaper, multi-column) produce 2x duplicate text boxes.
**Rule:** When walking the DOM, skip elements that have extractable children. Only extract leaf elements (no children) or elements with direct text but no extractable child elements. Tables and images are always extracted regardless.
**Severity:** layout-breaking on dense slides (slide 4 had 33 elements, many duplicates)
**Source:** 2026-04-29 slide 4 newspaper layout overlap diagnosis

### E-PRES-038 — object-position requires height constraint on img, not parent overflow
**Pattern:** Evidence panel uses `overflow: hidden` + `max-height` on the parent container and `object-fit: cover` + `object-position` on the `<img>`. The intent is to show a specific crop region of a tall screenshot. But `object-position` has no effect — the image always shows from the top.
**Root cause:** Without `height: 100%` on the `<img>`, the element expands to its cover-scaled natural height (e.g., 971px) inside the 171px parent. The parent's `overflow: hidden` clips the excess, but `object-fit: cover` + `object-position` operate relative to the img element's OWN content box. Since the 1920×1080 image scales to exactly 1726×971 to cover the 1726×971 img box, there is zero excess — `object-position` is a no-op. The visible top is always the image top.
**Fix:** Add `height: 100%` to the `<img>` rule. This constrains the img element to the parent's height (171px). Now `object-fit: cover` scales the 1920×1080 image to cover 1726×171, creating 800px of vertical excess. `object-position: 0 35%` then correctly hides 280px above the visible window, showing the article headline area instead of the navigation bar.
**Key insight:** `object-fit`/`object-position` position the image content within the img element's box. If the img box matches the image aspect ratio, there's no excess to position. The clipping must happen via `object-fit`, not via parent `overflow: hidden`.
**Severity:** quality-defining — evidence images show website navbars instead of article headlines, undermining Q8 (Visual Evidence) score
**Source:** 2026-04-30 Smart Tickets R4 convergence testing, S2 NPR evidence panel

### E-PPTX-005 — Proportional text padding destroys grid alignment
**Pattern:** Text boxes in PPTX get `w_pad = raw_w * 0.12` padding + left-shift by `w_pad/2`. A 325px heading shifts 19.5px left, while a 223px stat card shifts 13.4px left, while an 80px label shifts 4.8px. Three elements that should be left-aligned in HTML land at three different x positions in PPTX.
**Root cause:** Proportional padding (percentage of width) is asymmetric across elements of different widths. The left-shift (`raw_left -= w_pad/2`) compounds the problem by breaking grid lines.
**Fix:** Replace proportional padding with fixed constant (`0.06in ≈ 6px`), applied ONLY to the right side. Never shift left position. HTML positions now match PPTX at sub-pixel precision.
**Prevention:** Any future padding in the coordinate pipeline must be FIXED (constant), never proportional. Add a test: `assert abs(pptx_x - html_x / 960 * 10) < 0.01` for position fidelity.
**Severity:** layout-breaking — every slide with mixed-width text elements had visible margin drift
**Source:** 2026-04-30 Phase 5.5 Google Slides verification

### E-PPTX-006 — CSS linear-gradient backgrounds lost in PPTX [FIXED]
**Pattern:** HTML slides using `background: linear-gradient(...)` get white/black backgrounds in PPTX. White text on gradient slides becomes invisible.
**Root cause (deeper than originally thought):** Playwright extraction captured `getComputedStyle().backgroundColor` (line 524) but NOT `backgroundImage`. CSS gradients live in `backgroundImage`, so `backgroundColor` returns `rgba(0,0,0,0)` → transparent → no background applied. The gradient string never reached `parse_css_color()` at all.
**Fix (3-layer):**
1. Extraction: capture `backgroundImage` alongside `backgroundColor` in Playwright JS (line 525)
2. Parser: `parse_css_gradient()` — parenthesis-aware split, CSS→PPTX angle conversion, 2-stop extraction
3. Builder: `_build_pptx` applies native `fill.gradient()` + `gradient_stops[i].color.rgb` via python-pptx API
4. Defense-in-depth: `parse_css_color()` still extracts first hex from gradient strings as solid fallback
**Prevention:** 7 tests in `TestParseCssGradient` — angle conversion, rgb stops, transparent exclusion, radial rejection, native API integration.
**Severity:** visual — title/close slides with gradients lose their background
**Source:** 2026-04-30 Phase 5.5 discovery, root-cause fixed 2026-04-30 Phase 6

### E-PRES-039 — Diagram shape infidelity
**Pattern:** AI simplifies shapes to what's easy in CSS — funnels become stacked rectangles, flowcharts lose connecting arrows, snowball diagrams miss the connecting curves. The resulting shapes don't match their real-world analogues, making diagrams look like wireframes instead of finished designs.
**Root cause:** CSS `div` elements default to rectangles. The AI takes the path of least resistance instead of using `clip-path`, inline SVG, or CSS `polygon()` to create proper shapes.
**Fix:** For non-rectangular shapes, use:
  - `clip-path: polygon(...)` for trapezoids, funnels, arrows, chevrons
  - Inline SVG for curves, connecting arrows, flow lines, circular relationships
  - CSS borders (`border-left: transparent`) for triangles as a last resort
  - Never use stacked rectangles for shapes that taper, curve, or connect
**Failure example:** Douyin P9 funnel (漏斗式) rendered as 3 equal-width rectangles instead of tapering trapezoids. Snowball (滚雪球式) circles had no connecting arrows showing the cyclical relationship.
**Severity:** quality-defining — diagrams are the slide's primary communication tool
**Source:** 2026-05-01 signature slide benchmark — 6 slides at 60% quality

### E-PRES-040 — Placeholder laziness
**Pattern:** When images aren't available (replication tests, early drafts), AI uses labeled gray blocks (`[Model Photo]`, `[Chart]`) as placeholders. These carry zero design information — they don't show composition, proportions, or visual weight. The result looks like a wireframe, not a design draft.
**Fix:** Use representative placeholders that preserve the SHAPE of the intended design:
  - Photography: dark gradient silhouette matching the image's compositional weight
  - Charts: simplified bar/line shapes with approximate proportions
  - Logos: rounded rectangle with brand color fill
  - Screenshots: light gray with subtle UI chrome lines (nav bar, sidebar hints)
  Never use a labeled text block as a placeholder.
**Failure example:** Douyin P12 FACT model had 3 gray blocks labeled `[Model 1/2/3]` — the slide's bottom half looked empty despite being designed for full-bleed photography.
**Severity:** visual — placeholders determine whether a draft "reads" as designed or unfinished
**Source:** 2026-05-01 signature slide benchmark

### E-PRES-041 — Inconsistent letter-spacing
**Pattern:** AI picks letter-spacing per-element — one header at `0.08em`, another at `0.25em`, body text with none. The Douyin reference deck uses ultra-wide letter-spacing as a deliberate design choice applied consistently to ALL headers. Per-element decisions break this consistency and create visual noise.
**Fix:** Define letter-spacing as design tokens (CSS custom properties) with 2-3 roles:
  - `--ls-display: 0.2em;` — hero/display text (wide, dramatic)
  - `--ls-label: 0.08em;` — labels, badges, uppercase text
  - `--ls-body: normal;` — body text, descriptions
  Apply these roles deck-wide. Every element uses a role, never a raw value.
**Extends:** E-PRES-013 (typographic rhythm) which covers line-height but not letter-spacing.
**Failure example:** Douyin P3 column headers had mixed spacing — "EMERGING CHANNEL" at 0.08em, "FOR COMMERCE" at 0.15em, "POTENTIAL CATEGORY" at 0.25em — destroying the uniform typographic grid.
**Severity:** quality — inconsistent letter-spacing is subliminal but noticeable, like a slightly crooked picture frame
**Source:** 2026-05-01 signature slide benchmark

## E-PRES-045: Convergence dead zone — iteration trigger too loose
**Pattern:** Step 5 convergence loop triggers re-scoring only when "any dimension <6" but the target is avg ≥8.5. A deck scoring all 7's (70% avg) passes without any iteration — a 15-point dead zone. Quality "converges" at a level far below the stated target.
**Root cause:** The exit condition was designed for a 60% baseline (where <6 catches real failures). When the target rose to 85%, the trigger wasn't updated.
**Fix:** Multi-condition trigger: iterate if (avg < YAML first_pass target OR any Q < 7 OR gate violation). One-bottleneck-per-round with oscillation detection. See SKILL.md Step 5 and `pptx-quality.yaml` convergence.iteration_trigger.
**Research:** Self-Refine (NeurIPS 2023), Theory of Constraints, IMPROVE (arXiv 2025). Sources: `output/research/convergence-architecture-2026-05-02/sources.yaml`
**Source:** 2026-05-02 convergence gap research session

## E-PRES-046: Self-scoring circularity — LLM judges own intent
**Pattern:** Proposed `data-intent` attribute had the LLM declare sizing intent ("order" vs "hierarchy") at build time, then check its own declaration at score time. The LLM never declares intent that contradicts its implementation — it's laundering a judgment call through an attribute. Expert 2 flagged this as circular self-evaluation.
**Fix:** Intent must come from an EARLIER pipeline stage (ghost deck content analysis) or from human input, never from the same inference pass that generates HTML. For E-PRES-009 sizing checks, derive intent from ghost deck: flat list/"compare" → uniform, "primary/secondary"/ranking → varied.
**Source:** 2026-05-02 Expert 2 (LLM Prompt Engineer) review

## E-PRES-042: Content floats instead of centering
**Pattern:** When a slide has limited content, it hugs the top-left and leaves large empty space in the middle/bottom. The content appears "floating" rather than anchored.
**Fix:** Use CSS Grid `align-content: center` on the content container so elements naturally center in the available space. Don't rely on `flex: 1` stretching — that enlarges items, but centering keeps them naturally sized and visually balanced.
**Failure example:** BCG10 chart+analysis had bars aligned to top-left and analysis text in top-right, leaving a white band across the middle.
**Source:** 2026-05-01 signature slide benchmark V2 review

## E-PRES-043: Text sized for web, not presentation distance
**Pattern:** Description text at 9px on a 960×540 viewport (≈18px at 1920×1080) is technically readable but feels cramped when the slide has white space that could be used. Layout is good but text doesn't expand to fill available area.
**Fix:** When the layout has unused white space and text is at minimum sizes, increase text to fill — larger fonts improve readability and canvas utilization simultaneously. Body text should be ≥11px at 960×540 (≈22px at full HD).
**Source:** 2026-05-01 signature slide benchmark V2 review

## E-PRES-047: Procedure says 1920×1080 but SSOT says 960×540
**Pattern:** Step 5a in SKILL.md said "screenshot at 1920×1080" but E-PRES-036 CTO ruling established 960×540 as the authoritative rendering resolution. The LLM followed the procedure's explicit instruction over the principle, even when both were loaded in context. This is a shadow policy: the old procedure overrides the newer, correct ruling.
**Root cause:** Step 5a was written before E-PRES-036 was discovered. When the CTO ruling was added, Step 5a was never updated. The `docs/MEGAPLAN.md` had both the old and new values simultaneously — self-contradictory SSOT.
**Fix:** All Playwright screenshot steps in procedures MUST specify 960×540. Fixed in SKILL.md Step 5a and `docs/MEGAPLAN.md` Step 5a on 2026-05-02. Prevention: when a CTO ruling changes a parameter, grep ALL procedure steps for the old value and update them — don't just add the ruling as a principle.
**Source:** 2026-05-02 convergence validation session — LLM defaulted to 1920×1080 despite knowing the 960×540 rule

## E-PRES-048: Missing so-what on slide (F9)
**Pattern:** Slide title is a label ("Market Overview", "Our Team", "Technology") instead of an assertive claim. The audience can't extract the message without reading the body. This is the most basic ghost deck violation — every title must be a complete sentence that states a position.
**Fix:** At ghost deck stage (Step 2), validate: can you read ONLY the titles in sequence and understand the full argument? If any title is a noun phrase instead of a claim, rewrite it. "Market Overview" → "The healthcare transparency market will reach $1.2B by 2028."
**Source:** 2026-05-02 SSOT audit — F9 was the only F-table entry without an E-PRES code

## E-PRES-044: Source/footnote line doesn't span full width
**Pattern:** Footnotes/source citations rendered as short text in the bottom-left, leaving 2/3 of the bottom edge empty. Creates an asymmetric bottom margin.
**Fix:** Make footnotes span the full slide width (`left: pad; right: pad;`) as a single line. Use `|` separators to join multiple footnotes on one line rather than stacking with `<br>`.
**Source:** 2026-05-01 signature slide benchmark V2 review
