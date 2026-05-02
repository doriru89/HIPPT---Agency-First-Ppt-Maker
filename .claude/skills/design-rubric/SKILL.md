---
name: design-rubric
description: "10-dimension design critique rubric — consulting mode (dashboards, presentations) and art mode (3D, cinematic). Extracted from design-critic agent."
user-invocable: true
auto_invoke: false
keywords: ["design critique", "rubric", "score", "visual review"]
allowed-tools: Read
side_effects: read-only
categories: [design, review]
---

# /design-rubric

Scoring rubric for visual design critique. Two modes: `consulting` (default) and `art`.

## When to Use

- Called during Step 5 of the presentation pipeline for critique scoring
- Standalone: `/design-rubric output/html/hero-page.html`
- When reviewing any visual output for quality before shipping

## Workflow

1. Determine mode from argument or context: `consulting` (default), `art`, or `presentation`
2. Read the target file/screenshot
3. Score each dimension 1-5 (or 1-10 for presentation)
4. Produce the output report with scores + priority fixes

## CONSULTING MODE (10 Dimensions, score 1-5 each)

### 1. First Impression (3-second test)
What do you notice first? What's the emotional response? Does it feel designed or generated? Is there a memorable visual hook?

### 2. Typography & Hierarchy
- Is there a clear heading -> subheading -> body hierarchy?
- Are display fonts distinctive (not system-ui/Inter/Roboto for headings)?
- Is body text readable (>=16px, sufficient contrast)?
- Does the typography set a tone?

### 3. Layout & Alignment
- Is content properly centered within its container?
- Are elements symmetrically aligned?
- Is there a consistent content column width?
- Do block elements (diagrams, cards) break out wider than text for visual emphasis?
- Is the section-inner wrapper pattern used? (R-FE-15, R-FE-17)

### 4. Color & Contrast
- Is the palette cohesive and intentional?
- Do accent colors serve a purpose (not just decoration)?
- Is text contrast sufficient for accessibility?
- Is there color consistency across sections?

### 5. Information Density
- Is content scannable without being sparse?
- Are complex concepts visualized (R-FE-16 diagram patterns)?
- Is there a rhythm of dense -> light -> dense sections?
- Are there visual anchors (diagrams, callouts, cards) breaking up prose?

### 6. Visual Diagrams & Data Visualization
- Do diagrams teach or just decorate?
- Are SVG arrows using orthogonal routing? (R-FE-10)
- Do SVG diagrams have self-contained dark backgrounds? (R-FE-11)
- Are inline HTML/CSS diagrams used for concept-level teaching? (R-FE-16)
- Is the right diagram type chosen for each concept?

### 7. Interactivity & Progressive Disclosure
- Are hover/click interactions used where appropriate?
- Does progressive disclosure reduce cognitive load?
- Are interactive elements discoverable (hover cues, cursor changes)?

### 8. Responsive Behavior (only when requested)
Skip unless the user explicitly asks for mobile/tablet review. When activated:
- Does it work at 768px (tablet), 390px (mobile)?
- Does the sidebar collapse gracefully?
- Do grids reflow without breaking?
Default score: N/A (not tested).

### 9. Whitespace & Breathing Room
- Is there enough space between sections?
- Do elements feel cramped or too spread apart?
- Is whitespace used intentionally to create visual rhythm?

### 10. User Preferences Check
Verify against established preferences (R-FE-09):
- Opening animations: exaggerated, cinematic (not subtle)?
- Real images over abstract SVGs (where applicable)?
- Color-coded labels readable?
- Design feels *designed* not *generated*?

---

## ART MODE (10 Dimensions, score 1-5 each)

Used when `mode: art` is specified. For immersive 3D, gallery exhibitions, cinematic scroll experiences.

### 1. Atmosphere (3-second test)
Does the scene transport you somewhere? Is there an emotional environment? Does it feel like entering a space?

### 2. Typography-as-Art
Is type used as a visual element, not just information delivery? Large-scale display type? Intentional weight contrast?

### 3. Scroll Choreography
Does motion tell a story as you scroll? Is there a narrative arc (build -> climax -> resolve)? Scroll-driven 3D camera movement?

### 4. Color + Light
3D lighting, postprocessing (bloom, LUT grading), time-of-day atmosphere? Coherent color story?

### 5. Technical Craft
Shader quality, WebGL performance, no visual jank. Smooth 60fps? Clean transitions? 3D assets < 2MB? `prefers-reduced-motion`?

### 6. Surprise
Is there one moment that makes you stop scrolling? A visual hook that signals "designed, not generated"?

### 7. Interactivity
Does touching/hovering/clicking change the experience meaningfully? Mouse-follow, drag, hover depth, cursor effects?

### 8. Responsive
Does it work at 768px, 390px? Do 3D scenes degrade gracefully on mobile?

### 9. Coherence
Do ALL elements serve the same emotional goal? Unified visual language across 3D, typography, color, motion?

### 10. Accessibility Floor
Keyboard navigation works, screen reader gets core content, contrast on text readable, `prefers-reduced-motion` respected.

---

## PRESENTATION MODE (10 Dimensions Q1-Q10, score 1-10 each, target 90/100)

Used when `mode: presentation` is specified OR when reviewing a slide deck. Replaces consulting mode for presentations. Full rubric definition: `config/pptx-quality.yaml`.

### Q1: Structure & Narrative (1-10)
- **Ghost deck quality:** Do titles alone tell a complete story? All assertions, no labels?
- **SCR arc:** Clear Situation → Complication → Resolution?
- **Assertion-evidence:** Every slide title is a claim, body is proof?
- **Exec summary:** Can slide 2 convey the full message alone?
- **MECE:** No overlapping slides, no gaps in the argument?
- **9+ bright line:** Titles alone tell the complete story without reading body text

### Q2: Canvas Utilization (1-10) — MANDATORY GATE
- **Viewport fill:** Does each detail slide use ≥80% of available width?
- **Grid/flex balance:** Multi-column layouts balanced, no dead space?
- **Intentional whitespace:** Empty space = design choice, not layout failure?
- **Slide consistency:** Similar fill levels across deck?
- **9+ bright line:** Every detail slide ≥80% fill, breathing slides have intentional empty space
- **Gate:** Q2 < 7 → max total score capped at 7/10 average

### Q3: Typography & Hierarchy (1-10)
- **Size ratios:** Clear 3-level hierarchy (display/heading/body)?
- **Rhythm consistency:** Consistent line-heights per role across slides?
- **Font pairing:** Intentional contrast between display and body fonts?
- **Readability at distance:** Titles ≥48px, body ≥18px (E-PRES-001)?
- **9+ bright line:** Hierarchy weight ratio matches reference ±15%, consistent line-heights per role

### Q4: Color & Harmony (1-10)
- **Palette adherence:** All colors from extracted token palette?
- **Contrast ratios:** WCAG AA compliant on all text?
- **Rogue hues:** ≤5 distinct hues excluding photos (E-PRES-014)?
- **Intentional accent:** Accent colors serve a purpose, not decoration?
- **9+ bright line:** ≤5 distinct hues, all from token palette, WCAG AA contrast

### Q5: Data Presentation (1-10)
- **Data-ink ratio:** Maximize information per visual element (Tufte)?
- **Chartjunk absence:** No decorative borders, 3D effects, gradient fills?
- **Direct labeling:** Labels on the data, not in a separate legend?
- **Evidence density:** Every assertion backed by data evidence?
- **9+ bright line:** No chartjunk, every number earns its pixel, direct labeling on all data
- **Note:** Score N/A (8/10 default) if deck has no data slides

### Q6: Editability & Fidelity (1-10) — MANDATORY GATE
- **Native shapes:** ≥90% elements are native shapes, not screenshots?
- **Text editable:** 100% text editable in PowerPoint/Keynote?
- **Font availability:** Safe fonts or fallback-mapped (E-PPTX-003)?
- **Gradient survival:** CSS effects classified as PPTX-safe vs rasterize-fallback?
- **9+ bright line:** 100% text editable, ≥90% elements native shapes
- **Gate:** Q6 < 8 → max total score capped at 8/10 average

### Q7: Professional Polish (1-10)
- **Alignment consistency:** No misaligned elements across slides?
- **Spacing rhythm:** Consistent spacing ±2px (E-PRES-016)?
- **Visual weight balance:** Elements balanced within each slide (E-PRES-015)?
- **Slide-to-slide coherence:** Visual language consistent across deck?
- **Atmosphere:** Does the deck have a mood, or is it sterile?
- **Surprise:** Is there one slide that makes you stop? A visual hook?
- **9+ bright line:** Pixel-perfect alignment, spacing rhythm matches reference
- **E-PRES-009 bright line:** Card grids — derive sizing intent from ghost deck content. Flat list / "compare" / "features" → uniform width required. "Primary/secondary" / ranking / "hierarchy" → 2-3 width tiers required. Mismatch caps Q7 at 7 for that slide. Intent comes from ghost deck, NOT from the HTML build pass (avoid circular self-judgment).
- **E-PRES-015 bright line:** Content centroid direction changes >2 times in any 4 consecutive slides caps Q7 at 7 — unless shift is intentional cinematic pan (L→C→R). Requires pre-computed centroid values from Playwright/script; do NOT estimate from reading HTML.

### Q8: Visual Evidence (1-10)
- **Image-assertion alignment:** Does each slide's visual PROVE its assertion, not just decorate?
- **Source quality:** Real product screenshots, real data, real photos — not placeholders or stock?
- **Balance:** Mix of text-heavy and image-impact slides? Neither all-text nor all-image?
- **Space allocation:** Images sized appropriately (50-70% of slide for visual-led, 30-40% for text-led)?
- **Data outputs:** Charts/metrics generated from real data where applicable?
- **9+ bright line:** Every assertion backed by visual proof. Eye goes to image first, text supports.
- **E-PRES-011 bright line:** Cards in evidence/milestone grids must have 1 or 3+ content rows. 2-row cards cap Q8 at 7 for that slide. Exception: 2 rows are allowed when one is a heading/label element (h3, h4, .card-label) and the other is a data element (.metric, strong, number). The failure mode is two lines of body text that should be one or three.
- **Note:** Score N/A (7/10 default) for pure data/consulting decks that are intentionally text-heavy.

### Q9: Vision Adherence (1-10)
- **North star alignment:** Does every slide serve the locked vision from Step 0?
- **Audience fit:** Would THIS audience care about what's shown? Or is it self-serving?
- **Goal delivery:** If the goal is "raise money" — does every slide build investor confidence? If "academic defense" — does every slide prove rigor?
- **Tone consistency:** Does the deck FEEL like what was agreed? (consulting tone stays consulting, not creative. Pitch tone stays pitch, not academic.)
- **No drift:** Did the deck drift from the vision during iteration? (common: AI adds "nice-to-have" slides that dilute the core message)
- **9+ bright line:** A stranger reading the vision statement, then viewing the deck, would say "yes, this deck achieves exactly that"

### Q10: Export Fidelity (1-10)
- **Visual match:** Does the PPTX look identical to the approved HTML at 960×540?
- **Text preservation:** All text editable, no rasterized text blocks?
- **Shape fidelity:** CSS shapes survived as native PPTX shapes (not images)?
- **Font survival:** Fonts render correctly in Google Slides / PowerPoint? Fallbacks work?
- **Layout accuracy:** Element positions within ±5px of HTML coordinates?
- **9+ bright line:** Side-by-side HTML vs PPTX screenshot shows no visible differences except anti-aliasing
- **Gate:** Q10 < 8 → iterate export handlers before declaring PPTX done

**Anti-patterns** (instant flags): AP1: screenshot-as-slide (Q6 fail), AP2: >5 hues (E-PRES-014), AP3: <40% fill on detail slides (E-PRES-006), AP4: web-sized text (E-PRES-001), AP5: inconsistent line-heights (E-PRES-013), AP6: font substitution without fallback (E-PPTX-003), AP7: generic stock image not proving assertion (E-PRES-020), AP8: slide that doesn't serve the locked vision (Q9 fail), AP9: PPTX visually diverges from approved HTML (Q10 fail).

**Auto-block:** If any Q < 7, flag specific slides and trigger convergence iteration. Q2 < 7 caps total at 7/10 avg. Q6 < 8 caps total at 8/10 avg. Q10 < 8 → iterate export handlers. If Q1-Q9 avg below `pptx-quality.yaml` first_pass target, trigger convergence even if no single Q is below 7. Fix ONE weakest dimension per round per bottleneck routing in presentation SKILL.md Step 5c.

### Presentation Output Format
```
## Presentation Critique: [deck name]

## Scores
| Dim | Name | Score | Gate | Key Issue |
|-----|------|-------|------|-----------|
| Q1 | Structure & Narrative | X/10 | | ... |
| Q2 | Canvas Utilization | X/10 | Q2<7→cap7 | ... |
| Q3 | Typography & Hierarchy | X/10 | | ... |
| Q4 | Color & Harmony | X/10 | | ... |
| Q5 | Data Presentation | X/10 | | ... |
| Q6 | Editability & Fidelity | X/10 | Q6<8→cap8 | ... |
| Q7 | Professional Polish | X/10 | | ... |
| Q8 | Visual Evidence | X/10 | | ... |
| Q9 | Vision Adherence | X/10 | | ... |
| Q10 | Export Fidelity | X/10 | Q10<8→iterate | ... |
| **Total** | | **X/100** | | Target: 90/100 (9/10 avg) |

## Anti-Pattern Flags
[AP1-AP8 if detected, else "None"]

## Weakest Dimension: Q[N] — [name]
Priority fixes (fix this dimension first):
1. [slide N] — [specific issue] — [specific fix]
2. ...

## Slide-by-Slide Flags
| Slide | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Q9 | Q10 | Issue |
|-------|----|----|----|----|----|----|----|----|----|----|-------|
| 1 | .. | .. | .. | .. | .. | .. | .. | .. | .. | .. | ... |
```

---

## OUTPUT FORMAT

```
# Design Critique: [page name]

## Overall Score: X/50
[1-2 sentence summary]

## What Works Well
- [specific element + why it works]

## What Needs Attention
- [specific element + what's wrong + how to fix]

## Dimension Scores
| Dimension | Score | Key Observation |
|---|---|---|
| First Impression | X/5 | ... |
| Typography | X/5 | ... |
| ... | ... | ... |

## Priority Fixes (top 3)
1. [most impactful fix] -- [effort estimate]
2. ...
3. ...

## Creative Opportunities
- [ideas that would elevate the design from good to memorable]
```

