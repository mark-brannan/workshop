"""Tests for the desk presence sensor: shell, back plate, D1 retainer. Bounding box, volume, features."""

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
IN_W = P["box_w"] - 2 * P["wall"]
RD_CY = 0.5 + P["rd_rib_t"] + P["rd_slack"] + P["rd_h"] / 2
TM_CY = RD_CY + P["rd_h"] / 2 + P["rd_slack"] + P["rd_rib_t"] + P["gap"] + P["tm_clear"] + P["tm_w"] / 2
OL_CY = TM_CY + P["tm_w"] / 2 + P["tm_clear"] + P["gap"] + P["ol_h"] / 2
IN_H = OL_CY + P["ol_h"] / 2 + 0.5
TM_BOARD_Z = P["tm_recess"] + P["tm_disp_h"]
OL_BOARD_Z = P["face_t"] + P["ol_gap"] + P["ol_glass_h"]
D1_X = IN_W / 2 - P["can_clr"] - P["d1_shield_h"] - P["d1_t"] / 2
D1_Z0 = P["rd_stack"] + 1
D1_Z1 = D1_Z0 + P["d1_w"]
D1_ZC = (D1_Z0 + D1_Z1) / 2
D1_Y1 = P["d1_y0"] + P["d1_l"]
SHELL_D = D1_Z1 + P["ret_t"] + 0.5
SLOT_W = P["d1_t"] + 2 * P["slot_clr"]
LEDGE_Y0 = D1_Y1 + P["d1_slack"] - P["slot_deep"]


def build(tmp_path_factory, scad):
    d = tmp_path_factory.mktemp(scad)
    for f in ("model.scad", scad):
        (d / f).write_text((HERE / f).read_text())
    return trimesh.load(build_scad(d / scad, d, scad, render=False)["stl"])


@pytest.fixture(scope="module")
def shell(tmp_path_factory):
    return build(tmp_path_factory, "model.scad")


@pytest.fixture(scope="module")
def back(tmp_path_factory):
    return build(tmp_path_factory, "part-back.scad")


@pytest.fixture(scope="module")
def retainer(tmp_path_factory):
    return build(tmp_path_factory, "part-retainer.scad")


def down(mesh, x, y, z=80):
    return ray_hits(mesh, (x, y, z), (0, 0, -1))


def test_shell_bounds_volume(shell):
    assert shell.is_watertight
    assert np.allclose(shell.bounds[:, 2], [0, SHELL_D], atol=0.05)
    assert np.isclose(shell.bounds[1][0] - shell.bounds[0][0], P["box_w"], atol=0.05)
    assert np.isclose(shell.bounds[1][1] - shell.bounds[0][1], IN_H + 2 * P["wall"], atol=0.05)
    assert 18_000 < shell.volume < 30_000


def test_windows_through_radar_behind_solid_face(shell):
    cx, cy = P["tm_disp_dx"], TM_CY + P["tm_disp_dy"]
    assert len(down(shell, cx, cy)) == 0
    assert len(down(shell, 0, OL_CY + P["ol_win_dy"])) == 0
    assert np.isclose(down(shell, 0, RD_CY)[0][2], P["face_t"], atol=0.02)


def test_board_posts_blind_pilots_at_board_height(shell):
    for sx in (-1, 1):
        for sy in (-1, 1):
            for x, y, d, z in ((sx * P["tm_hole_dx"] / 2, TM_CY + sy * P["tm_hole_dy"] / 2, P["tm_pilot_d"], TM_BOARD_Z),
                               (sx * P["ol_hole_dx"] / 2, OL_CY + sy * P["ol_hole_dy"] / 2, P["ol_pilot_d"], OL_BOARD_Z)):
                assert np.isclose(down(shell, x, y)[0][2], P["face_t"] - 1, atol=0.02)
                assert np.isclose(down(shell, x + d / 2 + 0.3, y)[0][2], z, atol=0.02)


def test_d1_floor_slot_stops_the_board_front_edge(shell):
    y = P["d1_y0"] + 0.5
    assert np.isclose(down(shell, D1_X, y)[0][2], D1_Z0, atol=0.05)      # open from the back to the stop
    assert down(shell, D1_X + SLOT_W, y)[0][2] > SHELL_D - 0.1           # rail beside the slot


def test_d1_ledge_slot_open_except_at_usb(shell):
    y = LEDGE_Y0 + 0.5
    assert down(shell, D1_X, y)[0][2] <= P["face_t"] + 0.01             # slot clear down to the face
    beside = down(shell, D1_X - SLOT_W, y)
    assert beside[0][2] > SHELL_D - 0.1                                  # back segment from the rim
    zs = sorted(h[2] for h in beside)
    assert any(D1_ZC - P["usb_gap"] / 2 - 0.1 < z < D1_ZC - P["usb_gap"] / 2 + 0.1 for z in zs)  # gap for the plug


def test_d1_clear_of_radar_jumpers_and_tm1637():
    assert D1_Z0 > P["rd_stack"]
    assert D1_X - P["d1_t"] / 2 - P["jumper_h"] > -IN_W / 2              # its Dupont housings fit across
    assert D1_X + P["d1_t"] / 2 + P["d1_shield_h"] + P["can_clr"] <= IN_W / 2 + 1e-9
    assert D1_Y1 < OL_CY - P["ol_h"] / 2                                 # USB plug end sits below the OLED board


def test_cable_slot_open_to_rim(shell):
    hits = ray_hits(shell, (D1_X, IN_H + 10, SHELL_D - 1), (0, -1, 0))
    assert hits[0][1] < IN_H - 1                                         # nothing in the top wall there
    assert ray_hits(shell, (D1_X, IN_H + 10, D1_ZC - 6), (0, -1, 0))[0][1] > IN_H  # wall below the slot


def test_back_flat_tape_face_and_tabs(back):
    assert back.is_watertight
    assert np.allclose(back.bounds[:, 2], [0, P["back_t"] + P["tab_len"]], atol=0.05)
    assert np.isclose(back.bounds[1][0] - back.bounds[0][0], P["box_w"], atol=0.05)
    assert 6_000 < back.volume < 12_000
    assert np.isclose(ray_hits(back, (0, IN_H / 2, -10), (0, 0, 1))[0][2], 0, atol=0.05)


def test_retainer_fits_between_rails(retainer):
    assert retainer.is_watertight
    assert 150 < retainer.volume < 400
    assert np.isclose(retainer.bounds[1][2] - retainer.bounds[0][2], P["ret_body"], atol=0.05)
