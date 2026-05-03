# Architecture — Per-Slide Co-Authoring Pipeline

## Design Philosophy

Presentations are built one slide at a time. Each slide gets its own HTML (for visual iteration) and its own JSON (for PPTX export), co-authored simultaneously. No extraction step. No drift.

This approach achieved the **79% quality baseline** — the golden standard that proved the pipeline works.

## Primary Engine — `hippt/slides_to_pptx.py`

- **Input:** Combined sidecar JSON (assembled from per-slide JSONs)
- **Output:** Editable PPTX with native shapes, text boxes, charts
- **How:** 16 element-type handlers map JSON primitives to python-pptx calls
- **Features:** Gradient fills, CSS-to-pt font calibration, collision detection, dynamic height estimation
- **CLI:** `hippt-draft <slides.json> --tokens <tokens.yaml>`

### Sidecar JSON Contract

JSON elements are **granular primitives only** — `text`, `shape`, `image`. No abstract types (`stat_card`, `hero_stat`, `timeline`). A stat card decomposes into 5 primitives: rounded rectangle background + metric text + label text + delta text + unit text.

Font sizes in JSON are **CSS pixels** (matching the 960x540 viewport). The engine converts at render: `pptx_pt = css_px × CSS_PX_TO_PT (0.75)`.

## Assembly Step — `hippt/assemble_sidecar.py`

Mechanically concatenates per-slide JSONs into the combined sidecar:
```bash
hippt-assemble output/html/<slug>/
```
Reads `s01-*.json`, `s02-*.json`, ..., plus `design-tokens.json`. Validates each slide has `elements[]`. No transformation — purely concatenation + metadata injection.

## Backup Engine — `hippt/html_to_pptx.py`

Available for pixel-accurate positioning when needed, but **NOT part of the primary flow**:
- **Input:** HTML file + optional reference PPTX
- **How:** Renders at 960x540 via Playwright, walks DOM tree, maps elements to PPTX
- **CLI:** `hippt-export <file.html> --reference <ref.pptx>`
- **Requires:** Playwright + Chromium (`uv sync --extra export`)

## Fidelity Validation — `hippt/pptx_fidelity.py`

Post-export quality gate (Step 6.5):
- Screenshots HTML slides via Playwright at 960x540
- Extracts PPTX element data via pptx_to_layout
- Compares per-slide: position deltas, font differences, missing content
- Severity: "blocking" (>1" delta), "degrading" (>0.3"), "cosmetic"
- Blocks delivery if blocking findings detected

## Coordinate System

All rendering uses **960x540 fixed viewport** at 96 DPI. This is non-negotiable (E-PRES-036):
- 1 CSS pixel = 1/96 inch = exact PPTX coordinate
- `font_pt = font_px * 0.75` (CSS_PX_TO_PT from design_tokens.py)
- Rendering at 1920x1080 creates a 2x mismatch that compounds across every element
- `device_scale_factor=1` to prevent Retina 2x

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
Step 4: Per-slide HTML + co-authored JSON (960x540, CSS Grid, granular primitives)
    ↓
Step 4.9: Per-slide HTML Approval Gate (HUMAN)
    ↓
Step 5: Convergence (max 3 rounds, per-slide Q1-Q9 scoring + cross-slide coherence)
    ↓
Step 6a: Assembly (hippt-assemble → combined sidecar)
    ↓
Step 6b: Export (hippt-draft → editable PPTX)
    ↓
Step 6.5: Fidelity Gate (HTML vs PPTX screenshot comparison)
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
| `hippt-assemble` | assemble_sidecar.py | Per-slide JSONs → combined sidecar |
| `hippt-export` | html_to_pptx.py | HTML → PPTX via Playwright (backup) |
| `hippt-tokens` | pptx_to_tokens.py | Extract design tokens from reference PPTX |
| `hippt-layouts` | pptx_to_layout.py | Extract layouts from reference PPTX |
| `hippt-extract-layouts` | extract_layouts.py | Extract layouts from HTML debug JSON |
| `hippt-analyze` | analyze_pptx.py | Analyze PPTX (fill %, fonts, colors) |
| `hippt-cockpit` | review_cockpit.py | Generate side-by-side comparison HTML |
