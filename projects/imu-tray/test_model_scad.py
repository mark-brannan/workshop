"""Tests for the IMU tray and cover: bounding box, volume window, feature counts, boards clear of the cover."""

import re
import tempfile
from pathlib import Path

import numpy as np
import pytest
import trimesh
from shop.scad import OpenSCAD, find_openscad
from shop.testing import ray_hits

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")

P = {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*(-?[\d.]+)\s*;", (HERE / "model.scad").read_text(), re.M)}
EP = [44.45, 25.4, 1.6]
IMU = [25.4, 17.78, 1.6]
EP_X0 = 9.7
EP_X1 = EP_X0 + EP[0]
IMU_X0 = EP_X1 + P["board_gap"]
IMU_CX = IMU_X0 + IMU[0] / 2
IN_X1 = IMU_X0 + IMU[0] + P["end_gap"]
Z_B = P["floor_t"] + P["post_h"]
TOP = P["floor_t"] + P["in_h"] + P["roof_t"]


def run(part: str) -> trimesh.Trimesh:
    osc = OpenSCAD()
    with tempfile.TemporaryDirectory() as d:
        stl = Path(d) / "m.stl"
        osc.run(HERE / "model.scad", stl, "-D", f'part="{part}"')
        mesh = trimesh.load(stl)
    osc.cleanup()
    return mesh


@pytest.fixture(scope="module")
def tray():
    return run("tray")


@pytest.fixture(scope="module")
def cover():
    return run("cover")


def down(mesh, x, y):
    return ray_hits(mesh, (x, y, 100), (0, 0, -1))


def test_tray_bounds_and_volume(tray):
    assert tray.is_watertight
    lo, hi = tray.bounds
    assert np.isclose(lo[0], P["tie_x"] - 7 / 2, atol=0.02)          # saddle [7, 16, 11]
    assert np.isclose(hi[0], IN_X1 + P["wall"], atol=0.02)
    assert np.isclose(lo[2], 0) and np.isclose(hi[2], 11, atol=0.02)
    assert 10_000 < tray.volume < 20_000


def test_tray_posts_hold_inserts_without_breaking_through(tray):
    holes = [(EP_X1 - dx, sy * 10.16, 5.5) for dx in (2.54, 22.86) for sy in (-1, 1)]
    holes += [(IMU_CX + sx * 10.16, sy * 6.35, 4.5) for sx in (-1, 1) for sy in (-1, 1)]
    for x, y, depth in holes:
        h = down(tray, x, y)
        assert np.isclose(h[0][2], Z_B - depth, atol=0.02)    # floor of the insert hole: blind, inside the post
        assert Z_B - depth > 0.5
        assert np.isclose(down(tray, x + 2.4, y)[0][2], Z_B, atol=0.02)   # post rim at board height


def test_four_ear_holes_go_through(tray, cover):
    for x in (6, 88):
        for y in (-17 - 5.5 + 1, 26 + 5.5 - 1):
            assert len(down(tray, x, y)) == 0
            assert len(down(cover, x, y)) == 0


def test_cover_bounds_and_volume(cover):
    assert cover.is_watertight
    lo, hi = cover.bounds
    assert np.isclose(hi[2] - lo[2], TOP - P["floor_t"], atol=0.02)
    assert 15_000 < cover.volume < 30_000


def test_boards_and_jack_inside_the_cover():
    # cover inside: x 0..IN_X1, y in_y0..in_y1, z up to floor_t + in_h; jack top is a guess at 13.5 above the board
    jack_top = Z_B + EP[2] + 13.5
    assert jack_top + 2 <= P["floor_t"] + P["in_h"]
    assert EP[1] / 2 < -P["in_y0"] and EP[1] / 2 + 8 < P["in_y1"]    # room for the Qwiic plug on the +y edge
    assert IMU_X0 + IMU[0] < IN_X1


def test_plug_opening_clears_the_plug():
    plug_axis = Z_B + EP[2] + 6.5
    assert P["slot_w"] >= 11.7 + 6
    assert P["floor_t"] + P["slot_top"] >= plug_axis + 7 + 1


def test_cover_vents_and_plug_slot(cover):
    # printed roof-down: cover z = TOP - assembled z. A ray across the -x wall at the plug axis finds the slot.
    z = TOP - (Z_B + EP[2] + 6.5)
    assert len(ray_hits(cover, (-10, 0, z), (1, 0, 0))) == 2       # only the +x wall
    zv = TOP - (P["floor_t"] + 2 + P["vent_h"] / 2)
    xs = np.arange(EP_X0 + 4, IN_X1 - 6 + 1e-6, P["vent_pitch"])
    open_ = sum(len(ray_hits(cover, (x + P["vent_w"] / 2, 0, zv), (0, -1, 0))) == 0 for x in xs)   # from inside out through the -y wall
    assert open_ >= 10
