"""Tests for design_tokens.py — PPTX pipeline SSOT module."""

from __future__ import annotations

from hippt.design_tokens import (
    ALIGN_CSS_TO_PPTX,
    COLUMN_COUNT,
    COL_WIDTH_IN,
    CSS_PX_TO_PT,
    DEFAULT_FONT,
    MARGIN_IN,
    SAFE_FONTS,
    SLIDE_DPI,
    SLIDE_HEIGHT_IN,
    SLIDE_WIDTH_IN,
    TEXT_PAD_IN,
    VIEWPORT_H,
    VIEWPORT_W,
    css_px_to_pt,
    hex_to_rgb,
    parse_css_color,
    parse_css_px,
    parse_pct,
    px_to_inches,
    rgb_to_hex,
)


# ── Known-good values (blast-radius snapshot) ─────────────────────


class TestConstantDerivations:
    """Constants are physics — if any drift, the entire pipeline breaks."""

    def test_css_px_to_pt_derived_from_dpi(self):
        assert CSS_PX_TO_PT == 72 / SLIDE_DPI

    def test_viewport_matches_slide_dpi(self):
        assert VIEWPORT_W / SLIDE_WIDTH_IN == SLIDE_DPI

    def test_viewport_aspect_ratio_matches_slide(self):
        assert abs(VIEWPORT_W / VIEWPORT_H - SLIDE_WIDTH_IN / SLIDE_HEIGHT_IN) < 1e-9

    def test_col_width_derived(self):
        expected = (SLIDE_WIDTH_IN - 2 * MARGIN_IN) / COLUMN_COUNT
        assert abs(COL_WIDTH_IN - expected) < 1e-9

    def test_frozen_values(self):
        assert VIEWPORT_W == 960
        assert VIEWPORT_H == 540
        assert SLIDE_WIDTH_IN == 10.0
        assert SLIDE_HEIGHT_IN == 5.625
        assert SLIDE_DPI == 96
        assert CSS_PX_TO_PT == 0.75

    def test_font_thresholds(self):
        from hippt.design_tokens import BODY_MIN_PT, DISPLAY_MIN_PT, HEADING_MIN_PT  # noqa: PLC0415

        assert DISPLAY_MIN_PT == 32.0
        assert HEADING_MIN_PT == 22.0
        assert BODY_MIN_PT == 13.0

    def test_margin_and_padding(self):
        assert MARGIN_IN == 0.4
        assert TEXT_PAD_IN == 0.06
        assert COLUMN_COUNT == 12

    def test_default_font_in_safe_fonts(self):
        assert DEFAULT_FONT in SAFE_FONTS

    def test_safe_fonts_is_frozenset(self):
        assert isinstance(SAFE_FONTS, frozenset)

    def test_align_map_superset(self):
        assert set(ALIGN_CSS_TO_PPTX.keys()) == {
            "left",
            "center",
            "right",
            "start",
            "end",
            "justify",
        }


# ── parse_css_color ───────────────────────────────────────────────


class TestParseCssColor:
    def test_rgb(self):
        assert parse_css_color("rgb(255, 128, 0)") == (255, 128, 0, 1.0)

    def test_rgba(self):
        assert parse_css_color("rgba(10, 20, 30, 0.5)") == (10, 20, 30, 0.5)

    def test_rgba_zero_alpha(self):
        assert parse_css_color("rgba(0, 0, 0, 0)") == (0, 0, 0, 0.0)

    def test_hex6(self):
        assert parse_css_color("#FF8000") == (255, 128, 0, 1.0)

    def test_hex3(self):
        assert parse_css_color("#F80") == (255, 136, 0, 1.0)

    def test_hex8_strips_alpha(self):
        assert parse_css_color("#FF8000CC") == (255, 128, 0, 1.0)

    def test_transparent_keyword(self):
        assert parse_css_color("transparent") == (0, 0, 0, 0.0)

    def test_empty_string(self):
        assert parse_css_color("") == (0, 0, 0, 0.0)

    def test_gradient_fallback(self):
        r, g, b, a = parse_css_color("linear-gradient(90deg, #FF0000, #00FF00)")
        assert (r, g, b) == (255, 0, 0)
        assert a == 1.0

    def test_unparseable_returns_black_opaque(self):
        assert parse_css_color("some-garbage") == (0, 0, 0, 1.0)

    def test_rgb_clamps_to_255(self):
        assert parse_css_color("rgb(300, 300, 300)") == (255, 255, 255, 1.0)

    def test_rgb_with_floats(self):
        r, g, b, a = parse_css_color("rgb(128.5, 64.2, 0.9)")
        assert (r, g, b) == (128, 64, 0)

    def test_hex_lowercase(self):
        assert parse_css_color("#ff8000") == (255, 128, 0, 1.0)


# ── hex_to_rgb / rgb_to_hex ──────────────────────────────────────


class TestHexConversion:
    def test_hex6_with_hash(self):
        assert hex_to_rgb("#FF8000") == (255, 128, 0)

    def test_hex6_without_hash(self):
        assert hex_to_rgb("FF8000") == (255, 128, 0)

    def test_hex3(self):
        assert hex_to_rgb("#F80") == (255, 136, 0)

    def test_hex8_strips_alpha(self):
        assert hex_to_rgb("#FF8000CC") == (255, 128, 0)

    def test_rgb_to_hex(self):
        assert rgb_to_hex(255, 128, 0) == "#FF8000"

    def test_roundtrip(self):
        r, g, b = 42, 128, 255
        assert hex_to_rgb(rgb_to_hex(r, g, b)) == (r, g, b)


# ── Coordinate conversion ────────────────────────────────────────


class TestCoordinateConversion:
    def test_px_to_inches_full_width(self):
        result = px_to_inches(960, 960, 10.0)
        assert result == 10.0

    def test_px_to_inches_half_width(self):
        result = px_to_inches(480, 960, 10.0)
        assert result == 5.0

    def test_px_to_inches_zero(self):
        assert px_to_inches(0, 960, 10.0) == 0.0

    def test_css_px_to_pt(self):
        assert css_px_to_pt(16) == 12.0

    def test_css_px_to_pt_identity(self):
        assert css_px_to_pt(1) == CSS_PX_TO_PT


# ── String parsing ───────────────────────────────────────────────


class TestStringParsing:
    def test_parse_pct_basic(self):
        assert parse_pct("5.2%") == 5.2

    def test_parse_pct_integer(self):
        assert parse_pct("100%") == 100.0

    def test_parse_pct_no_sign(self):
        assert parse_pct("42") == 42.0

    def test_parse_css_px_basic(self):
        assert parse_css_px("14.5px") == 14.5

    def test_parse_css_px_integer(self):
        assert parse_css_px("24px") == 24.0

    def test_parse_css_px_empty(self):
        assert parse_css_px("") == 0.0

    def test_parse_css_px_no_unit(self):
        assert parse_css_px("16") == 16.0

    def test_parse_css_px_garbage(self):
        assert parse_css_px("abc") == 0.0


_cfr = __import__(
    "hippt.design_tokens", fromlist=["classify_font_role"]
).classify_font_role


class TestClassifyFontRole:
    """Boundary tests for classify_font_role — uses DISPLAY/HEADING/BODY_MIN_PT."""

    def test_display_at_boundary(self):
        assert _cfr(32.0) == "display"

    def test_display_above(self):
        assert _cfr(48.0) == "display"

    def test_heading_just_below_display(self):
        assert _cfr(31.9) == "heading"

    def test_heading_at_boundary(self):
        assert _cfr(22.0) == "heading"

    def test_body_just_below_heading(self):
        assert _cfr(21.9) == "body"

    def test_body_at_boundary(self):
        assert _cfr(13.0) == "body"

    def test_small_just_below_body(self):
        assert _cfr(12.9) == "small"

    def test_small_zero(self):
        assert _cfr(0) == "small"
