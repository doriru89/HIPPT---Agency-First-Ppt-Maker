# HIPPT — Agency-First Presentation Maker

## What This Is

HIPPT is a standalone presentation pipeline. It takes an idea through research, structure, HTML mockup, and PPTX export — targeting 80%+ quality scores on a 10-dimension rubric.

## Skills

Three skills power the pipeline:
- `/presentation --mode deck|visual-aid|export` — full pipeline (Steps 0-7)
- `/design-rubric` — Q1-Q10 scoring critique
- `/reference-extract <url>` — extract visual tokens from a website

## Tools

| Command | Purpose |
|---------|---------|
| `hippt-draft <slides.json>` | Sidecar JSON → editable PPTX (primary engine) |
| `hippt-export <file.html>` | HTML → PPTX via Playwright (refinement engine) |
| `hippt-tokens <ref.pptx> --slug <name>` | Extract design tokens from reference PPTX |
| `hippt-layouts <ref.pptx> --out <dir>` | Extract layouts from reference PPTX |
| `hippt-analyze <file.pptx>` | Analyze PPTX (fill %, fonts, colors) |
| `hippt-cockpit --tokens <yaml> --slides <json>` | Side-by-side comparison HTML |

## Config

- `config/pptx-quality.yaml` — Q1-Q10 rubric, convergence targets, anti-patterns (SSOT)
- `config/layout-extraction.yaml` — layout matching, selector roles, scoring weights
- `config/philosophies/*.yaml` — mckinsey, editorial, data-forward, cinematic frameworks
- `config/examples/carecost-tokens.yaml` — example design tokens from a real deck

## Key Constraints (non-negotiable)

1. **960x540 viewport** — no clamp(), no vw/vh. Match PPTX 96 DPI native. (E-PRES-036)
2. **HTML is SSOT** — iterate and approve HTML before any PPTX work
3. **Canvas fill >= 80%** — size elements to ZONE not CONTENT (E-PRES-006)
4. **Errata is a hard gate** — read `errata/presentation_design.md` BEFORE building any HTML
5. **One bottleneck per round** — fix ONE Q dimension per convergence iteration
6. **Evidence proves, not decorates** — images must contain data that supports the assertion

## Before Building HTML

1. Read `errata/presentation_design.md` — 48 failure patterns learned from real sessions
2. Read `templates/presentation-components.md` — 15 slide types with CSS patterns
3. Read `docs/decisions.md` — 26 key decisions that make the pipeline work

## Directory Layout

- `hippt/` — Python package (11 modules)
- `config/` — YAML configs (rubric, layouts, philosophies)
- `templates/` — slide component specs
- `errata/` — failure patterns
- `layouts/` — 17 YAML layout templates from real decks
- `schemas/` — JSON/YAML schemas for extraction output
- `baselines/` — gold-standard examples (CareCost 79%)
- `tests/` — 132 tests (50 design tokens, 27 html-to-pptx, 37 layout select, 18 layout assertions)
- `docs/` — architecture, principles, pipeline, scoring, decisions, session learnings
- `input/` — drop source materials here (reference PPTX, briefs, images)
- `output/` — runtime artifacts (.gitignored)

## Running Tests

```bash
just test              # unit tests only
just test-all          # includes integration tests (need reference PPTX in tests/fixtures/)
just smoke             # quick: generate PPTX from example
```
