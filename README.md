# HIPPT — Agency-First Presentation Maker

AI can create generic-looking HTML presentations, but professional work lives in PPTX. HIPPT bridges the gap with a quality-gated pipeline: from "I have an idea" to "here's an editable, 80%+ scored PowerPoint."

## Quick Start

### Prerequisites

1. **uv** (Python package manager):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Claude Code** (AI agent):
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```
   Set your `ANTHROPIC_API_KEY` environment variable.

### Install

```bash
git clone https://github.com/doriru89/HIPPT---Agency-First-Ppt-Maker.git
cd HIPPT---Agency-First-Ppt-Maker
uv sync
```

### Verify It Works

```bash
uv run hippt-draft examples/sample-slides.json
open output/pptx/*.pptx
```

### Optional: DOM Engine (Playwright)

For the HTML-to-PPTX extraction engine:
```bash
uv sync --extra export
uv run playwright install chromium
```

## Full Pipeline

Start Claude Code in the repo:
```bash
claude
```

Then run the presentation skill:
```
/presentation --mode deck "Why remote work increases productivity for knowledge workers"
```

Claude will walk you through:
1. **Vision & Requirements** — clarifying questions, audience, goal
2. **Structure** — philosophy-aware ghost deck (Pyramid Principle, narrative arc, etc.)
3. **Content Enrichment** — sourced evidence for every assertion
4. **Expert Critique** — 3-lens stress test of the thesis
5. **HTML Build** — 960x540 fixed viewport, CSS Grid, canvas fill >= 80%
6. **Quality Scoring** — Q1-Q10 rubric, convergence iteration
7. **PPTX Export** — editable PowerPoint via python-pptx

## Architecture

Two PPTX engines:

| Engine | Command | Input | Best For |
|--------|---------|-------|----------|
| **Semantic** (primary) | `hippt-draft` | Sidecar JSON | General decks, fast iteration |
| **DOM** (refinement) | `hippt-export` | HTML file | Pixel-accurate positioning |

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for full data flow.

## Quality System

10-dimension rubric (Q1-Q10), each scored 1-10:
- Q1: Structure & Narrative
- Q2: Canvas Utilization (gate: Q2 < 7 caps total)
- Q3: Typography & Hierarchy
- Q4: Color & Harmony
- Q5: Data Presentation
- Q6: Editability & Fidelity (gate: Q6 < 8 caps total)
- Q7: Professional Polish
- Q8: Visual Evidence
- Q9: Vision Adherence
- Q10: Export Fidelity (gate: Q10 < 8 iterates)

Target: 80/100 first pass, 95/100 after convergence.

See [docs/SCORING.md](docs/SCORING.md) for details.

## Project Structure

```
hippt/          Python package (11 modules)
config/         YAML configs (rubric, philosophies, layout extraction)
templates/      Slide component specs (15 types)
errata/         48 failure patterns from real sessions
layouts/        17 layout templates from reference decks
baselines/      Gold-standard examples (79% CareCost pitch)
docs/           Architecture, principles, pipeline, scoring, decisions
tests/          132 tests
```

## Key Docs

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — dual-engine design, data flow
- [PRINCIPLES.md](docs/PRINCIPLES.md) — 10 agency-first principles
- [PIPELINE.md](docs/PIPELINE.md) — Steps 0-7 reference
- [SCORING.md](docs/SCORING.md) — Q1-Q10 explained
- [decisions.md](docs/decisions.md) — 26 hard-won pipeline rules
- [sessions/](docs/sessions/) — learnings from CareCost, Smart Tickets, Steam XAI

## License

MIT
