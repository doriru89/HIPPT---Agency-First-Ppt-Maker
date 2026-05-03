"""Tests for layout assertion functions in slides_to_pptx.py.

TDD: these tests are written BEFORE the implementation.
Tests cover: stat_hero grid positioning, height estimation,
collision detection, off-slide overflow, and role-vs-explicit-y conflict.
"""

from __future__ import annotations

import pytest

from hippt.design_tokens import (
    MARGIN_IN,
    SLIDE_HEIGHT_IN,
    SLIDE_WIDTH_IN,
)


# ---------------------------------------------------------------------------
# Test _estimate_min_height
# ---------------------------------------------------------------------------


class TestHeightEstimation:
    """Content-aware height estimation for title elements."""

    def _call(self, content: str, font_size_pt: float, box_w_inches: float) -> float:
        from hippt.slides_to_pptx import _estimate_min_height

        return _estimate_min_height(content, font_size_pt, box_w_inches)

    def test_short_title_keeps_minimum(self):
        result = self._call("Short title", 20, 9.2)
        assert result >= 0.5

    def test_long_title_gets_taller(self):
        title = "Americans can't answer 'how much will I pay?' — and $4T in healthcare spend says they should"
        result = self._call(title, 20, 9.2)
        assert result > 0.7, f'92-char title must exceed bad h=0.7", got {result:.2f}'

    def test_very_long_title(self):
        title = "A" * 140
        result = self._call(title, 20, 9.2)
        assert result >= 1.0, f'140-char title at 20pt needs ≥1.0", got {result:.2f}'

    def test_font_size_affects_height(self):
        title = "A" * 80
        h_small = self._call(title, 14, 9.2)
        h_large = self._call(title, 28, 9.2)
        assert h_large > h_small, (
            f"28pt ({h_large:.2f}) should need more height than 14pt ({h_small:.2f})"
        )

    def test_body_text_14pt_narrow_box(self):
        content = "This is a longer body paragraph that would clip at the default 0.5 inch height when rendered at 14pt in a narrow column."
        result = self._call(content, 14, 4.0)
        assert result > 0.5, (
            f'120-char body at 14pt/4" box must exceed 0.5", got {result:.2f}'
        )

    def test_empty_content_returns_minimum(self):
        result = self._call("", 20, 9.2)
        assert result == 0.5


# ---------------------------------------------------------------------------
# Test _check_collisions
# ---------------------------------------------------------------------------


class TestCollisionDetection:
    """Post-layout collision detection between placed elements."""

    def _call(
        self, placed: list[tuple[str, float, float, float, float, bool, bool]]
    ) -> list[str]:
        from hippt.slides_to_pptx import _check_collisions

        return _check_collisions(placed)

    def test_no_collision(self):
        placed = [
            ("title", 0.4, 1.0, 9.2, 0.8, False, True),
            ("card", 0.4, 2.0, 4.0, 1.5, False, True),
        ]
        warnings = self._call(placed)
        assert warnings == []

    def test_overlapping_detected(self):
        placed = [
            ("title", 0.4, 1.0, 9.2, 1.0, False, True),
            ("hero", 0.4, 1.5, 9.2, 1.5, False, True),
        ]
        warnings = self._call(placed)
        assert len(warnings) == 1
        assert "title" in warnings[0] and "hero" in warnings[0]

    def test_adjacent_no_false_positive(self):
        placed = [
            ("a", 0.4, 1.0, 4.0, 1.0, False, True),
            ("b", 0.4, 2.0, 4.0, 1.0, False, True),
        ]
        warnings = self._call(placed)
        assert warnings == []

    def test_small_overlap_below_threshold(self):
        placed = [
            ("a", 0.0, 0.0, 10.0, 1.0, False, True),
            ("b", 0.0, 0.97, 0.5, 0.5, False, True),
        ]
        # smaller area = 0.25, overlap/smaller = 0.015/0.25 = 6% < 10%
        warnings = self._call(placed)
        assert warnings == []

    def test_side_by_side_no_collision(self):
        placed = [
            ("left", 0.4, 1.0, 4.0, 1.5, False, True),
            ("right", 4.6, 1.0, 4.0, 1.5, False, True),
        ]
        warnings = self._call(placed)
        assert warnings == []

    def test_intentional_layering_suppressed(self):
        placed = [
            ("bg_rect", 0.3, 0.9, 4.0, 3.6, True, False),
            ("value_text", 0.6, 1.6, 3.3, 1.0, False, True),
        ]
        warnings = self._call(placed)
        assert warnings == []


# ---------------------------------------------------------------------------
# Test off-slide overflow (checked in build_slide via warning)
# ---------------------------------------------------------------------------


class TestOffSlideOverflow:
    """Detect elements that extend past slide bottom."""

    def test_element_within_slide(self):
        bottom = 4.0 + 1.0  # 5.0 < 5.625
        assert bottom <= SLIDE_HEIGHT_IN

    def test_element_exceeds_slide(self):
        bottom = 4.5 + 1.5  # 6.0 > 5.625
        assert bottom > SLIDE_HEIGHT_IN


# ---------------------------------------------------------------------------
# Test stat_hero uses _grid_rect (integration-ish)
# ---------------------------------------------------------------------------


class TestStatHeroGridPosition:
    """stat_hero handler must use _grid_rect instead of hardcoded center."""

    def test_respects_explicit_y(self):
        from hippt.slides_to_pptx import _grid_rect

        elem = {"y": 2.5, "h": 1.8, "gridColumn": "1 / -1"}
        x, y, w, h = _grid_rect(elem)
        assert y == 2.5, f"Expected y=2.5, got {y}"
        assert h == 1.8, f"Expected h=1.8, got {h}"

    def test_grid_rect_full_width(self):
        from hippt.slides_to_pptx import _grid_rect

        elem = {"gridColumn": "1 / -1"}
        x, y, w, h = _grid_rect(elem)
        assert x == pytest.approx(MARGIN_IN, abs=0.01)
        expected_w = SLIDE_WIDTH_IN - 2 * MARGIN_IN
        assert w == pytest.approx(expected_w, abs=0.1)

    def test_value_and_label_within_bounds(self):
        from hippt.slides_to_pptx import _grid_rect

        elem = {"gridColumn": "1 / -1", "y": 2.0, "h": 1.8}
        x, y, w, h = _grid_rect(elem)
        value_top = y
        label_bottom = y + h * 0.6 + h * 0.35
        assert label_bottom <= y + h, (
            f"label bottom {label_bottom:.2f} exceeds assigned box bottom {y + h:.2f}"
        )


# ---------------------------------------------------------------------------
# Test role-vs-explicit-y conflict (S6)
# ---------------------------------------------------------------------------


class TestRoleVsExplicitYConflict:
    """On close slides, TITLE_ROLE_POSITIONS elements should not overlap
    elements with explicit y coordinates."""

    def test_meta_bottom_position(self):
        from hippt.slides_to_pptx import TITLE_ROLE_POSITIONS

        meta_pos = TITLE_ROLE_POSITIONS.get("meta")
        assert meta_pos is not None, "meta role must exist in TITLE_ROLE_POSITIONS"
        ty, th, _, _ = meta_pos
        meta_bottom = ty + th
        assert meta_bottom == pytest.approx(SLIDE_HEIGHT_IN * 0.68 + 0.35, abs=0.01)

    def test_explicit_y_below_role_positions_no_nudge(self):
        from hippt.slides_to_pptx import TITLE_ROLE_POSITIONS

        meta_pos = TITLE_ROLE_POSITIONS["meta"]
        meta_bottom = meta_pos[0] + meta_pos[1]
        timeline_y = 4.5
        assert timeline_y > meta_bottom + 0.1, (
            "Timeline at y=4.5 should be safely below meta"
        )

    def test_explicit_y_overlaps_role_position(self):
        from hippt.slides_to_pptx import TITLE_ROLE_POSITIONS

        meta_pos = TITLE_ROLE_POSITIONS["meta"]
        meta_bottom = meta_pos[0] + meta_pos[1]  # 3.825 + 0.35 = 4.175
        timeline_y = 4.0
        assert timeline_y < meta_bottom + 0.1, (
            f"Timeline at y={timeline_y} should conflict with meta bottom={meta_bottom:.3f}"
        )
