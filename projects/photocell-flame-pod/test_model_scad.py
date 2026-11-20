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
LEAD_L = P["solder_out"]  # lead = "solder", the default; potted = true
EXIT_X = P["cell_end"] + P["board_l"] + LEAD_L + P["cable_d"] / 2
IN_L = EXIT_X + P["cable_d"] / 2 + P["end_clear"]
IN_W = P["board_w"] + 2 * P["fit"]
OUT_L, OUT_W = IN_L + 2 * P["wall"], IN_W + 2 * P["wall"]
BOARD_Z = P["floor_t"] + P["ledge"]
BOARD_TOP = BOARD_Z + P["board_t"]
POUR_Z = BOARD_TOP + P["cell_h"] - P["cell_t"]
TRAY_H = POUR_Z + P["pour_rim"]
CABLE_Z = BOARD_TOP + P["pin_z"]
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
    y0 = -OUT_W / 2 - P["tie_out"]
    assert np.allclose(tray.bounds, [[x0, y0, 0], [x1, OUT_W / 2, TRAY_H]], atol=0.05)
    assert 4_000 < tray.volume < 7_500


def test_potting_covers_board_and_trimpot_leaves_cell_proud():
    assert POUR_Z > BOARD_TOP + P["pot_h"] + 1
    assert BOARD_TOP + P["cell_h"] > TRAY_H  # the cell's face stands above the rim


def test_board_rests_on_ledges_and_boss(tray):
    y_ledge = IN_W / 2 - P["fit"] - P["ledge_lip"] / 2
    for y in (-y_ledge, y_ledge):
        assert np.isclose(down(tray, P["cell_end"] + P["board_l"] / 2, y)[0][2], BOARD_Z, atol=0.02)
    assert np.isclose(down(tray, P["cell_end"] + 1, y_ledge)[0][2], P["floor_t"], atol=0.02)  # bare under the cell end
    assert np.isclose(down(tray, HOLE_X + P["boss_d"] / 2 - 0.3, 0)[0][2], BOARD_Z, atol=0.02)


def test_locating_pin_through_board_hole_no_floor_hole(tray):
    assert np.isclose(down(tray, HOLE_X, 0)[0][2], BOARD_TOP, atol=0.02)
    assert P["locate_d"] < 4 - 0.4  # board hole ~4
    assert len(down(tray, HOLE_X, 0)) == 2  # pin top and the underside: solid, no leak for the pour


def test_cable_exits_side_wall_clear_of_tabs(tray):
    hits = ray_hits(tray, (EXIT_X, -OUT_W, CABLE_Z), (0, 1, 0))
    assert hits[0][1] > 0  # nothing in the -Y wall at cable height: first hit is across the tray
    assert CABLE_Z - P["cable_d"] / 2 > BOARD_Z  # round bottom stays above the board underside
    assert EXIT_X + P["cable_d"] / 2 < IN_L  # inside the end wall, not over the end tab
    assert EXIT_X - P["cable_d"] / 2 > P["cell_end"] + P["board_l"] + LEAD_L - 0.01  # past the heatshrink


def test_tie_block_under_exit_with_tunnel(tray):
    y = -OUT_W / 2 - P["tie_out"] / 2
    assert np.isclose(down(tray, EXIT_X, y)[0][2], CABLE_Z - P["cable_d"] / 2, atol=0.02)  # cable bed
    through = ray_hits(tray, (EXIT_X - 20, y, P["tie_h"] / 2), (1, 0, 0))
    assert all(abs(h[0] - EXIT_X) > P["tie_w"] / 2 + P["tie_side"] - 0.05 for h in through)


def test_two_mounting_tab_holes(tray):
    for x in (-P["wall"] - P["tab_l"] / 2, IN_L + P["wall"] + P["tab_l"] / 2):
        assert len(down(tray, x, 0)) == 0
        assert np.isclose(down(tray, x + P["tab_hole"] / 2 + 0.5, 0)[0][2], P["tab_t"], atol=0.02)


def test_lid_outline_and_two_holes(lid):
    assert lid.is_watertight
    assert np.allclose(lid.bounds, [[-P["wall"], -OUT_W / 2, 0], [IN_L + P["wall"], OUT_W / 2, P["lid_t"]]], atol=0.02)
    ci = P["col_in"]
    assert len(down(lid, ci, -(IN_W / 2 - ci))) == 0 and len(down(lid, IN_L - ci, IN_W / 2 - ci)) == 0
    assert len(down(lid, ci, IN_W / 2 - ci)) > 0  # the other diagonal is solid
    # hole edge at least 2 mm from the lid's edge
    assert ci + P["wall"] - P["lid_hole_d"] / 2 >= 2
