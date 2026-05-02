# Scoring — Q1-Q10 Quality Dimensions

Full rubric definition: `config/pptx-quality.yaml` (SSOT).

## Dimensions

| Dim | Name | Weight | Gate |
|-----|------|--------|------|
| Q1 | Structure & Narrative | High | — |
| Q2 | Canvas Utilization | High | Q2 < 7 → cap total at 7/10 avg |
| Q3 | Typography & Hierarchy | Medium | — |
| Q4 | Color & Harmony | Medium | — |
| Q5 | Data Presentation | Medium | N/A default 8/10 if no data slides |
| Q6 | Editability & Fidelity | High | Q6 < 8 → cap total at 8/10 avg |
| Q7 | Professional Polish | Medium | — |
| Q8 | Visual Evidence | High | N/A default 7/10 for text-heavy decks |
| Q9 | Vision Adherence | High | — |
| Q10 | Export Fidelity | High | Q10 < 8 → iterate export handlers |

## Targets

- **First pass (HTML):** 80/100 (per `pptx-quality.yaml` convergence.html_first_pass)
- **After 3 rounds:** 95/100 (per convergence.html_after_3_rounds)
- **Bottleneck priority:** Q1 > Q8 > Q5 > Q2 > Q9 > Q7 > Q3 > Q4

## Anti-Patterns (instant flags)

| ID | Pattern | Dimension |
|----|---------|-----------|
| AP1 | Screenshot-as-slide | Q6 fail |
| AP2 | >5 distinct hues | Q4 (E-PRES-014) |
| AP3 | <40% fill on detail slides | Q2 (E-PRES-006) |
| AP4 | Web-sized text (12px body) | Q3 (E-PRES-001) |
| AP5 | Inconsistent line-heights | Q3 (E-PRES-013) |
| AP6 | Font substitution without fallback | Q6 (E-PPTX-003) |
| AP7 | Generic stock image | Q8 (E-PRES-020) |
| AP8 | Slide not serving vision | Q9 |
| AP9 | PPTX diverges from HTML | Q10 |

## Convergence Rules

1. **Iteration trigger:** Q1-Q9 avg below target, OR any Q below 7, OR gate violation
2. **Fix ONE dimension per round** (TOC pattern)
3. **Regression gate:** if any previously-passing Q drops > 0.5 points, reject the fix
4. **Oscillation detector:** if this round's bottleneck = two rounds ago, exit with best round's output
5. **Max 3 rounds** — if still below target, report to user and offer to re-enrich at Step 3.7
