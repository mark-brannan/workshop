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


def test_pilot_takes_a_nylon_m4_tap():
    """Printed Ø3 is drilled to 3.3 and tapped M4 (README, 2026-11-24): the pilot must be under 3.3, the boss wall after drilling at least 2.8."""
    assert P["hole_d"] < 3.3
    assert (P["boss_d"] - 3.3) / 2 >= 2.8


def test_tie_slits_and_fairlead_funnels(installed):
    """Each end arch has a round-ended 12 mm slit, no V, tilted tie_tilt with its outboard end low; above it a fairlead
    funnel a tie_lead deep runs up the tie's slant to the deck top; the slit's outer mouth is rounded."""
    tilt = math.radians(P["tie_tilt"])
    lean = math.atan2(P["tie_top_x"] - P["tie_x"], P["tie_top_z"] - P["tie_zc"])
    half, ends, L = P["tie_slit_l"] / 2, P["tie_slit_w"] / 2, P["len"] / 2
    assert P["tie_slit_l"] == 12
    for s in (1, -1):
        def slit(a, b, f=1):  # a along the slit, b across it (up), from outside the end face f
            return [s * (P["tie_x"] + a * math.cos(tilt) - b * math.sin(tilt)), f * 60, P["tie_zc"] - a * math.sin(tilt) + b * math.cos(tilt)]
        for a in (0, -half + ends, half - ends):
            assert not ray_hits(installed, slit(a, 0), [0, -1, 0]), f"tie run blocked at {s}, {a}"
        assert ray_hits(installed, slit(half + 1, 0), [0, -1, 0]), "arch beyond the slit's end"
        assert ray_hits(installed, slit(0, -ends - P["tie_lead"] - 0.5), [0, -1, 0]), "arch below the slit"
        for f in (1, -1):
            mouth = ray_hits(installed, slit(0, ends + 0.6, f), [0, -f, 0])
            assert mouth and abs(mouth[0][1]) < L - P["tie_lead"] - 0.1, "rounded slit mouth"
            for x in range(88, 101, 2):  # the deck top under the tab is whole out to its end
                assert ray_hits(installed, [s * x, f * (L - 0.2), 5], [0, 0, -1])[0][2] == pytest.approx(0, abs=0.05), f"deck top at {s * x}, {f}"
            for z in (-3.5, -5):  # the funnel floor along the tie's slant
                x = P["tie_x"] + (z - P["tie_zc"]) * math.tan(lean)
                hit = ray_hits(installed, [s * x, f * 60, z], [0, -f, 0])
                assert abs(hit[0][1]) == pytest.approx(L - P["tie_lead"], abs=0.05), f"funnel floor at {s}, {f}, {z}"
            beside = ray_hits(installed, [s * (P["tie_x"] - half - 4), f * 60, P["tie_zc"]], [0, -f, 0])
            assert abs(beside[0][1]) == pytest.approx(L, abs=0.05), "end face beside the funnel"
