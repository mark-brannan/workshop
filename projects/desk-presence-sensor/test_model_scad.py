"""Tests for the desk presence sensor: front plate and back tray. Bounding box, volume, features."""

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
PW = IN_W - 2 * P["plate_clr"]
TM_CY = P["tm_clear"] + P["tm_w"] / 2
OL_CY = P["tm_w"] + 2 * P["tm_clear"] + P["gap"] + P["ol_h"] / 2
D1_CY = OL_CY + P["ol_h"] / 2 + P["d1_slack"] + P["d1_l"] / 2   # D1 stands behind the displays, USB up
IN_H = D1_CY + P["d1_l"] / 2 + P["d1_slack"] + P["d1_rib_t"] + 0.3
SHELL_H = P["plate_z0"] + P["d1_front_z"] + P["d1_t"] + P["jumper_h"] + P["bend"]
BOX_D = SHELL_H + P["back_t"]
TM_BOARD_Z = P["tm_recess"] + P["tm_disp_h"]
OL_BOARD_Z = P["face_t"] + P["ol_gap"] + P["ol_glass_h"]
USB_Z = P["plate_z0"] + P["d1_front_z"] - 1.4
CY0 = IN_H / 2


def build(tmp_path_factory, scad):
    d = tmp_path_factory.mktemp(scad)
    for f in ("model.scad", scad):
        (d / f).write_text((HERE / f).read_text())
    return trimesh.load(build_scad(d / scad, d, scad, render=False)["stl"])


@pytest.fixture(scope="module")
def plate(tmp_path_factory):
    return build(tmp_path_factory, "model.scad")


@pytest.fixture(scope="module")
def tray(tmp_path_factory):
    return build(tmp_path_factory, "part-tray.scad")


def down(mesh, x, y):
    return ray_hits(mesh, (x, y, 80), (0, 0, -1))


def test_plate_bounds_volume(plate):
    assert plate.is_watertight
    assert np.allclose(plate.bounds[:, 2], [0, P["d1_front_z"] + P["d1_t"] + 1], atol=0.05)
    assert np.isclose(plate.bounds[1][0] - plate.bounds[0][0], PW, atol=0.05)
    assert 4_000 < plate.volume < 12_000


def test_tm1637_fits_across_and_window_is_through(plate):
    assert P["tm_l"] + 2 * P["tm_clear"] <= IN_W + 1e-9
    cx, cy = P["tm_disp_dx"], TM_CY + P["tm_disp_dy"]
    assert len(down(plate, cx, cy)) == 0
    assert len(down(plate, cx + P["tm_disp_l"] / 2 + 1.0, cy)) > 0


def test_oled_window_through(plate):
    assert len(down(plate, 0, OL_CY + P["ol_win_dy"])) == 0
    assert len(down(plate, 0, OL_CY + P["ol_win_dy"] + P["ol_win_h"] / 2 + 1)) > 0


def test_radar_looks_through_solid_face(plate):
    rd_cy = OL_CY + P["ol_h"] / 2 + P["gap"] + P["rd_rib_t"] + P["rd_slack"] + P["rd_h"] / 2
    hits = down(plate, 0, rd_cy)
    assert len(hits) > 0 and np.isclose(hits[0][2], P["face_t"], atol=0.02)


def test_board_posts_blind_pilots_at_board_height(plate):
    for sx in (-1, 1):
        for sy in (-1, 1):
            for x, y, d, z in ((sx * P["tm_hole_dx"] / 2, TM_CY + sy * P["tm_hole_dy"] / 2, P["tm_pilot_d"], TM_BOARD_Z),
                               (sx * P["ol_hole_dx"] / 2, OL_CY + sy * P["ol_hole_dy"] / 2, P["ol_pilot_d"], OL_BOARD_Z)):
                assert np.isclose(down(plate, x, y)[0][2], P["face_t"] - 1, atol=0.02)  # blind, never through the face
                assert np.isclose(down(plate, x + d / 2 + 0.3, y)[0][2], z, atol=0.02)


def test_d1_pillars_carry_its_corners(plate):
    x = P["d1_w"] / 2 - 0.5
    for sx in (-1, 1):
        for y in (D1_CY - P["d1_l"] / 2 + 1.5, D1_CY + P["d1_l"] / 2 - 2):
            assert np.isclose(down(plate, sx * x, y)[0][2], P["d1_front_z"], atol=0.05)
    assert D1_CY - P["d1_l"] / 2 >= OL_CY + P["ol_h"] / 2  # D1 starts at the OLED header edge


def test_tray_bounds_flat_tape_face(tray):
    assert tray.is_watertight
    assert np.allclose(tray.bounds[:, 2], [0, BOX_D], atol=0.05)
    assert np.isclose(tray.bounds[1][0] - tray.bounds[0][0], P["box_w"], atol=0.05)
    assert 8_000 < tray.volume < 30_000
    assert len(ray_hits(tray, (0, CY0, -10), (0, 0, 1))) > 0  # solid middle: the tape face on the bed
    assert np.isclose(ray_hits(tray, (0, CY0, -10), (0, 0, 1))[0][2], 0, atol=0.05)


def test_usb_hole_in_top_wall(tray):
    z = BOX_D - USB_Z   # printed tape face down
    top_hit = lambda x, zz: ray_hits(tray, (x, IN_H + 20 + P["wall"], zz), (0, -1, 0))
    assert top_hit(0, z)[0][1] < IN_H
    assert np.isclose(top_hit(P["usb_w"] / 2 + 2, z)[0][1], IN_H + P["wall"] - 0 + 0, atol=P["wall"] + 0.1)
    assert USB_Z - P["usb_h"] / 2 > P["plate_z0"] + P["face_t"]  # plug clears the plate


def test_snap_leaves_and_stop_ribs(tray):
    z = BOX_D - 5   # inside a leaf
    for y in (TM_CY, OL_CY):
        side = lambda yy: ray_hits(tray, (IN_W / 2 + 20, yy, z), (-1, 0, 0))
        assert np.isclose(side(y)[0][0], IN_W / 2 + P["wall"], atol=0.1)           # the leaf itself
        assert len(side(y + P["leaf_w"] / 2 + P["slit"] / 2)) == 0         # the slits on both walls let the ray clean through
    # the stop rib narrows the opening just behind where the plate's back face sits
    zb = BOX_D - (P["plate_z0"] + P["face_t"] + 0.2)
    rd_cy = OL_CY + P["ol_h"] / 2 + P["gap"] + P["rd_rib_t"] + P["rd_slack"] + P["rd_h"] / 2
    assert np.isclose(ray_hits(tray, (IN_W / 2 + 20, rd_cy, zb), (-1, 0, 0))[0][0], IN_W / 2 + P["wall"], atol=0.1)
    assert np.isclose(ray_hits(tray, (0, rd_cy, zb), (1, 0, 0))[0][0], IN_W / 2 - P["rib"] * 0.8, atol=0.4)


def test_plate_fits_the_tray_mouth():
    assert PW < IN_W and (IN_W - PW) / 2 > 0.2
    assert SHELL_H - (P["plate_z0"] + P["d1_front_z"] + P["d1_t"] + P["jumper_h"]) >= 4  # jumper bend room
