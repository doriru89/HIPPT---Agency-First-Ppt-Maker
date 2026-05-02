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

## Step 4: Generate HTML

960x540 fixed viewport. CSS Grid mandatory. Read `errata/presentation_design.md` first (hard gate). Follow F1-F10 prevention table. Write to `output/html/`.

## Step 4.5: Canvas Fill Gate (MECHANICAL)

Self-check every slide: viewport fill >= 80%, font minimums, contrast, overflow.

## Step 4.9: HTML Approval Gate (HUMAN GATE — blocks PPTX)

User reviews in full-screen browser. Must approve before ANY PPTX work.

## Step 5: Convergence (max 3 rounds)

Score Q1-Q9 per slide. Fix ONE bottleneck per round. Regression gate on all dimensions.

## Step 6: Export to PPTX

- **Primary:** `hippt-draft <slides.json> --tokens <tokens.yaml>`
- **Refinement:** `hippt-export <html> --reference <ref.pptx>`
- Review in native PPTX renderer (never PDF)

## Step 7: Archive

Archive final HTML + PPTX + tokens. Write `capture.yaml` with scores and errata encountered.
