# HIPPT — Agency-First Presentation Maker

# Run all tests (skip integration tests that need reference PPTX)
test:
    uv run pytest tests/ -v -k "not integration"

# Run all tests including integration
test-all:
    uv run pytest tests/ -v

# Draft PPTX from sidecar JSON
draft slides_json tokens_yaml="":
    uv run hippt-draft {{slides_json}} {{if tokens_yaml != "" { "--tokens " + tokens_yaml } else { "" }}}

# Export HTML to PPTX via Playwright DOM extraction
export html_path *args="":
    uv run hippt-export {{html_path}} {{args}}

# Analyze a PPTX file (fill %, fonts, colors)
analyze pptx_path:
    uv run hippt-analyze {{pptx_path}}

# Extract design tokens from a reference PPTX
tokens pptx_path slug:
    uv run hippt-tokens {{pptx_path}} --slug {{slug}}

# Extract layouts from a reference PPTX
layouts pptx_path slug:
    uv run hippt-layouts {{pptx_path}} --out output/layouts/{{slug}}/ --verify

# Generate review cockpit HTML
cockpit tokens_yaml slides_json *args="":
    uv run hippt-cockpit --tokens {{tokens_yaml}} --slides {{slides_json}} {{args}}

# Install Playwright + Chromium (one-time setup for DOM engine)
setup-playwright:
    uv sync --extra export
    uv run playwright install chromium

# Lint
lint:
    uv run ruff check hippt/ tests/

# Quick smoke test: generate a PPTX from the example
smoke:
    uv run hippt-draft examples/sample-slides.json
    @echo "Check output/pptx/ for the generated PPTX"
