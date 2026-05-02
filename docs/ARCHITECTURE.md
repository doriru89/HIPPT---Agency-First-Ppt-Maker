# Architecture — Dual-Engine PPTX Pipeline

## Design Philosophy

Presentations are HTML-first, PPTX-second. HTML is the SSOT for design iteration; PPTX is a one-shot export after HTML approval.

## Dual Engine

Two engines produce PPTX from different inputs:

### Semantic Engine (Primary) — `hippt/slides_to_pptx.py`
- **Input:** Sidecar JSON (structured slide data)
- **Output:** Editable PPTX with native shapes, text boxes, charts
- **How:** 16 element-type handlers map JSON to python-pptx calls
- **Strengths:** Fast, no browser needed, 79% quality baseline
- **CLI:** `hippt-draft <slides.json> --tokens <tokens.yaml>`

### DOM Engine (Complementary) — `hippt/html_to_pptx.py`
- **Input:** HTML file + optional reference PPTX
- **Output:** Pixel-accurate PPTX via Playwright extraction
- **How:** Renders HTML at 960x540, walks DOM tree, maps elements to PPTX
- **Strengths:** Exact coordinates, reference inheritance, layout remapping
- **CLI:** `hippt-export <file.html> --reference <ref.pptx>`
- **Requires:** Playwright + Chromium (`uv sync --extra export`)

### Hybrid Approach (Phase D — under development)
DOM extraction positions feed the semantic engine: `html_to_sidecar.py` extracts element positions from rendered HTML, then `slides_to_pptx.py` builds native PPTX with correct coordinates. Best of both worlds: pixel accuracy + native editability.

## Coordinate System

All rendering uses **960x540 fixed viewport** at 96 DPI. This is non-negotiable (E-PRES-036):
- 1 CSS pixel = 1/96 inch = exact PPTX coordinate
- `font_pt = font_px * 0.75` (at this DPI)
- Rendering at 1920x1080 creates a 2x mismatch that compounds across every element

## Data Flow

```
User Input
    ↓
Step 0: Vision & Requirements (interactive)
    ↓
Step 0.5: Reference Analysis (optional PPTX → tokens + layouts)
    ↓
Step 1-2: Structure + Ghost Deck (philosophy-driven)
    ↓
Step 3: Content Enrichment + Expert Critique
    ↓
Step 4: Generate HTML (960x540, CSS Grid mandatory)
    ↓
Step 4.9: HTML Approval Gate (HUMAN)
    ↓
Step 5: Convergence (max 3 rounds, Q1-Q9 scoring)
    ↓
Step 6: Export to PPTX
    ├── Path A: Sidecar JSON → slides_to_pptx.py (semantic)
    └── Path B: HTML → html_to_pptx.py (DOM extraction)
    ↓
PPTX Review (native renderer, never PDF)
```

## Config Cascade

```
config/philosophies/<name>.yaml    → Step 1 (framework, vocabulary, density limits)
    ↓
templates/presentation-components.md → Step 4 (15 slide types, CSS patterns)
    ↓
config/pptx-quality.yaml           → Step 5 (Q1-Q10 scoring, convergence targets)
    ↓
config/layout-extraction.yaml      → Step 6 (layout matching, selector roles)
```

## Tool Inventory

| Command | Module | Purpose |
|---------|--------|---------|
| `hippt-draft` | slides_to_pptx.py | Sidecar JSON → PPTX (primary) |
| `hippt-export` | html_to_pptx.py | HTML → PPTX via Playwright (refinement) |
| `hippt-tokens` | pptx_to_tokens.py | Extract design tokens from reference PPTX |
| `hippt-layouts` | pptx_to_layout.py | Extract layouts from reference PPTX |
| `hippt-extract-layouts` | extract_layouts.py | Extract layouts from HTML debug JSON |
| `hippt-analyze` | analyze_pptx.py | Analyze PPTX (fill %, fonts, colors) |
| `hippt-cockpit` | review_cockpit.py | Generate side-by-side comparison HTML |
