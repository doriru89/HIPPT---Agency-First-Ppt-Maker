---
name: reference-extract
description: "Extract visual design tokens (colors, typography, spacing, motion) from a reference URL via Playwright."
allowed-tools: [Read, Write, Bash, mcp__playwright__browser_navigate, mcp__playwright__browser_take_screenshot, mcp__playwright__browser_evaluate, mcp__playwright__browser_click, mcp__playwright__browser_snapshot]
argument-hint: "<url> [--element 'selector or description']"
auto_invoke: false
keywords: [reference, extract, design tokens, visual dna, screenshot, style, cherry-pick]
user_invocable: true
categories: [creation]
---

# /reference-extract — Visual Token Extraction from Reference URL

Extract visual DNA (palette, typography, spacing, motion) from a live website via Playwright. Outputs structured YAML for the design cockpit's Reference Board + Cherry-Pick UI.

## When to Use

- the user provides a reference URL: "make it look like metamask.io"
- Called when a reference URL is in the request
- Standalone: `/reference-extract https://example.com`
- With element focus: `/reference-extract https://example.com --element '.hero-button'`

## Procedure

### Step 1: Parse + Slugify

Extract URL from arguments. Slugify domain+path for file naming:
- `https://metamask.io/` → `metamask-io`
- `https://linear.app/features` → `linear-app-features`

### Step 2: Navigate + Screenshot

```
browser_navigate to <url>
```

Wait 3 seconds for animations, lazy-loaded content, and font rendering to settle.

```
browser_take_screenshot to /tmp/playwright-review/ref-<slug>.png
```

### Step 3: Extract Tokens

Run a single `browser_evaluate` call with this JS function that walks the DOM and returns structured token data:

```javascript
(() => {
  const colors = new Map();
  const fonts = new Map();
  const spacings = new Map();
  const radii = new Set();
  const shadows = new Set();
  const motions = new Set();
  const gradients = new Set();

  const els = document.body.querySelectorAll('*');
  els.forEach(el => {
    const s = getComputedStyle(el);

    // Colors
    [s.color, s.backgroundColor, s.borderColor].forEach(c => {
      if (c && c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent') {
        colors.set(c, (colors.get(c) || 0) + 1);
      }
    });

    // Typography
    const family = s.fontFamily.split(',')[0].trim().replace(/['"]/g, '');
    const size = s.fontSize;
    const weight = s.fontWeight;
    const key = `${family}|${weight}|${size}`;
    fonts.set(key, (fonts.get(key) || 0) + 1);

    // Spacing
    [s.paddingTop, s.paddingRight, s.paddingBottom, s.paddingLeft,
     s.marginTop, s.marginRight, s.marginBottom, s.marginLeft].forEach(v => {
      const px = parseFloat(v);
      if (px > 0 && px < 200) spacings.set(px, (spacings.get(px) || 0) + 1);
    });

    // Border radius
    const r = parseFloat(s.borderRadius);
    if (r > 0) radii.add(r);

    // Box shadow
    if (s.boxShadow && s.boxShadow !== 'none') shadows.add(s.boxShadow);

    // Gradients
    if (s.backgroundImage && s.backgroundImage.includes('gradient')) {
      gradients.add(s.backgroundImage);
    }

    // Motion
    if (s.transition && s.transition !== 'all 0s ease 0s') {
      s.transition.split(',').forEach(t => motions.add(t.trim()));
    }
  });

  // CSS custom properties from :root
  const rootStyle = getComputedStyle(document.documentElement);
  const cssVars = [];
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules) {
        if (rule.selectorText === ':root' || rule.selectorText === 'html') {
          const text = rule.cssText;
          const varMatches = text.matchAll(/--([\w-]+)\s*:\s*([^;]+)/g);
          for (const m of varMatches) {
            cssVars.push({ name: `--${m[1]}`, value: m[2].trim() });
          }
        }
      }
    } catch (e) { /* cross-origin stylesheet, skip */ }
  }

  // Helper: rgba to hex
  function rgbaToHex(rgba) {
    const m = rgba.match(/\d+/g);
    if (!m || m.length < 3) return rgba;
    return '#' + [m[0], m[1], m[2]].map(x => parseInt(x).toString(16).padStart(2, '0')).join('');
  }

  // Sort colors by frequency, convert to hex, classify
  const sortedColors = [...colors.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 20)
    .map(([c, freq]) => ({ hex: rgbaToHex(c), raw: c, frequency: freq }));

  // Classify font roles by size
  const fontList = [...fonts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([key, freq]) => {
      const [family, weight, size] = key.split('|');
      const px = parseFloat(size);
      const role = px > 32 ? 'display' : px > 22 ? 'heading' : px > 13 ? 'body' : 'small'; // px ≈ pt at 96 DPI (960×540); thresholds from pptx-quality.yaml
      return { family, weight: parseInt(weight), size, role, frequency: freq };
    });

  // Spacing rhythm: find most common spacing value
  const sortedSpacings = [...spacings.entries()].sort((a, b) => b[1] - a[1]);
  const rhythm = sortedSpacings.length > 0 ? sortedSpacings[0][0] : 8;
  const uniqueSpacings = [...new Set(sortedSpacings.slice(0, 10).map(s => s[0]))].sort((a, b) => a - b);

  return {
    palette: sortedColors,
    typography: fontList,
    spacing: { rhythm: `${rhythm}px`, values: uniqueSpacings },
    radii: [...radii].sort((a, b) => a - b).slice(0, 8),
    shadows: [...shadows].slice(0, 5),
    gradients: [...gradients].slice(0, 3),
    motion: [...motions].slice(0, 8).map(t => {
      const parts = t.split(' ');
      return { raw: t, property: parts[0] || '', duration: parts[1] || '', easing: parts[2] || '' };
    }),
    css_variables: cssVars.slice(0, 30),
  };
})()
```

### Step 3.5: Detect Asset Types

Run a second `browser_evaluate` call to detect what asset technologies the reference site uses. This is informational — no gate, just detection chips for the cockpit Reference Board.

```javascript
(() => {
  const detected = {
    three_js: false, lottie: false, dotlottie: false,
    rive: false, spline: false, video_bg: false,
    webgl_shader: false, canvas_2d: false,
    svg_animation: false, model_viewer: false
  };

  const scripts = [...document.querySelectorAll('script[src]')];
  const scriptSrcs = scripts.map(s => s.src.toLowerCase());
  const inlineScripts = [...document.querySelectorAll('script:not([src])')].map(s => s.textContent);
  const allScriptText = inlineScripts.join(' ').toLowerCase();

  detected.three_js = scriptSrcs.some(s => s.includes('three')) ||
    allScriptText.includes('three.module') ||
    allScriptText.includes('webglrenderer') ||
    !!document.querySelector('canvas[data-engine*="three"]');

  detected.lottie = scriptSrcs.some(s => s.includes('lottie')) ||
    !!document.querySelector('lottie-player, dotlottie-player, [data-lottie]') ||
    allScriptText.includes('lottie');
  detected.dotlottie = !!document.querySelector('dotlottie-player') ||
    scriptSrcs.some(s => s.includes('dotlottie'));

  detected.rive = scriptSrcs.some(s => s.includes('rive')) ||
    !!document.querySelector('canvas[data-rive], [data-rive-canvas]') ||
    allScriptText.includes('rive');

  detected.spline = scriptSrcs.some(s => s.includes('spline')) ||
    !!document.querySelector('spline-viewer') ||
    [...document.querySelectorAll('iframe')].some(f => f.src.includes('spline'));

  const videos = document.querySelectorAll('video');
  detected.video_bg = [...videos].some(v => {
    const s = getComputedStyle(v);
    return s.position === 'absolute' || s.position === 'fixed' ||
           v.closest('[class*="hero"], [class*="bg"], [class*="background"]');
  });

  const canvases = document.querySelectorAll('canvas');
  detected.webgl_shader = [...canvases].some(c => {
    try { return !!(c.getContext('webgl2') || c.getContext('webgl')); }
    catch { return false; }
  }) && !detected.three_js;

  detected.canvas_2d = [...canvases].some(c => {
    try { return !!c.getContext('2d'); }
    catch { return false; }
  }) && !detected.three_js && !detected.webgl_shader;

  const svgs = document.querySelectorAll('svg');
  detected.svg_animation = [...svgs].some(svg =>
    svg.querySelector('animate, animateTransform, animateMotion, set') ||
    [...svg.querySelectorAll('*')].some(el => {
      const s = getComputedStyle(el);
      return s.animationName !== 'none' || s.transition !== 'all 0s ease 0s';
    })
  );

  detected.model_viewer = !!document.querySelector('model-viewer');

  const activeTypes = Object.entries(detected).filter(([,v]) => v).map(([k]) => k);
  return { detected, active_types: activeTypes };
})()
```

Append results to the extraction output YAML under `assets_detected`:

```yaml
assets_detected:
  active_types: [three_js, webgl_shader, svg_animation]
  detected:
    three_js: true
    lottie: false
    dotlottie: false
    rive: false
    spline: false
    video_bg: false
    webgl_shader: true
    canvas_2d: false
    svg_animation: true
    model_viewer: false
```

### Step 4: Element Focus (optional)

If `--element` flag provided:
1. `browser_click` on the specified selector or use `browser_snapshot` to find it
2. `browser_evaluate` on the clicked element to get its full computed style
3. Add to output under `element_focus` key with all style properties

### Step 5: Output YAML

Write to `output/design/ref-<slug>.yaml`:

```yaml
source_url: "<url>"
screenshot: "/tmp/playwright-review/ref-<slug>.png"
extracted_at: <YYYY-MM-DD>
palette:
  - {hex: "#037DD6", role: primary, frequency: 23}
typography:
  - {family: "Euclid Circular B", weight: 500, size: "16px", role: body}
spacing:
  rhythm: "8px"
  values: [8, 16, 24, 32, 48, 64]
radii: [8, 12, 16, 24]
shadows:
  - "0 2px 8px rgba(0,0,0,0.08)"
gradients: []
motion:
  - {property: "transform", duration: "0.3s", easing: "ease-out"}
css_variables:
  - {name: "--color-primary", value: "#037DD6"}
element_focus: null
```

### Step 6: Report

Show the user:
- Screenshot path (suggest opening it)
- Top 5 palette colors with hex values
- Primary font families
- Spacing rhythm
- Suggest next step: "Open cockpit to cherry-pick, or run `/reference-extract <another-url>` to compare."

## Color Role Classification

Heuristic for auto-classifying extracted colors:
- **bg**: Most frequent backgroundColor (>30% of elements)
- **text**: Most frequent color (text foreground)
- **accent**: Colors used on <5% of elements but appearing on buttons, links, or interactive elements
- **surface**: Second-most-frequent backgroundColor
- **border**: Most frequent borderColor

## Rules

- Screenshot path: always `/tmp/playwright-review/ref-<slug>.png` (ephemeral, R-ROOT-01 compliant)
- YAML output: always `output/design/ref-<slug>.yaml`
- Skip iframes and shadow DOM elements (future enhancement)
- Deduplicate: same hex appearing as rgb/rgba/hex → normalize to hex
- Max 20 palette entries, 10 typography entries, 30 CSS variables (prevent noise)
- **BLOCKED — Playwright unavailable:** If Playwright MCP tools fail to connect or `browser_navigate` errors → stop, report "Playwright MCP unavailable", and suggest manual analysis instead. Do not attempt DOM extraction without a live browser.
