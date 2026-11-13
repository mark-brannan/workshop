"""Tests for the segment display enclosure: bounding box, volume window, feature counts."""

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
IN_L, IN_W = P["board_l"] + 2 * P["board_clear"], P["board_w"] + 2 * P["board_clear"]
OUT_L, OUT_W = IN_L + 2 * P["wall"], IN_W + 2 * P["wall"]
BOARD_Z = max(P["disp_recess_min"] + P["disp_h"], P["face_t"] + P["pin_h"] + P["plug_h"] / 2 + P["plug_clear"])
NOTCH_Z = BOARD_Z - P["pin_h"] - P["plug_h"] / 2 - P["plug_clear"]
WINDOW_TOP = NOTCH_Z + P["plug_h"] + 2 * P["plug_clear"]
SHELL_H = BOARD_Z + P["board_t"] + P["rear_clear"]
HOLES = [(sx * P["hole_dx"] / 2, sy * P["hole_dy"] / 2) for sx in (-1, 1) for sy in (-1, 1)]


def build(tmp_path_factory, part):
    d = tmp_path_factory.mktemp(part)
    for f in ("model.scad", "part-back.scad"):
        (d / f).write_text((HERE / f).read_text())
    src = d / ("model.scad" if part == "shell" else "part-back.scad")
    return trimesh.load(build_scad(src, d, part, render=False)["stl"])


@pytest.fixture(scope="module")
def shell(tmp_path_factory):
    return build(tmp_path_factory, "shell")


@pytest.fixture(scope="module")
def back(tmp_path_factory):
    return build(tmp_path_factory, "back")


def down(mesh, x, y):
    return ray_hits(mesh, (x, y, 50), (0, 0, -1))


def test_shell_bounds_volume(shell):
    assert shell.is_watertight
    assert np.allclose(shell.bounds, [[-OUT_L / 2, -OUT_W / 2, 0], [OUT_L / 2, OUT_W / 2, SHELL_H]], atol=0.02)
    assert 3_500 < shell.volume < 7_000


def test_window_fits_display_and_is_through(shell):
    cx, cy = P["disp_dx"], P["disp_dy"]
    assert len(down(shell, cx, cy)) == 0
    assert len(down(shell, cx + P["disp_l"] / 2 + 0.2, cy + P["disp_w"] / 2 + 0.2)) == 0  # clearance at the corner
    assert len(down(shell, cx + P["disp_l"] / 2 + 1.0, cy)) > 0  # face beyond the window


def test_display_recessed_and_plug_clears_face():
    assert BOARD_Z - P["disp_h"] >= P["disp_recess_min"]
    assert NOTCH_Z >= P["face_t"]  # the plug's housing never meets the face


def test_window_chamfered_on_outer_face(shell):
    cx, cy = P["disp_dx"], P["disp_dy"]
    edge = cx + P["disp_l"] / 2 + P["window_clear"] + 0.5
    assert np.isclose(down(shell, edge, cy)[-1][2], P["window_chamfer"] - 0.5, atol=0.05)


def test_four_blind_pilot_posts_at_board_height(shell):
    for x, y in HOLES:
        assert np.isclose(down(shell, x, y)[0][2], P["face_t"] - 1, atol=0.02)  # blind, never through the face
        assert np.isclose(down(shell, x + P["pilot_d"] / 2 + 0.4, y)[0][2], BOARD_Z, atol=0.02)


def test_screw_stack_fits_m2p5x12():
    engage = 12 - P["cover_t"] - P["rear_clear"] - P["board_t"]
    assert engage >= 4 and engage <= BOARD_Z - (P["face_t"] - 1)


def test_back_bounds_holes_tongue(back):
    assert back.is_watertight
    top = P["cover_t"] + P["rear_clear"]
    tongue_top = P["cover_t"] + SHELL_H - WINDOW_TOP  # tongue reaches down to the top of the plug
    assert np.allclose(back.bounds, [[-OUT_L / 2, -OUT_W / 2, 0], [OUT_L / 2, OUT_W / 2, tongue_top]], atol=0.02)
    for x, y in HOLES:
        assert len(down(back, x, y)) == 0
        assert np.isclose(down(back, x + P["screw_clear_d"] / 2 + 0.4, y)[0][2], top, atol=0.02)
    assert len(down(back, 0, 0)) > 0  # no openings in the cover's middle


def side(mesh, z, y=0):
    return ray_hits(mesh, (-50, y, z), (1, 0, 0))


def test_header_end_has_plug_window_and_open_notch(shell):
    notch_z = NOTCH_Z
    first_wall = lambda z: side(shell, z)[0][0]
    assert first_wall(notch_z + 0.5) > -IN_L / 2  # plug window: no end wall at plug height
    assert first_wall(SHELL_H - 0.5) > -IN_L / 2  # open to the rim for the cover's tongue
    assert np.isclose(first_wall(notch_z - 0.5), -OUT_L / 2, atol=0.05)  # wall below the window
    assert np.isclose(side(shell, notch_z + 0.5, y=P["board_w"] / 2)[0][0], -OUT_L / 2, atol=0.05)  # wall beside it
    assert notch_z >= P["face_t"] - 0.01


def test_posts_clear_display():
    hole_to_disp_y = P["hole_dy"] / 2 - (abs(P["disp_dy"]) + P["disp_w"] / 2 + P["window_clear"])
    assert hole_to_disp_y - P["pilot_d"] / 2 >= 0.8


def test_display_offsets_match_calipers():
    assert np.isclose((P["disp_dx"] - P["disp_l"] / 2) + P["board_l"] / 2, 5)  # pin end
    assert np.isclose(P["board_w"] / 2 + (P["disp_dy"] - P["disp_w"] / 2), 4.5)  # -Y edge


def test_lip_fits_inside_shell():
    assert P["lip_clear"] > 0 and P["lip_t"] >= 1
    assert P["hole_dx"] / 2 + P["tube_d"] / 2 < IN_L / 2
