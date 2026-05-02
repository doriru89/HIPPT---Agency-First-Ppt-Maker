# AI PPTX Generation Pipeline — MEGAPLAN

> **Status (2026-05-02):** MEGAPLAN has served its purpose. Phases 1-8, 1B, 1C, 1D, 2A-2G are COMPLETE.
> Remaining active work → **FINAL_PLAN.md** (SSOT fixes + PPTX export + validation).
> Deferred items → **BACKLOG.md** (with prerequisites and triggers).
> This file is now a **read-only architectural reference**, not an active plan.

## 1. Vision

Reference-driven HTML presentations that faithfully capture designs Austin likes, exportable as editable PPTX. The pipeline starts with a PPTX design Austin admires → extracts its design DNA (tokens, layout patterns, screenshots) → builds HTML that visually matches the reference → iterates HTML until it captures the design → exports to PPTX as a one-shot operation. A growing layout pattern library accelerates every future deck.

**What makes this unique:** No tool reliably takes a reference PPTX design, builds HTML that captures its layout language, and round-trips back to editable PPTX. We're not competing with Gamma (prompt→slides) or PPTAgent (edit one reference at a time) — we solve reference-to-HTML fidelity: making the LLM build HTML that actually looks like the professional design you pointed at, with PPTX export as a reliable final step.

---

## 2. Landscape & Scope

### Competitive Context

| Tool | Approach | How We Differ |
|------|----------|---------------|
| dom-to-pptx (134★) | Client-side JS, getBoundingClientRect → PptxGenJS | We're server-side (Playwright + python-pptx). No layout library, no quality gates |
| Gamma (70M users, $2.1B) | Prompt → slides, 20+ models in parallel | Different approach entirely — they generate from text, we convert approved HTML |
| PPTAgent (3.3K★, EMNLP 2025) | Reference slide editing, 2-stage pipeline | Edits one reference at a time — no persistent layout library, no flywheel |
| SlideAudit (UIST 2025) | Expert taxonomy of 2,400 slide design flaws | Complements our Q1-Q10 rubric — taxonomy maps to our dimensions |
| AeSlides (arXiv 2026) | RL-verifiable layout metrics (aspect ratio, whitespace, collisions) | Future opportunity: mechanical post-generation checks |

### Intentional Exclusions

| Feature | Rationale |
|---------|-----------|
| Animations/transitions | Static slides are the professional standard (McKinsey, BCG). Complexity without value |
| Speaker notes | Out of pipeline scope — the presentation IS the deliverable |
| i18n/RTL | All presentations are English/中文 — no RTL need currently |
| MCP server exposure | Pipeline is agent-internal, not an API product (re-evaluate when layout library matures) |
| Multi-model parallel gen | Single orchestrator is simpler and sufficient |

---

## 3. System Architecture

```
                        ┌─────────────────────────────────────────────────────────────┐
                        │                    PRESENTATION PIPELINE                     │
                        │              Reference-First Design Flow                     │
                        └─────────────────────────────────────────────────────────────┘

  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐    ┌───────────────┐
  │ Step 0   │    │ Step 0.5 │    │ Steps    │    │ Step 4       │    │ Step 4.9      │
  │ Vision & │───▶│ Reference│───▶│ 1-3      │───▶│ Build HTML   │───▶│ HTML          │
  │ Require  │    │ Analysis │    │ Structure│    │ (guided by   │    │ APPROVED ✓    │
  │          │    │          │    │ + Ghost  │    │ design brief)│    │               │
  └──────────┘    └────┬─────┘    └──────────┘    └──────┬───────┘    └───────┬───────┘
                       │                                 │                    │
  Reference PPTX ──────┘                            ◄────┘                    │
  ├─ tokens (palette, fonts)                   Iteration loop                 │
  ├─ layout hints (regions %)                  (score → fix → rescore)        │
  └─ screenshots (ground truth)                                               ▼
       │                                                              ┌───────────────┐
       │                                                              │ Step 5        │
       │         Design brief guides HTML ────────────────────────▶   │ Convergence   │
       │         (layout patterns = input to Step 4,                  │ HTML vs Ref   │
       │          not remapping at Step 6)                             │ screenshots   │
       │                                                              └───────┬───────┘
       │                                                                      │
       │               ┌──────────────────────────────────────────────────────┘
       │               │
       │               ▼
       │         ┌──────────┐    ┌──────────┐    ┌──────────┐
       │         │ Step 6   │    │ Step 7   │    │ Layout   │
       │         │ PPTX     │───▶│ Design   │───▶│ Pattern  │───────┐
       │         │ Export   │    │ Capture  │    │ Library  │       │
       │         │ (1-shot) │    │          │    │ Growth   │       │
       │         └──────────┘    └──────────┘    └──────────┘       │
       │                                                            │
       └────────────────────────────────────────────────────────────┘
                    Flywheel: approved patterns guide future HTML creation
```

### Dual Path — Primary vs Refinement

```
  ┌─────────────────────────────────────┐
  │ slides_to_pptx.py                   │
  │ PRIMARY engine                      │
  │ Input: sidecar JSON + tokens YAML   │
  │ Speed: fast (no browser)            │
  │ 15 semantic handlers (radial, etc.) │
  │ Used: primary export from sidecar   │
  └─────────────────────────────────────┘

  ┌─────────────────────────────────────┐
  │ html_to_pptx.py                     │
  │ REFINEMENT engine                   │
  │ Input: approved HTML file           │
  │ Speed: slow (Playwright)            │
  │ Accuracy: exact at 960×540          │
  │ 5 generic DOM builders              │
  │ Used: refinement after HTML approval│
  └─────────────────────────────────────┘

  Both coexist permanently. Different problems, different inputs.
```

### Reference Analysis — Design Brief Pipeline

```
  Reference PPTX (design Austin likes)
  ┌──────────────────────────────┐
  │ McKinsey template,           │
  │ conference deck,             │
  │ designer reference           │
  │ (PPTX or PDF-of-PPTX)       │
  └──────────────┬───────────────┘
                 │
                 ▼
  ┌──────────────────────────────┐
  │   Step 0.5: Reference        │
  │   Analysis Pipeline           │
  │                              │
  │  pptx_to_tokens.py           │
  │  → palette, fonts, spacing   │
  │                              │
  │  pptx_to_layout.py           │
  │  → approximate layout hints  │
  │    (regions as percentages)  │
  │                              │
  │  Playwright screenshots      │
  │  → per-slide visual ground   │
  │    truth at 960×540          │
  └──────────────┬───────────────┘
                 │
                 ▼
  ┌──────────────────────────────┐
  │   Design Brief (YAML)       │
  │                              │
  │  ├─ tokens: palette, fonts   │
  │  ├─ layout_hints:            │
  │  │   per-slide approximate   │
  │  │   regions (% positions)   │
  │  │   NOTE: hints, not SSOT   │
  │  └─ screenshots:             │
  │      per-slide PNG paths     │
  │      (convergence ground     │
  │       truth)                 │
  └──────────────┬───────────────┘
                 │
                 ▼
  ┌──────────────────────────────┐
  │   Step 4: Build HTML         │
  │   LLM receives design brief  │
  │   + PPTX-safe CSS rules      │
  │   → HTML that matches ref    │
  └──────────────────────────────┘

  After approval + export, novel approved patterns
  enter the Layout Pattern Library for future decks.
```

---

## 3.5 Design Tokens SSOT

Two levels of single source of truth serve different audiences:

| Level | SSOT | Audience | Contents |
|-------|------|----------|----------|
| Project | `MEGAPLAN.md` | Humans + LLMs | Phases, decisions, architecture, process rules |
| Code | `TOOLS/lib/design_tokens.py` | Pipeline code | Constants, color parsing, coordinate conversion |

### Dependency Graph

```
design_tokens.py  (leaf — zero TOOLS imports, only stdlib)
    ^
    |
layout_utils.py  (imports VIEWPORT_W/H, parse_px)
    ^
    |
layout_select.py  (imports from layout_utils + design_tokens)
    ^           ^
    |           |
html_to_pptx.py  slides_to_pptx.py  pptx_to_layout.py  extract_layouts.py
```

### Division Rule

| Category | Location | Examples |
|----------|----------|----------|
| Physics (invariants) | Python constants in `design_tokens.py` | VIEWPORT_W=960, CSS_PX_TO_PT=0.75, SLIDE_DPI=96 |
| Tunables (per-deck) | YAML config in `layout-extraction.yaml` | Scoring weights, thresholds, structural_roles |
| Engine-specific | Local to each pipeline script | Gradient parsing, TokenResolver, semantic handlers |

### Locked Decision #12 (design_tokens.py boundary)

`design_tokens.py` has zero python-pptx dependency. Functions return raw tuples `(int,int,int,float)` — each pipeline wraps with `RGBColor` at its own boundary. This keeps the module testable and importable without installing python-pptx. (Also recorded in table as #12.)

---

## 4. Standard Process Rules

### HTML Creation Rules

| Rule | Source | What |
|------|--------|------|
| **960×540 viewport** | E-PRES-036 | All HTML authored at 960×540, matching PPTX 96 DPI native. Fixed px at 960×540 produces exact PPTX-appropriate font sizes. 1920×1080 creates 2x mismatch. |
| **Canvas fill ≥80%** | E-PRES-006 | Detail slides fill ≥80% viewport. AI defaults to 8%; professionals fill 80%+. Prevent at build time. 90% aspirational. |
| **Evidence proves** | E-PRES-032 | Website screenshots are decorative. Use metric cards with data that proves the assertion. |
| **No image reuse** | E-PRES-033 | Each image on exactly one slide. Second occurrence → metric card or pull quote. |
| **Image audit before build** | E-PRES-030 | VIEW every captured image. Paywalls, redirects, generic pages = failed capture. |
| **Image readability** | E-PRES-026 | Evidence images ≥200px height. Thumbnails are decorative, not evidence. |
| **So-what gate** | Ghost deck | Every slide answers "so what?" + declares slide goal. Process-level in Step 2. |
| **Convergence gates** | E-PRES-031 | No "breathing slide" exemption for data slides. Q2 ≥80% fill mechanical. |
| **Base64 last** | E-PRES-034 | Base64 embedding is the final step, after PPTX export succeeds. |

### PPTX-Safe CSS Constraints (applied at Step 4 — HTML authoring)

PPTX limitations are design constraints from day one. If PPTX can't do it, don't build it in HTML.

| CSS Feature | PPTX Support | HTML Rule |
|-------------|-------------|-----------|
| `border-radius: 50%` | ROUNDED_RECTANGLE (fixed radius) | Use sparingly; will be rasterized as PNG |
| `radial-gradient`, `conic-gradient` | None | Avoid; use `linear-gradient` (2-stop) |
| `clip-path` | None | Avoid entirely |
| `backdrop-filter` | None | Avoid entirely |
| `box-shadow` | Approximate via python-pptx shadow | Simple drop shadows only |
| `linear-gradient` (2-stop) | Native GradientFill | Safe |
| Solid fills | Full RGBColor support | Preferred |
| `transform: rotate()` | python-pptx rotation | Safe |
| Complex SVG | None (rasterized) | Use simple shapes or rasterize intentionally |
| `overflow: hidden` with clipping | None | Content must fit within element bounds |

### HTML→PPTX Conversion Rules

| Rule | Source | What |
|------|--------|------|
| **Render at 960×540** | E-PRES-036 | 1 CSS px = 1/96" = exact PPTX native coordinates. `font_px × 0.75 = correct pt`. No custom scaling. |
| **Leaf preference** | E-PRES-037 | DOM walker extracts leaves, not parents. Parents contain all child text → duplicate overlapping text boxes. |
| **Google Slides verify** | E-PRES-035 | Upload to GDrive, Playwright screenshot each slide. Never verify via PDF or Preview. |
| **Coordinate unity** | E-PRES-036 | Positions AND fonts use same coordinate system. At 960×540, both match CSS 96 DPI spec. Layout YAML percentages are DPI-agnostic. |
| **Direct DOM extraction** | E-PRES-028 | html_to_pptx.py extracts from rendered HTML directly — inherently avoids sidecar staleness. |
| **Native font families** | E-PRES-029 | DOM extraction gives actual families ("Playfair Display"), not roles ("display"). No TokenResolver needed. |

### Failure Taxonomy (html_to_pptx.py)

| Level | Behavior | Examples |
|-------|----------|----------|
| **FATAL** | raise + exit | Playwright crash, no slides found, save failure |
| **RECOVER** | log + skip element | Zero-size, corrupt base64, unparseable color |
| **DEGRADE** | rasterize instead of native | SVG, complex CSS (gradients, clip-path, border-radius: 50%) |

### Anti-Patterns (AP1-AP11)

| AP | What | Rubric Impact |
|----|------|---------------|
| AP1 | Screenshot pasted as slide image | Q6 fail |
| AP2 | >5 distinct hues excluding photos | E-PRES-014, Q4 |
| AP3 | <40% fill on detail slides | E-PRES-006, Q2 |
| AP4 | Web-sized text on presentation slides | E-PRES-001, Q3 |
| AP5 | Inconsistent line-heights across slides | E-PRES-013, Q3 |
| AP6 | Font substitution without fallback | E-PPTX-003, Q6 |
| AP7 | Generic image not proving assertion | E-PRES-020, Q8 |
| AP8 | Slide doesn't serve locked vision | Q9 fail |
| AP9 | CSS-only fix for content problem | Empty space = missing content |
| AP10 | Skipping Context Review after screenshots | Fixing symptoms not causes |
| AP11 | Thumbnail strips as "evidence" (≤130px) | E-PRES-026, Q8 |

---

## 5. Stage Details

### Full Presentation Pipeline

**Step 0 — Vision & Requirements** `[HUMAN GATE — interactive]`
- **0a:** Input scan + clarifying questions (audience, goal, duration, constraints, tone)
- **0b:** Research support — recall.py for Austin's context, local materials, internet if directed
- **0c:** Lock vision (1 sentence) + requirements (bullet list) = source of truth for all subsequent steps
- **0d:** Content inventory + framework selection (mckinsey/editorial/data-forward/cinematic)
- **Output:** Locked vision + requirements. Every subsequent decision measured against these.

**Step 0.5 — Reference Analysis** `[MECHANICAL + HUMAN GATE]`
- **0.5a:** Austin provides a reference PPTX (or PDF-of-PPTX) — the design he wants to capture
- **0.5b:** `pptx_to_tokens.py` extracts palette, typography, spacing, hierarchy ratio
- **0.5c:** `pptx_to_layout.py` extracts approximate layout hints per slide (region positions as percentages). NOTE: these are hints, not SSOT — the 7-level heuristic cascade produces approximations
- **0.5d:** Playwright screenshots each reference slide at 960×540 — these are the visual ground truth for convergence scoring at Step 5
- **0.5e:** Produce design brief YAML: tokens + per-slide layout hints + screenshot paths
- **Gate:** Austin reviews design brief — confirms it captures what he likes about the reference. Lightweight review: tokens + layout diagram, not full iteration.
- **Output:** `OUTPUT/design/ref-brief-<slug>.yaml` + `OUTPUT/design/ref-screenshots/<slug>-s{N}.png`

**Step 1 — Structure** `[LLM]`
- Select framework from philosophy YAML (`TOOLS/config/design/philosophies/<name>.yaml`)
- Read `structure.slide_vocabulary`, `density_limits`, `ghost_deck_criteria`, `asset_guidance`
- **Output:** Framework-specific structure (Pyramid/Narrative/Evidence/Problem-Solution)

**Step 2 — Ghost Deck** `[LLM]`
- Assertion titles (complete sentences, not labels) + `so_what:` + `goal:` per slide
- Horizontal logic: titles alone read as cohesive persuasive essay
- Vertical logic: body evidence supports each assertion
- **Gate:** Ghost deck scored on assertion strength. Auto-block if score <18/25.
- **Output:** Ghost deck JSON/YAML with slide structure

**Step 3 — Executive Summary** `[LLM]`
- Slide 2 = full message. Three required perspectives:
  - Top-down: does the narrative arc hold?
  - Bottom-up: does every claim have sourced support?
  - "So what?" lens: does every slide answer why the audience should care?
- **Output:** Executive summary slide content

**Step 3.5 — Visual Plan + Grid** `[HUMAN GATE]`
- Grid decision (12-col, margins, gutters from tokens)
- Per-slide visual reasoning: what image BEST proves this assertion?
- Data output reasoning: charts, metrics from Python/research
- Space allocation + image candidates → present as HTML wireframes, not text descriptions
- **Output:** Visual plan approved by Austin

**Step 3.7 — Content Enrichment** `[LLM + AIOS tools]`
- recall.py batch search by theme (core, drill, errata)
- /deep-research for external evidence gaps
- idea-explore for cross-domain connections
- **Output:** Per-slide evidence brief (claim → source → figure → citation) + consolidated sources.md

**Step 3.8 — 3-Lens Expert Critique** `[LLM — 3 parallel agents]`
- Industry Insider: "Would the board buy this?"
- Technical Skeptic: "Can this actually be built?"
- Strategy Professor: "Is the logic rigorous?"
- **Output:** Must-address (🔴) vs should-address (🟡) findings

**Step 3.9 — Image Audit** `[LLM + Playwright]`
- Capture evidence images via Playwright at ≥1200px width
- VIEW each image — verify content, readability, assertion coherence (E-PRES-030)
- Failed captures (paywalls, redirects, generic pages) block build
- Image-to-slide mapping: each image under the specific claim it supports
- **Output:** Verified image set with base64 conversion (file paths during iteration)

**Step 4 — Build HTML** `[LLM — guided by design brief]`
- 960×540 viewport, design tokens from reference (Step 0.5) applied
- **Design brief drives layout:** LLM receives per-slide layout hints (region positions as %) from the reference. HTML should visually approximate the reference layout patterns — where the title goes, how many columns, content area proportions. Not pixel-for-pixel copy, but same spatial language.
- **PPTX-safe CSS only:** follow the PPTX-Safe CSS Constraints table. If PPTX can't render it natively, don't build it in HTML (or build it knowing it will be rasterized).
- `.slide-body` wrapper for vertical centering
- min-height on cards/elements to force canvas fill
- Sidecar JSON emitted alongside HTML for primary PPTX engine
- **Errata focus:** E-PRES-001 (font size), E-PRES-006 (canvas fill), E-PRES-014 (hues)

**Step 4.5 — Canvas Fill Gate** `[MECHANICAL]`
- Remove position:relative on slide-level classes (E-PRES-004)
- Viewport fill ≥80% width
- Title ≥48px, body ≥18px minimums
- Each slide: height:540px; overflow:hidden — split if overflow
- **Gate:** Automated check, auto-fix where possible

**Step 4.9 — HTML Approval** `[HUMAN GATE — blocks PPTX]`
- Austin reviews HTML in browser at full screen
- **Gate:** Austin approves at quality level per `pptx-quality-rubric.yaml` convergence.html_first_pass (SSOT) before ANY PPTX work
- All design iteration happens on HTML — PPTX is a one-shot export
- If not approved: iterate (Steps 4-4.5), re-present
- **Output:** "HTML APPROVED" — locks HTML as design source of truth

**Step 5.0 — Sidecar JSON Sync** `[MECHANICAL]`
- Re-extract all slide content from approved HTML into JSON (E-PRES-028)
- Diff HTML vs JSON for content drift
- Verify all image paths resolve, all element types have handlers
- **Gate:** JSON must match approved HTML exactly before PPTX export

**Step 5 — Convergence** `[LLM + Playwright — max 3 rounds]`
- **5a:** Playwright screenshot all slides at 960×540 (native PPTX resolution per E-PRES-036 — 1 CSS px = 1/96" = exact PPTX coordinates)
- **5b:** Score Q1-Q9 per slide (screenshot-before-score hard gate, E-PRES-017). Q10 scored post-export only
- **5b.5:** Reference Fidelity Check — the new comparison:
  - Load reference screenshots from Step 0.5
  - Side-by-side: HTML screenshot vs reference PPTX screenshot for each slide
  - Score: does HTML capture the layout patterns, typography hierarchy, color palette of the reference?
  - This is NOT pixel-perfect comparison — it measures design language fidelity (same spatial zones, same visual weight distribution, same color family)
  - Q1-Q9 rubric measures content quality. Reference fidelity measures design faithfulness. Both matter.
- **5c-5h:** See `.claude/skills/presentation/SKILL.md` Step 5 for authoritative sub-step ordering (SKILL.md = procedure SSOT). Summary:
- **5c (SKILL.md):** Context Review — the key step:
  - Top-down: re-read vision, ghost deck, requirements. Every slide serves the north star?
  - Bottom-up: re-read sources.md. Strongest sources actually on slides? All 🔴 findings resolved?
  - Per empty/weak slide: (1) add content, (2) add visual data, (3) add real-world image, (4) condense slides, (5) CSS fix only if content is already right
- **5d:** Image Coherence Review — view rendered images, check readability + assertion match
- **5e:** Fix → re-screenshot → re-score (if any dimension <6)
- Repeat up to 3 rounds until target met or diminishing returns

**Step 6 — Export PPTX** `[MECHANICAL — html_to_pptx.py]`
- Render at 960×540 (E-PRES-036) — exact coordinate mapping
- DOM walk → classify (native/rasterize/skip) → build python-pptx
- Debug output: `OUTPUT/debug/layout-classified.json`
- **Errata focus:** E-PPTX-001 (hex colors), E-PPTX-002 (EMU precision), E-PPTX-003 (font fallback), E-PPTX-004 (gradient/border-radius degradation)

**Step 6 — PPTX Review** `[HUMAN GATE — via Google Slides]`
- Upload to Google Drive, open in Google Slides via Playwright
- Screenshot each slide, compare vs HTML (E-PRES-035)
- Never declare PPTX done without visual review
- Iterate html_to_pptx.py handlers until delta is acceptable

**Step 7 — Design Capture** `[MECHANICAL + LLM]`
- Archive approved HTML + PPTX
- Capture learnings → errata growth
- Tag novel layouts as candidates for layout library (see Section 6)

### html_to_pptx.py — Internal Pipeline

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                     html_to_pptx.py                             │
  │                                                                 │
  │  ┌───────────┐    ┌────────────┐    ┌───────────────────────┐  │
  │  │ Phase 1   │    │ Phase 2    │    │ Phase 3               │  │
  │  │ EXTRACT   │───▶│ CLASSIFY   │───▶│ BUILD                 │  │
  │  │           │    │            │    │                       │  │
  │  │ Playwright│    │ native     │    │ _add_text()     ──┐  │  │
  │  │ @960x540  │    │ rasterize  │    │ _add_image()     │  │  │
  │  │           │    │ skip       │    │ _add_shape()   ──┼─▶│  │
  │  │ Per slide:│    │            │    │ _add_table()     │  │  │
  │  │ getBBox() │    │ overflow   │    │ _add_rasterized()┘  │  │
  │  │ getStyle()│    │ warnings   │    │                     │  │
  │  │ walkLeafs │    │            │    │ parse_css_color()   │  │
  │  │  → runs[] │    │ --debug    │    │ px_to_in()          │  │
  │  │           │    │ JSON dump  │    │ validate_roundtrip()│  │
  │  └───────────┘    └────────────┘    └───────────────────────┘  │
  └─────────────────────────────────────────────────────────────────┘

  Input:  HTML file (approved, 960×540 native, .slide/.active navigation)
  Output: Editable PPTX (python-pptx, exact coordinates)
  Debug:  OUTPUT/debug/layout-classified.json

  Accuracy: EXACT at 960×540 (1 CSS px = 1/96" = PPTX native)
  Known element-specific bugs (Phase 2 remaining):
  - Body paragraph walker: E-PRES-037 refinement needed for nested body text
  - Multi-run newlines: _add_text() newline→line-break mapping
  - Border-radius circles: E-PPTX-004 rasterize-fallback (CSS border-radius: 50%)
```

### Per-Step Errata Focus

| Step | Errata Focus | Common Failures |
|------|-------------|-----------------|
| 0 | Vision drift | Vision too vague → slides diverge |
| 2 | Ghost deck logic | Label titles, missing so-what/goal |
| 3.5 | Visual plan | No wireframes → builder improvises |
| 3.7 | Source quality | Unverifiable stats ($2.1B, "zero incidents") |
| 3.9 | Image capture | Failed captures (paywalls, redirects), wrong page |
| 4 | Build regression | Canvas fill, font sizes, grid not used |
| 4.9 | HTML approval skip | PPTX work before Austin approved HTML |
| 5 | Scoring bias | Scoring from metadata without screenshots (E-PRES-017) |
| 6 | Export corruption | Font substitution, element misalignment |

---

## 6. Layout Pattern Library

### Purpose

The layout library is a collection of **approved design patterns that guide HTML creation** (Step 4). It is NOT a PPTX export remapping tool. The LLM receives layout patterns as input when building HTML — "put the title at y=5%, content grid at y=20% spanning 60% width" — so the HTML naturally matches the design language.

### Lifecycle

```
  ┌────────────┐    ┌────────────┐    ┌──────────────┐    ┌────────────┐
  │ Reference  │───▶│ Design     │───▶│ HTML built   │───▶│ Approved   │
  │ PPTX       │    │ Brief      │    │ from brief   │    │ Pattern    │
  │            │    │            │    │              │    │            │
  │ Design     │    │ Tokens +   │    │ Austin       │    │ L-XXX-NNN  │
  │ Austin     │    │ layout     │    │ approves     │    │ .yaml      │
  │ likes      │    │ hints +    │    │ HTML look    │    │            │
  │            │    │ screenshots│    │ matches ref  │    │ + context  │
  └────────────┘    └────────────┘    └──────────────┘    │ + anti-pat │
                                                          └────────────┘
                                                               │
                                             Future decks ◄────┘
                                             search library at Step 4
```

### Selection Algorithm (runs at Step 4 — HTML creation, not Step 6 — export)

```
  20+ patterns in library
         │
         ▼
  ┌──────────────────┐
  │ Layer 1: Tags    │  density, slide_type, supports[], tags[]
  │ Filter: 20 → 8  │  Pure YAML search — no screenshots needed
  └────────┬─────────┘
           ▼
  ┌──────────────────┐
  │ Layer 2: Context │  "Good for ecosystems", anti-patterns
  │ Narrow: 8 → 3-5 │  AI reasons about intent, not just structure
  └────────┬─────────┘
           ▼
  ┌──────────────────┐
  │ Layer 3: Visual  │  Screenshot review of 3-5 finalists only
  │ Pick: 3-5 → 1   │  Human picks or requests novel layout
  └──────────────────┘
```

### Schema & Storage

- Layout files: `WORK/PROJECTS/ai-pptx-gen/layouts/L-XXX-NNN.yaml`
- Schema: `WORK/PROJECTS/ai-pptx-gen/schemas/schema-layout.yaml` (69 lines)
- Positions stored as **percentages** (DPI-agnostic, safe across coordinate systems)
- Metadata: tags, density, slide_type, supports[]
- Context: semantic guidance, anti-patterns, "good for" descriptions

---

## 7. Human Gates

| Gate | Step | What Austin Reviews | What Blocks |
|------|------|-------------------|-------------|
| **Vision Lock** | 0c | 1-sentence vision + requirements bullet list | All subsequent work uses wrong north star |
| **Reference Approval** | 0.5e | Design brief: tokens + layout diagram + screenshots | HTML built from wrong design DNA |
| **Visual Plan** | 3.5 | HTML wireframes with image candidates, grid layout, space allocation | Builder improvises layout without visual reasoning |
| **HTML Approval** | 4.9 | Full HTML in browser. Score per `pptx-quality-rubric.yaml` convergence.html_first_pass (SSOT) | ALL PPTX work blocked until approved. No exceptions |
| **PPTX Review** | 6 | Google Slides screenshots vs HTML side-by-side | PPTX declared done without visual verification |

**Gate protocol:** Present → Austin decides → if not passed, iterate and re-present. AskUserQuestion with diagnosis and proposed solution before implementing changes.

---

## 8. Locked Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | HTML-first workflow | Iterate HTML to approval; PPTX is one-shot export |
| 2 | Dual engine coexistence | slides_to_pptx.py (primary, fast) + html_to_pptx.py (refinement, exact). Different problems |
| 3 | 960×540 viewport = exact | 6 iterations (r7-r13). At 960×540: 1 CSS px = 1/96" = PPTX native. No custom scaling |
| 4 | Google Slides for verification | Never PDF — font substitution masks bugs (E-PRES-035, 5-point Q7 gap on Mid Model) |
| 5 | Canvas fill ≥80% hard gate | AI defaults to 8%; breathing exemption only for title/divider slides. 90% aspirational |
| 6 | Evidence proves, not decorates | Homepage screenshots ≠ evidence; data must prove assertion (E-PRES-032) |
| 7 | Layout YAML uses percentages | DPI-agnostic positions, safe across any coordinate system |
| 8 | Sidecar JSON re-synced at Step 5.0 | Not carried from initial build — staleness invalidates export (E-PRES-028) |
| 9 | Q1-Q10 rubric with mandatory gates | Q2<7 caps at 7/10 avg; Q6<8 caps at 8/10 avg |
| 10 | AP9: empty space = content problem | CSS padding ≠ fix; add evidence, data, images via Context Review (Step 5c) |
| 11 | python-pptx for final engine | CTO approved; full API, headless operation, layout library reuse |
| 12 | design_tokens.py zero python-pptx dep | Returns raw tuples; each pipeline wraps with RGBColor at own boundary |
| 13 | PPTX limitations = HTML design constraints | CSS features that can't survive export are avoided at Step 4, not handled at Step 6. If PPTX can't do it, don't build it in HTML |
| 14 | Layout patterns guide HTML creation | 1 approved layout (L-TITLE-001), 122 extracted but uncalibrated. Comprehensive library paused — focus on process quality. Revisit when 3+ decks hit 90% |
| 15 | CSS Grid is MANDATORY for all slide layouts | Every slide must use `display: grid` with explicit `grid-template-columns` and `grid-template-rows`. No `position: absolute` for content layout. Exception: creative/artistic slides verified via Playwright screenshot |
| 16 | White-space auto-scaling (mechanical) | After grid layout, measure: can text be zoomed 2× and still not overflow? If yes, zoom until overflow threshold (~80% fill). This is a mechanical check, not subjective — compute available space ÷ content size, scale text proportionally. Applied at Step 4 build time. Step 4.6 is the Brutal Honest Critic (gestalt self-review) |
| 17 | Errata check is a HARD GATE before any HTML | Read `TOOLS/errata/presentation_design.md` BEFORE writing any HTML. Not after. Not optional. Every errata pattern is a known failure that must be prevented at build time. Skipping errata = repeating known mistakes |

### 8.5 Process Enhancement Decisions (2026-05-01)

**Goal:** Raise default first-pass quality from 60% to `pptx-quality-rubric.yaml` convergence.html_first_pass target (80%, lowered 2026-05-02) through process improvements, not more code.

| Decision | Detail |
|----------|--------|
| Q10 Export Fidelity added | 10th scoring dimension (100-point total). Measures PPTX vs HTML visual similarity. Gate: Q10 < 8 → iterate export handlers |
| Step 4.6 Brutal Honest Critic | Gestalt self-review before human gate. 5-point checklist: Professional, Canvas, Typography, Diagram, Spacing. NOT Q1-Q10 scoring |
| Failure prevention table (F1-F6) | Build-time warnings in Step 4: content-sized elements, web-sized text, arbitrary spacing, rectangles for funnels, gray placeholders, mixed letter-spacing |
| Scenario-specific guardrails | Per-type rules for all 16 slide components: canvas fill %, typography minimums, spacing rules, anti-patterns. In `presentation-components.md` |
| 6 signature slides as benchmark | BCG 10 (chart+analysis), 30 (stacked bar), 35 (dense table); Douyin 3 (4-column data), 9 (funnel vs snowball), 12 (FACT framework). Baseline: 60% |
| Convergence targets | Per `pptx-quality-rubric.yaml` convergence section (SSOT): 80% first HTML pass (lowered 2026-05-02), 95% after 3 rounds, Q10 ≥ 9/10 for PPTX |
| Convergence fix (2026-05-02) | Dead zone closed: "any Q<6" replaced with multi-condition (avg < YAML target OR any Q<7 OR gate violation). One-bottleneck-per-round (TOC pattern). Oscillation detector + regression gate. YAML is SSOT for all numeric targets. Research: `OUTPUT/research/convergence-architecture-2026-05-02/` |
| Two reference PPTXs | BCG (programmatic token extraction, `ref-bcg-template.yaml`) + Douyin Xiaodian (manual token extraction from PDF, bilingual EN/中文, `ref-douyin-tokens.yaml`) |
| Prevention > screening | Errata rules belong in build prompt (Step 4), not only in post-build scoring (Step 5). AI knows what NOT to do before writing HTML |

### Known Operational Problems

| ID | Problem | Mitigation |
|----|---------|------------|
| P1 | AI drifts from pipeline chain in long sessions | Re-read pipeline reference at every HUMAN GATE. Consider chunking into per-step skills |
| P2 | Canvas fill unsolved at CSS level | AP9: treat as content problem. Use Step 5c Context Review. Investigate CSS Grid explicit row sizing |
| P3 | Regressions across handoffs | Grep-based checks for known-bad strings in handoff verification section |
| P4 | Sidecar JSON missing from initial builds | Step 4 must emit JSON alongside HTML. Auto-check: `test -f *-slides.json` |
| P5 | Q2/Q7 oscillation trap in convergence | Oscillation detector: if round N bottleneck = round N-2 bottleneck, exit with best-scoring round. Joint resolution when Q2/Q7 within 1 point |
| P6 | Self-scoring leniency on Q7 (polish) | Deferred: decompose Q7 into mechanical sub-checks (gap consistency, font-size count, alignment grid snap). Currently mitigated by regression gate |

---

## 9. Phased Delivery

### Phase 1: DOM Extraction Engine ✅ COMPLETE
`TOOLS/scripts/html_to_pptx.py` — 977 lines, 3-phase pipeline (extract → classify → build).
6 iterations (r7→r13). Final insight: viewport must match slide DPI, not font scale factor.
Exact coordinate mapping at 960×540. Registered as `html-to-pptx` in registry.yaml.

### Phase 2: Google Slides Visual Verification ✅ COMPLETE (2026-04-30)
r13 verified — slides 1, 2, 3, 4, 6, 9 checked in Google Slides. Remaining 6 slides (5, 7, 8, 10, 11, 12) pending GSlides upload.
**Bug fixes applied (2026-04-30):**
- [x] Body paragraph walker — E-PRES-037: recursive `hasVisibleDescendant()` + post-extraction containment dedup. Slide 4: 33→25 elements.
- [x] Multi-run text newlines — two-pass paragraph group rewrite, eliminates `first_para` leak.
- [x] Border-radius rasterization — E-PPTX-004: classification (ratio > 0.4 of min dim, guarded by br > 4px) + Playwright element capture during extraction + image insertion in build. S9 radial hub correctly rasterized as PNG.

**AeSlides thresholds validated (2026-04-30):** fill <40% correctly warns on title/close slides (S1:6%, S12:12%) and diagrams (S9:21%). Borderline detail slides (S3:38%, S10:36%) flagged as early warning — caught by Q2 ≥80% gate at Step 4.5. Collision detection: 1 per affected slide (S4, S8, S11) — real overlaps, not systematic false positives. Thresholds retained as-is.

**Q8-Q9 calibration anchors added (2026-04-30):** All 4 reference templates scored on Q8 (Visual Evidence) and Q9 (Vision Adherence). Templates score Q8:6-8 (images serve design, not evidence) and Q9:7 (neutral default — no external vision). Score range: 7.0-7.9 avg on full Q1-Q9.

### Phase 3: Layout Library Infrastructure ✅ COMPLETE (2026-04-30)
12 layouts extracted from Smart Tickets deck via `TOOLS/scripts/extract_layouts.py` (config-driven).
- [x] `extract_layouts.py` — config-driven role classification (YAML, not hardcoded), selector-family grouping + chaining generic assignment + post-assignment y-band split
- [x] `TOOLS/config/design/layout-extraction.yaml` — externalized selector→role mapping, thresholds, merge rules
- [x] 12 layout YAMLs in `layouts/` (L-TITLE-001 through L-CLOSE-001), 3-8 content regions each
- [x] `--layout-library <dir>` flag on html_to_pptx.py — non-blocking, runs after classification
- [x] `layouts/index.yaml` — schema v1 with origin field for Phase 4 dual ingestion
- [x] Schema amended with 4 forward-compat fields: `origin`, `slide_master`, `aspect_ratio`, `thumbnail`
- [x] Registered `extract-layouts` in registry.yaml with config reference
- [x] Verified: S7 2×2 grid (4 cells via y-band split), S9 radial (5 spokes via 3% threshold), S3 stat cards unified (min-elements gate prevents false split)

### Phase 4: Dual Ingestion Pipeline ✅
- [x] `pptx_to_layout.py` (380 lines) — EMU→percentage conversion via adapter pattern
- [x] 7-level role classification cascade: placeholder → shape type → decorative → position → text pattern → font size → default
- [x] Style-family grouping (font-size bucketing) replaces CSS-family grouping
- [x] Config-driven: `pptx_roles` section in `layout-extraction.yaml` (placeholder map, position rules, text patterns, thresholds)
- [x] Tested against `st-r2-verified.pptx`: 12 layouts, all within tolerance, S1=title, S12=close, S3=data with stat_value
- [x] Registered `pptx-to-layout` in `registry.yaml`
- [x] Importable API: `extract_pptx_layouts(pptx_path)` → list[dict]
- [x] Reuses 12 functions from `extract_layouts.py` (write_layout_yaml, _pct_box, _auto_tags, etc.)
**Known trade-offs:** PPTX path produces fewer, larger regions than HTML (no CSS selectors for fine-grained families). Radial/spoke/era detection relies on CSS classes in HTML but falls back to editorial in PPTX. Professional PPTXs with placeholder types will produce better classification.

### Phase 4.5: Shared Module Extraction ✅ (2026-04-30)
- [x] `TOOLS/lib/layout_utils.py` (263 lines) — 15 shared functions extracted from extract_layouts.py
- [x] `extract_layouts.py` updated: imports from layout_utils, re-exports under old names for compat
- [x] `pptx_to_layout.py` updated: imports from layout_utils directly (no underscore prefixes)
- [x] `html_to_pptx.py` updated: lazy import uses layout_utils for --layout-library path
- [x] `sys.path.insert` hack removed from pptx_to_layout.py's layout imports (retained for analyze_pptx sibling import only)
- [x] VIEWPORT_W/VIEWPORT_H constants defined once in layout_utils (DRY)

### Phase 5: Reference PPTX Theme Inheritance ✅ (2026-04-30)
`--reference` flag for html_to_pptx.py. Opens existing PPTX as template base.
Preserves slide masters, theme colors, font themes. Uses Blank layout from reference.
Content positions from DOM extraction unchanged. Fail loudly on aspect ratio mismatch,
corrupt files, or missing layouts. Layout cloning deferred to Phase 7 (requires selection intelligence).
- [x] `_prepare_template(reference_path)` — load, validate 16:9, strip all slides via XML manipulation
- [x] `_find_blank_layout(prs)` — name-based search (no hardcoded indices), fewest-placeholders fallback, FATAL if none
- [x] `_extract_theme_fonts(prs)` — parse OOXML theme XML for majorFont/minorFont via lxml
- [x] `_apply_run_style` modified — heading font (>20pt) / body font override when theme fonts available
- [x] `--reference` CLI flag wired, composable with `--layout-library` and `--debug`
- [x] Fail-loudly gates: non-existent file, corrupt PPTX, wrong aspect ratio, no usable layout — all FATAL
- [x] Verified: 199 elements identical with/without reference; fonts change from HTML families to theme families
- [x] Tested: agency.pptx (Calibri Light/Calibri), produce-review.pptx, mid-model.pptx; bcg-template.pptx correctly rejected (4:3)
**Scope decision:** Theme inheritance only. Layout cloning later deleted — contradicts HTML-first (Locked Decision #1).

### Phase 5.5: Reference → HTML Fidelity Validation [HUMAN GATE — in progress]
End-to-end test of the reference-first pipeline. For each reference PPTX:
1. Run Step 0.5 (extract design brief: tokens + layout hints + screenshots)
2. Build HTML guided by the design brief (Step 4)
3. Screenshot HTML and reference side-by-side
4. Austin scores: does the HTML capture the layout patterns, color language, and typography hierarchy?
5. Iterate until fidelity is acceptable
6. If a layout pattern is novel and approved, it enters the library with `calibration_status: approved`
**Validates:** the entire PPTX → design brief → HTML flow, not just coordinate extraction accuracy.
**Agency review (2026-05-01):** 1/14 layouts approved (L-TITLE-001), 13 rejected — extraction quality too noisy for non-title slides. Floor-anchor: all 3 too sparse. Remaining: mid-model (42), produce-review (51).
**Blocked by:** Human availability + reference_analyze.py orchestrator (not yet built).

### Phase 6: Integration ✅ COMPLETE (2026-04-30)
- [x] `--use-layouts` wired into `pptx-from-source` chain step 8
- [x] `--reference` already in chain step 8 (was already there)
- [x] Layout flywheel step 8.5 added to chain
- [x] SKILL.md Step 6 updated with correct flag names and command template
- [x] Default layout directory: `WORK/PROJECTS/ai-pptx-gen/layouts/`

### Phase 7: Layout Selection Intelligence ✅ COMPLETE (2026-04-30)
2-layer selection: L1 (tag Jaccard) → top-k(8) → L2 (structural role overlap) → best above threshold(0.35).
Match ratio gate (`min_match_ratio: 0.6`) prevents mixed-coordinate-system collisions: only remaps when ≥60% of elements match layout regions. CTO-reviewed, 37 tests.
- [x] `TOOLS/lib/layout_select.py` (530 lines) — `SlideProfile`, `LayoutMatch`, `select_layout()`, `match_elements_to_regions()`, `remap_elements()` with deep-copy guard
- [x] `TOOLS/lib/layout_utils.py:145-210` — shared `classify_role_html()`, `infer_slide_type()`, `parse_px()`
- [x] `TOOLS/scripts/html_to_pptx.py:1282-1365` — `--use-layouts DIR` CLI flag + per-slide orchestration + post-remap quality check + match ratio gate + enriched debug JSON
- [x] `TOOLS/config/design/layout-extraction.yaml:149-173` — all scoring weights config-driven: L1/L2 weights, blend ratio, threshold, top-k, min_match_ratio, shape config
- [x] `TOOLS/tests/test_layout_select.py` (723 lines) — 37 TDD tests covering profiling, scoring, matching, remapping, shape vectors, edge cases
- [x] CTO review: module split (layout_select vs layout_utils), zero hardcoded magic numbers, dead alias cleanup, cache poisoning fix
- [x] Post-remap collision fix: `min_match_ratio: 0.6` gate reduced collisions 110→9 on Smart Tickets deck
**Layout cloning** deleted — contradicts HTML-first (Locked Decision #1). If HTML matches reference, PPTX export preserves it.
**Layer 2 LLM context reasoning** deferred — `context`/`anti_patterns` fields need approved layouts from Phase 5.5 reviews.
**Layer 3 visual review** deferred — `thumbnail` field null on all layouts; populate when library reaches 20+ approved patterns.

### Phase 7b: Reference Fidelity Automation [not started]
Build automated comparison tooling to reduce human effort in convergence loop:
- Structural similarity scoring between HTML screenshots and reference screenshots
- Layout region overlap measurement (are spatial zones in the same positions?)
- Palette distance metric (does the HTML use the same color family as the reference?)
- Typography hierarchy comparison (heading/body/detail size ratios match?)
**Replaces:** Layout cloning (deleted — cloning PPTX placeholders bypasses HTML-first, contradicts Locked Decision #1).
**Prerequisite:** At least 3 reference PPTX designs processed through the full pipeline.

### Phase 8: Vector Shape Search ✅ COMPLETE (2026-04-30)
Prerequisite met: 122 > 50 layouts. Spatial geometry vectors for shape-based layout matching.
Pure geometry (no LLM embedding), brute-force cosine (no vector DB at 122 items), blends into L2 scoring.
- [x] `shape_vector()` — flattens content region bboxes into 65-dim vector (16 slots × 4 coords + density)
- [x] Canonical sort by (y, x) — input-order invariant. Structural roles filtered.
- [x] `_cosine_sim()` — pure Python, no dependencies
- [x] `_score_shape()` — cosine similarity with min_content_regions gate and dimension mismatch guard
- [x] `SlideProfile.shape_vec` — computed from element bboxes normalized via viewport (960×540)
- [x] `LayoutMatch.shape_score` — carried through to debug JSON
- [x] `load_layout_library()` precomputes `_shape_vec` on all 122 layouts using config `max_content_slots`
- [x] Blend formula: `l2_blended = (1 - shape_w) * l2_norm + shape_w * shape_score`
- [x] Default `shape_weight: 0.0` — zero behavior change until explicitly activated after calibration
- [x] CTO review: 7 CAUTIONs, 3 fixed (ZeroDivisionError guard, dimension mismatch guard, config threading)
- [x] 14 Phase 8 tests including backward compat (bit-identical scores), truncation, viewport normalization
**Extensibility path:** When library crosses ~300 layouts, add sqlite-vec KNN index as a build step. `shape_vector()` and vector format remain identical.

### Phase 9: Deferred Items [backlog]

**Low risk / small scope:**
- [ ] 3+ gradient stop support — `html_to_pptx.py:228-229`, first+last collapse is interim
- [x] Dead `font_fallbacks` config key — deleted from `layout-extraction.yaml`, design_tokens.py is now authoritative
- [ ] 30 duplicate layout codes — L-TITLE-001 in 5 subdirectories, `source` field disambiguates. Cross-directory search uses compound keys.
- [ ] 7 `sys.exit(1)` calls in library functions — `html_to_pptx.py` has exit calls in functions that could be imported. Flag if reusing outside CLI.
- [ ] Scoring weight calibration — run `--use-layouts` on 3+ decks, inspect debug JSON, tune weights. CTO flagged 0.35 threshold and Jaccard weighting may need adjustment.
- [ ] Shape weight activation — change `shape_weight` from 0.0 to 0.3, validate against real decks

**Medium risk / requires iteration:**
- [ ] Test coverage for core pipeline — 88% of pipeline functions untested. Priority: `_build_pptx`, `_classify_elements`, `_group_elements`, `px_to_in`, `_check_layout_quality`, `auto_tags`, `auto_supports`
- [ ] Layer 2 LLM context reasoning — blocked by approved layouts with `context`/`anti_patterns` filled
- [ ] Reference fidelity scoring automation — structural similarity, layout region overlap, palette distance metrics (Phase 7b)
- [ ] `reference_analyze.py` orchestrator — compose pptx_to_tokens + pptx_to_layout + Playwright screenshots into single CLI producing design brief YAML

**Deprioritized (less critical under reference-first flow):**
- [ ] Scoring weight calibration for `--use-layouts` remapping — less important if HTML already matches reference layout
- [ ] Shape weight activation (0.0 → 0.3) — remapping is fallback, not primary alignment
- [ ] Layer 3 visual review — `thumbnail` field null; will populate when library reaches 20+ approved patterns

**Convergence architecture — deferred after research (2026-05-02):**
Research: `OUTPUT/research/convergence-architecture-2026-05-02/sources.yaml`
- [ ] Best-across-iterations watermark — track best score across rounds, select from candidate pool (Self-Refine pattern). Currently using latest round. Measure oscillation frequency on real decks first.
- [ ] Evidence anchoring per Q dimension — Rulers framework: scores require extractive evidence (measured + reference + delta). Currently scores are numbers without justification. Heavy to implement.
- [ ] Per-slide-type scoring floors — data slides Q5≥8, visual slides Q8≥8. Novel (no prior art in AeSlides/SlideAudit/BCG). Measure per-type Q variance on real decks first.
- [ ] Minimum entry threshold (75%) — below 75% avg, regenerate don't converge. Need first-pass score data from real decks.
- [ ] Bottleneck routing table in YAML — CTO ruled: keep routing as procedure in SKILL.md, not config in YAML. Re-evaluate if routing grows past 9 entries.
- [ ] Content re-enrichment mid-convergence — IMPROVE + Self-Refine consensus: no backtracking to earlier stages. If content is bottleneck, exit convergence with human gate, re-enrich at Step 3.7, restart Step 4.
- [ ] Q7 mechanical decomposition — Expert 2: Q7 (polish) is most vulnerable to self-scoring leniency. Decompose into named sub-checks (gap consistency ±2px, font-size count, alignment grid snap). Score = minimum, not average.
- [ ] Centroid computation script — E-PRES-015 needs pre-computed centroid values from Playwright/DOM. LLM cannot estimate from HTML. Build script that dumps centroid JSON alongside screenshots.
- [ ] F-table expansion F11-F13 — decorative panel (E-PRES-010), card sizing intent (E-PRES-009), 2-row cards (E-PRES-011). Low priority — caught at scoring time via bright lines.
- [ ] Component guardrails in presentation-components.md — Q2 exemption list, decorative panel detection. Low priority — covered by rubric bright lines.

### Phase 1B: Grid Recipes Rewrite [COMPLETE — 2026-05-01]
160 lines at `.claude/skills/html/templates/presentation-components.md:607-772`.

### Phase 1C: SKILL Contradictions [PENDING]
5 line-level fixes: presentation/SKILL.md (245/256/257), html/SKILL.md (95-96). Errata prevention mapping table.

### Phase 1D: Q10 Rubric Header [PENDING]
Add Q10 Export Fidelity to design-rubric/SKILL.md. Update header Q1-Q7→Q1-Q10.

### Phase 2A-2G: Prevention Architecture [MOSTLY COMPLETE]
F-table F1-F10 (2A, DONE). Component guardrails all 15 types (2B, DONE). Errata prevention mapping F→E (2D, DONE). Canvas fill 3-layer sequence in SKILL.md Step 4 (2G, DONE 2026-05-02). Remaining: content density reference table (2F, nice-to-have — values exist per component, not centralized).

### Phase 3b: Pipeline Restructure [DEFERRED]
Step renumbering (4.0-4.9), convergence stops, wireframe Step 3.5, narrative flow.

### Phase 5b: Ticketmaster Validation [DEFERRED]
Validate dual engines via existing Ticketmaster data.

### Phase 7c: V3 Bug Verification [DEFERRED]
Use signature-slides-v3-2026-05-01.html as regression test.

### Future: Domain-Expert Consulting Agent [IDEA]
Composes /consulting-analysis + /deep-research + /design-rubric. Step 3.8 experts → agent invocations.

### Future: YAML-Python Unification (LEGO) [IDEA]
`load_rubric_config()` function reads `pptx-quality-rubric.yaml` and exposes typed values. Then `slides_to_pptx.py` and `html_to_pptx.py` validate against the SAME font minimums the scoring rubric uses.

**Current deck status:** Smart Tickets at 74/90, path to 80/90 in `smart-tickets-80-90-plan.md`.

---

## 10. SSOT Health (2026-05-02 Audit)

### Authoritative Sources

| Domain | SSOT File | Consumers |
|--------|-----------|-----------|
| Numeric thresholds (targets, gates, font mins) | `TOOLS/config/design/pptx-quality-rubric.yaml` | SKILL.md, design-rubric, design-pipeline, convergence loop |
| Coordinate constants (viewport, DPI, scaling) | `TOOLS/lib/design_tokens.py` | html_to_pptx.py, slides_to_pptx.py, pptx_to_layout.py |
| Known failure patterns | `TOOLS/errata/presentation_design.md` | Step 4 build gate, F-table, convergence diagnosis |
| Font role classification | `pptx-quality-rubric.yaml` font_role_thresholds | pptx_to_tokens.py, reference-extract SKILL.md |
| Decisions & architecture | This file (MEGAPLAN) | All skills and agents |
| Step procedures | `.claude/skills/presentation/SKILL.md` | LLM execution |

### Pipeline Data Contract Map

```
Reference PPTX → [pptx_to_tokens.py] → OUTPUT/design/ref-<slug>.yaml
Reference PPTX → [pptx_to_layout.py] → layouts/<slug>/L-*.yaml
Reference URL  → [/reference-extract] → OUTPUT/design/ref-<slug>.yaml (same schema)
                                          ↓
Step 0-3.9 → [LLM + tools] → ghost deck + vision + evidence
                                          ↓
Step 4 → [LLM builds HTML] → OUTPUT/html/presentation-<slug>.html
Step 4 → [LLM emits JSON]  → OUTPUT/html/presentation-<slug>-slides.json
                                          ↓
Step 5 → [convergence loop] → approved HTML + re-synced JSON (Step 4.95)
                                          ↓
Step 6a → [slides_to_pptx.py] → sidecar JSON + tokens YAML → PPTX (PRIMARY)
Step 6b → [html_to_pptx.py]   → approved HTML → PPTX (REFINEMENT)
                                          ↓
Step 6c → [Google Slides + Playwright] → verification screenshots
Step 6d → [pptx_to_layout.py --verify] → layout capture (flywheel)
```

### Key Relationship: font_minimums vs design_tokens.py

- `pptx-quality-rubric.yaml` font_minimums = presentation BUILD minimums (CSS px: title≥48, body≥18)
- `design_tokens.py` thresholds = CLASSIFICATION boundaries (pt: what counts as heading vs body)
- These are DIFFERENT concepts. A font can satisfy the minimum (≥18px body) but be classified as "small" by the classification threshold (<13pt). The classification drives role assignment; the minimum drives validation.

---

## 11. Key Files

| File | Lines | Status | Purpose |
|------|-------|--------|---------|
| `TOOLS/lib/design_tokens.py` | 181 | ✅ Built (SSOT) | **SSOT** — viewport, slide dims, DPI scaling, font thresholds, safe fonts, color parsing, coordinate conversion |
| `TOOLS/tests/test_design_tokens.py` | 170 | ✅ Built (SSOT) | 42 TDD tests: known-good values snapshot, color parsing, hex roundtrip, conversions |
| `TOOLS/scripts/html_to_pptx.py` | ~1350 | ✅ Built (Phase 7) | Final PPTX engine — DOM extraction + `--use-layouts` + `--reference` + match ratio gate |
| `TOOLS/lib/layout_select.py` | 530 | ✅ Built (Phase 7-8) | Layout selection: 2-layer scoring + shape vectors + matching + remapping |
| `TOOLS/lib/layout_utils.py` | 358 | ✅ Built (Phase 4.5) | Shared layout functions: geometry, config, role classification, YAML I/O |
| `TOOLS/scripts/extract_layouts.py` | 400 | ✅ Refactored (Phase 4.5) | HTML-specific layout extraction (imports shared from layout_utils) |
| `TOOLS/config/design/layout-extraction.yaml` | 173 | ✅ Extended (Phase 8) | Selector→role mapping, thresholds, merge rules, selection scoring, shape config |
| `layouts/**/*.yaml` | 122 files | ✅ Generated (4 dirs) | Layout library across agency, floor-anchor, mid-model, produce-review |
| `layouts/index.yaml` | 1 file | ✅ Generated | Layout index with origin field |
| `TOOLS/tests/test_layout_select.py` | 723 | ✅ Built (Phase 7-8) | 37 TDD tests: profiling, scoring, matching, remapping, shape vectors |
| `TOOLS/scripts/slides_to_pptx.py` | 1255 | ✅ Exists | PRIMARY PPTX engine — sidecar JSON |
| `TOOLS/scripts/analyze_pptx.py` | 545 | ✅ Exists | PPTX metrics analysis |
| `TOOLS/scripts/pptx_to_tokens.py` | 246 | ✅ Exists | Reference PPTX → design tokens |
| `TOOLS/scripts/pptx_review_cockpit.py` | 386 | ✅ Exists | 3-panel review HTML for PPTX gate |
| `TOOLS/scripts/pptxgen/engine.mjs` | 262 | ✅ Exists | PptxGenJS alternative engine |
| `TOOLS/scripts/pptx_to_layout.py` | 380 | ✅ Built (Phase 4) | PPTX → layout hints extraction (7-level cascade, approximate) |
| `TOOLS/scripts/reference_analyze.py` | — | 📋 Planned | Step 0.5 orchestrator: tokens + layout hints + screenshots → design brief YAML |
| `TOOLS/config/design/pptx-safe-css.yaml` | — | 📋 Planned | PPTX-safe CSS constraint list, loaded at Step 4 |
| `.claude/skills/presentation/SKILL.md` | 484 | ✅ Active | 3-mode presentation skill |
| `.claude/skills/design-rubric/SKILL.md` | 272 | ✅ Active | Q1-Q10 rubric + anti-patterns |
| `TOOLS/errata/presentation_design.md` | 253 | ✅ Active | 37 errata rules (E-PRES + E-PPTX) |
| `TOOLS/config/design/pptx-quality-rubric.yaml` | 138 | ✅ Updated | Q1-Q10 rubric config (v2) |
| `TOOLS/config/design/pptx-quality-standards.yaml` | 682 | ✅ Active | Evidence-grounded design standards |
| `TOOLS/config/design/pptx-calibration-log.yaml` | 199 | ✅ Active | Anchor scores + round data |
| `schemas/schema-layout.yaml` | 74 | ✅ Amended (Phase 3) | Layout YAML template + 4 forward-compat fields |
| `schemas/schema-extraction.yaml` | 86 | ✅ Defined | Debug extraction JSON |

---

## 12. Verification & Quality

### Four-Level Verification Stack

```
  Level 0: Reference Fidelity           ← Design-level (Step 5b.5)
  │ Does HTML capture the reference design language?
  │ Side-by-side: HTML screenshot vs reference PPTX screenshot
  │ Checked BEFORE PPTX export — if HTML doesn't match reference, no point exporting

  Level 1: validate_roundtrip()        ← Code-level
  │ slide count matches, per-slide element counts, no exceptions on reopen

  Level 2: analyze_pptx.py             ← Metrics-level
  │ canvas fill (target ≥80%), font range, color palette, layout distribution

  Level 3: Google Slides + Playwright   ← Visual-level (the REAL test)
  │ Upload → screenshot each slide → side-by-side diff vs HTML → iterate
  Level 0 gates everything. Level 3 is the REAL validation. Levels 1-2 are automated gates.
```

### Q1-Q10 Rubric (compact)

| Q | Dimension | Gate | Key Metric |
|---|-----------|------|------------|
| Q1 | Structure & Narrative | — | Ghost deck titles tell complete story |
| Q2 | Canvas Utilization | **<7 caps at 7** | Fill ≥80% on detail slides |
| Q3 | Typography & Hierarchy | — | 3-level hierarchy, readable at distance |
| Q4 | Color & Harmony | — | ≤5 hues, WCAG AA, palette adherence |
| Q5 | Data Presentation | — | Data-ink ratio, no chartjunk (Tufte) |
| Q6 | Editability & Fidelity | **<8 caps at 8** | ≥90% native shapes, editable text |
| Q7 | Professional Polish | — | Alignment ±2px, spacing rhythm |
| Q8 | Visual Evidence | — | Images prove assertions, not decorate |
| Q9 | Vision Adherence | — | Every slide serves locked Step 0 vision |
| Q10 | Export Fidelity | **<8→iterate** | PPTX vs HTML visual match |

**Target:** 90/100 (9.0 avg). **Convergence:** 3 consecutive rounds, human-AI gap max 0.5.

Full rubric: `TOOLS/config/design/pptx-quality-rubric.yaml` (v2).
Full criteria: `.claude/skills/design-rubric/SKILL.md`.

---

## 13. Evidence Base

### Calibration Anchors

| Template | AI Score | Human Notes |
|----------|----------|-------------|
| Mid Model | 7.0 | Q1:4, Q7:4 — text overlaps lines 15-18, 25. Font substitution masked in PDF |
| Agency | 7.1 | Format/fill good. Letters clipping intentional design |
| BCG | 7.6 | Best content anchor — assertion titles, dense data |
| Produce Review | 8.0 | Highest execution metrics. Minimal palette |
| Floor Anchor | 3.1 | 3 slides, label titles, content islands — ensures rubric discriminates |

### Session Learning (r7→r13)

6 iterations to discover: the problem was never font scale — it was rendering at the wrong resolution. At 960×540, CSS standard px→pt (×0.75) matches PPTX's 96 DPI natively.

### Academic References

- **SlideAudit** (UIST 2025): 27 flaw categories across 5 dimensions, 2,400-slide dataset. GPT-4o with taxonomy prompting: F1 0.655. Strong coverage of Q2 (canvas), Q3 (typography), Q4 (color), Q7 (polish). **Zero coverage** for Q1, Q5, Q6, Q8, Q9 — our rubric's differentiation is exactly in the semantic/intentional dimensions SlideAudit can't reach. Notes: `Drill/99. AI Notes/Learning/Papers/SlideAudit - Dataset and Taxonomy for Automated Evaluation of Presentation Slides.md` + `SlideAudit Taxonomy to Q1-Q9 Mapping.md`.
- **AeSlides** (arXiv 2026): 4 verifiable layout metrics that outperform VLM scoring (F1 0.47-0.83 vs 0.24-0.73 GPT-5.2). Maps to Step 4.5 as mechanical HTML-level checks. Notes: `Drill/99. AI Notes/Learning/Papers/AeSlides - Incentivizing Aesthetic Layout in LLM-Based Slide Generation via Verifiable Rewards.md` + `AeSlides Metrics to PPTX Pipeline Mapping.md`.
  - **Excessive Whitespace** → Step 4.5, Q2 gate (upgrades E-PRES-006 to pixel-level measurement, F1 0.80) — **P1 priority**
  - **Element Collision** → Step 4.5, Q2+Q7 (DOM bounding-box overlap detection, no current coverage) — **P2 priority**
  - **Aspect Ratio Compliance** → Step 4.5, Q2 (binary viewport verification)
  - **Visual Imbalance** → Step 5, Q7 (centroid-offset signal, d>2.0 caps Q7 at 6 without justification)
- **AutoPresent/SlidesBench** (CVPR 2025): First slide generation benchmark, 585 test slides.
- **Self-Refine** (NeurIPS 2023): Iterative refinement with self-feedback. Key insight for convergence: quality can oscillate — track best across iterations, not just latest. Task-specific `is_refinement_sufficient` with score threshold (0.7-0.85) + max iterations (default 3).
- **Rulers** (arXiv 2026): Locked rubrics compiled to immutable JSON. Evidence-anchored scoring — high scores mathematically impossible without grounding. Anti-halo constraint forces differentiated per-dimension reasoning. Deferred for future rubric hardening.
- **IMPROVE** (arXiv 2025): One-component-at-a-time pipeline refinement. Forward-only with conditional revert. Predefined constant interface prevents cascading. Causal attribution requires isolation — directly supports one-bottleneck-per-round.
- **Autorubric** (arXiv 2026): Weighted per-dimension scoring with negative penalties for anti-patterns. CANNOT_ASSESS handling. No built-in convergence detection.
- **Theory of Constraints**: Fix ONE constraint, re-identify. Most systems have 1 constraint. No exit condition — perpetual improvement. Maps to our one-bottleneck-per-round convergence pattern.

### Related Artifacts

| Artifact | Path |
|----------|------|
| Architecture diagram (HTML) | `OUTPUT/html/visual-aid-pptx-pipeline-architecture-2026-04-29.html` |
| Layout research | `WORK/PROJECTS/design-system/docs/pptx-layout-research-2026-04-29.md` |
| 80→90 plan | `WORK/PROJECTS/design-system/docs/smart-tickets-80-90-plan.md` |
| Debug extraction | `OUTPUT/debug/layout-classified.json` |
| Latest PPTX | `OUTPUT/smart-tickets-r13.pptx` |
| Test HTML source | `OUTPUT/html/presentation-smart-tickets-r2-2026-04-28.html` |
