"""Shared fixtures for HIPPT tests."""
from pathlib import Path

import pytest


@pytest.fixture
def output_dir(tmp_path):
    """Provide a temporary output directory tree."""
    for d in ["pptx", "html", "design", "debug", "layouts", "research"]:
        (tmp_path / d).mkdir()
    return tmp_path


@pytest.fixture
def fixtures_dir():
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"
