"""Tests for the desk presence sensor: shell, back plate, D1 tray. Bounding box, volume, features."""

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
OL_BOARD_Z = P["face_t"] + P["ol_gap"] - P["ol_fwd"] + P["ol_glass_h"]
OL_BACK_Z = OL_BOARD_Z + P["ol_t"] + P["ol_pins"]
TRAY_Z0 = TM_BOARD_Z + P["tm_t"]
D1_Z0 = TRAY_Z0 + P["tray_t"]
D1_Y1 = P["d1_y0"] + P["d1_l"]
USB_Z = D1_Z0 + P["d1_t"] + P["usb_h"]
PLUG_Y0 = D1_Y1 + P["usb_lip"]
SHELL_D = max(USB_Z + P["plug_t"] / 2, D1_Z0 + P["d1_t"] + P["d1_shield_h"]) + P["back_clr"]
CABLE_Z0 = USB_Z - P["cable_d"] / 2 - 0.5
TRAY_HW = IN_W / 2 - P["tray_side"]
TRAY_Y0 = P["d1_y0"] - P["d1_clr"] - P["lip_t"]
TRAY_Y1 = TM_CY + P["tm_w"] / 2 + 1.35
POST_Y0 = D1_Y1 + P["d1_clr"]
CATCH_Z = D1_Z0 + P["d1_t"] + 0.05 - P["d1_clr"]
HOOK_TOP = CATCH_Z + 2 * (P["catch"] + P["d1_clr"]) - TRAY_Z0   # print coordinates: tray front on the bed
TM_HOLES = [(sx * P["tm_hole_dx"] / 2, TM_CY + sy * P["tm_hole_dy"] / 2) for sx in (-1, 1) for sy in (-1, 1)]


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
def tray(tmp_path_factory):
    return build(tmp_path_factory, "part-tray.scad")


def down(mesh, x, y, z=80):
    return ray_hits(mesh, (x, y, z), (0, 0, -1))


def test_shell_bounds_volume(shell):
    assert shell.is_watertight
    assert np.allclose(shell.bounds[:, 2], [0, SHELL_D], atol=0.05)
    assert np.isclose(shell.bounds[1][0] - shell.bounds[0][0], P["box_w"], atol=0.05)
    assert np.isclose(shell.bounds[1][1] - shell.bounds[0][1], IN_H + 2 * P["wall"], atol=0.05)
    assert 9_000 < shell.volume < 14_000


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


def test_nothing_in_the_shell_behind_the_boards(shell):
    for x, y in ((0, P["d1_y0"] + 2), (15, TM_CY + 6), (0, PLUG_Y0 + 5)):   # D1, tray and plug space: open down to the face
        assert down(shell, x, y, SHELL_D - 0.1)[0][2] <= P["face_t"] + 0.01


def test_cable_slot_open_to_rim(shell):
    hits = ray_hits(shell, (0, IN_H + 10, SHELL_D - 1), (0, -1, 0))
    assert hits[0][1] < IN_H - 1                                         # nothing in the top wall there
    assert ray_hits(shell, (0, IN_H + 10, CABLE_Z0 - 1), (0, -1, 0))[0][1] > IN_H  # wall below the slot


def test_depth_stack_clearances():
    plug_front = USB_Z - P["plug_t"] / 2
    assert plug_front > OL_BACK_Z + 1                                    # plug and cable pass behind the OLED
    assert plug_front > TRAY_Z0                                          # and behind the TM1637's top edge
    assert D1_Z0 - P["d1_under"] > TRAY_Z0 + P["tm_joint_h"]             # D1 underside parts clear the TM1637 joints
    assert TRAY_Z0 > P["face_t"] + P["rd_t"] + P["rd_back"]              # tray clear of the radar's wires
    assert PLUG_Y0 + P["plug_l"] < IN_H - P["cable_d"]                   # plug ends below the top wall
    assert 20 < SHELL_D + P["back_t"] < 24                               # outside depth near the 23 asked


def test_back_flat_tape_face_and_tabs(back):
    assert back.is_watertight
    assert np.allclose(back.bounds[:, 2], [0, P["back_t"] + P["tab_len"]], atol=0.05)
    assert np.isclose(back.bounds[1][0] - back.bounds[0][0], P["box_w"], atol=0.05)
    assert 6_000 < back.volume < 12_000
    assert np.isclose(ray_hits(back, (0, IN_H / 2, -10), (0, 0, 1))[0][2], 0, atol=0.05)


def test_tray_bounds_volume(tray):
    assert tray.is_watertight
    assert np.allclose(tray.bounds[:, 0], [-TRAY_HW, TRAY_HW], atol=0.05)
    assert np.allclose(tray.bounds[:, 1], [TRAY_Y0, TRAY_Y1], atol=0.05)
    assert np.allclose(tray.bounds[:, 2], [0, HOOK_TOP], atol=0.05)
    assert 2_500 < tray.volume < 4_500


def test_tray_screw_holes_through_pads_bear(tray):
    for x, y in TM_HOLES:
        assert len(down(tray, x, y)) == 0                                # four clearance holes, through
        beside = (x - np.sign(x) * (P["tray_hole_d"] / 2 + 0.4), y)
        assert np.isclose(ray_hits(tray, (*beside, -10), (0, 0, 1))[0][2], 0, atol=0.02)   # pad on the TM1637
        assert np.isclose(down(tray, *beside)[0][2], P["tray_t"], atol=0.02)


def test_tray_windows(tray):
    assert len(down(tray, 0, TM_CY)) == 0                                # D1 underside and display pins
    assert len(down(tray, -TRAY_HW + 1, 34)) == 0                        # TM1637 header joints
    strap = down(tray, 0, TRAY_Y1 - 1)                                   # plug passes over the strap
    assert np.isclose(strap[0][2], P["strap_t"], atol=0.02)
    assert USB_Z - P["plug_t"] / 2 - TRAY_Z0 - P["strap_t"] >= 1.0        # room under a plug fatter than guessed
    assert np.isclose(down(tray, 11, P["d1_y0"] + 1)[0][2], P["tray_t"], atol=0.02)   # D1 seat, bottom (corner)


def test_tray_stop_block_corner_hooks_and_pocket(tray):
    stop = down(tray, 0, TRAY_Y0 + 0.5)
    assert np.isclose(stop[0][2], P["tray_t"] + P["d1_t"], atol=0.02)    # stop block flush with the board's face: no overhang
    wall_y = P["d1_y0"] - P["d1_clr"] - 0.5
    assert np.isclose(down(tray, 0, wall_y)[0][2], P["tray_t"] + P["d1_t"], atol=0.02)   # board edge meets the block
    for sx in (-1, 1):
        zs = down(tray, sx * 11, TRAY_Y0 + 0.5)                          # corner hook wall stands over the board
        assert zs[0][2] > P["tray_t"] + P["d1_t"] + 0.5
        assert len(down(tray, sx * 11, P["d1_y0"] - P["d1_clr"] + P["lip_catch"])) > 0   # catch reaches over the board edge
    assert np.isclose(down(tray, 0, P["d1_y0"] + 1)[0][2], P["tray_t"] - P["stop_rec"], atol=0.02)   # seat pocket by the block
    assert np.isclose(down(tray, 11, P["d1_y0"] + 1)[0][2], P["tray_t"], atol=0.02)                   # corner seats full height
    for sx in (-1, 1):
        x = sx * (P["hook_x0"] + P["hook_w"] / 2)
        assert np.isclose(down(tray, x, POST_Y0 + P["hook_t"] / 2)[0][2], HOOK_TOP, atol=0.05)  # post
        for y in (POST_Y0 - P["hook_slot"] / 2, POST_Y0 + P["hook_t"] + P["hook_slot"] / 2):     # free both sides
            zs = [h[2] for h in down(tray, x, y)]
            assert np.isclose(sorted(zs)[1], P["hook_root"], atol=0.02)      # only the root layer below, then air (or the catch)
    assert len(down(tray, 0, POST_Y0 + 0.5)) == 0                        # no hook in the plug's path


def test_radar_hooks_lips_and_oled_frame(shell):
    rd_cy = 0.5 + P["rd_rib_t"] + P["rd_slack"] + P["rd_h"] / 2
    y_lip = rd_cy + P["rd_h"] / 2 - 1 - P["rd_lip_len"] / 2
    x_in = P["rd_w"] / 2 + P["rd_slack"] - 0.3          # inside the rib, under a lip
    for sx in (-1, 1):
        assert len(down(shell, sx * x_in, y_lip)) > len(down(shell, sx * x_in, rd_cy))   # upper lip over the board edge, none between
        assert len(down(shell, sx * x_in, rd_cy - y_lip + rd_cy)) == len(down(shell, sx * x_in, rd_cy))  # none on the lower side ribs
        assert len(down(shell, sx * (P["rd_w"] / 2 + P["rd_slack"] + P["rd_rib_t"] - 0.1), y_lip + 2.5)) == 2  # slot: face only
    yh = rd_cy - P["rd_h"] / 2 - P["rd_slack"] + 0.4          # under the bottom lip, anywhere along it
    for x in (-9, 0, 9):
        assert len(down(shell, x, yh)) > len(down(shell, x, rd_cy))
    y_frame = OL_CY - P["ol_h"] / 2 - P["ol_slack"] - P["ol_rib_t"] / 2
    assert len(down(shell, 0, y_frame)) > 0 and max(h[2] for h in down(shell, 0, y_frame)) > OL_BOARD_Z


def test_oled_reverse_chamfer_relief(shell):
    yb = OL_CY + P["ol_glass_dy"] - (P["ol_glass_l"] / 2 + 0.35)
    top = max(h[2] for h in down(shell, 0, yb - 0.6))
    assert top < P["face_t"] - 0.05                                        # face thinned under the ribbon end
    assert np.isclose(max(h[2] for h in down(shell, 9, yb - 0.6)), P["face_t"], atol=0.01)   # untouched beside it


def test_oled_header_relief(shell):
    y = OL_CY + P["ol_glass_dy"] + P["ol_glass_l"] / 2 + 2
    assert np.isclose(max(h[2] for h in down(shell, 0, y)), P["face_t"] - P["ol_pin_rec"], atol=0.01)   # floor of the relief
    assert max(h[2] for h in down(shell, 0, y)) > 0.3                                                   # skin left on the front
    assert np.isclose(max(h[2] for h in down(shell, 9, y)), P["face_t"], atol=0.01)                      # untouched beside it
