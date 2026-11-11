"""Tests for the DIN-rail PSU mount: bounding box, volume window, feature counts.

Features are counted by vertical ray probes through the STL: a probe through a
hole or a slot meets nothing; through the plate, top and bottom; through a
hook lip over the plate, four faces.
"""

import re
from pathlib import Path

import numpy as np
import pytest
import trimesh
from shop.scad import build_scad, find_openscad
from shop.testing import ray_hits

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")


def params(path: Path) -> dict[str, float]:
    return {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*([-\d.]+)\s*;", path.read_text(), re.M)}


P = params(HERE / "model.scad")
L, W, T = P["plate_l"], P["plate_w"], P["plate_t"]
WALL_IN = P["rail_w"] / 2 + P["side_clr"]
LIP_TOP = T + P["flange_t"] + P["clr"] + P["lip_t"]


def build(tmp_path_factory, part: str) -> trimesh.Trimesh:
    d = tmp_path_factory.mktemp(part)
    src = d / "model.scad"
    src.write_text((HERE / "model.scad").read_text().replace('part = "print"', f'part = "{part}"', 1))
    return trimesh.load(build_scad(src, d, part, render=False)["stl"])


@pytest.fixture(scope="module")
def mesh(tmp_path_factory) -> trimesh.Trimesh:
    return build(tmp_path_factory, "assembled")


@pytest.fixture(scope="module")
def layout(tmp_path_factory) -> trimesh.Trimesh:
    return build(tmp_path_factory, "print")


def test_print_layout_is_base_plus_four_clips(layout):
    bodies = layout.split(only_watertight=False)
    assert len(bodies) == 5
    assert all(b.is_watertight for b in bodies)
    # four clips are separate from the plate and lie wholly beside it
    clips = [b for b in bodies if b.bounds[0][1] > W / 2]
    assert len(clips) == 4


def hits(mesh, x, y):
    return len(ray_hits(mesh, (x, y, 20), (0, 0, -1)))


def test_bounding_box(mesh):
    lo, hi = mesh.bounds
    assert np.allclose(lo, [-L / 2, -W / 2, 0], atol=0.05)
    assert np.allclose(hi, [L / 2, W / 2, LIP_TOP], atol=0.05)


def test_watertight(mesh):
    assert mesh.is_watertight


def test_volume_window(mesh):
    assert 33000 < mesh.volume < 36500, mesh.volume


def test_two_diagonal_holes(mesh):
    dx, dy = P["hole_dx"] / 2, P["hole_dy"] / 2
    assert hits(mesh, -dx, -dy) == 0 and hits(mesh, dx, dy) == 0
    assert P["hole_d"] <= 3.3  # the PSU's own holes take 3.3 mm at the very most
    # the other diagonal is solid: the PSU has only two holes
    assert hits(mesh, -dx, dy) == 2 and hits(mesh, dx, -dy) == 2


def test_latch_beams(mesh):
    y_in = WALL_IN - P["slot_in"] / 2
    y_beam = WALL_IN + P["wall_t"] / 2
    y_out = WALL_IN + P["wall_t"] + P["slot_out"] / 2
    for x in (-20, 20):  # beyond the hook, still on the beam
        assert hits(mesh, x, y_in) == 0
        assert hits(mesh, x, y_beam) == 2
        assert hits(mesh, x, y_out) == 0


def test_hook_lips(mesh):
    y_lip = WALL_IN - P["lip_len"] / 2  # under the lip, over the plate
    for x in (-8, 8):
        assert hits(mesh, x, -y_lip) == 4  # fixed hook: plate + lip
    for x in (-8, 8):
        assert hits(mesh, x, y_lip) == 2  # latch hook: lip only, slot beneath
    # clearance between plate top and lip underside is the flange plus clr
    zs = [p[2] for p in ray_hits(mesh, (8, -y_lip, 20), (0, 0, -1))]
    assert np.isclose(zs[1] - zs[2], P["flange_t"] + P["clr"], atol=0.01), zs
