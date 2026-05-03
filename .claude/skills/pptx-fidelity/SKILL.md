---
name: pptx-fidelity
description: "Visual fidelity review — screenshot HTML vs PPTX, compare structure, diagnose divergences, route fixes."
user-invocable: true
auto_invoke: false
keywords: [pptx, fidelity, visual, comparison, review, screenshot, quality]
allowed-tools: [Bash, Read, mcp__playwright__browser_navigate, mcp__playwright__browser_resize, mcp__playwright__browser_take_screenshot, mcp__playwright__browser_press_key, mcp__claude_ai_Google_Drive__search_files]
argument-hint: "<html_path> <pptx_path> [--rerun]"
side_effects: writes-tmp
categories: [presentation, review, quality]
capabilities:
  required:
    - tool: Bash
      purpose: "run Python Playwright capture, PPTX extraction"
    - tool: Read
      purpose: "view screenshots, read errata"
    - tool: mcp__playwright__browser_take_screenshot
      purpose: "capture Google Slides slides"
  optional:
    - tool: mcp__claude_ai_Google_Drive__search_files
      purpose: "find PPTX file ID in Drive"
      fallback: "user provides file ID manually"
    - tool: mcp__playwright__browser_navigate
      purpose: "open Google Slides for PPTX screenshots"
      fallback: "user manually screenshots each slide and places as pptx-s{N}.png in output dir"
---

# /pptx-fidelity — PPTX Visual Fidelity Review

Compare HTML (ground truth) against PPTX (generated output) per slide. Diagnose divergences, classify against errata, route to fixes.

## When to Use

After generating a PPTX via `slides_to_pptx.py` or `html_to_pptx.py`, before declaring quality. E-PRES-017 hard gate: no score without screenshot.

## Pipeline

### 1. CAPTURE HTML
```bash
uv run python -c "
from hippt.pptx_fidelity import capture_html_slides
from pathlib import Path
capture_html_slides(Path('<html_path>'), Path('/tmp/pptx-fidelity/<slug>/'))
"
```

### 2. CAPTURE PPTX (Google Slides)
1. Find file ID: `mcp__claude_ai_Google_Drive__search_files` with title query
2. Navigate: `mcp__playwright__browser_navigate` to `https://docs.google.com/presentation/d/{id}/present`
3. Resize: `mcp__playwright__browser_resize` to 960x540
4. For each slide: `mcp__playwright__browser_take_screenshot`, then `mcp__playwright__browser_press_key` ArrowRight
5. Move screenshots from repo root to `/tmp/pptx-fidelity/<slug>/`

### 3. EXTRACT + COMPARE
```bash
uv run python -c "
import json
from pathlib import Path
from hippt.pptx_fidelity import extract_pptx_structure, compare_slide, generate_comparison_html

out_dir = Path('/tmp/pptx-fidelity/<slug>/')
sidecar = json.loads(Path('<sidecar_json>').read_text())
pptx_slides = extract_pptx_structure(Path('<pptx_path>'))
html_shots = sorted(out_dir.glob('html-s*.png'))
pptx_shots = sorted(out_dir.glob('pptx-s*.png'))

findings = []
for i, (sc, px) in enumerate(zip(sidecar['slides'], pptx_slides), 1):
    findings.append(compare_slide(sc.get('elements', []), px, slide_idx=i))

generate_comparison_html(html_shots, pptx_shots, findings, out_dir / 'compare.html')
"
```

### 4. CLASSIFY
Read `errata/presentation_design.md` BEFORE diagnosing. Match each finding to known patterns. Flag NEW patterns for errata addition.

### 5. DIAGNOSE + ROUTE
For each non-cosmetic finding, classify root cause:

| Route | Meaning | Action |
|-------|---------|--------|
| `sidecar_data` | Sidecar JSON missing layout info | Re-extract or regenerate sidecar |
| `handler_bug` | Engine handler produces wrong output | Fix specific handler in slides_to_pptx.py |
| `css_limitation` | CSS effect has no PPTX equivalent | Add to rasterize list in pptx-quality.yaml |
| `font_rendering` | Google Slides font substitution | Accept as expected cosmetic |
| `NEW` | Unknown failure pattern | Add to errata |

### 6. REPORT
Open comparison HTML. Present top-3 findings with fix instructions.

### 7. ITERATE
After fix: `--rerun` to regenerate PPTX, re-capture, compare `findings.json` deltas.

## Constraints

- Viewport MUST be 960x540 (E-PRES-036)
- MCP Playwright blocks `file://` — use Python Playwright for HTML
- Google Slides font substitution is EXPECTED, not a bug (E-PRES-019)
- Output to `/tmp/pptx-fidelity/<slug>/` (ephemeral)
- Read errata BEFORE classifying (E-PRES errata hard gate)
