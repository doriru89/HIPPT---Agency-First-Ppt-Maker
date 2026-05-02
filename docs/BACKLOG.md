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

## Nice-to-Have (No Blocker)

| ID | Item | What | Priority |
|----|------|------|----------|
| B16 | Phase 2F: Centralized density table | Extract limits from 15 component guardrails into one table | Low — values exist per-component already |
| B17 | Domain-expert consulting agent | Compose /consulting-analysis + /deep-research + /design-rubric | Low — Step 3.8 experts work manually |
| B18 | Dense mode auto-detection | Auto-apply .slide--dense class based on content type | Low — manual class works |
| B19 | MCP server exposure | Expose pipeline as API for external tools | Low — re-evaluate when layout library matures |

## Reference: Complete Slide Sessions

Search for past deck sessions to inform future features:
```bash
find WORK/HANDOFFS/ -name "*presentation*" -o -name "*pptx*" -o -name "*carecost*" | sort
ls OUTPUT/html/presentation-*.html
```

BCG (programmatic tokens), Douyin Xiaodian (manual tokens, bilingual), CareCost (seed pitch).
