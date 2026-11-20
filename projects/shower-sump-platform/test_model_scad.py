"""Tests for the shower-sump platform: bounding box, volume window, frame count, the V and the limber notch."""

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
W = P["sump_w"] + 2 * P["margin"]
L = P["sump_l"] + 2 * P["margin"]
RISE = (W / 2 - P["keel_w"] / 2) * math.tan(math.radians(P["deadrise_aft"])) + P["side"]


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
    assert installed.extents == pytest.approx([W, L, RISE + P["deck_t"]], abs=0.1)
    assert installed.is_watertight and 250_000 < installed.volume < 500_000


def test_frames_and_v(installed):
    up = [0, 0, 1]
    # a ray up the keel line, beside the notch, meets one frame per station
    x = P["limber_w"] / 2 + 2
    hits = ray_hits(installed, [x, -L, 1], [0, 1, 0])
    assert len(hits) == 2 * P["frames"]
    # under a frame, the bottom follows the deadrise
    y = -L / 2 + P["frame_t"] / 2
    for xo in (40, 70):
        z = ray_hits(installed, [xo, y, -10], up)[0][2]
        assert z == pytest.approx((xo - P["keel_w"] / 2) * math.tan(math.radians(P["deadrise_aft"])), abs=0.2)
    # the limber notch is open at the keel
    assert ray_hits(installed, [0, y, -10], up)[0][2] == pytest.approx(P["limber_h"], abs=0.05)
