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
DEPTH = P["floor_t"] + P["tape_t"] + P["mod_h"] + P["top_clear"] + P["buzzer_h"]
BOSS_X = P["in_w"] / 2 - P["boss_d"] / 2 + 0.5
BOSS_Y = P["in_l"] / 2 - P["boss_d"] / 2 + 0.5
CORNERS = [(sx * BOSS_X, sy * BOSS_Y) for sx in (-1, 1) for sy in (-1, 1)]


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
    assert np.allclose(box.bounds, [[-OUT_W / 2, -OUT_L / 2, 0], [OUT_W / 2, OUT_L / 2, DEPTH]], atol=0.05)
    assert 15_000 < box.volume < 25_000


def test_lid_bounds_volume(lid):
    assert lid.is_watertight
    assert np.allclose(lid.bounds[:, :2], [[-OUT_W / 2, -OUT_L / 2], [OUT_W / 2, OUT_L / 2]], atol=0.05)
    assert np.isclose(lid.bounds[1][2], P["lid_t"] + P["collar_h"], atol=0.05)
    assert 4_000 < lid.volume < 8_000


def test_module_and_buzzer_stack_inside():
    assert P["mod_w"] < 2 * BOSS_X - P["boss_d"]  # module passes between the bosses
    assert P["mod_l"] / 2 < P["mount_y"] - P["mount_d"]  # bulkhead screws clear of the module
    assert P["window_d"] < P["buzzer_d"]  # the lid stops the buzzer


def test_four_pilots_and_lid_holes_line_up(box, lid):
    for x, y in CORNERS:
        assert np.isclose(ray_hits(box, (x, y, DEPTH + 5), (0, 0, -1))[0][2], P["floor_t"], atol=0.05)  # blind pilot
        assert len(ray_hits(lid, (x, y, -1), (0, 0, 1))) == 0  # lid clearance hole through


def test_two_bulkhead_holes_through_floor(box):
    for s in (-1, 1):
        assert len(ray_hits(box, (0, s * P["mount_y"], -1), (0, 0, 1))) == 0


def test_cable_notch_open_at_rim(box):
    z = DEPTH - P["notch_d"] / 2
    assert len(ray_hits(box, (0, -OUT_L, z), (0, 1, 0))) == 2  # only the top wall, the bottom one is notched


def test_buzzer_window_through_lid(lid):
    assert len(ray_hits(lid, (0, 0, -1), (0, 0, 1))) == 0
