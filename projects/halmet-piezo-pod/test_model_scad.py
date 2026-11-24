"""Tests for the HALMET piezo pod box and lid: bounding box, volume window, feature counts."""

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
OUT_W = P["in_w"] + 2 * P["wall"]
OUT_L = P["in_l"] + 2 * P["wall"]
SEAT_Z = P["floor_t"] + P["plinth_h"]
INSERT_DEPTH = P["insert_l"] + 0.8
COL_R = P["insert_hole_d"] / 2 + P["insert_wall"]
EAR_A = np.arcsin((P["mod_w"] / 2 + P["fit"] + P["col_gap"] + COL_R) / (P["ear_pitch"] / 2))
EAR_XY = [(s * -np.sin(EAR_A) * P["ear_pitch"] / 2, s * np.cos(EAR_A) * P["ear_pitch"] / 2) for s in (-1, 1)]
LEDGE_Z = SEAT_Z + P["mod_h"] + P["buzz_clear"]
DEPTH = LEDGE_Z + P["buzzer_h"] - P["proud"] - P["lid_t"]
TAB_Y = OUT_L / 2 + P["tab_reach"]
def build(tmp_path_factory, src, name):
    d = tmp_path_factory.mktemp(name)
    for f in ("model.scad", "part-lid.scad"):
        (d / f).write_text((HERE / f).read_text())
    return trimesh.load(build_scad(d / src, d, name, render=False)["stl"])


@pytest.fixture(scope="module")
def box(tmp_path_factory):
    return build(tmp_path_factory, "model.scad", "box")


@pytest.fixture(scope="module")
def lid(tmp_path_factory):
    return build(tmp_path_factory, "part-lid.scad", "lid")


def test_box_bounds_volume(box):
    assert box.is_watertight
    assert np.allclose(box.bounds, [[-OUT_W / 2, -TAB_Y - P["tab_r"], 0], [OUT_W / 2, TAB_Y + P["tab_r"], DEPTH]], atol=0.05)
    assert 14_000 < box.volume < 28_000


def test_lid_bounds_volume(lid):
    assert lid.is_watertight
    assert np.allclose(lid.bounds[:, :2], [[-OUT_W / 2, -OUT_L / 2], [OUT_W / 2, OUT_L / 2]], atol=0.05)
    assert np.isclose(lid.bounds[1][2], P["lid_t"] + P["skirt_h"], atol=0.05)
    assert 2_500 < lid.volume < 7_000


def test_stack_fits():
    assert P["plinth_h"] > P["pin_out"]  # pins clear of the pocket floor
    for x, y in EAR_XY:
        assert abs(x) - COL_R > P["mod_w"] / 2 + P["fit"]  # columns clear the module's sides
    tip = P["ear_span"] / 2 * np.array([np.sin(EAR_A), np.cos(EAR_A)]) + 3.5 * np.array([np.cos(EAR_A), np.sin(EAR_A)])
    assert tip[0] < P["in_w"] / 2 and tip[1] < P["in_l"] / 2  # ear tips clear the walls
    assert LEDGE_Z + P["ear_t"] + 2.5 < DEPTH  # M3 heads inside, under the lid
    assert 0 <= P["proud"] < 2  # buzzer top flush or just proud of the lid
    assert P["ear_span"] < P["in_l"]
    assert P["in_w"] - P["buzzer_d"] >= 6  # room for the leads leaving the buzzer's side
    assert P["body_hole_d"] > P["buzzer_d"]
    assert abs(P["hole_x"]) - P["hole_w"] / 2 > P["tab_base"] - 0.5  # ...and of the tab


def test_seat_pocket_and_pilots(box):
    pocket_y = -P["mod_l"] / 2 + P["pocket_gap"] + P["pocket_l"] / 2
    hole_e = P["hole_gap"] + P["hole_d"] / 2
    assert np.isclose(ray_hits(box, (0, pocket_y, DEPTH + 5), (0, 0, -1))[0][2], P["floor_t"], atol=0.05)
    assert np.isclose(ray_hits(box, (0, 0, DEPTH + 5), (0, 0, -1))[0][2], SEAT_Z, atol=0.05)
    for s in (-1, 1):
        hit = ray_hits(box, (s * P["hole_pitch"] / 2, P["mod_l"] / 2 - hole_e, DEPTH + 5), (0, 0, -1))[0][2]
        assert np.isclose(hit, SEAT_Z - P["m2_depth"], atol=0.05)  # blind, deep enough for a longer M2


def test_insert_columns_at_ear_holes(box):
    for x, y in EAR_XY:
        hits = ray_hits(box, (x, y, DEPTH + 5), (0, 0, -1))
        assert np.isclose(hits[0][2], LEDGE_Z - INSERT_DEPTH, atol=0.05)  # blind insert hole in the column top
        rim = ray_hits(box, (x + COL_R - 0.5, y, DEPTH + 5), (0, 0, -1))[0][2]
        assert np.isclose(rim, LEDGE_Z, atol=0.05)


def test_lid_has_only_the_body_hole(lid):
    for x, y in EAR_XY:
        assert len(ray_hits(lid, (x, y, -1), (0, 0, 1))) == 2  # no screw holes: the buzzer screws are inside


def test_two_tab_holes_through(box):
    for s in (-1, 1):
        assert len(ray_hits(box, (0, s * TAB_Y, -1), (0, 0, 1))) == 0


def test_mousehole_at_floor_terminal_end(box):
    z = P["floor_t"] + 1
    hits = ray_hits(box, (P["hole_x"], -OUT_L, z), (0, 1, 0))
    assert hits[0][1] > -P["in_l"] / 2 + 1  # passes the terminal-end wall at its foot
    above = P["floor_t"] + P["hole_side"] + P["hole_w"] / 2 + 0.5
    assert ray_hits(box, (P["hole_x"], -OUT_L, above), (0, 1, 0))[0][1] < -P["in_l"] / 2  # wall above the roof


def test_snap_ridge_engages_groove(box, lid):
    assert P["snap_d"] < P["groove_d"] < P["wall"] - 1
    x = P["in_w"] / 2 - P["skirt_gap"] + P["snap_d"] / 2
    assert len(ray_hits(lid, (x, -50, P["lid_t"] + P["snap_z"]), (0, 1, 0))) == 2  # ridge on the skirt
    assert len(ray_hits(box, (P["in_w"] / 2 + P["groove_d"] / 2, -50, DEPTH - P["snap_z"]), (0, 1, 0))) == 4  # groove breaks the wall


def test_body_hole_through_lid(lid):
    assert len(ray_hits(lid, (0, 0, -1), (0, 0, 1))) == 0
