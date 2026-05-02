"""Shared layout extraction utilities for both HTML and PPTX paths.

Geometry primitives, config loading, YAML output, and verification functions
used by extract_layouts.py (HTML path) and pptx_to_layout.py (PPTX path).
"""

from __future__ import annotations

import re
import threading
from datetime import date
from pathlib import Path

import yaml

from hippt.design_tokens import parse_css_px as parse_px


def hex_color(rgb_color) -> str | None:
    """Extract hex string from an RGBColor or similar object."""
    try:
        if rgb_color is None:
            return None
        r, g, b = rgb_color[0], rgb_color[1], rgb_color[2]
        return f"#{r:02X}{g:02X}{b:02X}"
    except Exception:
        return None


_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent / "config/layout-extraction.yaml"
)
_cfg_cache: dict[str, dict] = {}
_cfg_lock = threading.Lock()


def load_config(config_path: str | Path | None = None) -> dict:
    with _cfg_lock:
        p = Path(config_path).resolve() if config_path else _CONFIG_PATH
        key = str(p)
        if key in _cfg_cache:
            return _cfg_cache[key]
        with open(p) as f:
            cfg = yaml.safe_load(f)
        _cfg_cache[key] = cfg
        return cfg


def get_thresholds(cfg: dict) -> dict:
    t = cfg.get("thresholds", {})
    return {
        "x_prox": t.get("x_proximity_pct", 3) / 100,
        "y_band": t.get("y_band_split_pct", 10) / 100,
        "generic_max": t.get("generic_max_dist_pct", 40) / 100,
        "x_margin": t.get("x_overlap_margin_pct", 5) / 100,
        "min_split": t.get("min_elements_for_split", 5),
    }


# ── Geometry primitives ────────────────────────────────────────────────────


def merge_bbox(bboxes: list[dict]) -> dict:
    x1 = min(b["x"] for b in bboxes)
    y1 = min(b["y"] for b in bboxes)
    x2 = max(b["x"] + b["w"] for b in bboxes)
    y2 = max(b["y"] + b["h"] for b in bboxes)
    return {"x": x1, "y": y1, "w": x2 - x1, "h": y2 - y1}


def cluster_by_x(elements: list[dict], threshold: float) -> list[list[dict]]:
    if not elements:
        return []
    sorted_elems = sorted(elements, key=lambda e: e["bbox"]["x"])
    clusters = [[sorted_elems[0]]]
    for e in sorted_elems[1:]:
        cluster_max_x = max(ce["bbox"]["x"] for ce in clusters[-1])
        if e["bbox"]["x"] - cluster_max_x <= threshold:
            clusters[-1].append(e)
        else:
            clusters.append([e])
    return clusters


def split_y_bands(elements: list[dict], gap_threshold: float) -> list[list[dict]]:
    if len(elements) <= 1:
        return [elements]
    sorted_elems = sorted(elements, key=lambda e: e["bbox"]["y"])
    bands = [[sorted_elems[0]]]
    for e in sorted_elems[1:]:
        prev = bands[-1][-1]
        gap = e["bbox"]["y"] - (prev["bbox"]["y"] + prev["bbox"]["h"])
        if gap > gap_threshold:
            bands.append([e])
        else:
            bands[-1].append(e)
    return bands


# ── Role and type classification ───────────────────────────────────────────


def dominant_role(elements: list[dict], cfg: dict | None = None) -> str:
    cfg = cfg or load_config()
    roles = [e["_role"] for e in elements]
    for p in cfg.get("role_priority", []):
        if p in roles:
            return p
    return roles[0] if roles else "body_text"


def element_type(elements: list[dict]) -> str:
    types = {e.get("type", "text") for e in elements}
    if len(types) == 1:
        t = types.pop()
        return {
            "text": "text",
            "image": "image",
            "shape": "shape",
            "table": "table",
        }.get(t, "composite")
    return "composite"


# ── HTML element role classification ──────────────────────────────────────


def _get_selector_roles(cfg: dict):
    return [(entry["selectors"], entry["role"]) for entry in cfg["selector_roles"]]


def _get_text_patterns(cfg: dict):
    return [(re.compile(p["pattern"]), p["role"]) for p in cfg.get("text_patterns", [])]


def classify_role_html(elem: dict, cfg: dict | None = None) -> str:
    """Classify an HTML-extracted element's semantic role via CSS selector, text, and font size."""
    cfg = cfg or load_config()
    sel = elem.get("selector", "")
    for patterns, role in _get_selector_roles(cfg):
        if any(p in sel for p in patterns):
            return role
    if elem.get("type") == "image":
        return "evidence_image"
    if elem.get("isDecorative"):
        return "divider" if elem["bbox"]["h"] < 6 else "decorative_shape"
    text = (elem.get("text") or "").strip()
    for pat, role in _get_text_patterns(cfg):
        if pat.match(text):
            return role
    fs = parse_px(elem.get("style", {}).get("fontSize", "0"))
    fw = str(elem.get("style", {}).get("fontWeight", "400"))
    if fs > 24:
        return "headline"
    if 15 <= fs <= 17 and fw in ("700", "800", "bold"):
        return "section_heading"
    if fs <= 12:
        return "detail_text"
    return "body_text"


# ── Slide type inference ─────────────────────────────────────────────────


_MASTER_NAME_MAP = {
    "title slide": "title",
    "section header": "title",
    "two content": "comparison",
    "comparison": "comparison",
    "title only": "editorial",
    "blank": None,
}


def infer_slide_type(regions, index, total_slides, master_name=""):
    """Infer slide type from region composition + optional slide master name."""
    if master_name:
        mapped = _MASTER_NAME_MAP.get(master_name.lower())
        if mapped:
            return mapped

    roles = {r["role"] for r in regions}
    content_count = sum(
        1
        for r in regions
        if r["role"]
        not in ("progress_bar", "section_label", "slide_counter", "footer", "masthead")
    )

    if index == 0 and content_count <= 5:
        return "title"
    if index == total_slides - 1 and content_count <= 5:
        return "close"
    if "data_table" in roles:
        return "data"
    if "stat_value" in roles:
        return "data"
    if "radial_hub" in roles or "spoke_item" in roles:
        return "radial"
    if "era_marker" in roles or "timeline_bar" in roles:
        return "timeline"
    if sum(1 for r in regions if r["role"] == "evidence_image") >= 2:
        return "comparison"
    return "editorial"


# ── Percentage box and YAML output ─────────────────────────────────────────


class BoxDict(dict):
    """Dict subclass for flow-style YAML output of box coordinates."""

    pass


class LayoutDumper(yaml.SafeDumper):
    pass


LayoutDumper.add_representer(
    BoxDict,
    lambda d, data: d.represent_mapping(
        "tag:yaml.org,2002:map", data.items(), flow_style=True
    ),
)


def pct_box(bbox: dict, vw: float, vh: float) -> BoxDict:
    def fmt(val: float, total: float) -> str:
        p = val / total * 100
        return f"{int(p)}%" if p == int(p) else f"{p:.1f}%"

    return BoxDict(
        {
            "x": fmt(bbox["x"], vw),
            "y": fmt(bbox["y"], vh),
            "w": fmt(bbox["w"], vw),
            "h": fmt(bbox["h"], vh),
        }
    )


# ── Tag and support generation ─────────────────────────────────────────────


def auto_tags(regions: list[dict]) -> list[str]:
    tags = []
    roles = {r["role"] for r in regions}
    xs = sorted(
        {
            round(r["bbox"]["x"] + r["bbox"]["w"] / 2, -1)
            for r in regions
            if r["role"] not in ("progress_bar", "section_label", "slide_counter")
        }
    )
    if len(xs) >= 3:
        tags.append("three-column")
    elif len(xs) >= 2:
        tags.append("two-column")
    for role, tag in [
        ("evidence_image", "evidence-images"),
        ("data_table", "data-table"),
        ("stat_value", "stat-cards"),
        ("timeline_bar", "timeline"),
        ("era_marker", "timeline"),
        ("radial_hub", "radial"),
        ("spoke_item", "hub-and-spoke"),
    ]:
        if role in roles and tag not in tags:
            tags.append(tag)
    return tags


def auto_supports(regions: list[dict]) -> list[str]:
    supports = set()
    for r in regions:
        et, role = r["element_type"], r["role"]
        if et == "text" and role in ("headline", "subtitle", "section_heading"):
            supports.add("text-heading")
        elif et == "text":
            supports.add("text-body")
        elif et == "image":
            supports.add("image-proof")
        elif et == "shape":
            supports.add("accent-bar")
        elif et == "table":
            supports.add("data-table")
        elif et == "composite":
            supports.add("composite-region")
    return sorted(supports)


# ── YAML file output ──────────────────────────────────────────────────────


def write_layout_yaml(layout: dict, output_dir: str | Path) -> Path:
    path = Path(output_dir) / f"{layout['code']}.yaml"
    with open(path, "w") as f:
        yaml.dump(
            layout,
            f,
            Dumper=LayoutDumper,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
    return path


def write_layout_index(layouts: list[dict], output_dir: str | Path) -> Path:
    entries = [
        {
            "code": la["code"],
            "name": la["name"],
            "type": la["slide_type"],
            "source": la["source"],
            "origin": la["origin"],
            "regions": la["max_regions"],
        }
        for la in layouts
        if la
    ]
    index = {
        "schema_version": 1,
        "extracted": str(date.today()),
        "source": layouts[0]["source"].rsplit("-s", 1)[0] if layouts else "unknown",
        "layouts": entries,
    }
    path = Path(output_dir) / "index.yaml"
    with open(path, "w") as f:
        yaml.dump(
            index,
            f,
            Dumper=LayoutDumper,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
    return path


# ── Verification ──────────────────────────────────────────────────────────


def verify_layouts(layouts: list[dict], viewport: dict) -> list[str]:
    vw = viewport["w"]
    warnings = []
    for i, layout in enumerate(layouts):
        if not layout:
            continue
        for reg in layout["regions"]:
            box = reg["box"]
            x_px = float(box["x"].rstrip("%")) / 100 * vw
            w_px = float(box["w"].rstrip("%")) / 100 * vw
            if x_px + w_px > vw * 1.02:
                warnings.append(
                    f"S{i + 1} {reg['role']}: x overflow ({box['x']}+{box['w']})"
                )
    return warnings
