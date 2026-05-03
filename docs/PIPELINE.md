# Pipeline — Steps 0-7 Reference

Human-readable reference for the full presentation pipeline. The authoritative version is `.claude/skills/presentation/SKILL.md`.

## Step 0: Vision & Requirements (HUMAN GATE)

Interactive. AI asks, user decides:
- **Audience:** Who? What do they know? What's their bias?
- **Goal:** ONE thing you want them to do/feel/remember?
- **Duration:** Minutes? (drives slide count)
- **Constraints:** Required content, format rules, grading rubric?
- **Tone:** Consulting? Creative? Academic? Casual?

**Output:** Vision (one sentence) + Requirements (bullet list). These are the SSOT for the entire pipeline.

## Step 0.5: Reference Analysis (optional)

If user provides a reference PPTX:
1. `hippt-tokens <ref.pptx> --slug <name>` → design tokens YAML
2. `hippt-layouts <ref.pptx> --out output/layouts/<slug>/ --verify` → layout hints
3. Playwright screenshots at 960x540
4. **GATE:** User confirms design brief

## Step 1: Structure (Philosophy-Aware)

Read `config/philosophies/<name>.yaml` for framework:
- **mckinsey:** Pyramid Principle (SCR + 3-5 clusters)
- **editorial:** Narrative arc (hook → tension → resolution)
- **data-forward:** Evidence-first (finding → evidence → implication)
- **cinematic:** Emotional arc (wonder → tension → revelation)

## Step 2: Ghost Deck

Assertive sentence titles. Validate:
- **Horizontal logic:** titles alone tell a complete story
- **Vertical logic:** every element proves its title

## Step 3: Executive Summary

Slide 2: top-level conclusion + 3 supporting points. This slide alone conveys the full message.

## Step 3.5: Visual Plan + Grid (HUMAN GATE)

Per-slide: grid layout, image candidate, space allocation. Present to user as rendered HTML wireframe.

## Step 3.7: Content Enrichment

Fill assertions with sourced evidence. SCAC 6-gate audit (Goal, Self-Sufficiency, Data Grounding, Evidence, Specificity, Depth). **HUMAN GATE** on enriched story flow.

## Step 3.8: Expert Critique (3-Lens)

3 parallel expert personas stress-test the thesis. Classify findings as must-address / should-address / strengthens. **HUMAN GATE** on revised ghost deck.

## Step 3.9: Image Audit

Capture evidence images via Playwright. VIEW each image. Failed captures block build.

## Step 4: Per-Slide HTML + Co-Authored JSON

Generate **one HTML + one JSON per slide**, co-authored simultaneously. 960x540 fixed viewport. CSS Grid mandatory. Read `errata/presentation_design.md` first (hard gate).

- Output: `output/html/<slug>/s01-title.html`, `s01-title.json`, `s02-situation.html`, `s02-situation.json`, ...
- JSON contains **granular primitives only** (`text`, `shape`, `image`) — no abstract types
- Font sizes in JSON = CSS px (matching viewport). Engine converts at render.

## Step 4.5: Canvas Fill Gate (MECHANICAL)

Per-slide self-check: viewport fill >= 80%, font minimums, contrast, overflow.

## Step 4.9: Per-Slide HTML Approval Gate (HUMAN GATE — blocks PPTX)

User reviews each slide in browser. Must approve before ANY PPTX work.

## Step 5: Convergence (max 3 rounds)

Per-slide Q1-Q9 scoring + cross-slide coherence audit. Fix ONE bottleneck per round. Regression gate on all dimensions.

- **Step 5f:** JSON sync gate — verify per-slide JSON elements match rendered HTML
- **Step 5i:** Cross-slide coherence audit (visual consistency across deck)
- **Step 5j:** Self-learning errata capture at each convergence round

## Step 6: Export to PPTX

- **Step 6a:** Assembly — `hippt-assemble output/html/<slug>/` → combined sidecar JSON
- **Step 6b:** Export — `hippt-draft <combined-slides.json> --tokens <tokens.yaml>` → editable PPTX

## Step 6.5: Fidelity Gate

Playwright screenshots HTML vs PPTX per slide. Blocks if position delta >1" or content missing. Use `/pptx-fidelity` skill.

Review PPTX in native renderer (PowerPoint/Keynote/LibreOffice). Never PDF.

## Step 7: Archive

Archive final HTML + PPTX + tokens to `output/archive/<slug>/`. Write `capture.yaml` with scores and errata encountered.
