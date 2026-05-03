# PPTX Pipeline — Backlog

Items deferred until prerequisites are met. Not active work — revisit when triggers fire.

## Prerequisite: 3+ Decks Through Full Pipeline

These items need empirical data from real deck runs to inform design.

| ID | Item | What | Trigger |
|----|------|------|---------|
| B1 | Best-across-iterations watermark | Store html+scores per convergence round, select highest | Oscillation observed in 2+ decks |
| B2 | Per-slide-type scoring floors | Data slides Q5>=8, visual slides Q8>=8 | Score distribution data from 3+ decks |
| B3 | Minimum entry threshold | Below 75% avg → regenerate, don't converge | First-pass score distribution established |
| B4 | Centroid computation script | Playwright-based content centroid per slide (E-PRES-015) | Q7 decomposition approved |
| B5 | Shape weight activation | `layout-extraction.yaml` shape_weight: 0.0 → 0.3 | Calibration on 3+ decks with layout matching |
| B6 | Layout context reasoning at L2 | LLM-based structural reasoning in layout selection | 3+ approved layouts beyond L-TITLE-001 |
| B7 | Scoring weight calibration | Tune L1/L2 scoring coefficients in layout_select.py | 5+ deck runs with layout matching |

## Prerequisite: Layout Library Maturity

| ID | Item | What | Trigger |
|----|------|------|---------|
| B8 | Phase 5.5: Reference→HTML fidelity validation | End-to-end test, 13/14 layouts rejected | reference_analyze.py orchestrator built |
| B9 | Phase 7b: Reference fidelity automation | Structural similarity, palette distance scoring | 3+ reference PPTXs through pipeline |
| B10 | 30 duplicate layout disambiguation | Dedup near-identical layouts in library | Layout library actively used in production |

## Prerequisite: Rubric Redesign

| ID | Item | What | Trigger |
|----|------|------|---------|
| B11 | Evidence anchoring per Q dimension | Rulers framework: measured + reference + delta per score | Rubric merge (FINAL_PLAN item) complete |
| B12 | Q7 mechanical decomposition | Gap ±2px, font-size count, alignment grid snap | Expert 2 flagged Q7 as most leniency-prone |

## Prerequisite: Pipeline Restructure Decision

| ID | Item | What | Trigger |
|----|------|------|---------|
| B13 | Phase 3b: Step renumbering | Renumber Steps 4.0-4.9, add wireframe Step 3.5 narrative | Pipeline stable for 2+ sessions without step confusion |
| B14 | Phase 5b: Ticketmaster validation | Dual-engine A/B comparison on existing Ticketmaster data | Both engines stable, export tested |
| B15 | Phase 7c: V3 bug verification | Use signature-slides-v3 as regression test | Regression test infrastructure exists |

## Prerequisite: 5+ Fidelity Review Runs

| ID | Item | What | Trigger |
|----|------|------|---------|
| B20 | Classification engine (YAML rules) | Extract stable patterns from LLM classification into machine-readable YAML | Same errata codes appear in 5+ runs across 3+ decks |
| B21 | Automated severity thresholds | Normalize thresholds to slide dimensions (not absolute inches) | Non-10" slides through pipeline |
| B22 | Font substitution baseline | Catalog expected Google Slides font differences as "known acceptable" | 3+ decks reviewed in Google Slides |
| B23 | Perceptual diff (SSIM) | Add scikit-image structural similarity scoring per slide pair | When pixel-level diff adds signal beyond structural comparison |
| B24 | Run history dashboard | Track score improvement across all iterations of all decks | 10+ total fidelity runs completed |

## Nice-to-Have (No Blocker)

| ID | Item | What | Priority |
|----|------|------|----------|
| B16 | Phase 2F: Centralized density table | Extract limits from 15 component guardrails into one table | Low — values exist per-component already |
| B17 | Domain-expert consulting agent | Compose /consulting-analysis + /deep-research + /design-rubric | Low — Step 3.8 experts work manually |
| B18 | Dense mode auto-detection | Auto-apply .slide--dense class based on content type | Low — manual class works |
| B19 | MCP server exposure | Expose pipeline as API for external tools | Low — re-evaluate when layout library matures |

## Prerequisite: Granular Pipeline Validated on 2+ Decks

Items deferred from the 2026-05-02 gap-fix session. Need real usage to confirm value.

| ID | Item | What | Trigger |
|----|------|------|---------|
| B25 | G9: html_to_sidecar.py format update | Update extraction tool to output granular primitives instead of abstract types | Someone needs to retrofit an existing HTML that wasn't co-authored |
| B26 | G10: PptxGenJS engine validation | Test Engine B (Node.js) with granular JSON format, fix handler mismatches | Charts or icon rasterization needed that python-pptx can't handle |
| B27 | /review-errata skill | Standalone skill for periodic human review of errata entries — HIPPT-portable | Errata file exceeds 60 entries or HIPPT users onboard |
| B28 | Layout library auto-selection | Wire layout library YAMLs into Step 4 — LLM selects closest layout as starting skeleton | 10+ verified layouts in `layouts/` with quality scores |
| B29 | Layout library contribution pipeline | After Step 7 capture, extract approved slide as new L-TYPE-NNN.yaml automatically | 3+ decks through full pipeline to Step 7 |
| B30 | HIPPT extraction — portable errata | Filter 49 errata entries to ~25 universal (drop AIOS-specific session refs) | HIPPT Dockerfile + README ready for external users |
| B31 | HIPPT extraction — Dockerfile | Single Dockerfile: Python + Playwright + Chromium + assemble + slides_to_pptx | Decision to ship HIPPT as open-source tool |
| B32 | Gradient accent calibration | Test gradient fills across real decks, build gradient token library | 3+ slides with gradient accents through fidelity review |
| B33 | Fidelity score regression tracking | Store per-deck fidelity scores over time, alert on regression | 5+ fidelity review runs completed |

## Reference: Complete Slide Sessions

Search for past deck sessions to inform future features:
```bash
find WORK/HANDOFFS/ -name "*presentation*" -o -name "*pptx*" -o -name "*carecost*" | sort
ls OUTPUT/html/presentation-*.html
```

BCG (programmatic tokens), Douyin Xiaodian (manual tokens, bilingual), CareCost (seed pitch).
