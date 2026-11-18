"""Tests for the photocell flame pod: bounding box, volume window, feature counts."""

import re
from pathlib import Path

import numpy as np
import pytest
import trimesh
from shop.scad import build_scad, find_openscad
from shop.testing import ray_hits

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")

P = {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*([-\d.]+)\s*;", (HERE / "model.scad").read_text(), re.M)}
LEAD_L = P["plug_out"]  # lead = "dupont", the default
IN_L = P["cell_end"] + P["board_l"] + LEAD_L + P["wire_clear"]
IN_W = P["board_w"] + 2 * P["fit"]
OUT_L, OUT_W = IN_L + 2 * P["wall"], IN_W + 2 * P["wall"]
BOARD_Z = P["floor_t"] + P["ledge"]
BOARD_TOP = BOARD_Z + P["board_t"]
TRAY_H = BOARD_TOP + P["cell_h"] + P["top_clear"]
HOLE_X = P["cell_end"] + P["board_l"] - P["hole_from_hdr"]


def build(tmp_path_factory, src, name, two_d=False):
    d = tmp_path_factory.mktemp(name)
    for f in ("model.scad", "part-lid.scad"):
        (d / f).write_text((HERE / f).read_text())
    return trimesh.load(build_scad(d / src, d, name, two_d=two_d, render=False)["stl"])


@pytest.fixture(scope="module")
def tray(tmp_path_factory):
    return build(tmp_path_factory, "model.scad", "tray")


@pytest.fixture(scope="module")
def lid(tmp_path_factory):
    return build(tmp_path_factory, "part-lid.scad", "lid", two_d=True)


def down(mesh, x, y):
    return ray_hits(mesh, (x, y, 60), (0, 0, -1))


def test_tray_bounds_volume(tray):
    assert tray.is_watertight
    x0, x1 = -P["wall"] - P["tab_l"], IN_L + P["wall"] + P["tab_l"]
    assert np.allclose(tray.bounds, [[x0, -OUT_W / 2, 0], [x1, OUT_W / 2, TRAY_H]], atol=0.05)
    assert 5_000 < tray.volume < 9_000


def test_photocell_clears_the_lid():
    assert TRAY_H - (BOARD_TOP + P["cell_h"]) == pytest.approx(P["top_clear"]) and P["top_clear"] > 0


def test_board_rests_on_ledges_and_boss(tray):
    y_ledge = IN_W / 2 - P["fit"] - P["ledge_lip"] / 2
    for y in (-y_ledge, y_ledge):
        assert np.isclose(down(tray, P["cell_end"] + P["board_l"] / 2, y)[0][2], BOARD_Z, atol=0.02)
    assert np.isclose(down(tray, P["cell_end"] + 1, y_ledge)[0][2], P["floor_t"], atol=0.02)  # bare under the cell end
    assert np.isclose(down(tray, HOLE_X + P["boss_d"] / 2 - 0.3, 0)[0][2], BOARD_Z, atol=0.02)


def test_screw_through_and_nut_pocket(tray):
    assert len(down(tray, HOLE_X, 0)) == 0  # clearance through the floor
    nut_floor = down(tray, HOLE_X + P["screw_d"] / 2 + 0.6, 0)[0][2]
    assert np.isclose(nut_floor, BOARD_Z - P["nut_t"], atol=0.02) and nut_floor > 0


def test_four_lid_columns_with_pilots(tray):
    for x in (1.5, IN_L - 1.5):  # inside the column, outside its pilot
        for y in (-IN_W / 2 + 0.4, IN_W / 2 - 0.4):
            assert np.isclose(down(tray, x, y)[0][2], TRAY_H, atol=0.05)
    pilot_bottom = down(tray, 0, IN_W / 2)  # pilot centred on the inside corner
    assert np.isclose(pilot_bottom[0][2], TRAY_H - P["pilot_h"], atol=0.05)


def test_cable_slot_open_to_rim(tray):
    cable_z = BOARD_TOP + P["pin_z"]
    hits = ray_hits(tray, (IN_L + 10, 0, cable_z), (-1, 0, 0))
    assert hits[0][0] < P["cell_end"] + P["board_l"]  # nothing in the end wall at cable height
    assert cable_z - P["cable_d"] / 2 > BOARD_Z  # round bottom stays above the board underside
    assert np.isclose(ray_hits(tray, (IN_L + 10, 0, BOARD_Z - 1), (-1, 0, 0))[0][0], IN_L + P["wall"], atol=0.05)


def test_two_mounting_tab_holes(tray):
    for x in (-P["wall"] - P["tab_l"] / 2, IN_L + P["wall"] + P["tab_l"] / 2):
        assert len(down(tray, x, 0)) == 0
        assert np.isclose(down(tray, x + P["tab_hole"] / 2 + 0.5, 0)[0][2], P["tab_t"], atol=0.02)


def test_lid_outline_and_two_holes(lid):
    assert lid.is_watertight
    assert np.allclose(lid.bounds, [[-P["wall"], -OUT_W / 2, 0], [IN_L + P["wall"], OUT_W / 2, P["lid_t"]]], atol=0.02)
    assert len(down(lid, 0, -IN_W / 2)) == 0 and len(down(lid, IN_L, IN_W / 2)) == 0
    assert len(down(lid, 0, IN_W / 2)) > 0  # the other diagonal is solid
