# Presentation Slide Components

15 reusable slide types for presentation generation. Each component defines semantic structure, density constraints, and responsive behavior. **No layout prescriptions** — position and composition are left to creative exploration within the philosophy's bounds.

All sizing uses fixed px in the 960×540 coordinate space. All slides: `width: 960px; height: 540px; overflow: hidden;`.

**IMPORTANT — JSON Sidecar Rule**: These components define HTML structure only. When co-authoring the per-slide JSON sidecar, decompose each component into **granular primitives** (text, shape, image). Never emit abstract types like `stat_card`, `hero_stat`, `timeline`, or `evidence_cascade` in JSON. Example: a `hero-stat` HTML component → JSON with `rounded_rectangle` (bg) + `text` (number, 72px) + `text` (context, 16px). See SKILL.md Per-Slide JSON Contract for the canonical format.

## Component Index

| # | Type | When to Use | Max Content |
|---|------|-------------|-------------|
| 1 | `title` | Opening slide | 1 heading + 1 subtitle + optional tagline |
| 2 | `content` | Standard argument slide | 1 heading + 4-6 bullets OR 2 paragraphs |
| 3 | `two-column` | Comparison, contrast | 1 heading + 2 columns, 4 items each |
| 4 | `data` | Chart-driven insight | 1 heading + 1 chart + 1 annotation |
| 5 | `stat` | Single metric spotlight | 1 number + 1 label + 1 line context |
| 6 | `quote` | Pull quote, testimony | 1 quote (max 3 lines) + attribution |
| 7 | `hero-stat` | Oversized number as focal point | 1 number (4rem+) + 1 sentence |
| 8 | `full-bleed-image` | Photo as entire background | 1 image + optional text overlay (max 15 words) |
| 9 | `timeline` | Chronological sequence | 1 heading + 3-7 nodes on horizontal axis |
| 10 | `before-after` | Thesis inversion, pivot | 1 heading + 2 panels (before/after) + pivot label |
| 11 | `evidence-cascade` | Quantity IS the argument | 1 heading + 6-8 cards (3x2 or 4x2) |
| 12 | `section-break` | Chapter divider | 1 heading + optional subtitle. Breathing room. |
| 13 | `data-annotation` | Tufte-style annotated chart | 1 chart with direct labels (no legend) + 1 insight callout |
| 14 | `storyboard` | Demo walkthrough, process | 1 heading + 4-6 panels with captions |
| 15 | `argument-flow` | Logical chain, premises→conclusion | 1 heading + 3-5 connected nodes (vertical) |

---

## Slide Coordinate System (960×540)

Every presentation HTML starts with this CSS foundation. No `clamp()`, no `vw`/`vh`, no responsive logic — the slide IS the viewport. This is the coordinate space all content lives in (LD#3).

```css
:root {
  /* Spacing — all gaps are multiples of this (E-PRES-016) */
  --spacing-unit: 8px;
  --pad-h: 32px;
  --pad-v-top: 48px;
  --pad-v-bottom: 24px;

  /* Font scale — FLOORS, not targets. Auto-scaling pushes up from here.
     These are keynote-mode defaults. Dense mode overrides per slide. */
  --fs-title: 48px;      /* = 36pt in PPTX */
  --fs-subtitle: 28px;   /* = 21pt */
  --fs-body: 18px;       /* = 13.5pt */
  --fs-label: 14px;      /* = 10.5pt */
  --fs-source: 10px;     /* = 7.5pt */

  /* Line heights — one per role, deck-wide (E-PRES-013) */
  --lh-heading: 1.2;
  --lh-body: 1.5;
  --lh-caption: 1.4;

  /* Letter-spacing — 3 roles only (E-PRES-041) */
  --ls-display: 0.02em;
  --ls-label: 0.04em;
  --ls-body: normal;
}

.slide {
  width: 960px;
  height: 540px;
  position: relative;
  overflow: hidden;
}

.slide-content {
  display: grid;
  width: 100%;
  height: 100%;
  padding: var(--pad-v-top) var(--pad-h) var(--pad-v-bottom) var(--pad-h);
  align-content: center; /* (E-PRES-042) */
}

.footnote {
  position: absolute;
  left: var(--pad-h);
  right: var(--pad-h); /* full width (E-PRES-044) */
  bottom: 8px;
  font-size: var(--fs-source);
}
```

### Font Scale Modes

The `:root` variables above are **keynote-mode** defaults (conference/pitch presentations). For data-heavy consulting decks, override per-slide with a density class:

| Mode | Title | Body | Label | Source | When |
|------|-------|------|-------|--------|------|
| **Keynote** (default) | 36–48px | 18–24px | 14px | 10–12px | Conference talks, pitches, TED-style |
| **Dense** (.slide--dense) | 16–20px | 11–13px | 9–10px | 8–9px | BCG/McKinsey data slides, financial tables |

Override pattern: `.slide--dense { --fs-title: 20px; --fs-body: 13px; --fs-label: 10px; --fs-source: 8px; }`

Philosophy YAMLs set the deck-wide baseline. Component guardrails set per-slide-type density. The LLM applies `.slide--dense` to data-heavy slides within a keynote-baseline deck.

### Dual-Engine Note

This CSS foundation serves BOTH engine paths:
- **html_to_pptx.py** (DOM extraction): CSS is load-bearing — extractor reads computed styles
- **slides_to_pptx.py** (sidecar JSON): CSS governs the HTML preview Austin approves at Step 4.9

Risk: CSS font variables and sidecar JSON font sizes can diverge. The `/presentation` skill must emit JSON sizes derived from the same `:root` values.

---

## Component Specifications

### 1. title
```html
<div class="slide slide--title">
  <div class="slide-content">
    <h1 class="deck-title"><!-- Assertive sentence --></h1>
    <p class="deck-subtitle"><!-- Context or tagline --></p>
    <div class="deck-meta"><!-- Author · Date · Context --></div>
  </div>
</div>
```
**Density:** Max 15 words total. The title slide should breathe.

**Guardrails:**
- Canvas fill: EXEMPT — breathing room is intentional on title slides
- Title text: ≥ 48px, bold, centered or left-aligned with hero block
- Empty space must be DESIGNED (centered content, accent bar, hero color block) — not accidental margins
- Anti-pattern: tiny text centered in a vast white void. If centering, the text must be LARGE enough to anchor the space
- If using a color block (hero panel), it should cover ≥40% of the slide — not a thin strip

### 2. content
```html
<div class="slide slide--content">
  <div class="slide-content">
    <h2><!-- Assertive claim --></h2>
    <p class="context"><!-- Why this matters (italic, 2-3 sentences) --></p>
    <div class="body"><!-- Evidence proving the title --></div>
  </div>
</div>
```
**Density:** Max 50 words. If exceeding, split into two slides.

**Guardrails:**
- Canvas fill: ≥80% — content slides must fill the viewport
- Title: ≥ 48px, assertive sentence (not a label), accent color
- Body: ≥ 18px, regular weight. Evidence proving the title claim
- Source citation: present at bottom, ≥ 10px
- Spacing: consistent gap between title→context→body (use a single `--gap` variable)
- Anti-pattern: body text floating in top third with bottom half empty — size body container to fill available height
- Failure example: BCG slides had assertion titles but body content stopped at 60% height, leaving 40% blank

### 3. two-column
**Density:** Max 4 items per column. Columns may be unequal width if one side is more important.

**Guardrails:**
- Canvas fill: ≥80% — both columns together should fill the viewport width
- Column heights: EQUAL — use `align-items: stretch` or `min-height` to match
- Inner spacing: CONSISTENT between items in both columns — same gap value
- Column widths: may be unequal (60/40) but never <30% for the narrow side
- Anti-pattern: one column dense, other sparse — rebalance content or change layout type

### 4. data
**Density:** One chart per slide. Inline SVG only. Direct labels on data points (Tufte). No separate legend.

**Guardrails:**
- Canvas fill: chart ≥60% of slide area — the chart IS the evidence
- Axis labels: ≥ 14px, readable at presentation distance
- Chart labels at 5-7px = E-PRES-001 violation — minimum 10px for any text in charts
- Chart title: assertive insight (what the data SHOWS), not descriptive label (what the chart IS)
- Annotation callout: ≤ 2 lines, near the key data point
- Anti-pattern: tiny chart in corner with large text explanation — chart dominates, text supports
- Failure example: DY3 had chart labels at 5px, completely unreadable

### 5. stat
**Density:** One number, one label. The number should be 4rem+ and the visual focal point.

**Guardrails:**
- Canvas fill: ≥70% — spacious but not empty
- Stat value: ≥ 36px, bold, accent color — eye goes here FIRST
- Stat label: ≥ 14px, regular weight, muted color
- Spacing: equal gaps between stat groups — `space-evenly` or equal margins
- Anti-pattern: decorative panels beside stats (E-PRES-010) — give stats full width
- Anti-pattern: all stats same size when one is primary (E-PRES-009) — primary 1.5x larger
- Failure example: CareCost had 4 stats at 8% canvas fill — content-sized not canvas-sized

### 6. quote
**Density:** Max 3 lines of quote text. Attribution below. Generous whitespace.

**Guardrails:**
- Canvas fill: EXEMPT — generous whitespace is intentional, like title slides
- Quote text: ≥ 24px, italic or serif for visual distinction from body text
- Attribution: ≥ 14px, regular weight, muted color, positioned below quote
- Quotation marks: if decorative, ≥ 72px and accent color — they anchor the space
- Anti-pattern: tiny quote text lost in a vast empty slide — if the quote is short, make the text LARGER to fill the space
- Anti-pattern: attribution styled the same as quote text — must be visually subordinate

### 7. hero-stat
Like `stat` but the number dominates the slide. Think: "40+" taking up 30% of the viewport.
```html
<div class="slide slide--hero-stat">
  <div class="slide-content">
    <div class="hero-number"><!-- e.g., $4.2B --></div>
    <p class="hero-context"><!-- One sentence explaining the number --></p>
  </div>
</div>
```
**Density:** Max 10 words total. The number IS the slide.

**Guardrails:**
- Canvas fill: ≥70% — the number dominates but breathing room is acceptable
- Hero number: ≥ 72px (hero scale), bold, accent color — eye goes here FIRST and ONLY
- Context label: ≥ 18px, regular weight, muted — subordinate to the number
- No competing elements: no decorative graphics, icons, or panels beside the number (E-PRES-010)
- Anti-pattern: number at normal body size (≤36px) — if it's not oversized, use `stat` instead
- Anti-pattern: multiple numbers competing for attention — hero-stat is ONE number, one story

### 8. full-bleed-image
Image covers the entire slide. Text overlay is optional and minimal.
```html
<div class="slide slide--full-bleed" style="background-image: url(...);">
  <div class="slide-content">
    <div class="overlay-text"><!-- Max 15 words --></div>
  </div>
</div>
```
**Density:** Max 15 words of overlay text. The image IS the content.
**Asset requirement:** Requires a real photo (Unsplash, provided, or Playwright screenshot). Never a gradient or generated pattern.

**Guardrails:**
- Canvas fill: 100% — image covers entire viewport via `object-fit: cover` or `background-size: cover`
- Overlay text: ≥ 24px, white, with `text-shadow` or dark gradient scrim for contrast (WCAG AA)
- Image must bleed to ALL edges — no white margins or padding around image
- Gradient scrim: `linear-gradient(to top, rgba(0,0,0,0.7) 0%, transparent 70%)` for bottom-anchored text
- Anti-pattern: image with white margins or visible container border — defeats full-bleed purpose
- Anti-pattern: overlay text without contrast treatment — unreadable on light images

### 9. timeline
Horizontal axis with connected nodes. Each node: date/label + 1-line description.
```html
<div class="slide slide--timeline">
  <div class="slide-content">
    <h2><!-- Assertive claim about progression --></h2>
    <div class="timeline">
      <div class="timeline-node">
        <div class="timeline-date"><!-- Date/label --></div>
        <div class="timeline-desc"><!-- 1-line description --></div>
      </div>
      <!-- ... 3-7 nodes ... -->
    </div>
  </div>
</div>
```
**Density:** 3-7 nodes. Each node max 10 words.

**Guardrails:**
- Canvas fill: ≥80% — timeline should span the full width of the slide
- Nodes: evenly spaced along the axis — `justify-content: space-between` or equal grid columns
- Node text: ≥ 14px, date/label ≥ 12px
- Connector lines: visible between nodes (border, SVG line, or pseudo-element) — the connection IS the timeline
- Anti-pattern: nodes bunched on one side with empty space on the other — redistribute evenly
- Anti-pattern: vertical timeline on a horizontal slide — use horizontal axis to maximize canvas usage

### 10. before-after
Two panels showing transformation. A labeled pivot between them.
```html
<div class="slide slide--before-after">
  <div class="slide-content">
    <h2><!-- The inversion claim --></h2>
    <div class="ba-layout">
      <div class="ba-panel ba-before">
        <h3>Before</h3>
        <!-- Old state -->
      </div>
      <div class="ba-pivot"><!-- Arrow or label --></div>
      <div class="ba-panel ba-after">
        <h3>After</h3>
        <!-- New state -->
      </div>
    </div>
  </div>
</div>
```
**Density:** Max 30 words per panel. Visually differentiate: dim the "before", highlight the "after".

**Guardrails:**
- Canvas fill: ≥80% — both panels together should fill the viewport
- Panel heights: EQUAL — use `align-items: stretch` or matching `min-height`
- "Before" panel: visually dimmed (lower opacity, grayscale filter, or muted colors)
- "After" panel: visually highlighted (accent border, full color, or slight scale-up)
- Panel text: ≥ 16px, readable in both panels
- Pivot label/arrow: centered between panels, visually distinct (accent color, bold)
- Anti-pattern: panels different sizes — creates visual imbalance, defeats comparison purpose
- Anti-pattern: both panels styled identically — the transformation must be VISIBLE

### 11. evidence-cascade
Quantity is the argument. Grid of independent examples.
```html
<div class="slide slide--evidence">
  <div class="slide-content">
    <h2><!-- Claim that examples prove --></h2>
    <div class="evidence-grid">
      <!-- 6-8 cards, each with icon/emoji + 1-2 lines -->
    </div>
  </div>
</div>
```
**Density:** 6-8 cards max. Each card max 15 words.

**Guardrails:**
- Canvas fill: ≥80% — the grid of cards should fill the viewport
- Cards: uniform size — use CSS Grid `repeat(auto-fill, minmax(...))` or fixed columns
- Grid gap: consistent between all cards — same `gap` value
- Card text: ≥ 14px, each card has icon/emoji + short text
- Minimum 6 cards — quantity IS the argument. Fewer than 6? Use `content` slide instead
- Anti-pattern: 2-3 large cards instead of 6-8 small ones — defeats the "cascade" visual of overwhelming evidence
- Anti-pattern: cards with different heights in the same row — use equal height constraints

### 12. section-break
Chapter divider. The slide that lets the audience breathe and reset.
```html
<div class="slide slide--section-break">
  <div class="slide-content">
    <h2><!-- Section title --></h2>
    <p class="section-subtitle"><!-- Optional teaser for next section --></p>
  </div>
</div>
```
**Density:** Max 10 words. Generous negative space. NOT just a centered h2 — give it visual personality (accent bar, texture, color shift).

**Guardrails:**
- Canvas fill: EXEMPT — breathing room is intentional, like title slides
- Section title: ≥ 36px, bold, accent color or contrasting style
- Visual personality required: accent bar, color block, texture, or typographic treatment — NOT just centered text on white (E-PRES-040)
- Subtitle (if present): ≥ 18px, muted, teasing next section content
- Anti-pattern: plain centered h2 on white background — this is placeholder laziness, not a section break
- Anti-pattern: section break that looks identical to a content slide without body — must feel like a "chapter divider"

### 13. data-annotation
Chart with annotations directly on the data. Tufte's ideal.
```html
<div class="slide slide--data-annotation">
  <div class="slide-content">
    <h2><!-- Insight title (what the data shows) --></h2>
    <div class="annotated-chart">
      <svg><!-- Chart with inline text labels on data points --></svg>
      <div class="chart-callout"><!-- Key number or insight --></div>
    </div>
  </div>
</div>
```
**Density:** One chart. All labels directly on data (no separate legend). One callout.

**Guardrails:**
- Canvas fill: ≥70% — chart dominates the slide area
- All labels directly on data points (Tufte principle) — NO separate legend box
- Annotation text: ≥ 12px, callout ≤ 2 lines positioned near the key data point
- Chart title: assertive insight (what the data SHOWS), not descriptive label (what the chart IS)
- Axis labels: ≥ 14px, readable at presentation distance
- Anti-pattern: legend box beside or below chart — labels go ON the data
- Anti-pattern: annotation far from the data it references — proximity = clarity

### 14. storyboard
Sequential panels showing a process or demo walkthrough.
```html
<div class="slide slide--storyboard">
  <div class="slide-content">
    <h2><!-- Process or demo title --></h2>
    <div class="storyboard-grid">
      <div class="story-panel">
        <div class="panel-image"><!-- Screenshot or illustration --></div>
        <div class="panel-caption"><!-- 1-line caption --></div>
      </div>
      <!-- 4-6 panels -->
    </div>
  </div>
</div>
```
**Density:** 4-6 panels. Each caption max 8 words. Panels may be screenshots.

**Guardrails:**
- Canvas fill: ≥80% — panel grid should fill the viewport
- Panels: uniform size in grid layout — use CSS Grid `repeat(auto-fill, minmax(...))`
- Panel border or shadow: each panel must have visual definition (border, shadow, or background)
- Captions: ≥ 12px, positioned below each panel, consistent alignment
- Panel images: if screenshots, container ≥ 400px wide (E-PRES-008)
- Anti-pattern: panels of different sizes floating without grid alignment
- Anti-pattern: captions missing or inconsistently placed — every panel needs a caption

### 15. argument-flow
Vertical chain showing logical progression from premises to conclusion.
```html
<div class="slide slide--argument-flow">
  <div class="slide-content">
    <h2><!-- Conclusion --></h2>
    <div class="flow-chain">
      <div class="flow-node"><!-- Premise 1 --></div>
      <div class="flow-arrow"><!-- ↓ --></div>
      <div class="flow-node"><!-- Premise 2 --></div>
      <div class="flow-arrow"><!-- ↓ --></div>
      <div class="flow-node flow-conclusion"><!-- Therefore... --></div>
    </div>
  </div>
</div>
```
**Density:** 3-5 nodes. Each node max 15 words. The conclusion node is visually distinct.

**Guardrails:**
- Canvas fill: ≥80% — flow chain should span the slide vertically or horizontally
- Nodes connected by arrows/lines — the flow direction must be VISIBLE (SVG arrows, CSS borders, or unicode arrows)
- Node text: ≥ 14px, each node clearly bounded (border, background, or card style)
- Conclusion node: visually distinct — larger size (1.5x), accent color, heavier border, or different background
- Spacing: equal gaps between nodes — consistent `gap` or `margin`
- Anti-pattern: disconnected boxes without visible flow direction — defeats the "argument chain" purpose
- Anti-pattern: conclusion node styled same as premise nodes — the conclusion must stand out

### 16. overlapping-cascade
Scattered overlapping cards communicating chaos, fragmentation, or information overload. Cards partially cover each other like browser tabs in a messy session.
```html
<div class="slide slide--cascade">
  <div class="slide-content">
    <h2><!-- The problem/chaos statement --></h2>
    <div class="cascade-container">
      <div class="cascade-card layer-back"><!-- Label + 1-2 lines --></div>
      <div class="cascade-card layer-back"><!-- Label + 1-2 lines --></div>
      <div class="cascade-card layer-back"><!-- Label + 1-2 lines --></div>
      <div class="cascade-card layer-front"><!-- Label + 1-2 lines --></div>
      <div class="cascade-card layer-front"><!-- Label + 1-2 lines --></div>
    </div>
  </div>
</div>
```
**Density:** 4-6 cards. Each card: 1 label + 1-2 lines content. Overlap ≥20% between adjacent cards.

**Guardrails:**
- Canvas fill: ≥70% — cards should collectively cover most of the viewport
- Cards overlap ≥20% between adjacent cards — overlap IS the visual message (chaos, fragmentation)
- Card text: ≥ 14px, each card has label + 1-2 lines
- Rotation: ±2-5deg transforms for visual energy — cards should NOT be axis-aligned
- Z-index stacking: front cards cast deeper shadows than back cards
- Anti-pattern: cards in a neat grid with no overlap — defeats the cascade purpose entirely
- Anti-pattern: all cards same size and rotation — vary slightly for organic feel (E-PRES-009)

**Key CSS:**
- Two-tier sizing: back-layer `300px`, front-layer `260px` (E-PRES-009)
- `position: absolute` with `top/left/right/bottom %` — never `translate()` (E-PRES-005)
- Shadow depth by z-layer: back `box-shadow: 0 6px 24px rgba(0,0,0,0.35)`, front `box-shadow: 0 12px 40px rgba(0,0,0,0.55)`
- Rotation transforms (-4deg to +5deg) for visual energy
- If cards contain screenshots, container must be ≥400px wide (E-PRES-008)
**When to use:** Information overload, platform fragmentation, chaotic "before" state, overwhelming options

---

## Anti-Slop Component Rules

These apply to ALL components:

1. **No equal-width cards when importance differs** — make the primary item 50% wider
2. **No centered "Thank You" text stacks** — final slide should show the product or key takeaway
3. **No decorative blob/gradient backgrounds** — use texture, grain, photography, or solid color
4. **Vary visual rhythm** — never use the same component type 3 slides in a row
5. **Fragments by default** — content slides should use `.fragment` for progressive disclosure
6. **Viewport-locked** — every slide `width: 960px; height: 540px; overflow: hidden;`. Exceeds? Split.

---

## Canvas Fill Patterns (Framework Research)

How professional HTML slide frameworks solve the "content sits in 8% of the canvas" problem.

### reveal.js (transform-scale model)

**Strategy:** Author at fixed dimensions (960x700 default), then `transform: scale()` the entire slide to fill the viewport. Content layout never changes -- only the zoom factor.

```css
/* Viewport = full browser window */
.reveal-viewport {
  width: 100%; height: 100%; overflow: hidden;
}
/* Slides container = absolute-fill, JS applies transform */
.reveal .slides {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
}
/* Each section fills its container */
.reveal .slides > section {
  width: 100%; height: 100%;
}
/* JS calculates scale factor:
   scale = min(availW / slideW, availH / slideH)
   then applies via: */
.reveal .slides {
  transform: translate(-50%, -50%) scale(var(--slide-scale));
}
/* Backgrounds always cover */
.slide-background-content {
  position: absolute; inset: 0;
  background-size: cover;
  background-position: center;
}
```

**What it teaches:** Author in a fixed coordinate space, scale uniformly. Content uses the FULL 960x700 area because there are no default padding/margins on sections. Themes add padding intentionally (`padding: 30px` in cube/page modes) rather than having padding by default.

**Key defaults:** `margin: 0.04` (4% inset from viewport edge), `minScale: 0.2`, `maxScale: 2.0`. Base font: `40px`. H1: `3.77em` (~150px). These are large because they're designed for projection.

### Slidev (utility-class model)

**Strategy:** Slides are 100% width/height containers. Layouts use Tailwind utility classes for sizing. All styling is composable, not prescriptive.

```css
/* Base slide: full viewport, padded content zone */
.slidev-layout {
  height: 100%;
  padding: 2.5rem 3.5rem;  /* py-10 px-14 in Tailwind */
  font-size: 1.1rem;
}
/* Center layout: grid centering */
.slidev-layout.center {
  display: grid;
  place-content: center;
  height: 100%;
}
/* Two-column: equal split via CSS Grid */
.slidev-layout.two-columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  width: 100%; height: 100%;
}
/* Image-right: grid split with bg-cover pane */
.slidev-layout.image-right {
  display: grid;
  grid-template-columns: 1fr 1fr;
  width: 100%; height: 100%;
}
.slidev-layout.image-right .image-pane {
  background-size: cover;
  background-position: center;
}
```

**What it teaches:** `padding: 2.5rem 3.5rem` creates a generous but not excessive content zone (~6% vertical, ~4.5% horizontal on a 960×540 slide). Two-column layouts use `repeat(2, minmax(0, 1fr))` not `50% 50%` -- the `minmax(0, 1fr)` prevents content from overflowing the grid track. `place-content: center` on a grid is the cleanest centering pattern.

### WebSlides (semantic-class model)

**Strategy:** Sections are flex containers filling `min-height: 100vh`. A `.wrap` container constrains content to 90% width. Grid is flexbox-based with named layout patterns.

```css
/* Slide = flex column, vertically centered */
section {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 100vh;
  padding: 2.4rem;
}
@media (min-width: 1024px) {
  section { padding: 12rem 2.4rem; }
}
/* Content container = 90% width, auto-centered */
.wrap {
  margin-left: auto; margin-right: auto;
  max-width: 100%; width: 100%;
}
@media (min-width: 1024px) {
  .wrap { width: 90%; }
}
/* Grid = flexbox with equal columns */
.grid {
  display: flex; flex-wrap: wrap;
}
.grid > .column {
  display: flex; flex-direction: column;
  flex: auto; width: 100%; padding: 2.4rem;
}
@media (min-width: 768px) {
  .grid > .column { width: 25%; }
}
/* Full-bleed background */
.background {
  position: absolute; inset: 0;
  background-size: cover;
  background-position: center;
}
/* Big data numbers */
.text-data {
  font-size: 6.4rem; line-height: 8rem;
}
@media (min-width: 768px) {
  .text-data { font-size: 15.2rem; line-height: 16.8rem; }
}
```

**What it teaches:** The `padding: 12rem` on desktop creates ~35% vertical padding on a 540px slide viewport -- this is the "breathing room" that makes WebSlides feel cinematic. The `.wrap` at `width: 90%` means content uses 90% of horizontal space. Size utility classes (`.size-50`, `.card-60`) control element widths as percentages of the container. `.text-data` at `15.2rem` on desktop is how "the number IS the slide" works mechanically.

### Cross-Framework Synthesis

| Dimension | reveal.js | Slidev | WebSlides |
|---|---|---|---|
| Viewport lock | JS transform:scale | CSS 100% height | flex min-height:100vh |
| Content width | 100% (no default constraint) | ~91% (px-14 padding) | 90% (.wrap) |
| Vertical padding | 0 default, 4% margin via JS | 2.5rem (~6%) | 12rem (~11%) on desktop |
| Grid system | None built-in | CSS Grid (Tailwind) | Flexbox (.grid .column) |
| Full-bleed | background-size:cover on .slide-background | background-size:cover on image pane | position:absolute inset:0 + cover |
| Font scaling | Fixed px, scaled via transform | rem units + Tailwind scale | rem + media queries |

**The canvas-fill rule:** All three frameworks ensure content uses 80-100% of the slide area. reveal.js achieves this by having zero default padding. Slidev uses modest padding (~5%). WebSlides uses 90% width + generous vertical padding for cinematic feel. None of them leave content floating in 8% of the canvas.

---

## Grid Layout Recipes

Copy-pasteable CSS patterns for common slide layouts. All use fixed px in the 960×540 coordinate space and CSS Grid. Designed for 540px slide containers.

### Recipe 1: Two-Column Split (Text + Image)

Asymmetric split where text gets more space. Image covers its column edge-to-edge.

```css
.slide--split {
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
  height: 540px;
  overflow: hidden;
}
.slide--split .text-col {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 32px 48px;
}
.slide--split .image-col {
  background-size: cover;
  background-position: center;
  /* No padding -- image bleeds to slide edge */
}
```
**Usage:** `3fr / 2fr` = 60/40 split. Swap to `2fr / 3fr` for image-dominant. The `minmax(0, *)` prevents content overflow.

### Recipe 2: Three-Column Equal Grid

For evidence cascades, comparison grids, or feature showcases.

```css
.slide--three-col {
  display: grid;
  grid-template-rows: auto 1fr;
  height: 540px;
  overflow: hidden;
  padding: 32px 40px;
}
.slide--three-col h2 {
  grid-column: 1 / -1;  /* heading spans full width */
}
.slide--three-col .grid-area {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 24px;
  grid-column: 1 / -1;
  align-content: center;
}
.slide--three-col .grid-area > * {
  padding: 16px;
}
```
**Usage:** Heading sits above, three equal columns below. `repeat(3, minmax(0, 1fr))` prevents text overflow. Gap uses spacing-unit multiples.

### Recipe 3: Hero Stat + Supporting Content

Oversized number dominates the left; supporting points on the right.

```css
.slide--hero-split {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  height: 540px;
  overflow: hidden;
}
.slide--hero-split .hero-pane {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 32px;
}
.slide--hero-split .hero-number {
  font-size: 112px;
  font-weight: 800;
  line-height: 1;
}
.slide--hero-split .hero-label {
  font-size: var(--fs-body);
  margin-top: 8px;
  opacity: 0.7;
}
.slide--hero-split .support-pane {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 32px;
}
```
**Usage:** At 960×540, the hero number uses 112px — large enough to dominate the pane. Adjust per slide if the stat has more digits.

### Recipe 4: Full-Bleed Image with Text Overlay

Image covers entire slide. Text overlay anchored to a corner or centered.

```css
.slide--full-bleed {
  position: relative;
  height: 540px;
  overflow: hidden;
  background-size: cover;
  background-position: center;
}
.slide--full-bleed .overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: flex-end;
  padding: 32px 48px;
  /* Gradient scrim for text legibility */
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.7) 0%,
    rgba(0, 0, 0, 0.2) 40%,
    transparent 70%
  );
}
.slide--full-bleed .overlay-text {
  color: #fff;
  font-size: var(--fs-subtitle);
  max-width: 480px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}
```
**Usage:** `align-items: flex-end` anchors text to bottom. Change to `center` for centered overlay, `flex-start` for top. The gradient scrim ensures text is readable regardless of image brightness.

### Recipe 5: Asymmetric Two-Column (70/30)

Wide content area + narrow sidebar. For "main argument + supporting evidence" or "content + sidebar stats".

```css
.slide--asymmetric {
  display: grid;
  grid-template-columns: minmax(0, 7fr) minmax(0, 3fr);
  height: 540px;
  overflow: hidden;
}
.slide--asymmetric .main-col {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 32px 48px;
}
.slide--asymmetric .side-col {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 16px;
  padding: 24px;
  background: rgba(0, 0, 0, 0.03);  /* subtle differentiation */
  border-left: 1px solid rgba(0, 0, 0, 0.08);
}
.slide--asymmetric .side-col .side-stat {
  font-size: 40px;
  font-weight: 700;
  line-height: 1.1;
}
.slide--asymmetric .side-col .side-label {
  font-size: var(--fs-label);
  opacity: 0.6;
}
```
**Usage:** `7fr / 3fr` = 70/30 split. The sidebar background tint and border-left visually separate the zones without heavy decoration. Swap to `3fr / 7fr` for sidebar-first layouts.
