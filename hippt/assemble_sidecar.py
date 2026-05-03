#!/usr/bin/env python3
"""Assemble per-slide JSONs into a combined sidecar for slides_to_pptx.py.

Usage:
    hippt-assemble output/html/<slug>/
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: assemble_sidecar.py <slide_dir>", file=sys.stderr)
        return 1

    slide_dir = Path(sys.argv[1]).resolve()
    if not slide_dir.is_dir():
        print(f"Error: {slide_dir} is not a directory", file=sys.stderr)
        return 1

    tokens_path = slide_dir / "design-tokens.json"
    tokens = json.loads(tokens_path.read_text()) if tokens_path.exists() else {}

    per_slide = sorted(slide_dir.glob("s*.json"))
    if not per_slide:
        print(f"Error: no s*.json files found in {slide_dir}", file=sys.stderr)
        return 1

    slides = []
    for f in per_slide:
        slide = json.loads(f.read_text())
        if "elements" not in slide or not isinstance(slide.get("elements"), list):
            print(f"Error: {f.name} missing or invalid elements array", file=sys.stderr)
            return 1
        if "slide_index" not in slide:
            print(f"Warning: {f.name} missing slide_index", file=sys.stderr)
        slides.append(slide)

    slug = slide_dir.name
    combined = {
        "metadata": {
            "title": slug.replace("-", " ").title(),
            "author": "Austin Wang",
            "date": str(date.today()),
            "source_dir": str(slide_dir),
            "slide_count": len(slides),
        },
        "design_tokens": tokens,
        "slides": slides,
    }

    out = slide_dir.parent / f"{slug}-slides.json"
    out.write_text(json.dumps(combined, indent=2))
    print(f"Assembled {len(slides)} slides -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
