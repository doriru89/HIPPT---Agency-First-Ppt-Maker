#!/usr/bin/env python3
"""Extract layout library from html_to_pptx.py debug JSON.

Reads layout-classified.json, converts pixel bboxes to percentage-based regions,
classifies element roles, groups adjacent elements, and outputs layout YAMLs.

Usage:
    uv run python -m hippt.extract_layouts output/debug/layout-classified.json
    uv run python -m hippt.extract_layouts debug.json --out layouts/ --verify
"""

import argparse
import json
import logging
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

from hippt.layout_utils import (
    VIEWPORT_H,
    VIEWPORT_W,
    auto_supports,
    auto_tags,
    classify_role_html,
    cluster_by_x,
    dominant_role,
    element_type,
    get_thresholds,
    load_config,
    merge_bbox,
    pct_box,
    split_y_bands,
    verify_layouts,
    write_layout_index,
    write_layout_yaml,
)

log = logging.getLogger(__name__)


def _get_slide_layout_map(cfg):
    return {
        int(k): (v["code"], v["name"], v["type"])
        for k, v in cfg["slide_layouts"].items()
    }


def _extract_family(selector):
    if "." not in selector:
        return None
    cls = selector.split(".", 1)[1]
    return cls.split("-")[0]


def _group_elements(elements, vw, vh, cfg=None):
    cfg = cfg or load_config()
    th = get_thresholds(cfg)
    structural_roles = set(
        cfg.get("structural_roles", ["progress_bar", "section_label", "slide_counter"])
    )
    generic_pass = set(
        cfg.get(
            "generic_passthrough_roles",
            [
                "body_text",
                "detail_text",
                "headline",
                "section_heading",
                "evidence_image",
            ],
        )
    )
    merge_roles = cfg.get("merge_roles", {})
    x_thresh = vw * th["x_prox"]
    y_band_thresh = vh * th["y_band"]
    generic_max = vh * th["generic_max"]
    x_margin = vw * th["x_margin"]

    regions = []

    progress = [e for e in elements if e["_role"] == "progress_bar"]
    if progress:
        regions.append(
            {
                "role": "progress_bar",
                "bbox": merge_bbox([e["bbox"] for e in progress]),
                "elements": progress,
                "element_type": "shape",
            }
        )
    for e in elements:
        if e["_role"] in structural_roles and e["_role"] != "progress_bar":
            regions.append(
                {
                    "role": e["_role"],
                    "bbox": e["bbox"],
                    "elements": [e],
                    "element_type": "text",
                }
            )

    content = [e for e in elements if e["_role"] not in structural_roles]
    family_groups = defaultdict(list)
    generics = []
    for e in content:
        family = _extract_family(e.get("selector", ""))
        if family:
            family_groups[family].append(e)
        elif e["_role"] not in generic_pass:
            family_groups[f"_r_{e['_role']}"].append(e)
        else:
            generics.append(e)

    content_regions = []
    for _fam, elems in family_groups.items():
        for xc in cluster_by_x(elems, x_thresh):
            content_regions.append(
                {
                    "role": dominant_role(xc, cfg),
                    "bbox": merge_bbox([e["bbox"] for e in xc]),
                    "elements": list(xc),
                    "element_type": element_type(xc),
                }
            )

    for g in sorted(generics, key=lambda e: e["bbox"]["y"]):
        gx = g["bbox"]["x"] + g["bbox"]["w"] / 2
        gy = g["bbox"]["y"] + g["bbox"]["h"] / 2
        best_cr, best_dist = None, float("inf")
        for cr in content_regions:
            cb = cr["bbox"]
            rx1 = cb["x"] - x_margin
            rx2 = cb["x"] + cb["w"] + x_margin
            if not (rx1 <= gx <= rx2):
                continue
            ry_bot = cb["y"] + cb["h"]
            dist = max(0, gy - ry_bot) if gy > ry_bot else max(0, cb["y"] - gy)
            if dist < best_dist:
                best_dist, best_cr = dist, cr
        if best_cr is not None and best_dist < generic_max:
            best_cr["elements"].append(g)
            best_cr["bbox"] = merge_bbox([e["bbox"] for e in best_cr["elements"]])
            best_cr["element_type"] = element_type(best_cr["elements"])
        else:
            et = "image" if g.get("type") == "image" else "text"
            content_regions.append(
                {
                    "role": g["_role"],
                    "bbox": g["bbox"],
                    "elements": [g],
                    "element_type": et,
                }
            )

    min_split = th["min_split"]
    split_regions = []
    for cr in content_regions:
        if len(cr["elements"]) >= min_split:
            bands = split_y_bands(cr["elements"], y_band_thresh)
        else:
            bands = [cr["elements"]]
        for band in bands:
            split_regions.append(
                {
                    "role": dominant_role(band, cfg),
                    "bbox": merge_bbox([e["bbox"] for e in band]),
                    "elements": band,
                    "element_type": element_type(band),
                }
            )
    content_regions = split_regions

    for src_role, merged_name in merge_roles.items():
        matches = [r for r in content_regions if r["role"] == src_role]
        if len(matches) > 1:
            all_elems = [e for r in matches for e in r["elements"]]
            kept = [r for r in content_regions if r["role"] != src_role]
            kept.append(
                {
                    "role": merged_name,
                    "bbox": merge_bbox([e["bbox"] for e in all_elems]),
                    "elements": all_elems,
                    "element_type": element_type(all_elems),
                }
            )
            content_regions = kept

    regions.extend(content_regions)
    regions.sort(key=lambda r: (r["bbox"]["y"], r["bbox"]["x"]))
    return regions


def extract_slide_layout(
    slide_data, index, viewport, source="smart-tickets-r2", config_path=None
):
    cfg = load_config(config_path)
    vw, vh = viewport["w"], viewport["h"]
    elements = [
        dict(e, _role=classify_role_html(e, cfg))
        for e in slide_data.get("elements", [])
    ]
    if not elements:
        return None

    raw_regions = _group_elements(elements, vw, vh, cfg)
    structural = set(
        cfg.get("structural_roles", ["progress_bar", "section_label", "slide_counter"])
    )
    content_count = sum(1 for r in raw_regions if r["role"] not in structural)

    regions_out = []
    for r in raw_regions:
        regions_out.append(
            {
                "role": r["role"],
                "element_type": r["element_type"],
                "box": pct_box(r["bbox"], vw, vh),
            }
        )

    layout_map = _get_slide_layout_map(cfg)
    code, name, slide_type = layout_map.get(
        index, (f"L-UNK-{index:03d}", "Unknown", "unknown")
    )
    bg = slide_data.get("background", "")
    m = re.match(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", bg or "")
    r, g, b = (int(m.group(i)) for i in (1, 2, 3)) if m else (245, 243, 239)
    background = "dark" if (0.299 * r + 0.587 * g + 0.114 * b) / 255 < 0.5 else "light"
    density = (
        "low" if content_count <= 3 else ("medium" if content_count <= 6 else "high")
    )

    return {
        "code": code,
        "name": name,
        "source": f"{source}-s{index + 1}",
        "slide_type": slide_type,
        "background": background,
        "density": density,
        "max_regions": content_count,
        "tags": auto_tags(raw_regions),
        "supports": auto_supports(raw_regions),
        "regions": regions_out,
        "origin": "html",
        "slide_master": None,
        "aspect_ratio": "16:9",
        "thumbnail": None,
        "context": "",
        "anti_patterns": "",
        "created": str(date.today()),
        "verified_in": "pending",
        "calibration_status": "candidate",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract layout library from debug JSON"
    )
    parser.add_argument("json_path", help="Path to layout-classified.json")
    parser.add_argument("--out", default="output/layouts")
    parser.add_argument("--source", default="smart-tickets-r2")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    with open(args.json_path) as f:
        data = json.load(f)
    viewport = data.get("viewport", {"w": VIEWPORT_W, "h": VIEWPORT_H})
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    layouts = []
    for i, slide in enumerate(data["slides"]):
        layout = extract_slide_layout(slide, i, viewport, args.source)
        if layout:
            write_layout_yaml(layout, out_dir)
            log.info(
                "S%d → %s (%d regions)", i + 1, layout["code"], len(layout["regions"])
            )
            layouts.append(layout)

    write_layout_index(layouts, out_dir)
    log.info("Index: %d layouts → %s/index.yaml", len(layouts), out_dir)

    if args.verify:
        warns = verify_layouts(layouts, viewport)
        for w in warns:
            log.warning("VERIFY: %s", w)
        if not warns:
            log.info("VERIFY: all regions within tolerance")


if __name__ == "__main__":
    main()
