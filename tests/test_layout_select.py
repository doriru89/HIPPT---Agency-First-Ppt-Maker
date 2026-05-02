"""Tests for layout_select.py — Phase 7 layout selection intelligence.

TDD: these tests are written first, implementation follows.
"""

import copy

import yaml


# ── Fixtures ─────────────────────────────────────────────────────────────


def _make_layout(
    code="L-DATA-001",
    slide_type="data",
    density="medium",
    background="light",
    tags=None,
    supports=None,
    regions=None,
    source="test",
):
    return {
        "code": code,
        "slide_type": slide_type,
        "density": density,
        "background": background,
        "tags": tags or [],
        "supports": supports or [],
        "regions": regions or [],
        "max_regions": len(regions) if regions else 0,
        "source": source,
        "origin": "html",
        "context": "",
        "anti_patterns": "",
    }


def _make_region(role="body_text", element_type="text", x=5, y=5, w=90, h=20):
    return {
        "role": role,
        "element_type": element_type,
        "box": {"x": f"{x}%", "y": f"{y}%", "w": f"{w}%", "h": f"{h}%"},
    }


def _make_element(
    etype="text", selector="div.body", text="Hello", bbox=None, style=None
):
    return {
        "type": etype,
        "selector": selector,
        "text": text,
        "bbox": bbox or {"x": 48, "y": 27, "w": 864, "h": 108},
        "style": style or {"fontSize": "16px", "fontWeight": "400"},
        "render": "native",
    }


def _make_slide_data(elements=None, background="rgb(255,255,255)", slide_type=None):
    slide = {
        "background": background,
        "backgroundImage": None,
        "elements": elements or [],
    }
    if slide_type:
        slide["slideType"] = slide_type
    return {"viewport": {"w": 960, "h": 540}, "slide": slide}


# ── Step 2: Library loader ───────────────────────────────────────────────


class TestLoadLayoutLibrary:
    def test_loads_from_directory(self, tmp_path):
        from hippt.layout_select import load_layout_library

        layout = _make_layout(code="L-TEST-001")
        (tmp_path / "L-TEST-001.yaml").write_text(yaml.dump(layout))
        result = load_layout_library(tmp_path)
        assert len(result) == 1
        assert result[0]["code"] == "L-TEST-001"

    def test_skips_index_yaml(self, tmp_path):
        from hippt.layout_select import load_layout_library

        layout = _make_layout()
        (tmp_path / "L-DATA-001.yaml").write_text(yaml.dump(layout))
        (tmp_path / "index.yaml").write_text(yaml.dump({"layouts": []}))
        result = load_layout_library(tmp_path)
        assert len(result) == 1

    def test_loads_subdirectories(self, tmp_path):
        from hippt.layout_select import load_layout_library

        sub = tmp_path / "agency"
        sub.mkdir()
        (tmp_path / "L-ROOT.yaml").write_text(yaml.dump(_make_layout(code="L-ROOT")))
        (sub / "L-SUB.yaml").write_text(
            yaml.dump(_make_layout(code="L-SUB", source="agency"))
        )
        result = load_layout_library(tmp_path)
        assert len(result) == 2

    def test_bad_yaml_skipped(self, tmp_path):
        from hippt.layout_select import load_layout_library

        (tmp_path / "good.yaml").write_text(yaml.dump(_make_layout()))
        (tmp_path / "bad.yaml").write_text("{{invalid yaml::")
        result = load_layout_library(tmp_path)
        assert len(result) == 1


# ── Step 3: Slide profiling ─────────────────────────────────────────────


class TestInferSlideProfile:
    def test_data_slide_from_stat_selectors(self):
        from hippt.layout_select import infer_slide_profile

        elems = [
            _make_element(selector="div.stat-val", text="$42M"),
            _make_element(selector="div.stat-val", text="87%"),
            _make_element(
                selector="h2.headline",
                text="Revenue",
                style={"fontSize": "28px", "fontWeight": "700"},
            ),
        ]
        sd = _make_slide_data(elems)
        profile = infer_slide_profile(sd["slide"], index=2, total_slides=10)
        assert profile.slide_type == "data"

    def test_title_slide_from_position(self):
        from hippt.layout_select import infer_slide_profile

        elems = [
            _make_element(
                selector="h1.headline",
                text="Welcome",
                style={"fontSize": "36px", "fontWeight": "700"},
            ),
        ]
        sd = _make_slide_data(elems)
        profile = infer_slide_profile(sd["slide"], index=0, total_slides=10)
        assert profile.slide_type == "title"

    def test_density_thresholds(self):
        from hippt.layout_select import infer_slide_profile

        low = _make_slide_data([_make_element() for _ in range(2)])
        med = _make_slide_data([_make_element() for _ in range(5)])
        high = _make_slide_data([_make_element() for _ in range(8)])
        assert infer_slide_profile(low["slide"], 1, 10).density == "low"
        assert infer_slide_profile(med["slide"], 1, 10).density == "medium"
        assert infer_slide_profile(high["slide"], 1, 10).density == "high"

    def test_background_dark(self):
        from hippt.layout_select import infer_slide_profile

        sd = _make_slide_data([_make_element()], background="rgb(10, 20, 30)")
        profile = infer_slide_profile(sd["slide"], 1, 10)
        assert profile.background == "dark"

    def test_background_transparent_defaults_light(self):
        from hippt.layout_select import infer_slide_profile

        sd = _make_slide_data([_make_element()], background="rgba(0, 0, 0, 0)")
        profile = infer_slide_profile(sd["slide"], 1, 10)
        assert profile.background == "light"

    def test_explicit_slide_type_attr(self):
        from hippt.layout_select import infer_slide_profile

        sd = _make_slide_data([_make_element()], slide_type="comparison")
        profile = infer_slide_profile(sd["slide"], 1, 10)
        assert profile.slide_type == "comparison"


# ── Steps 4-5: Scoring + selection ───────────────────────────────────────


class TestScoring:
    def test_type_filter_rejects_mismatch(self):
        from hippt.layout_select import select_layout, infer_slide_profile

        library = [_make_layout(slide_type="editorial")]
        sd = _make_slide_data(
            [_make_element(selector="div.stat-val", text="$42M")] * 3,
        )
        profile = infer_slide_profile(sd["slide"], 2, 10)
        assert profile.slide_type == "data"
        result = select_layout(profile, library)
        assert result is None

    def test_density_background_scoring(self):
        from hippt.layout_select import select_layout, infer_slide_profile

        exact = _make_layout(
            code="EXACT", density="medium", background="dark", regions=[_make_region()]
        )
        wrong = _make_layout(
            code="WRONG", density="low", background="light", regions=[_make_region()]
        )
        library = [exact, wrong]
        sd = _make_slide_data([_make_element()], background="rgb(10, 10, 10)")
        profile = infer_slide_profile(sd["slide"], 1, 10)
        # Force type to match
        profile.slide_type = "data"
        for l in library:
            l["slide_type"] = "data"
        result = select_layout(profile, library)
        assert result is not None
        assert result.layout["code"] == "EXACT"

    def test_tag_jaccard(self):
        from hippt.layout_select import select_layout, SlideProfile
        from collections import Counter

        good = _make_layout(
            code="GOOD",
            tags=["stat-cards", "three-column"],
            regions=[_make_region("stat_value")],
        )
        bad = _make_layout(
            code="BAD", tags=["timeline"], regions=[_make_region("timeline_bar")]
        )
        profile = SlideProfile(
            slide_type="data",
            density="medium",
            background="light",
            roles=Counter({"stat_value": 2}),
            element_types={"text"},
            element_count=2,
            tags=["stat-cards", "three-column"],
            supports=["text-heading"],
        )
        result = select_layout(profile, [good, bad])
        assert result is not None
        assert result.layout["code"] == "GOOD"

    def test_role_overlap_scoring(self):
        from hippt.layout_select import select_layout, SlideProfile
        from collections import Counter

        matching = _make_layout(
            code="MATCH",
            regions=[
                _make_region("headline"),
                _make_region("stat_value"),
                _make_region("stat_value"),
            ],
        )
        mismatched = _make_layout(
            code="MISS",
            regions=[
                _make_region("evidence_image", "image"),
                _make_region("evidence_image", "image"),
            ],
        )
        profile = SlideProfile(
            slide_type="data",
            density="medium",
            background="light",
            roles=Counter({"headline": 1, "stat_value": 2}),
            element_types={"text"},
            element_count=3,
            tags=[],
            supports=[],
        )
        result = select_layout(profile, [matching, mismatched])
        assert result is not None
        assert result.layout["code"] == "MATCH"

    def test_element_count_fit(self):
        from hippt.layout_select import select_layout, SlideProfile
        from collections import Counter

        close = _make_layout(code="CLOSE", regions=[_make_region()] * 3)
        far = _make_layout(code="FAR", regions=[_make_region()] * 10)
        profile = SlideProfile(
            slide_type="data",
            density="medium",
            background="light",
            roles=Counter({"body_text": 3}),
            element_types={"text"},
            element_count=3,
            tags=[],
            supports=[],
        )
        result = select_layout(profile, [close, far])
        assert result is not None
        assert result.layout["code"] == "CLOSE"

    def test_combined_scoring(self):
        from hippt.layout_select import select_layout, SlideProfile
        from collections import Counter

        layout = _make_layout(
            code="ONLY",
            density="medium",
            background="light",
            tags=["stat-cards"],
            regions=[_make_region("headline"), _make_region("stat_value")],
        )
        profile = SlideProfile(
            slide_type="data",
            density="medium",
            background="light",
            roles=Counter({"headline": 1, "stat_value": 1}),
            element_types={"text"},
            element_count=2,
            tags=["stat-cards"],
            supports=[],
        )
        result = select_layout(profile, [layout])
        assert result is not None
        assert result.score > 0

    def test_threshold_returns_none(self):
        from hippt.layout_select import select_layout, SlideProfile
        from collections import Counter

        layout = _make_layout(
            code="BAD",
            density="high",
            background="dark",
            regions=[_make_region("evidence_image", "image")] * 8,
        )
        profile = SlideProfile(
            slide_type="data",
            density="low",
            background="light",
            roles=Counter({"headline": 1}),
            element_types={"text"},
            element_count=1,
            tags=[],
            supports=[],
        )
        result = select_layout(profile, [layout])
        assert result is None


# ── Step 6: Matching + remapping ─────────────────────────────────────────


class TestMatchAndRemap:
    def test_many_to_many_by_position(self):
        from hippt.layout_select import match_elements_to_regions

        elems = [
            _make_element(
                selector="div.stat-val", bbox={"x": 50, "y": 200, "w": 100, "h": 50}
            ),
            _make_element(
                selector="div.stat-val", bbox={"x": 200, "y": 200, "w": 100, "h": 50}
            ),
            _make_element(
                selector="div.stat-val", bbox={"x": 350, "y": 200, "w": 100, "h": 50}
            ),
        ]
        regions = [
            _make_region("stat_value", x=5, y=35, w=17, h=34),
            _make_region("stat_value", x=30, y=35, w=17, h=34),
            _make_region("stat_value", x=55, y=35, w=17, h=34),
        ]
        matched, unmatched = match_elements_to_regions(elems, regions)
        assert len(matched) == 3
        assert len(unmatched) == 0
        # First element (leftmost) should match first region (leftmost)
        assert matched[0][1]["box"]["x"] == "5%"
        assert matched[1][1]["box"]["x"] == "30%"
        assert matched[2][1]["box"]["x"] == "55%"

    def test_role_compat_fallback(self):
        from hippt.layout_select import match_elements_to_regions

        elems = [
            _make_element(
                selector="h3.section-heading",
                text="Details",
                style={"fontSize": "16px", "fontWeight": "700"},
            ),
        ]
        regions = [_make_region("headline", x=5, y=5, w=90, h=15)]
        matched, unmatched = match_elements_to_regions(elems, regions)
        assert len(matched) == 1
        assert len(unmatched) == 0

    def test_remap_positions(self):
        from hippt.layout_select import remap_elements, LayoutMatch

        elem = _make_element(bbox={"x": 48, "y": 27, "w": 864, "h": 108})
        region = _make_region("body_text", x=10, y=20, w=80, h=30)
        sd = _make_slide_data([elem])
        match = LayoutMatch(
            layout=_make_layout(),
            score=0.8,
            layer1_score=0.5,
            layer2_score=0.9,
            matched_regions=[(elem, region)],
            unmatched_elements=[],
        )
        remap_elements(sd, match, sd["viewport"])
        bbox = sd["slide"]["elements"][0]["bbox"]
        assert abs(bbox["x"] - 96.0) < 1  # 10% of 960
        assert abs(bbox["y"] - 108.0) < 1  # 20% of 540
        assert abs(bbox["w"] - 768.0) < 1  # 80% of 960
        assert abs(bbox["h"] - 162.0) < 1  # 30% of 540

    def test_remap_preserves_unmatched(self):
        from hippt.layout_select import remap_elements, LayoutMatch

        elem = _make_element(bbox={"x": 100, "y": 100, "w": 200, "h": 50})
        sd = _make_slide_data([elem])
        original_bbox = copy.deepcopy(elem["bbox"])
        match = LayoutMatch(
            layout=_make_layout(),
            score=0.8,
            layer1_score=0.5,
            layer2_score=0.9,
            matched_regions=[],
            unmatched_elements=[elem],
        )
        remap_elements(sd, match, sd["viewport"])
        assert sd["slide"]["elements"][0]["bbox"] == original_bbox

    def test_deepcopy_on_exception(self):
        from hippt.layout_select import remap_elements, LayoutMatch

        elem = _make_element(bbox={"x": 100, "y": 100, "w": 200, "h": 50})
        bad_region = {"role": "body_text", "element_type": "text", "box": {}}
        sd = _make_slide_data([elem])
        original_bbox = copy.deepcopy(sd["slide"]["elements"][0]["bbox"])
        match = LayoutMatch(
            layout=_make_layout(),
            score=0.8,
            layer1_score=0.5,
            layer2_score=0.9,
            matched_regions=[(elem, bad_region)],
            unmatched_elements=[],
        )
        remap_elements(sd, match, sd["viewport"])
        assert sd["slide"]["elements"][0]["bbox"] == original_bbox

    def test_image_aspect_ratio(self):
        from hippt.layout_select import remap_elements, LayoutMatch

        elem = _make_element(
            etype="image",
            selector="img",
            bbox={"x": 0, "y": 0, "w": 400, "h": 200},  # 2:1 aspect
        )
        region = _make_region("evidence_image", "image", x=10, y=10, w=50, h=50)
        sd = _make_slide_data([elem])
        match = LayoutMatch(
            layout=_make_layout(),
            score=0.8,
            layer1_score=0.5,
            layer2_score=0.9,
            matched_regions=[(elem, region)],
            unmatched_elements=[],
        )
        remap_elements(sd, match, sd["viewport"])
        bbox = sd["slide"]["elements"][0]["bbox"]
        # Region is 480x270 (50%x50% of 960x540). Image 2:1 should fit as 480x240.
        assert abs(bbox["w"] - 480) < 1
        assert bbox["h"] < 270  # height constrained by aspect ratio


# ── Phase 8: Shape vector search ───────────────────────────────────────


class TestShapeVector:
    def test_basic_vector_length(self):
        from hippt.layout_select import shape_vector

        regions = [
            _make_region("headline", x=5, y=5, w=90, h=10),
            _make_region("body_text", x=5, y=20, w=90, h=70),
        ]
        vec = shape_vector(regions, max_slots=16)
        assert len(vec) == 65  # 16*4 + 1
        # First 8 floats should be nonzero (2 regions x 4 coords)
        assert all(v > 0 for v in vec[:8])
        # Remaining slots zero-padded
        assert all(v == 0.0 for v in vec[8:64])
        # Density = 2/16
        assert abs(vec[64] - 2 / 16) < 1e-9

    def test_canonical_order_invariant(self):
        from hippt.layout_select import shape_vector

        r_top = _make_region("headline", x=5, y=5, w=90, h=10)
        r_bottom = _make_region("body_text", x=5, y=50, w=90, h=40)
        vec_a = shape_vector([r_top, r_bottom])
        vec_b = shape_vector([r_bottom, r_top])
        assert vec_a == vec_b

    def test_filters_structural_roles(self):
        from hippt.layout_select import shape_vector

        regions = [
            _make_region("headline", x=5, y=5, w=90, h=10),
            _make_region("progress_bar", x=0, y=95, w=100, h=5),
            _make_region("footer", x=0, y=90, w=100, h=5),
        ]
        vec = shape_vector(regions)
        # Only headline should contribute (1 content region)
        assert abs(vec[64] - 1 / 16) < 1e-9

    def test_zero_pad_empty(self):
        from hippt.layout_select import shape_vector

        vec = shape_vector([])
        assert len(vec) == 65
        assert all(v == 0.0 for v in vec)

    def test_truncates_beyond_max_slots(self):
        from hippt.layout_select import shape_vector

        regions = [
            _make_region("body_text", x=i * 5, y=i * 5, w=4, h=4) for i in range(18)
        ]
        vec = shape_vector(regions, max_slots=16)
        assert len(vec) == 65
        # Density records actual content count, not truncated count
        assert abs(vec[64] - 18 / 16) < 1e-9

    def test_max_slots_zero_safe(self):
        from hippt.layout_select import shape_vector

        vec = shape_vector([_make_region("headline")], max_slots=0)
        assert len(vec) == 5  # max(0,1)*4+1

    def test_viewport_normalization(self):
        from hippt.layout_select import _parse_box_to_floats

        box_px = {"x": 480, "y": 270, "w": 96, "h": 54}
        viewport = {"w": 960, "h": 540}
        x, y, w, h = _parse_box_to_floats(box_px, viewport)
        assert abs(x - 0.5) < 1e-9
        assert abs(y - 0.5) < 1e-9
        assert abs(w - 0.1) < 1e-9
        assert abs(h - 0.1) < 1e-9

    def test_percent_string_parsing(self):
        from hippt.layout_select import _parse_box_to_floats

        box_pct = {"x": "10%", "y": "20.5%", "w": "80%", "h": "60%"}
        x, y, w, h = _parse_box_to_floats(box_pct)
        assert abs(x - 0.10) < 1e-9
        assert abs(y - 0.205) < 1e-9


class TestCosineAndShapeScoring:
    def test_identical_vectors_score_1(self):
        from hippt.layout_select import _cosine_sim

        vec = [0.05, 0.05, 0.9, 0.1, 0.05, 0.5, 0.9, 0.4, 0.125]
        assert abs(_cosine_sim(vec, vec) - 1.0) < 1e-9

    def test_zero_vectors_score_0(self):
        from hippt.layout_select import _cosine_sim

        assert _cosine_sim([0, 0, 0], [0, 0, 0]) == 0.0

    def test_backward_compat_shape_weight_zero(self):
        """With shape_weight=0.0, scores are bit-identical to the pre-Phase-8 formula."""
        from hippt.layout_select import (
            select_layout,
            SlideProfile,
            _score_layer1,
            _score_layer2,
            _get_selection_config,
        )
        from collections import Counter

        layout_a = _make_layout(
            code="A",
            density="medium",
            background="light",
            tags=["stat-cards"],
            regions=[_make_region("headline"), _make_region("stat_value")],
        )
        profile = SlideProfile(
            slide_type="data",
            density="medium",
            background="light",
            roles=Counter({"headline": 1, "stat_value": 1}),
            element_types={"text"},
            element_count=2,
            tags=["stat-cards"],
            supports=[],
        )
        cfg = {
            "selection": {
                "layer1": {},
                "layer2": {},
                "blend_ratio": 0.6,
                "min_score_threshold": 0.1,
                "top_k_layer1": 8,
                "shape": {
                    "shape_weight": 0.0,
                    "max_content_slots": 16,
                    "min_content_regions": 2,
                },
            },
            "role_compatibility": {},
        }
        sel_cfg = _get_selection_config(cfg)
        l1 = _score_layer1(layout_a, profile, sel_cfg)
        l2 = _score_layer2(layout_a, profile, sel_cfg)
        expected = (1 - 0.6) * (l1 / 5.0) + 0.6 * (l2 / 5.0)

        result = select_layout(profile, [layout_a], cfg=cfg)
        assert result is not None
        assert abs(result.score - expected) < 1e-12
        assert result.shape_score == 0.0

    def test_dimension_mismatch_returns_zero(self):
        """Mismatched vector dimensions return 0.0, not silent truncation."""
        from hippt.layout_select import _score_shape, SlideProfile, shape_vector

        layout = _make_layout(
            regions=[_make_region("headline"), _make_region("body_text")]
        )
        layout["_shape_vec"] = shape_vector(layout["regions"], max_slots=16)
        profile = SlideProfile(
            slide_type="data",
            density="medium",
            background="light",
            shape_vec=shape_vector([_make_region("headline")], max_slots=8),
        )
        sel_cfg = {"shape": {"min_content_regions": 1, "max_content_slots": 16}}
        assert _score_shape(layout, profile, sel_cfg) == 0.0

    def test_single_region_below_min_gate(self):
        """Single content region gated by min_content_regions=2."""
        from hippt.layout_select import _score_shape, SlideProfile, shape_vector

        layout = _make_layout(regions=[_make_region("headline")])
        layout["_shape_vec"] = shape_vector(layout["regions"])
        profile = SlideProfile(
            slide_type="data",
            density="low",
            background="light",
            shape_vec=shape_vector([_make_region("headline")]),
        )
        sel_cfg = {"shape": {"min_content_regions": 2, "max_content_slots": 16}}
        assert _score_shape(layout, profile, sel_cfg) == 0.0

    def test_shape_improves_spatial_match(self):
        """Shape-similar layout ranks higher when shape_weight > 0."""
        from hippt.layout_select import (
            select_layout,
            SlideProfile,
            shape_vector,
        )
        from collections import Counter

        # Two layouts: same type/density/background, same roles, but different spatial shape
        spatial_match = _make_layout(
            code="SPATIAL",
            regions=[
                _make_region("headline", x=5, y=5, w=90, h=10),
                _make_region("body_text", x=5, y=20, w=90, h=70),
            ],
        )
        spatial_diff = _make_layout(
            code="DIFF",
            regions=[
                _make_region("headline", x=50, y=50, w=40, h=10),
                _make_region("body_text", x=50, y=65, w=40, h=30),
            ],
        )
        # Precompute shape vectors (normally done by load_layout_library)
        spatial_match["_shape_vec"] = shape_vector(spatial_match["regions"])
        spatial_diff["_shape_vec"] = shape_vector(spatial_diff["regions"])

        # Profile matching the spatial_match layout's shape
        profile = SlideProfile(
            slide_type="data",
            density="medium",
            background="light",
            roles=Counter({"headline": 1, "body_text": 1}),
            element_types={"text"},
            element_count=2,
            tags=[],
            supports=[],
            shape_vec=shape_vector(
                [
                    _make_region("headline", x=5, y=5, w=90, h=10),
                    _make_region("body_text", x=5, y=20, w=90, h=70),
                ],
            ),
        )
        cfg = {
            "selection": {
                "layer1": {},
                "layer2": {},
                "blend_ratio": 0.6,
                "min_score_threshold": 0.1,
                "top_k_layer1": 8,
                "shape": {
                    "max_content_slots": 16,
                    "shape_weight": 0.5,
                    "min_content_regions": 1,
                },
            },
            "role_compatibility": {},
        }
        result = select_layout(profile, [spatial_match, spatial_diff], cfg=cfg)
        assert result is not None
        assert result.layout["code"] == "SPATIAL"
        assert result.shape_score > 0.5
