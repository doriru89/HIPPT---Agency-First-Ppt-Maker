"""End-to-end smoke test: sidecar JSON -> PPTX via slides_to_pptx."""
from __future__ import annotations

import tempfile
from pathlib import Path

from hippt.slides_to_pptx import build_pptx


def test_minimal_deck():
    slides = {
        "metadata": {"title": "Test Deck", "author": "HIPPT", "date": "2026-05-02"},
        "slides": [
            {
                "type": "title",
                "title": "Test Presentation",
                "elements": [
                    {"type": "text", "content": "Smoke Test", "x": 0.5, "y": 2.5, "w": 9, "h": 0.8, "font_size": 28, "color": "475569"}
                ],
            },
            {
                "type": "content",
                "title": "This is an assertion slide",
                "elements": [
                    {"type": "text", "content": "With supporting evidence.", "x": 0.5, "y": 1.2, "w": 9, "h": 3, "font_size": 18, "color": "334155"}
                ],
            },
        ],
    }
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "test.pptx"
        result = build_pptx(slides, None, str(out_path))
        result_path = Path(result)
        assert result_path.exists(), f"PPTX not created at {result}"
        assert result_path.stat().st_size > 5000, "PPTX too small — likely empty"
