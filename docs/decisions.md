# Key Decisions — Presentation Pipeline

These 26 rules were learned across 12 build sessions (CareCost pitch, Smart Tickets deck, Steam XAI presentation). Each was discovered the hard way — violating any of them produces measurably worse output.

## Canvas & Layout

### D1: Canvas fill — content-sized vs canvas-sized
AI defaults to `width: auto`, producing elements at 8-11% of viewport. Presentations need 80%+ fill. Size elements to their ZONE, not their content (`width: 100%`, `min-height` on containers). This is the #1 failure mode (E-PRES-006).

### D2: White-space auto-scaling is mechanical
If text can zoom 2x without overflow, it's too small. Scale proportionally to fill grid cells. This is computed, not subjective.

### D3: space-between safe, stretch banned
CSS Grid `align-content: space-between` distributes gaps between rows (safe). `stretch` inflates items and breaks layout (AP9-banned).

### D4: Center content, don't float it
Use `align-content: center`, expand text to fill available space. Footnotes span full width. Content must not float top-left.

## Typography

### D5: One line-height per text role
No "editorial body" exceptions. The rubric requires strict per-role consistency — `body` at 1.5 everywhere, no 1.75 variant.

### D6: Accent colors need WCAG AA check
Vibrant accents (teal, gold) often fail 4.5:1 contrast ratio as small text on light backgrounds. Always darken globally.

## Coordinate System

### D7: 960x540 viewport law
Render HTML at 960x540 (not 1920x1080) so CSS px-to-pt conversion (0.75) matches PPTX coordinates at 96 DPI native. Rendering at higher resolution creates a 2x font overflow mismatch (E-PRES-036).

## Pipeline Process

### D8: Errata is a hard gate before HTML
Read `errata/presentation_design.md` BEFORE writing any HTML. Skipping errata = repeating known mistakes. Not optional.

### D9: HTML approval before PPTX
Iterate and approve HTML to 80/90 quality BEFORE any PPTX translation. Human gate is on HTML, not PPTX. PPTX is a one-shot export.

### D10: Content enrichment step before build
Ghost deck has structure but thin content. Step 3.7 fills assertions with sourced evidence — factual claims, real data, cited figures. Without enrichment, slides are hollow.

### D11: One bottleneck per convergence round
Fix ONE Q dimension per iteration → re-score ALL → check for regression. TOC (Theory of Constraints) pattern. Fixing multiple dimensions simultaneously prevents causal attribution and causes oscillation.

### D12: Convergence needs mechanical gates
AI labels content-rich slides as "breathing" to avoid flagging low canvas fill. Must use mechanical rules (Q2 < 7 → cap), not AI judgment.

### D13: Self-scoring circularity
LLM declaring intent then checking its own declaration is a laundered judgment call. Intent must come from an earlier stage (ghost deck) or human input, not from the same build pass.

## Evidence & Images

### D14: Evidence proves, not decorates
Website homepage screenshots show a site exists but don't prove the claim. Use data charts, key metrics, or headline excerpts that contain the specific data supporting the assertion.

### D15: No image reuse across slides
Same image on 2+ slides signals lazy evidence. Each slide needs unique visual proof. Second occurrence → metric card or pull quote.

### D16: Image audit: VIEW every capture
After Playwright capture, VIEW each image (E-PRES-030). Failed captures (paywalls, redirects, generic pages) are content-invalidating. Don't assign images to slides without verifying they show what you think.

### D17: Image readability gate
Images in presentations must be large enough to read key text at projector distance. Thumbnails are decorative, not evidentiary.

## Content Quality

### D18: So-what gate for ghost decks
Every slide must answer "so what?" with a position, not just state facts. Process-level requirement in Step 2, not a per-deck fix.

### D19: SCAC 6-gate content audit
Before build AND during convergence: Goal, Self-Sufficiency, Data Grounding, Evidence, Specificity, Depth. Any SHALLOW slide blocks proceeding.

### D20: Visual plan must be HTML not markdown
Step 3.5 visual plans must be rendered HTML with swatches/wireframes. Users can't evaluate spatial layout from text tables.

### D21: Constrain structure, free aesthetics
Tight structure constraints + loose visual style = less generic output. Detailed aesthetic prompts paradoxically make AI output MORE generic.

## Export & Review

### D22: Semantic handlers beat positional extraction
`slides_to_pptx.py` (semantic, 15 handlers) produced 79% quality baseline. Understanding WHAT elements are > knowing exact WHERE they are positioned.

### D23: DOM feeds semantic for PPTX
Use DOM extraction positions as INPUT to the semantic engine, not as independent output. Combines native editability with pixel accuracy.

### D24: Slide export: HTML -> validate -> PPTX
3-phase process. Never skip validation. HTML prototype → browser validation → native editable PPTX via python-pptx.

### D25: PPTX review via native renderer
Review in PowerPoint, Keynote, or LibreOffice Impress. Never review via PDF — it masks font substitution flaws and layout differences.

### D26: HTML-to-PPTX dual engine architecture
Two engines: semantic (slides_to_pptx.py, primary) + DOM extraction (html_to_pptx.py, refinement). Semantic for first pass, DOM for pixel-accurate positioning when needed.
