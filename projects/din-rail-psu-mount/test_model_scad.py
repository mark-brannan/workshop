"""Tests for the one-piece DIN-rail PSU mount: bounding box, volume window, feature counts.

Features are counted by vertical ray probes through the STL. The clip profile comes from
Thingiverse 3640994 (DINrail_Clip.stl, 6022 mm^3 over 12.3 mm, 60 x 16 mm section), so the
clip's volume is checked against that at the model's clip_len.
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



@pytest.fixture(scope="module")
def mount(tmp_path_factory):
    d = tmp_path_factory.mktemp("mount")
    return trimesh.load(build_scad(HERE / "model.scad", d, "mount", render=False)["stl"])


def first_z(mesh, x, y):
    h = ray_hits(mesh, (x, y, 50), (0, 0, -1))
    return h[0][2] if len(h) else None


CLIP_TOP = T + 16.012  # frame plus the profile's 10 + 6.012 depth


def test_one_watertight_piece(mount):
    assert mount.is_watertight
    assert len(mount.split(only_watertight=False)) == 1


def test_bounds(mount):
    # the PSU's own footprint, no overhang; the clips stand 16 mm above the frame
    assert np.allclose(mount.bounds, [[-L / 2, -W / 2, 0], [L / 2, W / 2, CLIP_TOP]], atol=0.05)
    assert T <= 2.5


def test_volume_is_frame_plus_two_clips(mount):
    clips = 2 * 6022.0 / 12.3 * P["clip_len"]
    assert clips < mount.volume < clips + 0.75 * L * W * T


def test_centre_is_open(mount):
    assert first_z(mount, 0, 0) is None
    assert first_z(mount, 0, W / 2 - P["rim_w"] / 2) is not None  # the rim


def test_two_diagonal_screw_holes(mount):
    dx, dy = P["hole_dx"] / 2, P["hole_dy"] / 2
    assert first_z(mount, -dx, -dy) is None and first_z(mount, dx, dy) is None
    # the other diagonal is solid: the PSU has only two holes
    assert np.isclose(first_z(mount, -dx, dy), T) and np.isclose(first_z(mount, dx, -dy), T)
    assert 3.3 <= P["hole_d"] <= 3.6  # M3, easy slip fit


def test_clips_stand_on_the_frame_and_clear_the_rail(mount):
    for sx in (-1, 1):
        x = sx * P["clip_x"]
        assert first_z(mount, x, 25) > T + 5  # the fixed hook stands well clear of the frame
        # the rail slot is open to the rail side at its centre, but for the profile's back bar
        assert first_z(mount, x, 0.5) < CLIP_TOP - 5
