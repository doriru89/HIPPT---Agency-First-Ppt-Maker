---
name: presentation
description: "Unified presentation skill — visual aids, McKinsey decks, and PPTX export. Three modes: visual-aid (concept diagrams), deck (structured presentations), export (editable PPTX)."
allowed-tools: [Read, Write, Bash, WebSearch]
argument-hint: "--mode deck|visual-aid|export 'topic and audience'"
auto_invoke: false
keywords: [slide, deck, presentation, mckinsey, pyramid, visual, aid, diagram, pptx, powerpoint, export]
user_invocable: true
categories: [creation]
supersedes: [slide-deck, visual-aid]
---

# /presentation — Philosophy-Driven Presentation Generator

Three modes, one skill. **Presentations flow through a quality-gated pipeline** (philosophy gate → ghost deck → direction → assets → build → critique → capture).

| Mode | Use Case | Output |
|------|----------|--------|
| `--mode deck` | Multi-slide presentation (any philosophy) | HTML (16:9) + optional PPTX |
| `--mode visual-aid` | Concept diagram, comparison, timeline | HTML (16:9) + optional PPTX |
| `--mode export` | Data/JSON → editable PPTX directly | .pptx only |

Default mode: inferred from request. Multi-slide → deck. Single concept → visual-aid. "PowerPoint"/"pptx" → export.

---

## Design Thesis: Constrain Structure, Free Aesthetics

Detailed aesthetic prompts make AI output MORE generic. Instead:
- **Tightly constrain** content structure (assertion-evidence, one-idea-per-slide, density limits)
- **Loosely constrain** visual style (provide palette + typography as starting point, explore freely)
- **Never constrain** creative expression within individual slides

## Pipeline Overview (deck mode)

For `--mode deck`, this skill runs the full pipeline:

1. **Philosophy Gate** — the user selects from `config/philosophies/` (mckinsey, editorial, data-forward, cinematic)
2. **Ghost Deck** (Step 1-2) — structural skeleton with auto-block gate
3. **Direction** — visual direction approval
4. **Assets** — real photos via Playwright capture or WebSearch (Unsplash). Save to `output/html/assets/<slug>/`
5. **Build** (Steps 3-4) — generate HTML/PPTX using philosophy constraints
6. **Critique** — 10-dim Q1-Q10 scoring (Structure, Canvas, Typography, Color, Data, Editability, Polish, Visual Evidence, Vision Adherence, Export Fidelity), target 90/100. Q10 post-export only
7. **Archive** — archive final outputs to `output/archive/<slug>/`. Write `capture.yaml` with scores and errata encountered

## Mode: deck

### Step 1: Structure (Philosophy-Aware)

Read the selected philosophy YAML from `config/philosophies/<name>.yaml`. Load:
- `structure.slide_vocabulary` — which slide components are allowed
- `structure.density_limits` — max content per slide
- `structure.ghost_deck_criteria` — what the ghost deck evaluates
- `asset_guidance` — what assets are required/optional/forbidden

Then follow the philosophy's `structure.framework`:
- **mckinsey:** Pyramid Principle (SCR + 3-5 clusters)
- **editorial:** Narrative arc (hook → tension → resolution)
- **data-forward:** Evidence-first (finding → evidence → implication)
- **cinematic:** Emotional arc (wonder → tension → revelation)

### Step 0: Presentation Vision & Requirements (HUMAN GATE — interactive)

Before structure, establish the vision. This step is **human-led** — AI asks questions, searches, and supports, but the user decides the vision. No AI scoring or ranking — work collaboratively until two things are clear:

**Source of truth outputs:**
1. **Vision** — one sentence: what is this presentation trying to achieve? (e.g., "convince Professor X that Artopath is production-grade", "raise $500K seed round", "teach classmates about knowledge graphs")
2. **Requirements** — audience, duration, constraints, mandatory content, tone

#### 0a. Clarifying Questions (interactive loop)
Read the user's initial input. Ask targeted questions — keep asking until vision + requirements are clear:
- **Audience:** Who is watching? What do they already know? What's their bias?
- **Goal:** What's the ONE thing you want them to do/feel/remember after?
- **Duration:** How many minutes? (drives slide count)
- **Constraints:** Required content, mandatory slides, format rules, grading rubric?
- **Tone:** Formal consulting? Creative pitch? Academic defense? Casual demo?

If the user gives sparse input, probe deeper. If the user says "just make it good" — push back: "Good for whom? What does success look like?"

#### 0b. Research Support (AI assists, human directs)
Once the user gives enough direction, AI searches for supporting context:
- **Memory** (project files) — the user's project history, past presentations, stated goals
- **Local materials** — project files, READMEs, course docs, research outputs
- **Internet** — only if the user directs ("look at how X presents this", "find competitor Y's pitch")

Surface what's found. Don't rank or score — present raw material and ask: "Does any of this change your vision?"

#### 0c. Lock Vision + Requirements
When the user confirms, write down:
- **Vision:** one sentence (this becomes the north star for all subsequent steps)
- **Requirements:** bullet list (audience, duration, constraints, tone, mandatory content)

These two documents are the **source of truth** for the entire pipeline. Every subsequent decision (structure, visuals, grid, images) is measured against them.

#### 0d. Content Inventory + Framework Selection
AI reviews all available content through the lens of the locked vision:
1. What content supports the vision? What's missing? What contradicts?
2. Suggest structural framework based on content + vision:
   - **Pyramid Principle** (SCR) — consulting/persuasion
   - **Narrative arc** — storytelling/demo
   - **Evidence-first** — data-heavy/research
   - **Problem-solution** — product/pitch
3. Flag content gaps that need filling before building

**GATE:** Present vision + requirements + content inventory + suggested framework. the user confirms before Step 0.5/1.

### Step 0.5: Reference Analysis (MECHANICAL + HUMAN GATE)

If the user provides a reference PPTX or PDF:
1. `uv run hippt-tokens <ref.pptx> --slug <name>` → `output/design/ref-<slug>.yaml`
2. `uv run hippt-layouts <ref.pptx> --out layouts/<slug>/ --verify` → layout YAML hints
3. Playwright screenshots of each reference slide at 960×540 → `output/design/ref-screenshots/<slug>-s{N}.png`
4. Produce design brief: tokens + layout hints + screenshot paths
5. **GATE:** the user confirms design brief captures the reference's visual DNA. Lightweight review.

Output: `output/design/ref-brief-<slug>.yaml`

If no reference provided, skip to Step 1.

### Step 1 (continued): Structure with Pyramid Principle

Before ANY visual work:

1. **Situation** — Current state (1-2 slides)
2. **Complication** — Problem or tension (1-2 slides)
3. **Resolution** — The answer (rest of deck)

Resolution structure:
- Group evidence into 3-5 argument clusters
- Each cluster → section header slide
- Each point → one slide
- Order by importance, not discovery sequence

### Step 2: Ghost Deck

Write titles as complete assertive sentences:
- Bad: "Market Overview"
- Good: "The healthcare transparency market will reach $4.2B by 2028"

Validate:
- **Horizontal logic** — reading only titles tells a complete story
- **Vertical logic** — every element on a slide proves its title

### Step 3: Executive Summary

Slide 2 (after title): top-level conclusion + 3 supporting points (one per cluster). This slide alone conveys the full message.

### Step 3.5: Visual Plan + Grid (E-PRES-020 — HUMAN GATE)

Before building HTML, reason about visuals for EACH slide:

1. **Grid decision** — choose column layout from tokens (12-col default, `grid-template-columns: repeat(12, 1fr)`). Define margin, gutter, and row zones (title/body/footer).
2. **Per-slide visual reasoning:**
   - What image BEST proves this slide's assertion? (not generic — specific to the claim)
   - Sources: project files in `input/`, product screenshots, online (via WebSearch), Python-generated data charts, animations
   - Space allocation: what % of slide should the image occupy?
   - Does this slide need a data output? (chart, metric, table from Python/research)
3. **Present visual plan to the user** — describe each image candidate, layout sketch (which grid columns), and space allocation. STOP and wait for feedback.
4. **Coherence check** — does the visual tell the same story as the text? Reject stock-photo thinking.

Example: "Cultural knowledge scatters" → DNA graph (proves unification) not hero page (generic). "No cultural lineage" on IMDb → screenshot of IMDb's cast-only page (shows the gap visually).

### Step 3.7: Content Enrichment

Before building HTML, enrich every assertion slide with sourced evidence. Ghost deck + visual plan give structure; this step fills it with substance.

**Tools for enrichment:**
- Search `input/` and `output/research/` for prior materials and source documents
- Read `errata/presentation_design.md` for known failure patterns
- Use WebSearch to verify factual claims — save sources to `output/research/<slug>-sources.md`
- Direct file reads of source materials (briefs, research outputs, notes in `input/`)

**Process:**
1. **Per-slide evidence gathering** — for each slide, batch searches by theme (hardest-to-source first). Use WebSearch for factual claims needing verification. Search `input/` for local source materials.
2. **Iterative reflection** — after each research round, assess whether findings change the thesis. Reframe arguments if needed. Use new understanding to sharpen the next search. Research is not a checklist; each round informs the next.
3. **Per-slide evidence brief** — for each assertion slide, produce: claim → source → exact figure → citation. Every assertion slide must have ≥1 sourced claim.
4. **SCAC audit (content gate)** — for each slide, verify 6 gates:

   | Gate | Question | Pass |
   |------|----------|------|
   | G1 Goal | ONE takeaway for the audience? | 1 sentence |
   | G2 Self-Sufficiency | Content achieves G1 WITHOUT speaker script? | Reader-only test |
   | G3 Data Grounding | Every number traceable to local file:field? | No generic AI filler |
   | G4 Evidence | Every assertion has evidence ON the slide? | No unsupported claims |
   | G5 Specificity | Replace project name with "Project X" — same? | Must be project-specific |
   | G6 Depth | SHALLOW / ADEQUATE / DEEP | ADEQUATE min, DEEP for core results |

   Any SHALLOW slide blocks proceeding. Core result slides must rate DEEP.

5. **Source consolidation** — write all sources to `output/research/<slug>-sources.md` with: source name, slide(s) used in, URL, tier (S1-S4), key claim extracted. This becomes the deck's bibliography and final validation checklist.
6. **Ghost deck story flow review (HUMAN GATE)** — present all slides as text (assertive title + key evidence + source). Check horizontal logic (titles tell a complete story). Flag any thesis changes or reordering. **STOP and wait for the user's approval** before Step 3.8.

### Step 3.8: Expert Critique (3-Lens Stress Test)

The best presentations survive hostile questions. Before building, stress-test the thesis through three expert lenses — each represents a likely audience skeptic.

1. **Select 3 experts** — choose lenses that match the deck's domain. Default set:
   - **Industry insider** — knows how the business actually works (economics, incentives, adoption friction)
   - **Technical skeptic** — has seen similar technology promises fail (feasibility, scale, alternatives)
   - **Strategy/academic** — grades argument coherence (frameworks, moats, adoption curves, math)
2. **Launch 3 parallel agents** — each agent receives the full ghost deck + enrichment data and searches for:
   - Gaps in the argument (what's missing or assumed?)
   - Counter-evidence (data/stories that contradict the thesis)
   - Supporting evidence the enrichment missed (new articles, incidents, data points)
3. **Synthesize findings** — classify each finding as:
   - 🔴 Must address in deck (argument breaks without it)
   - 🟡 Should address or have ready for Q&A
   - ✅ Strengthens the deck (new evidence to add)
4. **Counter-argument research** — for each 🔴/🟡 finding, search for evidence to support the counter. Don't self-question in slides — weave counters naturally into the narrative.
5. **Update ghost deck** — revise slides with new evidence and reframes. Update sources.md.
6. **Final story flow review (HUMAN GATE)** — present revised ghost deck. **STOP and wait for the user's approval** before Step 4.

### Step 3.9: Image Audit (after enrichment, before build)

Capture evidence images via Playwright at ≥1200px width. Then VIEW each image (E-PRES-030):
1. Does it show the claimed content? (not a paywall/redirect/generic page)
2. Can you read the key headline at 1080p? (E-PRES-026: ≥200px height)
3. Does it prove the specific assertion on the target slide? (coherence)
4. Is the source credible for this claim?

Failed captures block build. Base64 conversion happens after audit passes.
Each image on exactly one slide — no reuse (E-PRES-033).

### Step 4: Generate HTML

Write to `output/html/presentation-<slug>-<YYYY-MM-DD>.html`.

**HARD GATE: Before writing HTML, verify you can prevent F1-F10.** Each F is a known failure mode — if you can't prevent it, don't start building. Read `templates/presentation-components.md` and `errata/presentation_design.md` for the full failure patterns.

**Read `templates/presentation-components.md` before building.** Each slide type has specific Guardrails (canvas fill targets, font minimums, anti-patterns) — follow them for the slide type you're building.

**CSS Grid is MANDATORY for all slide layouts.** Every `.slide-content` or content container must use `display: grid` with explicit `grid-template-columns` and `grid-template-rows`. No `position: absolute` for content layout (only for title bar, footer, decorative elements). Exception: creative/artistic slides verified via Playwright screenshot.

#### White-Space Auto-Scaling (mechanical, at build time)

After laying out content in the grid, check: can all text be scaled 2× and still fit within its grid cell without overflow? If yes, the text is too small — scale up until ~80% of available cell space is used. This is not subjective; it's computed:
1. Grid cell size = available space for that element
2. Current text block size = content at current font size
3. Scale factor = cell size ÷ text block size (capped at 2×)
4. If scale factor > 1.3 → increase font size by that factor

The F2 minimums (title ≥48px, body ≥18px) are FLOORS, not targets. If the layout has room, go bigger.

#### Canvas Fill 3-Layer Sequence

Canvas fill ≥80% is achieved through three layers applied in order — not alternatives:
1. **Content layer:** Fill the grid with substance. Empty space = missing support for the assertion (E-PRES-003).
2. **Grid layer:** Size elements to their ZONE, not their content. `width: 100%`, `min-height` on containers (E-PRES-006).
3. **Scaling layer:** Auto-scale text to fill grid cells (white-space auto-scaling above). If text can zoom 2× without overflow, it's too small.

If canvas fill is still <80% after all three layers, the slide needs more content — go back to the ghost deck.

#### Common Build Failures to Prevent

These patterns cause 80% of quality failures. Read before writing any HTML.

| ID | Failure | Root Cause | Prevention |
|---|---|---|---|
| F1 | Content-sized elements (8% fill) | AI uses `width: auto` | Size to ZONE not CONTENT — use `width: 100%`, `min-height` on containers (E-PRES-006) |
| F2 | Web-sized text (12px body) | AI uses web defaults | Title ≥48px, body ≥18px, labels ≥14px, source ≥10px, chart labels ≥10px (E-PRES-001) |
| F3 | Arbitrary spacing | No rhythm base | Define `--spacing-unit: 8px` in `:root`, all gaps are multiples. One value, not per-element (E-PRES-016) |
| F4 | Rectangles for funnels/diagrams | CSS laziness | Use inline SVG for non-rectangular forms; `clip-path` degrades to raster in PPTX export (E-PRES-039) |
| F5 | Gray placeholder blocks `[Photo]` | Laziness | Use gradient silhouettes or patterns showing intended composition shape (E-PRES-040) |
| F6 | Mixed letter-spacing per element | No tokens | Define 2-3 letter-spacing roles as CSS custom properties, apply by role (E-PRES-041) |
| F7 | Image reuse across slides | Same image on 2+ slides | Each image on exactly one slide — second use → metric card or pull quote (E-PRES-033) |
| F8 | Decorative evidence | Keyword-matched screenshots | Evidence images must contain DATA proving the assertion (E-PRES-032) |
| F9 | Missing so-what | Slide without assertion | Every slide title is a claim, body is proof — no label-only titles |
| F10 | Inconsistent line-heights | Ad-hoc line-height values | Define 2-3 line-height roles as CSS custom properties, apply by role (E-PRES-013) |

**Edge cases (don't over-apply the rules):**
- Statement/title slides: large empty space IS correct — don't fill it with content
- Stat slides: the large stat value IS the content — don't add decorative panels next to it
- Data slides: the chart IS the evidence — make it ≥60% of slide area, not a thumbnail
- Photo slides: the image IS the slide — text overlay max 15 words with contrast scrim

| Rule | Spec |
|------|------|
| Aspect ratio | 16:9 strict |
| Content width | 960px (matches viewport) |
| Ideas per slide | One |
| Navigation | Arrow keys + progress indicator |
| Title | 48px+ |
| Subtitle | 28px |
| Body | 18px |
| Evidence | 14px |
| Color | From philosophy preset. No hardcoded defaults. Explore freely. |
| Data viz | Inline SVG. No external CDN. Direct labels (Tufte). |
| Components | Use slide types from `templates/presentation-components.md` |
| Density | Enforce limits from philosophy YAML (max words, max items per slide) |
| Viewport | Every slide `height: 540px; overflow: hidden;` — split if overflows |
| Sizing | Fixed px at 960×540 — no clamp(), no vw/vh |
| Images | If total base64 > 50KB, extract to `output/html/assets/<slug>/` |
| Assets | Real photos (Unsplash) over generated illustrations. Check philosophy `asset_guidance`. |

### Slide Templates

- **Title** — Project name (large, centered), subtitle with date/audience
- **Section Header** — Cluster title as assertive sentence, 2-3 bullet preview
- **Content** — Assertive title, body proving title, evidence/source, optional visual
- **Data** — Assertive insight title, chart/table as primary, annotation on key number, source

### Step 4.5: Canvas Fill Gate [MECHANICAL]

Before opening in browser, self-check every slide against known presentation anti-patterns:

| Check | Rule | Auto-Fix |
|-------|------|----------|
| No `position:relative` on `.s-*` | Breaks fixed stacking (E-PRES-004) | Remove or use child wrapper |
| Contrast on all text | No low-contrast combos (E-PRES-002) | Bump to WCAG AA |
| Viewport fill ≥ 80% width | Grids/flex use available space (E-PRES-006) | Widen max-width, adjust flex |
| Font size minimums | Title ≥ 48px, body ≥ 18px (E-PRES-001) | Bump to minimum |
| Content-richness match | If element contains image/screenshot, container ≥ 400px wide (E-PRES-008) | Widen container before inserting image |
| `height:540px; overflow:hidden` per slide | No overflow or void | Split or tighten |

Fix inline silently. Log to `brief.build.preflight_fixes[]`. Don't waste critique cycles on known anti-patterns.

### Step 4.6: Brutal Honest Critic (self-review before presenting)

Before showing ANY slide to the user, view each Playwright screenshot and answer these 5 questions honestly. If ANY answer is "no", fix before presenting.

| Test | Question | Failure = |
|------|----------|-----------|
| Professional | Would a McKinsey consultant put this in a client deck? | Redesign layout |
| Canvas | Does content fill ≥80% of the viewport? (title/section-break exempt) | Add content or resize — CSS padding is not a fix (AP9) |
| Typography | Can every text element be read at 3m from a projector? | Increase font size to minimums (E-PRES-001) |
| Diagram | Are shapes/icons recognizable, or are they gray rectangles? | Use real SVG shapes, not placeholders (E-PRES-040) |
| Spacing | Is whitespace distributed evenly, or clumped in one area? | Redistribute with consistent gap variable |

**This is NOT Q1-Q10 scoring.** This is a gestalt "does it look right?" check. Scoring happens at Step 5.

### Step 4.9: HTML Approval Gate [HUMAN GATE — blocks PPTX]

Open HTML in browser at full screen. the user reviews.
- **Gate:** the user approves at quality level per `pptx-quality.yaml` convergence.html_first_pass (SSOT) before ANY PPTX work
- All design iteration happens on HTML — PPTX is a one-shot export
- If not approved: iterate Steps 4-4.5, re-present
- AskUserQuestion with diagnosis and proposed solution before changes

### Step 4.95: Sidecar JSON Sync

After convergence rounds modify HTML, re-extract sidecar JSON before any PPTX export (E-PRES-028). Stale JSON from initial build will not match the converged HTML.

### Step 5: Convergence (max 3 rounds)

**Targets:** per `config/pptx-quality.yaml` convergence section (SSOT). Q10 scored post-export only.

**Iteration trigger** — re-enter loop if ANY of:
1. Q1-Q9 avg below `convergence.html_first_pass` target
2. Any single Q below `convergence.iteration_trigger.any_q_below`
3. Gate violation: Q2 < 7 or Q6 < 8

After HTML approval, score and iterate:
- **5a:** Playwright screenshot all slides at 960×540 (native PPTX resolution per E-PRES-036 — 1 CSS px = 1/96" = exact PPTX coordinates)
- **5b:** Score Q1-Q9 per slide (screenshot-before-score hard gate, E-PRES-017)
- **5b.1:** SCAC re-evaluation — re-run G1-G6 per slide alongside Q1-Q9. If any slide regressed in content depth (e.g., layout fix removed evidence text), flag as regression same as Q score drops. If Q1 or Q8 is the bottleneck, SCAC diagnosis determines whether the problem is content (backtrack to 3.7) or layout (fix in convergence).
- **5c:** Bottleneck diagnosis — identify the single lowest Q dimension. Fix ONLY that dimension this round (TOC one-constraint-at-a-time). Priority when tied: per `pptx-quality.yaml` convergence.bottleneck_priority (Q1 > Q8 > Q5 > Q2 > Q9 > Q7 > Q3 > Q4)
- **5d:** Context Review — re-read vision, ghost deck, sources.md. Top-down + bottom-up check. Per empty/weak slide: add content > add visual data > add image > condense > CSS fix only
- **5e:** Image Coherence Review — view rendered images, check readability + assertion match
- **5f:** Fix the bottleneck → re-screenshot → re-score ALL dimensions
- **5g:** Safety checks before accepting the fix:
  - **Regression gate:** if any previously-passing Q dropped more than `convergence.regression_threshold` points (0.5), reject the fix and try an alternative approach to the same bottleneck
  - **Oscillation detector:** if this round's bottleneck = two rounds ago's bottleneck, you are in a limit cycle (likely Q2↔Q7 coupling). Exit convergence with the best-scoring round's output
  - **Joint Q2+Q7:** if Q2 and Q7 are both below target and within 1 point of each other, treat as a single coupled constraint — "improve canvas fill WITHOUT degrading alignment"
- **5h:** If content is the bottleneck (Q1 or Q8 persistently low) and CSS/layout fixes cannot help: exit convergence, report to user, offer to re-enrich at Step 3.7 and restart from Step 4. Do NOT automatically backtrack.

### Step 6: Export to PPTX

Triggered when user requests PPTX (`--pptx` flag or explicit request).

1. **slides_to_pptx.py** (primary engine) — sidecar JSON + design tokens, fast, no browser. Default for all exports.
   ```bash
   uv run hippt-draft output/html/presentation-<slug>-slides.json \
     --tokens output/design/ref-<slug>.yaml \
     --out output/pptx/<slug>-<YYYY-MM-DD>.pptx
   ```
2. **html_to_pptx.py** (refinement engine) — DOM extraction at 960×540, exact coordinates. Use when layout remapping or reference-PPTX inheritance is needed.
   ```bash
   uv run hippt-export <approved-html> \
     --reference <source.pptx> \
     --use-layouts layouts/ \
     --debug \
     --out output/pptx/<slug>-<YYYY-MM-DD>.pptx
   ```
   - `--reference <pptx>`: inherit theme fonts (heading/body) from reference PPTX. Validates 16:9 aspect ratio.
   - `--use-layouts <dir>`: select best layout per slide from library, remap element positions. Default: `layouts/`.
   - `--debug`: outputs per-slide scoring to `output/debug/layout-selection.json`.
   - Composes: `--reference` + `--use-layouts` can be used together.
3. **PPTX Review** — upload to Google Drive, Playwright screenshot in Google Slides, compare vs HTML (E-PRES-035). Never verify via PDF.
4. **Layout capture** (flywheel) — extract layouts from the approved PPTX back into the library:
   ```bash
   uv run hippt-layouts output/pptx/<slug>.pptx \
     --out layouts/<slug>/ --verify
   ```

### Step 7: Archive (non-optional)

Archive approved HTML + PPTX + design tokens to `output/archive/<slug>/`. Write `capture.yaml` with scores, errata encountered, and techniques used. Tag novel layouts as candidates for `layouts/` library.

---

## Mode: visual-aid (Concept Diagrams)

### Step 1: Identify Concept Type

| Type | When | Layout |
|------|------|--------|
| **Flow** | Process, pipeline, sequence | Left-to-right arrows |
| **Comparison** | A vs B, trade-offs | Side-by-side columns or table |
| **Hierarchy** | Taxonomy, org chart | Tree or nested boxes |
| **Timeline** | History, phases, milestones | Horizontal or vertical |
| **Matrix** | 2-axis categorization | 2x2 or NxM grid |
| **Cycle** | Feedback loops | Circular arrows |
| **Layered** | Stack, architecture | Stacked horizontal bands |

If ambiguous, ask the user.

### Step 2: Extract Structure

1. Core concepts (nodes/items)
2. Relationships (arrows, containment, comparison axes)
3. Hierarchy level (primary vs supporting)
4. Data values (counts, percentages, scores)

### Step 3: Generate HTML

Write to `output/html/visual-aid-<slug>-<YYYY-MM-DD>.html`.

| Rule | Spec |
|------|------|
| Aspect ratio | 16:9 viewport-aware |
| Content width | 960px centered, symmetric margins (per E-PRES-036) |
| Navigation | Top nav (if multi-section), never sidebar |
| Row centering | flex-grow:0 + justify-content:center |
| Color coding | Consistent meaning (green=good, red=risk, blue=info) |
| Labels | 14-16px |
| Headers | 24-32px |
| Annotations | 12px |
| CDN | None. All inline. |

### Step 4: Design Principles (Tufte)

- **Data-ink ratio** — maximize information per visual element
- **Small multiples** — repeat same layout for parallel concepts
- **Chartjunk removal** — no decorative gradients, 3D effects, ornamental borders
- **Labels over legends** — annotate directly, not in a separate key

### Step 5: Open in Browser

```bash
open output/html/visual-aid-<slug>-<YYYY-MM-DD>.html
```

### Step 6 (optional): Export to PPTX

Same as deck mode — invoke export mode with the visual structure.

---

## Mode: export (Editable PPTX Generation)

### Sidecar JSON Contract

When `--mode deck` or `--mode visual-aid` generates HTML, it MUST also emit a **sidecar JSON file** alongside:
- HTML: `output/html/presentation-<slug>-<YYYY-MM-DD>.html` (for human review)
- JSON: `output/html/presentation-<slug>-<YYYY-MM-DD>-slides.json` (for PPTX export)

The sidecar JSON contains the structured slide data that `slides_to_pptx.py` consumes:
```json
{
  "metadata": {"title": "...", "author": "HIPPT", "date": "YYYY-MM-DD"},
  "design_tokens": {"palette": [...], "typography": [...], "spacing": {...}},
  "slides": [
    {
      "type": "title|content|data|comparison|flow|timeline|section",
      "title": "Assertive sentence title",
      "elements": [
        {"type": "text", "content": "...", "x": 0.5, "y": 1.0, "w": 9, "h": 0.8, "font_size": 28, "bold": true, "color": "1E293B"},
        {"type": "shape", "shape": "rectangle", "x": 0, "y": 0, "w": 10, "h": 0.06, "fill": "accent"},
        {"type": "image", "path": "/tmp/...", "x": 1, "y": 2, "w": 8, "h": 4},
        {"type": "chart", "chart_type": "bar", "data": [...], "x": 0.5, "y": 1, "w": 9, "h": 4},
        {"type": "table", "headers": [...], "rows": [...], "x": 0.5, "y": 1.5, "w": 9, "h": 3}
      ],
      "background": {"type": "solid|gradient", "color": "FFFFFF"}
    }
  ]
}
```

This avoids dual-SSOT: HTML renders for human review, JSON feeds PPTX export. Each has one consumer, one purpose.

### Dual Engine Support

Two PPTX engines are supported. Both consume the same sidecar JSON, produce the same `.pptx` output:

| Engine | Language | Status | Best For |
|--------|----------|--------|----------|
| **python-pptx** | Python | Proven (build_pitch_v6.py) | General decks, text-heavy, tables |
| **PptxGenJS** | Node.js | Researched (8 pitfalls documented) | Charts, icon rasterization |

Export invocation:
```bash
# Engine A (default, proven)
uv run hippt-draft output/html/presentation-<slug>-slides.json --tokens output/design/ref-<slug>.yaml

# Engine B (requires npm install pptxgenjs)
uv run hippt-draft output/html/presentation-<slug>-slides.json --engine pptxgenjs
```

### Path A: Sidecar JSON → PPTX (primary path)

1. Read the sidecar JSON emitted by deck/visual-aid mode
2. Load design tokens from `output/design/ref-<slug>.yaml` (if reference PPTX was provided)
3. Map each slide to engine-specific calls (python-pptx or PptxGenJS)
4. Generate `.pptx` with editable text boxes, shapes, charts
5. Round-trip validation: re-open with python-pptx, verify slide/element counts

### Path B: Data → PPTX (direct from JSON/YAML/conversation)

1. Accept structured slide data (JSON, YAML, or conversational description)
2. Convert to sidecar JSON format, then follow Path A
3. Faster for data-heavy decks, report generation

### Engine A: python-pptx (Proven)

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

prs = Presentation()
prs.slide_width = Inches(10)
prs.slide_height = Inches(5.625)
```

### Slide Type Mapping

| Slide Type | PptxGenJS Approach |
|------------|-------------------|
| Title | `addText` centered, large font + subtitle below |
| Section Header | `addText` with accent bar `addShape(RECTANGLE)` |
| Content | Title text box + body text box + optional image |
| Data | Title text box + `addChart` (BAR/LINE/PIE) + annotation |
| Comparison | Side-by-side text boxes or table |
| Flow | Shapes + connectors (LINE shapes between RECTANGLEs) |
| Timeline | Horizontal shapes with text labels |

### Typography for PPTX

| Element | Font | Size | Color |
|---------|------|------|-------|
| Slide title | Calibri Bold | 28pt | 1E293B |
| Subtitle | Calibri | 18pt | 475569 |
| Body text | Calibri | 14pt | 334155 |
| Evidence/source | Calibri | 10pt | 94A3B8 |
| Data callout | Calibri Bold | 36pt | accent color |

### Color Palettes (10 curated)

| Name | Primary | Accent | Light BG | Text |
|------|---------|--------|----------|------|
| Corporate Blue | 1E3A5F | 2563EB | F0F4F8 | 1E293B |
| Warm Minimal | 292524 | D97706 | FFFBEB | 1C1917 |
| Forest | 14532D | 059669 | ECFDF5 | 1E293B |
| Sunset | 7C2D12 | EA580C | FFF7ED | 1E293B |
| Ocean | 0C4A6E | 0284C7 | F0F9FF | 1E293B |
| Plum | 581C87 | 9333EA | FAF5FF | 1E293B |
| Slate Pro | 1E293B | 3B82F6 | F8FAFC | 1E293B |
| Coral Pop | 4A1D1D | F43F5E | FFF1F2 | 1E293B |
| Mint Fresh | 134E4A | 14B8A6 | F0FDFA | 1E293B |
| Charcoal Gold | 1C1917 | CA8A04 | FEFCE8 | 1E293B |

### Common Pitfalls — python-pptx (CRITICAL)

See `errata/presentation_design.md` E-PPTX-001 through E-PPTX-004 for full details:
1. **E-PPTX-001:** Always `RGBColor(0xRR, 0xGG, 0xBB)` — never hex strings
2. **E-PPTX-002:** Use `Inches()` for positions, `Pt()` for fonts — never raw EMU math
3. **E-PPTX-003:** Check font availability, maintain fallback mapping table
4. **E-PPTX-004:** Classify CSS effects as "PPTX-safe" vs "rasterize-fallback" during HTML build

### Common Pitfalls — PptxGenJS (Engine B)

1. **NEVER use "#" in hex colors** — causes file corruption. Use `"FF0000"` not `"#FF0000"`.
2. **NEVER encode opacity in hex string** — 8-char hex (`"00000020"`) corrupts file. Use `opacity` property.
3. **Use `bullet: true`** — never unicode symbols. Creates double bullets.
4. **Use `breakLine: true`** between text array items.
5. **Fresh pptxgen() per presentation** — never reuse instances.
6. **NEVER reuse option objects** — PptxGenJS mutates objects in-place (converts to EMU).
7. **Don't pair ROUNDED_RECTANGLE with accent bars** — rectangular overlays won't cover rounded corners.

### QA Process

After generating PPTX:
1. **Round-trip validation** — re-open with python-pptx, verify slide count + element counts match sidecar JSON
2. **Visual QA** — if LibreOffice available: convert to PDF → pdftoppm → screenshot each slide
3. **Human gate** — present to the user for approval before marking done

### Output

```bash
# HTML output (for human review)
output/html/presentation-<slug>-<YYYY-MM-DD>.html
# Sidecar JSON (for PPTX export)
output/html/presentation-<slug>-<YYYY-MM-DD>-slides.json
# PPTX output
output/pptx/<slug>-<YYYY-MM-DD>.pptx
```

### Dependencies

- `python-pptx>=1.0` (pip, in pyproject.toml extract extras) — Engine A
- `pptxgenjs` (npm, install separately) — Engine B
- `react-icons` + `sharp` (npm) — icon rasterization for Engine B (optional)

---

## Shared Rules (all modes)

1. **Structure first, aesthetics second.** Content hierarchy before visual polish.
2. **16:9, 960px, symmetric, centered.** Always for HTML output (per E-PRES-036).
3. **One idea per slide/section.** Split if needed.
4. **No external CDN** for HTML output. Everything inline.
5. **Top nav, never sidebar** (visual-aid multi-section).
6. **Consistent color coding** across all outputs.
7. **Pyramid Principle is non-negotiable** for deck mode.
8. **Ghost deck must pass** before building deck mode.
9. **Executive summary on slide 2** for deck mode.
10. **Tufte's principles** for visual-aid mode.
11. **Never artistic in visual-aid mode.** Clean, functional, informative.
12. **Always offer PPTX export** when user mentions PowerPoint, Keynote, or sharing with non-technical audience.

## Anti-Patterns

- NEVER use accent lines under titles in PPTX (AI slop marker)
- NEVER use Inter/Roboto for display text
- NEVER place charts without assertive insight titles
- NEVER create slides without clear hierarchy
