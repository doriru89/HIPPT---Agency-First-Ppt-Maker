"""PPTX pipeline design tokens — Single Source of Truth.

Physics constants (DPI, viewport, slide dimensions) and shared utilities
(color parsing, coordinate conversion) consumed by both the DOM pipeline
(html_to_pptx.py) and the JSON pipeline (slides_to_pptx.py).

No python-pptx dependency. No CLI entrypoint. No sys.exit().
"""

from __future__ import annotations

import re
from typing import TypedDict

# ── Viewport (CSS pixel space, browser rendering target) ──────────
VIEWPORT_W: int = 960
VIEWPORT_H: int = 540

# ── Slide (physical inches, python-pptx coordinate space) ────────
SLIDE_WIDTH_IN: float = 10.0
SLIDE_HEIGHT_IN: float = 5.625
SLIDE_DPI: int = 96

# ── Scaling ───────────────────────────────────────────────────────
# 1 CSS px at 96 DPI = 72pt/in / 96px/in = 0.75pt
CSS_PX_TO_PT: float = 72 / SLIDE_DPI  # 0.75

# ── Layout grid ──────────────────────────────────────────────────
MARGIN_IN: float = 0.4
COLUMN_COUNT: int = 12
COL_WIDTH_IN: float = (SLIDE_WIDTH_IN - 2 * MARGIN_IN) / COLUMN_COUNT
TEXT_PAD_IN: float = 0.06

# ── Font classification thresholds (canonical — pptx-quality.yaml font_role_thresholds) ─
DISPLAY_MIN_PT: float = 32.0
HEADING_MIN_PT: float = 22.0
BODY_MIN_PT: float = 13.0


def classify_font_role(size_pt: float) -> str:
    """Classify font size into display/heading/body/small."""
    if size_pt >= DISPLAY_MIN_PT:
        return "display"
    if size_pt >= HEADING_MIN_PT:
        return "heading"
    if size_pt >= BODY_MIN_PT:
        return "body"
    return "small"


# ── Safe fonts (cross-platform PPTX rendering) ──────────────────
SAFE_FONTS: frozenset[str] = frozenset(
    {
        "Calibri",
        "Arial",
        "Segoe UI",
        "Georgia",
        "Consolas",
        "Times New Roman",
        "Helvetica",
        "Verdana",
        "Tahoma",
        "Courier New",
        "Playfair Display",
        "Source Serif 4",
        "Inter",
    }
)
DEFAULT_FONT: str = "Calibri"

# ── Alignment names (CSS → PPTX enum name, no python-pptx import) ─
ALIGN_CSS_TO_PPTX: dict[str, str] = {
    "left": "LEFT",
    "center": "CENTER",
    "right": "RIGHT",
    "start": "LEFT",
    "end": "RIGHT",
    "justify": "JUSTIFY",
}


# ── Type hints (coordinate-space documentation) ──────────────────


class BBoxPx(TypedDict):
    """Pixel-space bounding box from DOM extraction."""

    x: float
    y: float
    w: float
    h: float


class BoxPct(TypedDict):
    """Percentage-space bounding box from layout YAML."""

    x: str
    y: str
    w: str
    h: str


# ── Color parsing (unified, no python-pptx dependency) ───────────


def parse_css_color(css: str) -> tuple[int, int, int, float]:
    """Parse CSS color string -> (r, g, b, alpha).

    Handles: rgb(), rgba(), #RGB, #RRGGBB, #RRGGBBAA, transparent,
    gradient fallback (extracts first hex as solid).
    Returns (0, 0, 0, 0.0) for transparent/unparseable-as-transparent.
    Returns (0, 0, 0, 1.0) for completely unparseable solid colors.
    """
    if not css or css == "transparent" or css == "rgba(0, 0, 0, 0)":
        return 0, 0, 0, 0.0

    m = re.match(
        r"rgba?\(\s*([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\s*\)", css
    )
    if m:
        r, g, b = int(float(m.group(1))), int(float(m.group(2))), int(float(m.group(3)))
        a = float(m.group(4)) if m.group(4) else 1.0
        return min(r, 255), min(g, 255), min(b, 255), a

    if css.startswith("#"):
        parsed = _parse_hex(css.lstrip("#"))
        if parsed:
            return parsed

    # Gradient fallback — extract first hex color as solid
    m_grad = re.search(r"#([0-9a-fA-F]{3,8})", css)
    if m_grad:
        parsed = _parse_hex(m_grad.group(1))
        if parsed:
            return parsed

    return 0, 0, 0, 1.0


def _parse_hex(h: str) -> tuple[int, int, int, float] | None:
    """Parse raw hex digits (no #) to (r, g, b, 1.0) or None."""
    if len(h) == 3:
        h = h[0] * 2 + h[1] * 2 + h[2] * 2
    if len(h) == 8:
        h = h[:6]
    if len(h) == 6:
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0
    return None


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """Convert '#RRGGBB' or 'RRGGBB' or '#RGB' to (r, g, b)."""
    h = hex_str.lstrip("#")
    if len(h) == 3:
        h = h[0] * 2 + h[1] * 2 + h[2] * 2
    if len(h) == 8:
        h = h[:6]
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert (r, g, b) to '#RRGGBB'."""
    return f"#{r:02X}{g:02X}{b:02X}"


# ── Coordinate conversion ───────────────────────────────────────


def px_to_inches(px: float, viewport_px: float, slide_in: float) -> float:
    """Convert CSS pixels to PPTX inches given viewport and slide dimensions."""
    return (px / viewport_px) * slide_in


def css_px_to_pt(css_px: float) -> float:
    """Convert CSS pixel font size to PowerPoint points."""
    return css_px * CSS_PX_TO_PT


# ── String parsing utilities ────────────────────────────────────


def parse_pct(val: str) -> float:
    """Parse '5.2%' to 5.2."""
    return float(str(val).rstrip("%"))


def parse_css_px(val: str) -> float:
    """Extract numeric value from CSS px string like '14.5px'."""
    if not val:
        return 0.0
    m = re.match(r"([\d.]+)", str(val))
    return float(m.group(1)) if m else 0.0
