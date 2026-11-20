"""Tests for the shower-sump platform: bounding box, volume window, the open underside and the skirt angle."""

import math
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
A = math.radians(P["hull_angle"])
HW = max(P["w_aft"], P["w_fwd"]) / 2 - P["bond_gap"] / math.sin(A)
HW0 = (P["w_aft"] + P["w_fwd"]) / 4 - P["bond_gap"] / math.sin(A)  # at y = 0


@pytest.fixture(scope="module")
def installed():
    osc = OpenSCAD()
    with tempfile.TemporaryDirectory() as d:
        stl = Path(d) / "m.stl"
        osc.run(HERE / "model.scad", stl, "-D", 'part="installed"')
        mesh = trimesh.load(stl)
    osc.cleanup()
    return mesh


def test_bbox_and_volume(installed):
    assert installed.extents == pytest.approx([2 * HW, P["len"], P["skirt_h"]], abs=0.1)
    assert installed.is_watertight and 100_000 < installed.volume < 250_000


def test_open_underside_and_skirt(installed):
    up = [0, 0, 1]
    # under the middle, the first thing met is the deck's underside
    assert ray_hits(installed, [0, 0, -50], up)[0][2] == pytest.approx(-P["deck_t"], abs=0.05)
    # the skirt (both V's: plan taper and hull angle)'s outer face leans in at the hull angle: halfway down it sits run/2 inside the top edge
    z = -P["skirt_h"] / 2
    x = ray_hits(installed, [HW + 20, 0, z], [-1, 0, 0])[0][0]
    assert x == pytest.approx(HW0 + z / math.tan(A), abs=0.1)
