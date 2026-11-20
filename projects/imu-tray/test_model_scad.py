"""Tests for the IMU tray and its lid: bounding box, volume window, feature counts, boards clear of the lid."""

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
H = P["lid_z"] + P["lid_t"]
W = P["wall"]


def run(scad: str, *defs: str) -> trimesh.Trimesh:
    osc = OpenSCAD()
    with tempfile.TemporaryDirectory() as d:
        stl = Path(d) / "m.stl"
        osc.run(HERE / scad, stl, *[a for kv in defs for a in ("-D", kv)])
        mesh = trimesh.load(stl)
    osc.cleanup()
    return mesh


@pytest.fixture(scope="module")
def tray():
    return run("model.scad")


@pytest.fixture(scope="module")
def lid():
    return run("part-lid.scad", 'mode="3d"')


def down(mesh, x, y):
    return ray_hits(mesh, (x, y, 100), (0, 0, -1))


def test_tray_bounds_and_volume(tray):
    assert tray.is_watertight
    FL = P["foot_l"]
    assert np.allclose(tray.bounds, [[-W - FL, P["in_y0"] - W, 0], [IN_X1 + W + FL, P["in_y1"] + W, H]], atol=0.02)
    assert 15_000 < tray.volume < 30_000


def test_eight_posts_with_blind_pilot_holes(tray):
    holes = [(EP_X1 - dx, sy * 10.16) for dx in (2.54, 22.86) for sy in (-1, 1)]
    holes += [(IMU_CX + sx * 10.16, sy * 6.35) for sx in (-1, 1) for sy in (-1, 1)]
    for x, y in holes:
        assert np.isclose(down(tray, x, y)[0][2], Z_B - 6, atol=0.02)     # floor of the pilot hole: blind, inside the post
        assert Z_B - 6 > 0.5
        assert np.isclose(down(tray, x + 2.4, y)[0][2], Z_B, atol=0.02)   # post rim at board height


def test_four_feet_outside_the_box_clear_of_the_plug(tray):
    FL, FW = P["foot_l"], P["foot_w"]
    for x in (-W - FL / 2, IN_X1 + W + FL / 2):
        for y in (P["in_y0"] - W + FW / 2, P["in_y1"] + W - FW / 2):
            assert len(down(tray, x, y)) == 0                            # the screw hole
            assert np.isclose(down(tray, x + 3.5, y)[0][2], P["foot_t"], atol=0.02)
    assert P["foot_t"] + 4 < Z_B + EP[2] + P["plug_z"] - 8          # the plug and cable pass well above the feet
    assert len(down(tray, 30, 19)) == 2                                  # no holes left in the floor


def test_lid_fits_the_rebate_flush(tray, lid):
    assert lid.is_watertight
    (x0, y0, z0), (x1, y1, z1) = lid.bounds
    assert np.isclose(z1 - z0, P["lid_t"])
    reb = P["ledge"]
    assert np.isclose(x1 - x0, IN_X1 + 2 * reb - 2 * P["lid_gap"], atol=0.02)
    assert np.isclose(down(tray, 30, P["in_y0"] - reb / 2)[0][2], P["lid_z"], atol=0.02)    # the ledge
    assert np.isclose(down(tray, 30, P["in_y0"] - reb - 0.5)[0][2], H, atol=0.02)          # the rim beside it


def test_jack_under_the_lid_and_plug_opening():
    assert Z_B + EP[2] + 13.5 + 1.5 <= P["lid_z"]
    assert EP[1] / 2 + 8 < P["in_y1"]                                 # room for the Qwiic plug on the +y edge
    assert P["slot_w"] >= 11.7 + 6


def test_plug_opening_in_the_minus_x_wall(tray):
    z = Z_B + EP[2] + 6.5
    assert len(ray_hits(tray, (-10, 0, z), (1, 0, 0))) == 2           # only the +x wall
    assert len(ray_hits(tray, (-10, -14, z), (1, 0, 0))) == 4         # beside the opening the -x wall is there
