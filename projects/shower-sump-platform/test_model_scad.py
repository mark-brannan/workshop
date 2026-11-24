"""Tests for the shower-sump platform: bounding box, volume window, the open underside and the skirt angle."""

import math
import re
import tempfile
from pathlib import Path

import pytest
import trimesh
from shop.scad import OpenSCAD, find_openscad
from shop.testing import ray_hits

import sys

sys.path.insert(0, str(Path(__file__).parent))
from wing_overlay import wing  # noqa: E402

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")
P = {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*(-?[\d.]+)\s*;", (HERE / "model.scad").read_text(), re.M)}
A = math.radians(P["hull_angle"])
HW = max(P["w_aft"], P["w_fwd"]) / 2 - P["bond_gap"] / math.sin(A)
HW0 = (P["w_aft"] + P["w_fwd"]) / 4 - P["bond_gap"] / math.sin(A) + 15 * (P["w_aft"] - P["w_fwd"]) / 2 / P["len"]  # at y = -15, clear of the bosses


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
    assert installed.is_watertight and 30_000 < installed.volume < 150_000


def test_open_underside_and_skirt(installed):
    up = [0, 0, 1]
    # under the deck beside the opening, the first thing met is the deck's underside
    assert ray_hits(installed, [0, -37, -50], up)[0][2] == pytest.approx(-P["deck_t"], abs=0.05)
    # the skirt (both V's: plan taper and hull angle)'s outer face leans in at the hull angle: halfway down it sits run/2 inside the top edge
    z = -P["skirt_h"] / P["fin_n"]  # between the first two ridges
    x = ray_hits(installed, [HW + 20, -15, z], [-1, 0, 0])[0][0]
    assert x == pytest.approx(HW0 + z / math.tan(A), abs=0.1)


def test_screw_holes_and_opening(installed):
    down = [0, 0, -1]
    for x, y in [(93, 25), (93, -34), (100, 0), (-93, 25), (-93, -34), (-100, 0)]:
        assert all(h[2] < -P["boss_h"] for h in ray_hits(installed, [x, y, 5], down)), f"pilot blocked at {x}, {y}"
        assert ray_hits(installed, [x + P["hole_d"] / 2 + 1, y, 5], down)[0][2] == pytest.approx(0, abs=0.05)
    assert not ray_hits(installed, [0, 0, 5], down), "opening in the middle"


def test_cable_tie_slits_clear_wing_and_skirt(installed):
    down = [0, 0, -1]
    ys = [float(v) for v in re.search(r"^tie_slit_y\s*=\s*\[([^\]]*)\]", (HERE / "model.scad").read_text(), re.M).group(1).split(",")]
    x0, t, w = P["tie_slit_x"], P["tie_slit_t"], P["tie_slit_w"]
    wing_pts = wing()
    for side in (1, -1):
        for y in ys:
            xm = side * (x0 + t / 2)
            # open through the deck; the skirt below, leaning in, is not the tie's path (it turns inboard under the deck)
            for dy in (0, -w / 2 + 0.3, w / 2 - 0.3):  # the slit is the full width along y
                assert ray_hits(installed, [xm, y + dy, 5], down)[0][2] < -P["deck_t"], f"slit not through the deck at {side}, {y + dy}"
            assert ray_hits(installed, [side * (x0 - 1), y, 5], down)[0][2] == pytest.approx(0, abs=0.05)  # deck beside it
            assert ray_hits(installed, [xm, y + w / 2 + 0.5, 5], down)[0][2] == pytest.approx(0, abs=0.05)
            # the skirt's inner face, at the deck underside, stays outboard of the slit
            hit = ray_hits(installed, [side * (x0 - 1), y + 0.13, -P["deck_t"] - 0.2], [side, 0, 0])
            assert hit and abs(hit[0][0]) > x0 + t, f"skirt meets the slit's under-deck exit at {side}, {y}"
            # outside the traced wing, with the wing's own edge near the slit run
            edge = max(x for x, py in wing_pts if abs(py - y) <= w / 2 + 1)
            assert edge < x0, f"wing edge {edge} reaches the slit at y={y}"


def test_rivet_holes_through_skirts(installed):
    a, pitch, reach = A, P["rivet_pitch"], P["rivet_reach"]
    n = [math.sin(a), 0, -math.cos(a)]  # out of the right skirt's face
    grid = [(6.5, -reach + i * pitch) for i in range(int(2 * reach / pitch) + 1)]
    grid += [(14, -reach + pitch / 2 + i * pitch) for i in range(int(2 * reach / pitch))]
    clear = [(sl, y) for sl, y in grid if all(abs(y - b) > 7 for b in (-34, 0, 25))]  # holes the bosses don't stop
    assert len(clear) >= 8
    for side in (1, -1):
        for sl, y in clear:
            hw = P["w_aft"] / 2 + (P["w_fwd"] - P["w_aft"]) / 2 * (y / P["len"] + 0.5) - P["bond_gap"] / math.sin(a)
            q = [side * (hw - sl * math.cos(a)), y, -sl * math.sin(a)]
            start = [q[0] + side * 5 * n[0], y, q[2] + 5 * n[2]]
            ray = [-side * n[0], 0, -n[2]]
            first = ray_hits(installed, start, ray)
            assert not first or math.dist(first[0], start) > 5 + P["skirt_t"] + 1, f"no hole at {side}, {y}"
            start_b = [start[0], y + 4, start[2]]
            beside = ray_hits(installed, start_b, ray)
            assert beside and math.dist(beside[0], start_b) < 6, f"skirt missing beside the hole at {side}, {y}"
