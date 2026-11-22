"""Tests for the HALPI2 EndPoint box: bounds, volume, solid floor, screws outside the cavity, openings."""

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
W = P["wall"]
IN_X0 = P["in_x0"]
IN_X1 = 44.45 + P["jack_over"]
EX = (IN_X0 + IN_X1) / 2
HY = P["in_half_y"]
Z_B = P["floor_t"] + P["post_h"]
Z_T = Z_B + 1.6
H = P["lid_z"] + P["lid_t"]
PITCH = P["mount_pitch"]


@pytest.fixture(scope="module")
def box():
    osc = OpenSCAD()
    with tempfile.TemporaryDirectory() as d:
        stl = Path(d) / "m.stl"
        osc.run(HERE / "model.scad", stl)
        mesh = trimesh.load(stl)
    osc.cleanup()
    return mesh


def down(mesh, x, y):
    return ray_hits(mesh, (x, y, 100), (0, 0, -1))


def test_bounds_and_volume(box):
    assert box.is_watertight
    r = P["ear_d"] / 2
    assert np.allclose(box.bounds, [[IN_X0 - W, -PITCH / 2 - r, 0], [IN_X1 + W, PITCH / 2 + r, H]], atol=0.05)
    assert 12_000 < box.volume < 25_000


def test_floor_is_solid_for_potting(box):
    for x in np.linspace(IN_X0 + 1, IN_X1 - 1, 9):
        for y in np.linspace(-HY + 1, HY - 1, 7):
            assert len(down(box, x, y)) >= 2, (x, y)          # every ray through the cavity meets a floor


def test_ear_holes_at_clip_pitch_outside_the_cavity(box):
    for sy in (-1, 1):
        y = sy * PITCH / 2
        assert len(down(box, EX, y)) == 0                      # the hole goes clean through
        assert np.isclose(down(box, EX + 3, y)[0][2], P["ear_t"], atol=0.02)
    assert PITCH / 2 - 6 >= HY + W                             # a head 12 across clears the wall
    assert P["ear_hole"] > 3.5                                 # a #6 wood screw passes


def test_body_is_the_board_width_plus_walls():
    assert 2 * (HY + W) <= 25.4 + 1 + 2 * W


def test_four_posts_with_blind_pilots(box):
    for x in (2.54, 22.86):
        for y in (-10.16, 10.16):
            assert np.isclose(down(box, x, y)[0][2], Z_B - P["pilot_depth"], atol=0.02)
            assert np.isclose(down(box, x + 2.5, y)[0][2], Z_B, atol=0.02)


def test_rj45_window_matches_the_jack(box):
    z = Z_T + P["jack_h"] / 2
    assert len(ray_hits(box, (IN_X1 - 5, 5, z), (1, 0, 0))) == 0
    half = P["jack_w"] / 2 + P["win_fit"]
    assert len(ray_hits(box, (IN_X1 - 5, half + 0.3, z), (1, 0, 0))) == 2       # wall beside the window
    assert len(ray_hits(box, (IN_X1 - 5, 0, Z_T - 0.3), (1, 0, 0))) == 2        # wall under it: resin stays in
    assert Z_T + P["jack_h"] + 1.5 <= P["lid_z"]


def test_qwiic_holes_at_the_sockets_and_no_other_side_openings(box):
    z = Z_T + 1.5
    assert len(ray_hits(box, (P["qwiic_x"], -HY - 10, z), (0, 1, 0))) == 0      # straight through both holes
    assert len(ray_hits(box, (P["qwiic_x"] + 5, -HY - 10, z), (0, 1, 0))) == 4  # beside them the walls are whole
    for x in (0, 30, 50):
        assert len(ray_hits(box, (x, -HY - 10, Z_T + 8), (0, 1, 0))) == 4


def test_lead_hole_in_the_minus_x_wall_at_the_terminal(box):
    z = Z_T + P["lead_z"]
    assert len(ray_hits(box, (IN_X0 + 2, P["term_y"], z), (-1, 0, 0))) == 0     # out through the hole
    assert len(ray_hits(box, (IN_X0 + 2, P["term_y"] + 5, z), (-1, 0, 0))) == 2 # beside it the wall is whole


def test_window_top_rests_on_the_tree(box):
    """No stretch of the RJ45 window's flat top is more than 2.5 from a branch tip."""
    def longest_gap(start, along, lo, hi):
        run = worst = 0.0
        for t in np.arange(lo, hi, 0.1):
            o = np.array(start, float) + t * np.array(along)
            below = [h for h in ray_hits(box, o, (0, 0, -1)) if o[2] - h[2] < 0.5]
            run = 0.0 if below else run + 0.1
            worst = max(worst, run)
        return worst

    top = Z_T + P["jack_h"] + P["win_fit"] - 0.01
    assert longest_gap((IN_X1 + W / 2, 0, top), (0, 1, 0), -8.55, 8.55) <= 2.5         # RJ45 window, on its tree


def test_no_flat_overhang_warning(box):
    from shop.overhang import flat_spans

    assert flat_spans(box) == []
