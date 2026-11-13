"""Tests for the DIN-rail PSU mount: bounding boxes, volume windows, feature counts.

Features are counted by vertical ray probes through the STL. The clip's volume
and bounding box are checked against the owner's DIN_Clip.stl (1884 mm^3,
-3.21..41.84 x -3.25..19.48 x 0..6) so a transcription slip in the outline shows.
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
RAIL_CX = (3.12 + 38.37) / 2


def build(tmp_path_factory, part: str) -> trimesh.Trimesh:
    d = tmp_path_factory.mktemp(part)
    src = d / "model.scad"
    src.write_text((HERE / "model.scad").read_text().replace('part = "print"', f'part = "{part}"', 1))
    return trimesh.load(build_scad(src, d, part, render=False)["stl"])


@pytest.fixture(scope="module")
def base(tmp_path_factory):
    return build(tmp_path_factory, "base")


@pytest.fixture(scope="module")
def clip(tmp_path_factory):
    return build(tmp_path_factory, "clip")


@pytest.fixture(scope="module")
def layout(tmp_path_factory):
    return build(tmp_path_factory, "print")


def first_z(mesh, x, y):
    h = ray_hits(mesh, (x, y, 50), (0, 0, -1))
    return h[0][2] if len(h) else None


def test_clip_matches_original(clip):
    assert clip.is_watertight
    assert np.allclose(clip.bounds, [[-3.21, -3.25, 0], [41.84, 19.48, P["clip_w"]]], atol=0.02)
    assert abs(clip.volume - 1884.0) < 5  # original DIN_Clip.stl, at its 6 mm width


def test_base_bounds_and_solid(base):
    assert base.is_watertight
    # the PSU's own footprint, no overhang; seats rise pad_t above the frame
    assert np.allclose(base.bounds, [[-L / 2, -W / 2, 0], [L / 2, W / 2, T + P["pad_t"]]], atol=0.02)
    assert T <= 2.5
    assert 4000 < base.volume < 0.65 * L * W * T  # lightened: the centre is open


def test_centre_is_open(base):
    assert first_z(base, 0, 0) is None
    assert first_z(base, 0, W / 2 - P["rim_w"] / 2) is not None  # the rim


def test_two_diagonal_screw_holes(base):
    dx, dy = P["hole_dx"] / 2, P["hole_dy"] / 2
    assert first_z(base, -dx, -dy) is None and first_z(base, dx, dy) is None
    # the other diagonal is solid: the PSU has only two holes
    assert np.isclose(first_z(base, -dx, dy), T) and np.isclose(first_z(base, dx, -dy), T)
    assert 3.3 <= P["hole_d"] <= 3.6  # M3, easy slip fit


def test_four_peg_holes_through_seats(base):
    assert T + P["pad_t"] > P["peg_len"]  # the pegs stop short of the PSU face
    assert P["peg_hole_d"] > P["peg_d"]  # clearance for print artefacts
    for sx in (-1, 1):
        for px in (5.9, 35.9):
            assert first_z(base, sx * P["clip_x"], px - RAIL_CX) is None
        # seat top beside the holes
        assert np.isclose(first_z(base, sx * P["clip_x"], 0), T + P["pad_t"], atol=0.02)


def test_print_layout_is_base_plus_two_clips(layout):
    bodies = layout.split(only_watertight=False)
    assert len(bodies) == 3 and all(b.is_watertight for b in bodies)
    assert sum(b.bounds[0][1] > W / 2 for b in bodies) == 2  # both clips beside the plate
