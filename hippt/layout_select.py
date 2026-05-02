"""Layout selection intelligence for Phase 7 of AI PPTX pipeline.

Selects the best layout from a YAML library for each slide, then remaps
element positions to match the layout's region coordinates.

Separate from layout_utils.py (geometry/config/YAML I/O) per CTO review.
"""

from __future__ import annotations

import copy
import logging
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from hippt.layout_utils import (
    auto_supports,
    auto_tags,
    classify_role_html,
    infer_slide_type,
    load_config,
)

log = logging.getLogger(__name__)

STRUCTURAL_ROLES = frozenset(
    {"progress_bar", "section_label", "slide_counter", "footer", "masthead"}
)

_DENSITY_ORDER = {"low": 0, "medium": 1, "high": 2}
_DEFAULT_MAX_SLOTS = 16


# ── Data classes ─────────────────────────────────────────────────────────


@dataclass
class SlideProfile:
    slide_type: str
    density: str
    background: str
    roles: Counter = field(default_factory=Counter)
    element_types: set = field(default_factory=set)
    element_count: int = 0
    tags: list = field(default_factory=list)
    supports: list = field(default_factory=list)
    shape_vec: list = field(default_factory=list)


@dataclass
class LayoutMatch:
    layout: dict
    score: float
    layer1_score: float
    layer2_score: float
    shape_score: float = 0.0
    matched_regions: list = field(default_factory=list)
    unmatched_elements: list = field(default_factory=list)


# ── Shape vector (Phase 8) ─────────────────────────────────────────────


def _parse_box_to_floats(box: dict, viewport: dict | None = None) -> tuple[float, ...]:
    """Convert a region box to (x, y, w, h) in [0,1]. Handles both % strings and pixel values."""
    if viewport:
        vw, vh = viewport["w"], viewport["h"]
        return (
            box.get("x", 0) / vw,
            box.get("y", 0) / vh,
            box.get("w", 0) / vw,
            box.get("h", 0) / vh,
        )
    return (
        float(str(box.get("x", "0%")).rstrip("%")) / 100,
        float(str(box.get("y", "0%")).rstrip("%")) / 100,
        float(str(box.get("w", "0%")).rstrip("%")) / 100,
        float(str(box.get("h", "0%")).rstrip("%")) / 100,
    )


def shape_vector(
    regions: list[dict],
    max_slots: int = _DEFAULT_MAX_SLOTS,
    viewport: dict | None = None,
) -> list[float]:
    """Flatten content region bboxes into a fixed-length spatial vector.

    Returns a (max_slots * 4 + 1)-dimensional vector: sorted region coordinates
    zero-padded to max_slots, plus a density float.
    """
    max_slots = max(max_slots, 1)
    box_key = "bbox" if viewport else "box"
    content = [
        r for r in regions if r.get("role") not in STRUCTURAL_ROLES and box_key in r
    ]
    coords = []
    for r in content:
        coords.append((r, _parse_box_to_floats(r[box_key], viewport)))
    coords.sort(key=lambda item: (item[1][1], item[1][0]))
    vec = []
    for _, (x, y, w, h) in coords[:max_slots]:
        vec.extend([x, y, w, h])
    vec.extend([0.0] * (max_slots * 4 - len(vec)))
    vec.append(len(content) / max_slots)
    return vec


def _cosine_sim(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _score_shape(layout: dict, profile: SlideProfile, sel_cfg: dict) -> float:
    shape_cfg = sel_cfg.get("shape", {})
    min_regions = shape_cfg.get("min_content_regions", 2)
    max_slots = shape_cfg.get("max_content_slots", _DEFAULT_MAX_SLOTS)
    layout_vec = layout.get("_shape_vec", [])
    profile_vec = profile.shape_vec
    if not layout_vec or not profile_vec:
        return 0.0
    if len(layout_vec) != len(profile_vec):
        return 0.0
    density_idx = len(layout_vec) - 1
    if layout_vec[density_idx] * max_slots < min_regions:
        return 0.0
    if profile_vec[density_idx] * max_slots < min_regions:
        return 0.0
    return _cosine_sim(layout_vec, profile_vec)


# ── Library loader ─────────────────────────────────────────────────────


def load_layout_library(layout_dir: str | Path, cfg: dict | None = None) -> list[dict]:
    """Load all layout YAMLs from a directory tree, flattening subdirs."""
    layout_dir = Path(layout_dir)
    cfg = cfg or load_config()
    shape_cfg = _get_selection_config(cfg).get("shape", {})
    max_slots = shape_cfg.get("max_content_slots", _DEFAULT_MAX_SLOTS)
    layouts = []
    for p in sorted(layout_dir.rglob("*.yaml")):
        if p.name == "index.yaml":
            continue
        try:
            with open(p) as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict) and "code" in data:
                data["_shape_vec"] = shape_vector(
                    data.get("regions", []), max_slots=max_slots
                )
                layouts.append(data)
        except Exception as exc:
            log.warning("Skipping bad layout YAML %s: %s", p, exc)
    if not layouts:
        log.warning("No layouts loaded from %s", layout_dir)
    return layouts


# ── Step 3: Slide profiling ─────────────────────────────────────────────


def _parse_css_rgb(css: str) -> tuple[int, int, int, float]:
    """Parse 'rgb(r,g,b)' or 'rgba(r,g,b,a)' to (r, g, b, alpha)."""
    m = re.match(
        r"rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)(?:\s*,\s*([\d.]+))?\s*\)",
        css,
    )
    if not m:
        return 255, 255, 255, 1.0
    r, g, b = int(float(m.group(1))), int(float(m.group(2))), int(float(m.group(3)))
    a = float(m.group(4)) if m.group(4) else 1.0
    return r, g, b, a


def infer_slide_profile(
    slide_info: dict,
    index: int,
    total_slides: int,
    cfg: dict | None = None,
) -> SlideProfile:
    """Build a SlideProfile from extracted slide data."""
    cfg = cfg or load_config()
    elements = [e for e in slide_info.get("elements", []) if e.get("render") != "skip"]

    roles: Counter = Counter()
    element_types: set = set()
    regions_for_inference = []

    for e in elements:
        role = classify_role_html(e, cfg)
        roles[role] += 1
        element_types.add(e.get("type", "text"))
        regions_for_inference.append(
            {
                "role": role,
                "element_type": e.get("type", "text"),
                "bbox": e.get("bbox", {}),
            }
        )

    # Slide type: explicit attribute > heuristic
    explicit_type = slide_info.get("slideType")
    if explicit_type:
        slide_type = explicit_type
    else:
        slide_type = infer_slide_type(regions_for_inference, index, total_slides)

    # Density from content element count (excluding structural)
    content_count = sum(
        1 for r, c in roles.items() if r not in STRUCTURAL_ROLES for _ in range(c)
    )
    if content_count <= 3:
        density = "low"
    elif content_count <= 6:
        density = "medium"
    else:
        density = "high"

    # Background: parse CSS color, check luminance
    bg_css = slide_info.get("background", "")
    r, g, b, a = _parse_css_rgb(bg_css)
    if a < 0.1:
        background = "light"
    else:
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        background = "dark" if luminance < 128 else "light"

    # Tags and supports via existing utilities
    tags = auto_tags(regions_for_inference) if regions_for_inference else []
    supports = auto_supports(regions_for_inference) if regions_for_inference else []

    # Shape vector from element bboxes (Phase 8)
    viewport = {"w": 960, "h": 540}
    shape_cfg = _get_selection_config(cfg).get("shape", {})
    max_slots = shape_cfg.get("max_content_slots", _DEFAULT_MAX_SLOTS)
    svec = shape_vector(regions_for_inference, max_slots=max_slots, viewport=viewport)

    return SlideProfile(
        slide_type=slide_type,
        density=density,
        background=background,
        roles=roles,
        element_types=element_types,
        element_count=len(elements),
        tags=tags,
        supports=supports,
        shape_vec=svec,
    )


# ── Steps 4-5: Scoring ──────────────────────────────────────────────────


def _get_selection_config(cfg: dict) -> dict:
    return cfg.get("selection", {})


def _score_layer1(layout: dict, profile: SlideProfile, sel_cfg: dict) -> float:
    """Tag-based scoring. Returns -1 if type doesn't match (hard filter)."""
    if layout["slide_type"] != profile.slide_type:
        return -1.0

    l1 = sel_cfg.get("layer1", {})
    score = 0.0

    # Density
    layout_d = _DENSITY_ORDER.get(layout.get("density", "medium"), 1)
    profile_d = _DENSITY_ORDER.get(profile.density, 1)
    dist = abs(layout_d - profile_d)
    if dist == 0:
        score += l1.get("density_exact", 1.0)
    elif dist == 1:
        score += l1.get("density_adjacent", 0.5)

    # Background
    if layout.get("background") == profile.background:
        score += l1.get("background_match", 1.0)

    # Tag Jaccard
    lt = set(layout.get("tags", []))
    pt = set(profile.tags)
    if lt or pt:
        union = len(lt | pt)
        score += (
            l1.get("tag_jaccard_weight", 2.0) * len(lt & pt) / union if union else 0.0
        )

    # Supports Jaccard
    ls = set(layout.get("supports", []))
    ps = set(profile.supports)
    if ls or ps:
        union = len(ls | ps)
        score += (
            l1.get("supports_jaccard_weight", 1.0) * len(ls & ps) / union
            if union
            else 0.0
        )

    return score


def _score_layer2(layout: dict, profile: SlideProfile, sel_cfg: dict) -> float:
    """Structural compatibility scoring."""
    l2 = sel_cfg.get("layer2", {})
    regions = layout.get("regions", [])
    content_regions = [r for r in regions if r["role"] not in STRUCTURAL_ROLES]

    # Role overlap
    layout_roles = Counter(r["role"] for r in content_regions)
    profile_roles = Counter(
        {r: c for r, c in profile.roles.items() if r not in STRUCTURAL_ROLES}
    )
    matched = sum((layout_roles & profile_roles).values())
    total = max(sum(profile_roles.values()), 1)
    role_score = matched / total
    score = l2.get("role_overlap_weight", 3.0) * role_score

    # Element count fit
    capacity = layout.get("max_regions", len(content_regions)) or 1
    count_ratio = min(profile.element_count, capacity) / max(
        profile.element_count, capacity, 1
    )
    score += l2.get("count_fit_weight", 1.0) * count_ratio

    # Element type compatibility
    layout_types = {r.get("element_type", "text") for r in content_regions}
    if profile.element_types:
        type_overlap = len(profile.element_types & layout_types) / len(
            profile.element_types
        )
    else:
        type_overlap = 0.0
    score += l2.get("type_compat_weight", 1.0) * type_overlap

    return score


def select_layout(
    profile: SlideProfile,
    library: list[dict],
    cfg: dict | None = None,
) -> LayoutMatch | None:
    """Two-layer layout selection. Returns best match or None."""
    cfg = cfg or load_config()
    sel_cfg = _get_selection_config(cfg)
    blend = sel_cfg.get("blend_ratio", 0.6)
    threshold = sel_cfg.get("min_score_threshold", 0.35)
    top_k = sel_cfg.get("top_k_layer1", 8)

    # Layer 1: filter + score
    l1_scored = []
    for layout in library:
        s1 = _score_layer1(layout, profile, sel_cfg)
        if s1 >= 0:
            l1_scored.append((s1, layout))

    if not l1_scored:
        return None

    l1_scored.sort(key=lambda x: x[0], reverse=True)
    candidates = l1_scored[:top_k]

    # Normalize L1 scores
    l1_max = max(s for s, _ in candidates) or 1.0

    # Layer 2 + shape scoring + combine
    shape_w = sel_cfg.get("shape", {}).get("shape_weight", 0.0)
    best: LayoutMatch | None = None
    for l1_raw, layout in candidates:
        l2_raw = _score_layer2(layout, profile, sel_cfg)
        ss = _score_shape(layout, profile, sel_cfg) if shape_w > 0 else 0.0

        l1_norm = l1_raw / 5.0
        l2_norm = l2_raw / 5.0
        l2_blended = (1 - shape_w) * l2_norm + shape_w * ss
        combined = (1 - blend) * l1_norm + blend * l2_blended

        if combined >= threshold and (best is None or combined > best.score):
            best = LayoutMatch(
                layout=layout,
                score=combined,
                layer1_score=l1_raw,
                layer2_score=l2_raw,
                shape_score=ss,
                matched_regions=[],
                unmatched_elements=[],
            )

    return best


# ── Step 6: Matching + remapping ─────────────────────────────────────────


def _parse_pct(val: str) -> float:
    """Parse '5.2%' to 5.2."""
    return float(str(val).rstrip("%"))


def match_elements_to_regions(
    elements: list[dict],
    regions: list[dict],
    cfg: dict | None = None,
) -> tuple[list[tuple[dict, dict]], list[dict]]:
    """Match elements to layout regions by role, then spatial order."""
    cfg = cfg or load_config()
    compat_map = cfg.get("role_compatibility", {})

    # Classify element roles
    elem_roles = [(e, classify_role_html(e, cfg)) for e in elements]

    # Group elements by role
    elem_by_role: dict[str, list[dict]] = {}
    for e, role in elem_roles:
        elem_by_role.setdefault(role, []).append(e)

    # Group regions by role
    region_by_role: dict[str, list[dict]] = {}
    for r in regions:
        region_by_role.setdefault(r["role"], []).append(r)

    def _sort_key(item):
        if "bbox" in item:
            return (item["bbox"].get("y", 0) // 50, item["bbox"].get("x", 0))
        box = item.get("box", {})
        return (_parse_pct(box.get("y", "0%")), _parse_pct(box.get("x", "0%")))

    matched: list[tuple[dict, dict]] = []
    used_regions: set[int] = set()
    matched_elems: set[int] = set()

    # Pass 1: exact role match
    for role, elems in elem_by_role.items():
        avail_regions = region_by_role.get(role, [])
        if not avail_regions:
            continue
        sorted_elems = sorted(elems, key=_sort_key)
        sorted_regions = sorted(avail_regions, key=_sort_key)
        for i, e in enumerate(sorted_elems):
            if i < len(sorted_regions):
                r = sorted_regions[i]
                matched.append((e, r))
                used_regions.add(id(r))
                matched_elems.add(id(e))

    # Pass 2: role compatibility fallback
    for role, elems in elem_by_role.items():
        compat_roles = compat_map.get(role, [])
        for e in elems:
            if id(e) in matched_elems:
                continue
            for cr in compat_roles:
                avail = [
                    r for r in region_by_role.get(cr, []) if id(r) not in used_regions
                ]
                if avail:
                    r = sorted(avail, key=_sort_key)[0]
                    matched.append((e, r))
                    used_regions.add(id(r))
                    matched_elems.add(id(e))
                    break

    unmatched = [e for e, _ in elem_roles if id(e) not in matched_elems]
    return matched, unmatched


def remap_elements(
    slide_data: dict,
    layout_match: LayoutMatch,
    viewport: dict,
) -> None:
    """Remap element bboxes to layout region coordinates. Deep-copy guard."""
    elements = slide_data["slide"]["elements"]
    vw, vh = viewport["w"], viewport["h"]

    # Deep-copy original bboxes for rollback
    original_bboxes = [copy.deepcopy(e.get("bbox", {})) for e in elements]

    try:
        # Build lookup: element id -> region
        remap_map: dict[int, dict] = {}
        for elem, region in layout_match.matched_regions:
            remap_map[id(elem)] = region

        for e in elements:
            region = remap_map.get(id(e))
            if region is None:
                continue

            box = region["box"]
            rx = _parse_pct(box["x"]) / 100 * vw
            ry = _parse_pct(box["y"]) / 100 * vh
            rw = _parse_pct(box["w"]) / 100 * vw
            rh = _parse_pct(box["h"]) / 100 * vh

            if e.get("type") == "image":
                # Preserve aspect ratio within region bounds
                orig_w = e["bbox"].get("w", 1)
                orig_h = e["bbox"].get("h", 1)
                if orig_w > 0 and orig_h > 0:
                    aspect = orig_w / orig_h
                    if rw / rh > aspect:
                        # Region wider than image — fit by height
                        new_h = rh
                        new_w = rh * aspect
                    else:
                        # Region taller than image — fit by width
                        new_w = rw
                        new_h = rw / aspect
                    e["bbox"] = {"x": rx, "y": ry, "w": new_w, "h": new_h}
                else:
                    e["bbox"] = {"x": rx, "y": ry, "w": rw, "h": rh}
            else:
                e["bbox"] = {"x": rx, "y": ry, "w": rw, "h": rh}

    except Exception as exc:
        log.warning("Remap failed, restoring original positions: %s", exc)
        for i, e in enumerate(elements):
            if i < len(original_bboxes):
                e["bbox"] = original_bboxes[i]
