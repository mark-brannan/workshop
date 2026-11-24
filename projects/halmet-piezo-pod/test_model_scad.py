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
DEPTH = SEAT_Z + P["mod_h"] + P["top_clear"] + P["ear_t"]
LEDGE_Z = DEPTH - P["ear_t"]
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
    assert P["ledge_front"] > P["mod_l"] / 2  # ledges past the module's ends
    assert P["ledge_front"] < P["ear_pitch"] / 2 - P["peg_d"] / 2  # peg on the ledge
    assert P["ear_span"] < P["in_l"]
    assert P["in_w"] - P["buzzer_d"] >= 6  # room for the leads leaving the buzzer's side
    assert P["body_hole_d"] > P["buzzer_d"]
    assert P["peg_h"] < P["ear_t"]  # lid clamps the ears, not the pegs
    assert abs(P["notch_x"]) - P["notch_w"] / 2 > P["ledge_w"] / 2  # notch clear of the bottom ledge


def test_seat_pocket_and_pilots(box):
    pocket_y = -P["mod_l"] / 2 + P["pocket_r"]
    assert np.isclose(ray_hits(box, (0, pocket_y, DEPTH + 5), (0, 0, -1))[0][2], P["floor_t"], atol=0.05)
    assert np.isclose(ray_hits(box, (0, 0, DEPTH + 5), (0, 0, -1))[0][2], SEAT_Z, atol=0.05)
    for s in (-1, 1):
        hit = ray_hits(box, (s * P["hole_pitch"] / 2, P["mod_l"] / 2 - P["hole_e"], DEPTH + 5), (0, 0, -1))[0][2]
        assert np.isclose(hit, SEAT_Z - P["m2_depth"], atol=0.05)  # blind, deep enough for a longer M2


def test_pegs_at_ear_pitch(box):
    for s in (-1, 1):
        top = ray_hits(box, (0, s * P["ear_pitch"] / 2, DEPTH + 5), (0, 0, -1))[0][2]
        assert np.isclose(top, LEDGE_Z + P["peg_h"], atol=0.05)


def test_two_tab_holes_through(box):
    for s in (-1, 1):
        assert len(ray_hits(box, (0, s * TAB_Y, -1), (0, 0, 1))) == 0


def test_cable_notch_open_at_rim(box):
    z = DEPTH - P["notch_d"] / 2
    assert len(ray_hits(box, (P["notch_x"], -OUT_L, z), (0, 1, 0))) == 2  # only the top wall


def test_snap_ridge_engages_groove(box, lid):
    assert P["snap_d"] < P["groove_d"] < P["wall"] - 1
    x = P["in_w"] / 2 - P["skirt_gap"] + P["snap_d"] / 2
    assert len(ray_hits(lid, (x, -50, P["lid_t"] + P["snap_z"]), (0, 1, 0))) == 2  # ridge on the skirt
    assert len(ray_hits(box, (P["in_w"] / 2 + P["groove_d"] / 2, -50, DEPTH - P["snap_z"]), (0, 1, 0))) == 4  # groove breaks the wall


def test_body_hole_through_lid(lid):
    assert len(ray_hits(lid, (0, 0, -1), (0, 0, 1))) == 0
