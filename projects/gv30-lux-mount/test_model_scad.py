"""Tests for the GV30 split ring: bounding box, volume window, the split and the cord hole."""

import re
import tempfile
from pathlib import Path

import pytest
import trimesh
from shop.scad import OpenSCAD, find_openscad
from shop.testing import ray_hits

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")
P = {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*(-?[\d.]+)\s*;", (HERE / "model.scad").read_text(), re.M)}


@pytest.fixture(scope="module")
def ring():
    osc = OpenSCAD()
    with tempfile.TemporaryDirectory() as d:
        stl = Path(d) / "m.stl"
        osc.run(HERE / "model.scad", stl)
        mesh = trimesh.load(stl)
    osc.cleanup()
    return mesh


def test_ring(ring):
    x, y, z = ring.extents
    assert y == pytest.approx(P["od"], abs=0.1) and z == pytest.approx(P["h"], abs=0.05)
    assert ring.is_watertight and 1500 < ring.volume < 3000
    assert not ray_hits(ring, [0, 0, -5], [0, 0, 1]), "bore clear over the stub"


def test_split_and_cord_hole(ring):
    r = (P["od"] + P["id"]) / 4
    assert not ray_hits(ring, [r, 0, -5], [0, 0, 1]), "split runs through"
    # opposite the split, so a ray along X goes in through the hole and out through the split
    assert not ray_hits(ring, [-P["od"], 0, P["h"] / 2], [1, 0, 0]), "cord hole runs through the wall"
