"""Tests for the desk presence sensor box: bounding box, volume window, feature counts."""

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
TM_CY = P["tm_clear"] + P["tm_w"] / 2
OL_CY = P["tm_w"] + 2 * P["tm_clear"] + P["gap"] + P["ol_h"] / 2
RD_CY = OL_CY + P["ol_h"] / 2 + P["gap"] + P["rd_rib_t"] + P["rd_slack"] + P["rd_h"] / 2
D1_CY = RD_CY + P["rd_h"] / 2 + P["rd_slack"] + P["rd_rib_t"] + P["gap"] + P["d1_slack"] + P["d1_l"] / 2
IN_H = D1_CY + P["d1_l"] / 2 + P["d1_usb_over"]
SHELL_H = P["d1_front_z"] + P["d1_t"] + P["jumper_h"] + P["bend"]
TM_BOARD_Z = P["tm_recess"] + P["tm_disp_h"]
OL_BOARD_Z = P["face_t"] + P["ol_gap"] + P["ol_glass_h"]
BOUNDS = [[-P["box_w"] / 2, -P["wall"]], [P["box_w"] / 2, IN_H + P["wall"]]]


def build(tmp_path_factory, name, view):
    d = tmp_path_factory.mktemp(view)
    (d / "model.scad").write_text((HERE / "model.scad").read_text())
    return trimesh.load(build_scad(d / "model.scad", d, name, render=False)["stl"]) if view == "shell" else _cover(d, name)


def _cover(d, name):
    (d / "part-cover.scad").write_text((HERE / "part-cover.scad").read_text())
    return trimesh.load(build_scad(d / "part-cover.scad", d, name, render=False)["stl"])


@pytest.fixture(scope="module")
def shell(tmp_path_factory):
    return build(tmp_path_factory, "shell", "shell")


@pytest.fixture(scope="module")
def cover(tmp_path_factory):
    return build(tmp_path_factory, "cover", "cover")


def down(mesh, x, y):
    return ray_hits(mesh, (x, y, 80), (0, 0, -1))


def test_shell_45_wide_bounds_volume(shell):
    assert shell.is_watertight
    (x0, y0), (x1, y1) = BOUNDS
    assert np.allclose(shell.bounds, [[x0, y0, 0], [x1, y1, SHELL_H]], atol=0.05)
    assert P["box_w"] == 45
    assert 18_000 < shell.volume < 32_000


def test_tm1637_fits_across_and_window_is_through(shell):
    assert P["tm_l"] + 2 * P["tm_clear"] <= IN_W + 1e-9
    cx, cy = P["tm_disp_dx"], TM_CY + P["tm_disp_dy"]
    assert len(down(shell, cx, cy)) == 0
    assert len(down(shell, cx + P["tm_disp_l"] / 2 + 1.0, cy)) > 0


def test_oled_window_through(shell):
    assert len(down(shell, 0, OL_CY + P["ol_win_dy"])) == 0
    assert len(down(shell, 0, OL_CY + P["ol_win_dy"] + P["ol_win_h"] / 2 + 1)) > 0


def test_radar_looks_through_solid_face(shell):
    hits = down(shell, 0, RD_CY)
    assert len(hits) > 0 and np.isclose(hits[0][2], P["face_t"], atol=0.02)


def test_board_posts_blind_pilots_at_board_height(shell):
    for sx in (-1, 1):
        for sy in (-1, 1):
            for x, y, d, z in ((sx * P["tm_hole_dx"] / 2, TM_CY + sy * P["tm_hole_dy"] / 2, P["tm_pilot_d"], TM_BOARD_Z),
                               (sx * P["ol_hole_dx"] / 2, OL_CY + sy * P["ol_hole_dy"] / 2, P["ol_pilot_d"], OL_BOARD_Z)):
                assert np.isclose(down(shell, x, y)[0][2], P["face_t"] - 1, atol=0.02)  # blind, never through the face
                assert np.isclose(down(shell, x + d / 2 + 0.3, y)[0][2], z, atol=0.02)


def test_usb_hole_in_top_wall(shell):
    usb_z = P["d1_front_z"] - 1.4
    top_hit = lambda x, z: ray_hits(shell, (x, IN_H + 20, z), (0, -1, 0))
    assert top_hit(0, usb_z)[0][1] < IN_H  # through the top wall
    assert np.isclose(top_hit(P["usb_w"] / 2 + 2, usb_z)[0][1], IN_H + P["wall"], atol=0.05)
    assert usb_z - P["usb_h"] / 2 > P["face_t"]  # plug clears the face


def test_four_insert_posts(shell):
    post_x = IN_W / 2 - P["post_d"] / 2 + 0.5
    for sx in (-1, 1):
        for y in (OL_CY, D1_CY - P["d1_l"] / 2 + 4):
            assert np.isclose(down(shell, sx * post_x, y)[0][2], SHELL_H - P["insert_depth"], atol=0.05)
            assert np.isclose(down(shell, sx * post_x + P["insert_d"] / 2 + 0.4, y)[0][2], SHELL_H, atol=0.05)


def test_jumper_depth():
    assert SHELL_H - (P["d1_front_z"] + P["d1_t"] + P["jumper_h"]) >= 4


def test_cover_flat_back_and_countersinks(cover):
    assert cover.is_watertight
    (x0, y0), (x1, y1) = BOUNDS
    assert np.allclose(cover.bounds, [[x0, y0, 0], [x1, y1, P["cover_t"] + P["lip_h"]]], atol=0.05)
    assert len(ray_hits(cover, (0, IN_H / 2, -10), (0, 0, 1))) > 0  # solid middle: the tape face
    post_x = IN_W / 2 - P["post_d"] / 2 + 0.5
    assert len(down(cover, post_x, OL_CY)) == 0  # screw hole through
