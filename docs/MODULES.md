> **Superseded by [MEGAPLAN.md](MEGAPLAN.md)** — this file is kept for reference only. The MEGAPLAN is the canonical source.

# PPTX Pipeline — Module Reference

## Tool Inventory

```
TOOLS/scripts/
├── slides_to_pptx.py     PRIMARY engine — sidecar JSON → PPTX (Phase 7 ✅)
├── html_to_pptx.py       REFINEMENT engine — DOM extraction → PPTX (Phase 1 ✅)
├── analyze_pptx.py       PPTX metrics — canvas fill, fonts, colors (exists)
├── pptx_to_tokens.py     Reference PPTX → design tokens YAML (exists)
└── pptx_to_layout.py     PPTX → layout YAML extraction (Phase 4 — planned)
```

## Module: html_to_pptx.py

**Purpose:** Convert approved HTML presentation → editable PPTX with pixel-accurate positioning.

**Input:** HTML file with `.slide` / `.active` navigation pattern
**Output:** Editable `.pptx` file + optional debug JSON

```
CLI:  uv run python TOOLS/scripts/html_to_pptx.py <html> --out <pptx> [--debug]

Internal pipeline:
  Phase 1 (Extract)  — Playwright at 960x540 → getBoundingClientRect + getComputedStyle
  Phase 2 (Classify) — native | rasterize | skip + overflow warnings
  Phase 3 (Build)    — python-pptx with exact coordinates (px → inches)
```

**Key functions:**
| Function | Role |
|----------|------|
| `_extract_slides()` | Launch Playwright, serve HTML, extract per-slide JSON |
| `_classify_elements()` | Tag each element: native, rasterize, or skip |
| `_build_pptx()` | Create PPTX with exact coordinates from extraction data |
| `_add_text()` | Textbox with multi-run support (per-node font/color/bold) |
| `_add_image()` | Image from base64, file path, or URL |
| `_add_shape()` | Rectangle or ROUNDED_RECTANGLE with fill/border |
| `_add_table()` | Native table with per-cell styling |
| `parse_css_color()` | rgb() / rgba() / #hex → (RGBColor, alpha) |
| `px_to_in()` | Pixel → inch coordinate mapping |
| `_validate_roundtrip()` | Reopen PPTX, check slide/element counts |

## Module: slides_to_pptx.py

**Purpose:** Draft PPTX during HTML iteration — fast, no browser, semantic understanding.

**Input:** Sidecar JSON (from /presentation --mode deck) + design tokens YAML
**Output:** Editable `.pptx` file

**Key difference from html_to_pptx.py:**
- Uses `TokenResolver` to map semantic roles ("display", "primary") → actual values
- 15 specialized handlers that understand slide semantics (radial, era_card, stat_hero, etc.)
- Approximate grid-based positioning (~60% accuracy)
- Fast — no Playwright, no browser

## Module: analyze_pptx.py

**Purpose:** Extract layout metrics from any PPTX for comparison and verification.

**Input:** One or more .pptx files
**Output:** JSON with per-slide metrics

```
CLI:  uv run python TOOLS/scripts/analyze_pptx.py <file.pptx> [--verbose]

Metrics: canvas fill ratio, font size range, color palette, padding,
         shape types, layout distribution (row/column), dominant patterns
```

## Module: pptx_to_tokens.py

**Purpose:** Extract design tokens (colors, fonts, spacing) from a reference PPTX.

**Input:** Reference .pptx file
**Output:** YAML design tokens file (ref-<slug>.yaml)

```
CLI:  uv run python TOOLS/scripts/pptx_to_tokens.py <reference.pptx> --out <tokens.yaml>
```

## Module: pptx_to_layout.py (Phase 4 — planned)

**Purpose:** Extract structural layout from a calibrated PPTX → layout YAML.

**Input:** Human-adjusted .pptx file (from either ingestion path)
**Output:** Layout YAML (L-XXX-NNN.yaml) with percentage-based regions

```
Planned pipeline:
  1. Open PPTX → enumerate shapes per slide
  2. Convert EMU coordinates → percentages
  3. Classify regions by content type (text, image, shape, table)
  4. Generate layout YAML with schema_version: 1
  5. Human + AI add metadata (tags, density) and context (semantic guidance)
```

## Verification Stack

```
Level 1: validate_roundtrip()          Structural — slide/element counts
Level 2: analyze_pptx.py              Metrics — canvas fill, fonts, colors
Level 3: Google Slides + Playwright    Visual — side-by-side screenshot diff

Level 3 is the REAL validation. Levels 1-2 are automated gates
that catch structural problems before the expensive visual check.
```

## Critical Design Rule: Render at Slide-Native DPI (E-PRES-036)

```
A 10" × 5.625" PPTX at 96 DPI = 960 × 540 pixels.

WRONG:  Render at 1920×1080 → 2x mismatch → fonts overflow OR are unreadable
RIGHT:  Render at 960×540   → 1 CSS px = 1/96" → matches PPTX natively

At 960×540:
  - Positions: px_to_in(px, 960, 10.0) maps 1:1 to CSS physical inches
  - Fonts: font_px × 0.75 = correct pt (standard CSS px→pt)
  - CSS clamp() produces PPTX-appropriate sizes naturally:
    Title: clamp(40px, 5.5vw, 78px) → 52.8px → 39.6pt
    Body:  clamp(15px, 1.4vw, 22px) → 15px   → 11.2pt
```

This applies to all viewport-to-slide mapping:
- `html_to_pptx.py`: viewport = 960×540, font scale = 0.75
- Layout YAML: percentages are DPI-agnostic (safe)
- Any future tool mapping browser pixels to PPTX units

**If viewport doesn't match slide DPI, fonts and boxes use different scales.**
Diagnosed in r7→r13 iteration (6 rounds). See errata E-PRES-036.

## Schemas

| Schema | Path | Purpose |
|--------|------|---------|
| Layout YAML | `schemas/schema-layout.yaml` | Template for layout library files |
| Extraction JSON | `schemas/schema-extraction.yaml` | Debug output from html_to_pptx.py |
