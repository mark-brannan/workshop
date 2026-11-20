"""``shop views``: six labelled renders of one model view, montaged into one PNG."""

import shutil
from pathlib import Path

import pytest
from shop.scad import find_openscad
from shop.views import VIEWS, render_views

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(find_openscad() is None or shutil.which("montage") is None, reason="needs openscad and montage")
def test_montage(tmp_path):
    out = render_views(ROOT / "projects/demo-bracket/model.scad", "any", tmp_path / "v.png")
    assert out.is_file() and out.stat().st_size > 10_000
    assert len(VIEWS) == 6
