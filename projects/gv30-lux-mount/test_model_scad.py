"""Tests for the GV30 split ring: bounding box, volume window, the split and the arm."""

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
    assert x == pytest.approx(P["od"] + P["arm_l"], abs=0.1) and y == pytest.approx(P["od"], abs=0.1)
    assert z == pytest.approx(P["h"], abs=0.05)
    assert ring.is_watertight and 4000 < ring.volume < 7000
    assert not ray_hits(ring, [0, 0, -5], [0, 0, 1]), "bore clear over the stub"


def test_split_runs_down_the_arm(ring):
    for x in (P["id"] / 2 + 1, P["od"] / 2 + P["arm_l"] - 1):
        assert not ray_hits(ring, [x, 0, -5], [0, 0, 1]), f"split open at x = {x}"
    # arm is uniform: full width at both ends
    for x in (P["od"] / 2 + 1, P["od"] / 2 + P["arm_l"] - 1):
        assert ray_hits(ring, [x, P["arm_w"] / 2 - 0.5, -5], [0, 0, 1])
        assert not ray_hits(ring, [x, P["arm_w"] / 2 + 0.5, -5], [0, 0, 1])
