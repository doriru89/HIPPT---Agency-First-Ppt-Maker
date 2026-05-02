#!/usr/bin/env python3
"""
pptx_review_cockpit.py — Generate 3-panel HTML review cockpit for PPTX chain Step 6 gate.

Panels:
  1. Reference tokens (palette, typography, fill stats from extracted YAML)
  2. Generated slides (structure from sidecar JSON)
  3. Token diff (applied vs deviated, per-slide canvas fill badges)

Plus Q1-Q7 score dashboard with mandatory gate indicators.

Usage:
    uv run python -m hippt.review_cockpit \
        --tokens output/design/ref-<slug>.yaml \
        --slides output/html/presentation-<slug>-slides.json \
        [--scores '{"Q1":8,"Q2":7,...}'] \
        [--out output/html/cockpit-<slug>.html]
"""

import argparse
import json
from html import escape
from pathlib import Path

import yaml


def load_tokens(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def load_slides(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def compute_token_diff(ref_tokens: dict, slides_data: dict) -> dict:
    """Compare reference tokens against what the generated slides actually use."""
    ref_palette = {c["hex"].upper(): c for c in ref_tokens.get("palette", [])}
    ref_fonts = {t["family"] for t in ref_tokens.get("typography", [])}

    gen_tokens = slides_data.get("design_tokens", {})
    gen_palette = {c["hex"].upper(): c for c in gen_tokens.get("palette", [])}
    gen_fonts = {t["family"] for t in gen_tokens.get("typography", [])}

    colors_matched = set(ref_palette.keys()) & set(gen_palette.keys())
    colors_added = set(gen_palette.keys()) - set(ref_palette.keys())
    colors_dropped = set(ref_palette.keys()) - set(gen_palette.keys())

    fonts_matched = ref_fonts & gen_fonts
    fonts_added = gen_fonts - ref_fonts
    fonts_dropped = ref_fonts - gen_fonts

    return {
        "colors": {
            "matched": sorted(colors_matched),
            "added": sorted(colors_added),
            "dropped": sorted(colors_dropped),
            "adherence_pct": round(
                len(colors_matched) / max(len(gen_palette), 1) * 100, 1
            ),
        },
        "fonts": {
            "matched": sorted(fonts_matched),
            "added": sorted(fonts_added),
            "dropped": sorted(fonts_dropped),
        },
    }


def estimate_slide_fill(slide: dict) -> float:
    """Estimate canvas fill % from element bounding boxes (10x5.625 inch canvas)."""
    canvas_w, canvas_h = 10.0, 5.625
    canvas_area = canvas_w * canvas_h
    if not slide.get("elements"):
        return 0.0

    filled = 0.0
    for el in slide["elements"]:
        w = el.get("w", 0)
        h = el.get("h", 0)
        filled += w * h

    return min(round(filled / canvas_area * 100, 1), 100.0)


def fill_badge_class(pct: float) -> str:
    if pct >= 85:
        return "fill-excellent"
    if pct >= 70:
        return "fill-good"
    if pct >= 40:
        return "fill-weak"
    return "fill-fail"


def score_bar_class(dim: str, score: int) -> str:
    if dim == "Q2" and score < 7:
        return "gate-violation"
    if dim == "Q6" and score < 8:
        return "gate-violation"
    if score >= 9:
        return "score-excellent"
    if score >= 7:
        return "score-good"
    return "score-weak"


def render_cockpit(
    ref_tokens: dict, slides_data: dict, scores: dict | None, out_path: str
) -> str:
    diff = compute_token_diff(ref_tokens, slides_data)
    slides = slides_data.get("slides", [])
    meta = slides_data.get("metadata", {})

    slide_fills = []
    for i, s in enumerate(slides):
        fill = estimate_slide_fill(s)
        slide_fills.append(
            {
                "index": i + 1,
                "type": s.get("type", "?"),
                "title": s.get("title", ""),
                "fill": fill,
            }
        )

    avg_fill = round(
        sum(sf["fill"] for sf in slide_fills) / max(len(slide_fills), 1), 1
    )

    total_score = sum(scores.values()) if scores else None
    avg_score = round(total_score / 7, 1) if total_score else None

    gate_cap = None
    if scores:
        if scores.get("Q2", 10) < 7:
            gate_cap = ("Q2", 7, "Canvas Utilization < 7 → capped at 7/10 avg")
        elif scores.get("Q6", 10) < 8:
            gate_cap = ("Q6", 8, "Editability < 8 → capped at 8/10 avg")

    ref_palette = ref_tokens.get("palette", [])
    ref_typo = ref_tokens.get("typography", [])
    ref_fill = ref_tokens.get("canvas_fill", {})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PPTX Review Cockpit — {escape(meta.get("title", "Untitled"))}</title>
<style>
:root {{
    --bg: #0F172A; --surface: #1E293B; --surface2: #334155;
    --text: #F1F5F9; --text2: #94A3B8; --accent: #3B82F6;
    --green: #22C55E; --yellow: #EAB308; --red: #EF4444; --orange: #F97316;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: var(--bg); color: var(--text); font-family: 'SF Mono', 'Fira Code', monospace; font-size: 13px; }}
.cockpit {{ max-width: 1400px; margin: 0 auto; padding: 24px; }}
h1 {{ font-size: 18px; font-weight: 600; margin-bottom: 4px; }}
h2 {{ font-size: 14px; font-weight: 600; color: var(--accent); margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.05em; }}
h3 {{ font-size: 12px; font-weight: 600; color: var(--text2); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.04em; }}
.meta {{ color: var(--text2); margin-bottom: 20px; }}

/* Score Dashboard */
.score-dashboard {{ background: var(--surface); border-radius: 8px; padding: 16px; margin-bottom: 20px; }}
.score-row {{ display: flex; gap: 8px; flex-wrap: wrap; }}
.score-card {{ flex: 1; min-width: 120px; background: var(--surface2); border-radius: 6px; padding: 10px; text-align: center; }}
.score-card .dim {{ font-size: 11px; color: var(--text2); margin-bottom: 4px; }}
.score-card .val {{ font-size: 28px; font-weight: 700; }}
.score-card .label {{ font-size: 10px; color: var(--text2); margin-top: 2px; }}
.score-excellent .val {{ color: var(--green); }}
.score-good .val {{ color: var(--accent); }}
.score-weak .val {{ color: var(--yellow); }}
.gate-violation {{ border: 2px solid var(--red); }}
.gate-violation .val {{ color: var(--red); }}
.gate-banner {{ background: var(--red); color: white; padding: 8px 12px; border-radius: 4px; margin-top: 12px; font-weight: 600; font-size: 12px; }}
.total-card {{ background: var(--bg); border: 2px solid var(--accent); }}

/* 3-Panel Layout */
.panels {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }}
@media (max-width: 900px) {{ .panels {{ grid-template-columns: 1fr; }} }}
.panel {{ background: var(--surface); border-radius: 8px; padding: 16px; min-height: 300px; }}

/* Palette Swatches */
.swatch-row {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }}
.swatch {{ width: 32px; height: 32px; border-radius: 4px; border: 1px solid var(--surface2); position: relative; cursor: default; }}
.swatch .tip {{ display: none; position: absolute; bottom: 38px; left: 50%; transform: translateX(-50%); background: var(--bg); padding: 4px 8px; border-radius: 4px; font-size: 10px; white-space: nowrap; z-index: 10; border: 1px solid var(--surface2); }}
.swatch:hover .tip {{ display: block; }}

/* Typography Samples */
.typo-sample {{ padding: 6px 0; border-bottom: 1px solid var(--surface2); }}
.typo-sample:last-child {{ border: none; }}
.typo-family {{ font-weight: 600; }}
.typo-meta {{ color: var(--text2); font-size: 11px; }}

/* Slide Cards */
.slide-card {{ background: var(--surface2); border-radius: 6px; padding: 10px; margin-bottom: 8px; }}
.slide-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }}
.slide-num {{ font-weight: 700; color: var(--accent); }}
.slide-type {{ font-size: 10px; color: var(--text2); text-transform: uppercase; padding: 2px 6px; background: var(--bg); border-radius: 3px; }}
.slide-title {{ font-size: 12px; color: var(--text); line-height: 1.4; }}
.fill-badge {{ display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 11px; font-weight: 700; margin-left: 8px; }}
.fill-excellent {{ background: rgba(34,197,94,0.2); color: var(--green); }}
.fill-good {{ background: rgba(59,130,246,0.2); color: var(--accent); }}
.fill-weak {{ background: rgba(234,179,8,0.2); color: var(--yellow); }}
.fill-fail {{ background: rgba(239,68,68,0.2); color: var(--red); }}

/* Token Diff */
.diff-section {{ margin-bottom: 16px; }}
.diff-label {{ font-size: 11px; color: var(--text2); margin-bottom: 6px; }}
.diff-row {{ display: flex; align-items: center; gap: 8px; padding: 4px 0; }}
.diff-badge {{ font-size: 10px; padding: 1px 6px; border-radius: 3px; font-weight: 600; }}
.badge-match {{ background: rgba(34,197,94,0.2); color: var(--green); }}
.badge-added {{ background: rgba(234,179,8,0.2); color: var(--yellow); }}
.badge-dropped {{ background: rgba(239,68,68,0.2); color: var(--red); }}
.adherence {{ font-size: 24px; font-weight: 700; margin: 8px 0; }}
.stat-row {{ display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid var(--surface2); font-size: 12px; }}
.stat-row:last-child {{ border: none; }}
.stat-label {{ color: var(--text2); }}
</style>
</head>
<body>
<div class="cockpit">
<h1>PPTX Review Cockpit</h1>
<div class="meta">{escape(meta.get("title", ""))} · {escape(meta.get("date", ""))} · {len(slides)} slides · Avg fill: {avg_fill}%</div>
"""

    # Score Dashboard
    if scores:
        dim_names = {
            "Q1": "Structure",
            "Q2": "Canvas",
            "Q3": "Typography",
            "Q4": "Color",
            "Q5": "Data",
            "Q6": "Editability",
            "Q7": "Polish",
        }
        html += '<div class="score-dashboard"><h2>Q1-Q7 Quality Scores</h2><div class="score-row">\n'
        for dim in ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7"]:
            s = scores.get(dim, 0)
            cls = score_bar_class(dim, s)
            gate = ""
            if dim == "Q2":
                gate = " · GATE: &lt;7→cap" if s < 7 else " · GATE: ✓"
            elif dim == "Q6":
                gate = " · GATE: &lt;8→cap" if s < 8 else " · GATE: ✓"
            html += f'<div class="score-card {cls}"><div class="dim">{dim}</div><div class="val">{s}</div><div class="label">{dim_names[dim]}{gate}</div></div>\n'
        html += f'<div class="score-card total-card"><div class="dim">TOTAL</div><div class="val">{total_score}/70</div><div class="label">Avg: {avg_score}/10 · Target: 9.0</div></div>\n'
        html += "</div>\n"
        if gate_cap:
            html += f'<div class="gate-banner">⚠ MANDATORY GATE: {gate_cap[2]}</div>\n'
        html += "</div>\n"
    else:
        html += '<div class="score-dashboard"><h2>Q1-Q7 Quality Scores</h2><div style="color:var(--text2)">No scores provided — run /design-rubric --mode presentation first</div></div>\n'

    # 3-Panel Layout
    html += '<div class="panels">\n'

    # Panel 1: Reference Tokens
    html += '<div class="panel"><h2>Reference Tokens</h2>\n'
    html += '<h3>Palette</h3><div class="swatch-row">\n'
    for c in ref_palette[:12]:
        hex_val = c.get("hex", "#000")
        role = c.get("role", "?")
        freq = c.get("frequency", 0)
        html += f'<div class="swatch" style="background:{hex_val}"><div class="tip">{hex_val} · {role} · ×{freq}</div></div>\n'
    html += "</div>\n"

    html += "<h3>Typography</h3>\n"
    for t in ref_typo[:6]:
        fam = t.get("family", "?")
        size = t.get("size", "?")
        role = t.get("role", "?")
        html += f'<div class="typo-sample"><span class="typo-family">{escape(fam)}</span> <span class="typo-meta">{size} · {role} · ×{t.get("frequency", 0)}</span></div>\n'

    html += "<h3>Canvas Fill (Reference)</h3>\n"
    for k, v in ref_fill.items():
        html += f'<div class="stat-row"><span class="stat-label">{k}</span><span>{v if isinstance(v, (int, float)) else v}{"%" if isinstance(v, float) and v <= 1 else ""}</span></div>\n'

    html += "<h3>Hierarchy</h3>\n"
    html += f'<div class="stat-row"><span class="stat-label">Ratio</span><span>{ref_tokens.get("hierarchy_ratio", "N/A")}×</span></div>\n'
    html += f'<div class="stat-row"><span class="stat-label">Title range</span><span>{ref_tokens.get("title_font_pt", "N/A")}pt</span></div>\n'
    html += f'<div class="stat-row"><span class="stat-label">Body range</span><span>{ref_tokens.get("body_font_pt", "N/A")}pt</span></div>\n'
    html += "</div>\n"

    # Panel 2: Generated Slides
    html += '<div class="panel"><h2>Generated Slides</h2>\n'
    for sf in slide_fills:
        badge_cls = fill_badge_class(sf["fill"])
        title_display = escape(sf["title"][:60]) if sf["title"] else "(no title)"
        html += f"""<div class="slide-card">
<div class="slide-header"><span class="slide-num">#{sf["index"]}</span><span class="slide-type">{sf["type"]}</span><span class="fill-badge {badge_cls}">{sf["fill"]}%</span></div>
<div class="slide-title">{title_display}</div>
</div>\n"""
    html += "</div>\n"

    # Panel 3: Token Diff
    html += '<div class="panel"><h2>Token Diff</h2>\n'

    html += '<div class="diff-section"><h3>Color Adherence</h3>\n'
    html += f'<div class="adherence" style="color:{"var(--green)" if diff["colors"]["adherence_pct"] >= 80 else "var(--yellow)"}">{diff["colors"]["adherence_pct"]}%</div>\n'
    for c in diff["colors"]["matched"]:
        html += f'<div class="diff-row"><div class="swatch" style="width:16px;height:16px;background:{c}"></div><span class="diff-badge badge-match">MATCH</span><span>{c}</span></div>\n'
    for c in diff["colors"]["added"]:
        html += f'<div class="diff-row"><div class="swatch" style="width:16px;height:16px;background:{c}"></div><span class="diff-badge badge-added">ADDED</span><span>{c}</span></div>\n'
    for c in diff["colors"]["dropped"]:
        html += f'<div class="diff-row"><div class="swatch" style="width:16px;height:16px;background:{c}"></div><span class="diff-badge badge-dropped">DROPPED</span><span>{c}</span></div>\n'
    html += "</div>\n"

    html += '<div class="diff-section"><h3>Font Adherence</h3>\n'
    for f in diff["fonts"]["matched"]:
        html += f'<div class="diff-row"><span class="diff-badge badge-match">MATCH</span><span>{escape(f)}</span></div>\n'
    for f in diff["fonts"]["added"]:
        html += f'<div class="diff-row"><span class="diff-badge badge-added">ADDED</span><span>{escape(f)}</span></div>\n'
    for f in diff["fonts"]["dropped"]:
        html += f'<div class="diff-row"><span class="diff-badge badge-dropped">DROPPED</span><span>{escape(f)}</span></div>\n'
    html += "</div>\n"

    html += '<div class="diff-section"><h3>Per-Slide Fill vs Reference</h3>\n'
    ref_avg = ref_fill.get("avg", 0)
    ref_avg_pct = ref_avg * 100 if ref_avg <= 1 else ref_avg
    for sf in slide_fills:
        delta = round(sf["fill"] - ref_avg_pct, 1)
        delta_str = f"+{delta}" if delta > 0 else str(delta)
        badge_cls = fill_badge_class(sf["fill"])
        html += f'<div class="stat-row"><span class="stat-label">Slide {sf["index"]} ({sf["type"]})</span><span class="fill-badge {badge_cls}">{sf["fill"]}% <span style="font-size:10px;opacity:0.7">({delta_str}% vs ref)</span></span></div>\n'
    html += "</div>\n"
    html += "</div>\n"  # panel 3

    html += "</div>\n"  # panels

    html += """
<div style="margin-top:24px;color:var(--text2);font-size:11px;text-align:center">
Generated by pptx_review_cockpit.py · PPTX-from-Source chain Step 6 gate
</div>
</div>
</body>
</html>"""

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    return str(out)


def main():
    parser = argparse.ArgumentParser(
        description="PPTX 3-panel review cockpit generator"
    )
    parser.add_argument("--tokens", required=True, help="Reference design tokens YAML")
    parser.add_argument("--slides", required=True, help="Generated sidecar JSON")
    parser.add_argument(
        "--scores", help="Q1-Q7 scores as JSON string, e.g. '{\"Q1\":8,...}'"
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output HTML path (default: output/html/cockpit-<slug>.html)",
    )
    args = parser.parse_args()

    ref_tokens = load_tokens(args.tokens)
    slides_data = load_slides(args.slides)

    scores = None
    if args.scores:
        scores = json.loads(args.scores)

    if not args.out:
        slug = Path(args.tokens).stem.replace("ref-", "")
        args.out = f"output/html/cockpit-{slug}.html"

    out_path = render_cockpit(ref_tokens, slides_data, scores, args.out)
    print(f"Cockpit: {out_path}")
    print(f"Slides: {len(slides_data.get('slides', []))}")
    if scores:
        total = sum(scores.values())
        print(f"Score: {total}/70 (avg {round(total / 7, 1)}/10)")


if __name__ == "__main__":
    main()
