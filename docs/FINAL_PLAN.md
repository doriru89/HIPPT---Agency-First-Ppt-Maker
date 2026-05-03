# FINAL PLAN — PPTX Pipeline Completion

**Goal:** End-to-end HTML→PPTX with ≥80% Q10 on first pass. Use CareCost deck as the test case to define rules that prevent mistakes at process level, not just capture them as errata.

**Errata:** `TOOLS/errata/presentation_design.md`. Read before any HTML/PPTX work.
**Commit:** `54875fe` (2026-05-02)

---

## Phase A: SSOT Fixes ✅ COMPLETE

| Task | What | Commit |
|------|------|--------|
| A1 | Font thresholds unified: `design_tokens.py` canonical (32/22/13pt), `classify_font_role()` moved there, 9 boundary tests | `54875fe` |
| A2 | `pptx-quality-rubric.yaml` + `pptx-quality-standards.yaml` → `pptx-quality.yaml` (971 lines, 5 sections). 7 consumers updated. | `54875fe` |
| A3 | `overlapping_cascade` → `add_evidence_row` in ELEMENT_HANDLERS (16 total). Comment mapping added. | `54875fe` |
| A4 | `pptx_css_safety` section (native/rasterize/avoid) in merged YAML | `54875fe` |

## Phase B: PPTX Export ✅ COMPLETE (Q10: ~6/10)

| Task | What | Result |
|------|------|--------|
| B1 | Sidecar JSON (6 slides, 44 elements) + `carecost-tokens.yaml` | Created |
| B2 | `slides_to_pptx.py` export — semantic, 38KB | Round-trip verified |
| B3 | `html_to_pptx.py` export — DOM extraction, 40KB | Round-trip verified |
| B4 | LibreOffice screenshots + Google Drive upload (`AI PPT/`) | Q10: ~6/10 |
| B5 | Issues documented below | Layout overlap on S2-S5 |

**B5 Issues (input for Phase D):**
- S2: stat_hero handler bypasses grid layout — hardcodes center position (line 522), ignoring y_cursor
- S3: Title overlaps subtitle; differentiator only renders left half
- S4: Title clipped; architecture diagram horizontal instead of vertical; text truncated
- S5: Title clipped; award cards overlap title
- S6: Timeline milestones cramped, overlap contact line

## Phase C: Validation ✅ COMPLETE

- 114 tests pass (35 new from this session)
- Zero stale references to deleted YAML files
- Import chain verified: `pptx_to_tokens.py` → `design_tokens.classify_font_role`
- Smoke test: 1-slide round-trip through both engines passes
- LibreOffice installed for future PPTX rendering

---

## Phase D-fix: Layout Bug Fixes ✅ COMPLETE (code correct, visual quality still poor)

| Task | What | Commit |
|------|------|--------|
| D-fix-1 | `add_stat_hero()` → `_grid_rect()` (was hardcoded center, bypassing grid) | `d9d7ffa` |
| D-fix-2 | `_estimate_min_height()` — content-aware title height using font size + box width | `d9d7ffa` |
| D-fix-2b | Off-slide overflow guard (warning when elements exceed slide bottom) | `d9d7ffa` |
| D-fix-3 | `_check_collisions()` — post-layout bounding box overlap detection with grid-aware x | `d9d7ffa` |
| D-fix-3b | S6 fix: pre-scan role positions, nudge explicit-y elements below on close slides | `d9d7ffa` |
| Tests | 18 new tests in `test_layout_assertions.py` (132 total, 0 regressions) | `d9d7ffa` |

**Outcome:** Code-level layout bugs fixed. All 5 B5 failures addressed. BUT visual quality of generated PPTX is still poor — layout math is correct but the visual result doesn't match the HTML. **Need Playwright visual comparison** (screenshot HTML vs screenshot PPTX per slide) to find what's actually wrong.

**Key finding:** CTO + /full-review found B5 S2 root cause was `add_stat_hero()` hardcoding center position (not "grid Y-advance insufficient" as originally documented). The 79% gold baseline was produced by `slides_to_pptx.py` alone — proving the engine CAN produce good output when sidecar data is right.

---

## Phase D: Engine Architecture & First-Pass Quality

**Strategic goal:** Use Playwright to screenshot both HTML and PPTX per slide, compare side-by-side, and troubleshoot exactly where layout diverges. Then apply DOM position overlay for pixel-accurate PPTX.

### D1. Dual-Engine Architecture
**Problem:** Two engines exist but their roles in the pipeline aren't formalized.

**Architecture decision needed:**
- **Semantic engine** (`slides_to_pptx.py`) = PRIMARY. Fast, editable, grid-based. Best for content.
- **DOM engine** (`html_to_pptx.py`) = COMPLEMENTARY. Pixel-accurate positions. Best for layout reference.

**How DOM extraction helps the semantic engine:**
1. DOM engine extracts exact `getBoundingClientRect()` positions for every element at 960×540
2. These positions become the grid placement hints for the semantic engine's sidecar JSON
3. Instead of guessing gridColumn positions, we read them from the approved HTML
4. This is the "same grid idea" — DOM gives us exact coordinates, semantic engine uses them for native shapes

**Proposed flow:**
```
HTML (approved at 80%) 
  → DOM extraction (Playwright: exact x,y,w,h for each element)
  → Position-aware sidecar JSON (merge semantic content + DOM positions)
  → slides_to_pptx.py (native shapes at exact positions)
  → PPTX (editable + pixel-accurate)
```

**Resolution (2026-05-02):** Semantic=primary, DOM=complementary. D2 deferred pending D-fix (Option A) results. If Option A achieves Q10 ≥ 8, D2 moves to Phase E.

### D2. Position-Aware Sidecar Generation
**Problem:** Current sidecar JSON uses gridColumn (approximate) for positioning. The DOM engine already has exact positions but outputs them to PPTX directly instead of feeding them to the semantic engine.

**Fix:** Create `html_to_sidecar.py` that:
1. Runs Playwright at 960×540
2. Extracts semantic content (text, role, element type) AND exact positions
3. Outputs sidecar JSON with explicit `x`, `y`, `w`, `h` (in inches) per element
4. `slides_to_pptx.py` uses these exact positions instead of grid auto-layout

**Target:** Q10 ≥ 8/10 on first pass (positions match HTML exactly, content is native/editable)

**Deferral (2026-05-02):** Deferred to Phase E. CTO review found the 3-pass text matcher is a coupling joint (L2 violation). If built, use `data-slide-idx`/`data-elem-idx` HTML attributes for O(1) matching instead. Trigger: D-fix achieves < Q10 8 on layouts grid can express.

### D3. Process Rules from CareCost Failures
**Problem:** The 5 B5 issues (title overlap, diagram layout, text truncation) are symptoms of the grid auto-layout guessing wrong. Instead of just adding errata, define prevention rules.

**Rules to formalize:**
1. **Title height auto-sizing** — if title text > 80 chars, allocate 2 lines minimum (h ≥ 1.2")
2. **Diagram orientation** — vertical stacks stay vertical; use aspect ratio from HTML bounding box
3. **Text truncation gate** — if text width > box width at assigned font size, flag before export
4. **Element collision check** — no two elements may overlap (check bounding boxes post-layout)
5. **Handler grid compliance** — all handlers must use `_grid_rect()` or explicit coords; no hardcoded slide-center positions

**Implementation:** Add these as assertions in `slides_to_pptx.py` that run at layout time, not post-hoc.

### D4. Design System Integration
**Problem:** The presentation skill generates HTML with a design system (tokens, components, grid), but this system doesn't flow to the PPTX export step. The sidecar JSON loses the design system's layout intent.

**Fix:** Design tokens should flow end-to-end:
```
reference-extract → tokens YAML → HTML (CSS vars) → sidecar JSON (tokens embedded) → PPTX (native)
```

Currently broken link: `HTML → sidecar JSON` doesn't preserve grid structure or spacing rhythm.

---

## Done Criteria (Updated)

- [x] Font thresholds unified in design_tokens.py (A1)
- [x] pptx-quality.yaml created, old files deleted (A2)
- [x] Component-handler mapping explicit (A3)
- [x] CSS safety table in unified YAML (A4)
- [x] CareCost PPTX exported via both engines (B2, B3)
- [x] Q10 scored via LibreOffice + Google Drive (B4) — 6/10
- [x] All tests pass — 114 (C1)
- [x] Smoke test passes both engines (C3)
- [x] stat_hero handler uses `_grid_rect()` (D-fix) — `d9d7ffa`
- [x] Content-aware height estimation for titles (D-fix) — `d9d7ffa`
- [x] Post-layout collision detection (D-fix) — `d9d7ffa`
- [x] S6 role-vs-explicit-y conflict resolved (D-fix) — `d9d7ffa`
- [x] Prevention rules replace B5 errata (D3) — `d9d7ffa`
- [x] Playwright visual comparison: HTML screenshot vs PPTX screenshot per slide (D-visual)
- [x] Visual troubleshooting pipeline: side-by-side diff via `/pptx-fidelity` tool (D-visual)
- [x] Shape naming for element ID linkage: `s{slide}-{type}-{idx}` (D-visual prereq)
- [x] `html_to_sidecar.py` built — DOM position extraction via Playwright (D2) — `2026-05-02`
- [x] `_estimate_min_height()` extended to all text elements, default aligned to 14pt — `2026-05-02`
- [x] `/pptx-fidelity` gate added to `/presentation` as Step 6.5 — `2026-05-02`
- [x] 143 tests pass (132 original + 1 height + 10 sidecar)
- [ ] Q10 ≥ 8/10 — S3 improved (3-col works), S4 regressed (metric/arch overlap), S5 text bug
- [ ] Design tokens flow end-to-end (D4 — Phase E)

---

## Phase E: D2 Position-Aware Sidecar — IN PROGRESS (2026-05-02)

**Tool built:** `TOOLS/scripts/html_to_sidecar.py` — extracts DOM positions at 960×540, merges with existing sidecar
**Enrichment:** CareCost 6 slides → S1: 2/3, S2: 6/6, S3: 6/6, S4: 8/8, S5: 5/5, S6: 2/3

### Visual Comparison After Enrichment

| Slide | Before (D-visual) | After (D2 enrichment) | Change |
|-------|-------------------|----------------------|--------|
| S1 | cosmetic | cosmetic | — |
| S2 | **blocking** (no 2-col) | improved (hero+cards) | ↑ layout present |
| S3 | **blocking** (no cards) | **3-col cards work** | ↑↑ major fix |
| S4 | **blocking** (horizontal arch) | regressed (metrics overlap arch shapes) | ↓ position conflict |
| S5 | **blocking** (no 2-col) | card 1 text upside-down | → new bug |
| S6 | degrading | match | ↑ |

### Open Issues (next iteration)
1. **S4 metric/arch overlap** — enriched stat_cards (2×3 grid) conflict with pre-positioned architecture shapes. Root: sidecar describes 6-across row but HTML renders 2×3 grid. Fix: either restructure sidecar element order or add position-conflict resolution to merge.
2. **S5 card 1 text flip** — first win-card renders with upside-down text. Likely handler or position issue.
3. **P/A/M badges** — sub_elements captured (1 per card on S3) but not yet rendered by `add_card()`.

---

## Phase D-visual: Fidelity Comparison Results ✅ COMPLETE

**Tool built:** `/pptx-fidelity` skill + `TOOLS/lib/pptx_fidelity.py` (capture, compare, report)
**Comparison:** `/tmp/pptx-fidelity/carecost/compare.html` (6 slides, HTML vs Google Slides)
**Shape naming:** `slides_to_pptx.py` now sets `shape.name = s{slide}-{type}-{idx}` for element linkage

### Per-Slide Diagnosis

| Slide | Severity | Visual Issue | Root Cause | Route |
|-------|----------|-------------|-----------|-------|
| S1 | cosmetic | Emoji heart vs stylized glyph | Font/glyph limitation | accept |
| S2 | **blocking** | Vertical stack vs HTML's 2-column ($4T LEFT, stats RIGHT) | Sidecar lacks gridColumn layout | sidecar_data |
| S3 | **blocking** | Title overlaps subtitle, no P/A/M badges, differentiator truncated | Title height + missing sub-shapes | handler_bug + sidecar_data |
| S4 | **blocking** | Stats in row (not 2×3 grid), arch diagram horizontal + overflow | Sidecar lacks grid + orientation | sidecar_data |
| S5 | **blocking** | Title clipped, no screenshot, single column | Sidecar lacks image + 2-column | sidecar_data |
| S6 | degrading | Minor timeline spacing (nudge fix working) | S6 nudge 0.33in delta | cosmetic |

### Key Finding

**4 of 6 slides have blocking issues. All are caused by sidecar data loss, not handler bugs.** The manually-created sidecar JSON doesn't capture 2-column layouts, icon badges, or grid structures from the HTML. The engine's handlers work correctly given the input — but the input is too lossy.

**This triggers D2 (html_to_sidecar.py).** The condition "D-fix achieves < Q10 8 on layouts grid can express" is definitively met. The grid CAN express these layouts with correct `gridColumn` values, but the sidecar doesn't have them.

---

## Backlog Items Triggered by This Session

From `BACKLOG.md`, the following items are now actionable:

| ID | Item | Why Now |
|----|------|---------|
| B14 | Dual-engine A/B comparison | Both engines stable, export tested — prerequisite met |
| B11 | Evidence anchoring per Q | YAML merge complete — prerequisite met |
| B4 | Centroid computation script | LibreOffice now installed, can render PPTX for measurement |

Items NOT yet triggered (need 3+ decks): B1-B3, B5-B7.

## Google Drive Access

PPTXs uploaded to `~/Library/CloudStorage/GoogleDrive-aozuozheng@gmail.com/My Drive/AI PPT/` for native Google Slides review. Per E-PRES-035, never review via PDF conversion.
