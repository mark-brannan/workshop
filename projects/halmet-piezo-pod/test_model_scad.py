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
EAR_A = np.arcsin((P["in_w"] / 2 - P["ear_tip_gap"] - P["ear_r"]) / (P["ear_span"] / 2 - P["ear_r"]))
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
        assert abs(x) - COL_R > P["mod_w"] / 2 + 1  # bosses clear the module's sides
    c = P["ear_span"] / 2 - P["ear_r"]
    assert c * np.sin(EAR_A) + P["ear_r"] <= P["in_w"] / 2 - 1  # ear tips clear the long walls
    assert c * np.cos(EAR_A) + P["ear_r"] < P["in_l"] / 2 - 1
    assert P["ledge_reach"] - (P["in_w"] / 2 - P["buzzer_d"] / 2) >= 1.5  # flange edge overlaps the ledges
    assert LEDGE_Z + P["ear_t"] + 2.5 < DEPTH  # M3 heads inside, under the lid
    assert 2 <= P["proud"] <= 4  # ~3 of the buzzer's housing shows above the lid (owner)
    assert P["hole_pitch"] / 2 + P["hole_d"] / 2 < P["mod_w"] / 2  # screw holes inside the board's edges
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
        assert np.isclose(hit, SEAT_Z - P["m25_depth"], atol=0.05)  # blind, deep enough for a longer M2.5


def test_insert_columns_at_ear_holes(box):
    for x, y in EAR_XY:
        hits = ray_hits(box, (x, y, DEPTH + 5), (0, 0, -1))
        assert np.isclose(hits[0][2], LEDGE_Z - INSERT_DEPTH, atol=0.05)  # blind insert hole in the column top
        rim = ray_hits(box, (x + COL_R - 0.5, y, DEPTH + 5), (0, 0, -1))[0][2]
        assert np.isclose(rim, LEDGE_Z, atol=0.05)
        inner = x - np.sign(x) * (COL_R - 0.5)  # the boss edge toward the module
        hits = ray_hits(box, (inner, y, DEPTH + 5), (0, 0, -1))
        assert np.isclose(hits[0][2], LEDGE_Z, atol=0.05)
        assert hits[1][2] > LEDGE_Z - INSERT_DEPTH - P["insert_floor"] - 0.6  # boss hangs off the wall
        assert np.isclose(hits[2][2], P["floor_t"], atol=0.05)  # floor clear under it, room for ferrules


def test_seat_ledges_mid_wall(box):
    for s in (-1, 1):
        assert np.isclose(ray_hits(box, (s * (P["in_w"] / 2 - 1), 0, DEPTH + 5), (0, 0, -1))[0][2], LEDGE_Z, atol=0.05)
        assert ray_hits(box, (s * (P["in_w"] / 2 - P["ledge_reach"] - 0.5), 0, DEPTH + 5), (0, 0, -1))[0][2] < LEDGE_Z - 5


TIES = [(-12.5, -22.5), (-12.9, -9)]


def test_tie_bridges(box):
    zt = P["floor_t"] + P["tie_gap"] / 2
    for x, y in TIES:
        hits = ray_hits(box, (x, y, DEPTH + 5), (0, 0, -1))[:3]
        assert np.isclose(hits[0][2], P["floor_t"] + P["tie_gap"] + P["tie_deck_t"], atol=0.05)
        assert np.isclose(hits[1][2], P["floor_t"] + P["tie_gap"], atol=0.05)
        assert np.isclose(hits[2][2], P["floor_t"], atol=0.05)
        for dy in (-P["tie_span"] / 2 + 0.3, P["tie_span"] / 2 - 0.3):  # tunnel open across X
            through = ray_hits(box, (x - P["tie_deck_w"] / 2 - 0.5, y + dy, zt), (1, 0, 0))
            assert through[0][0] > x + P["tie_deck_w"] / 2 + 0.5


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


FINGER_Y = P["in_l"] / 2 - P["in_r"] - P["finger_end"] - P["finger_w"] / 2


def test_finger_strain():
    # cantilever: strain = 1.5 t y / L^2, y = how far the ridge must push the finger in
    y = P["snap_d"] - P["skirt_gap"]
    assert 1.5 * P["skirt_t"] * y / P["snap_z"] ** 2 < 0.035  # PETG, repeated snaps
    assert P["snap_d"] + 0.1 < P["groove_d"] + P["skirt_gap"]  # finger springs fully back in the pocket
    assert P["groove_d"] <= P["wall"] - 1


def test_four_fingers_with_ridges(lid):
    x = P["in_w"] / 2 - P["skirt_gap"] + P["snap_d"] / 2
    z = P["lid_t"] + P["snap_z"]
    for sx in (-1, 1):
        hits = ray_hits(lid, (sx * x, -50, z), (0, 1, 0))
        assert len(hits) == 4  # two ridges along each long side
        for sy in (-1, 1):  # and nothing between them
            assert len(ray_hits(lid, (sx * x, sy * FINGER_Y, z), (0, 0, 1))) % 2 == 1


def test_four_pockets_line_up_with_ridges(box):
    z = DEPTH - P["snap_z"]
    for sx in (-1, 1):
        for sy in (-1, 1):
            hit = ray_hits(box, (0, sy * FINGER_Y, z), (sx, 0, 0))[0]
            assert np.isclose(abs(hit[0]), P["in_w"] / 2 + P["groove_d"], atol=0.05)
        plain = ray_hits(box, (0, 0, z), (sx, 0, 0))[0]
        assert np.isclose(abs(plain[0]), P["in_w"] / 2, atol=0.05)  # no groove mid-wall


def test_body_hole_through_lid(lid):
    assert len(ray_hits(lid, (0, 0, -1), (0, 0, 1))) == 0
