"""Tests for the one-piece DIN-rail PSU mount: bounding box, volume window, feature counts.

Features are counted by vertical ray probes through the STL. The clip profile comes from
Printables 420009 (4488 mm^3, 60 x 18 x 7.5), so the clips' volume is checked against that.
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
L, W, T, EXT = P["plate_l"], P["plate_w"], P["plate_t"], P["ext"]
TIE_Y = -W / 2 - EXT / 2
TIE_XS = [-18, 0, 18]



@pytest.fixture(scope="module")
def mount(tmp_path_factory):
    d = tmp_path_factory.mktemp("mount")
    return trimesh.load(build_scad(HERE / "model.scad", d, "mount", render=False)["stl"])


def first_z(mesh, x, y):
    h = ray_hits(mesh, (x, y, 50), (0, 0, -1))
    return h[0][2] if len(h) else None


CLIP_TOP = 7.5  # the clip stands on the PSU face and is 7.5 tall


def test_one_watertight_piece(mount):
    assert mount.is_watertight
    assert len(mount.split(only_watertight=False)) == 1


def test_bounds(mount):
    # the PSU's own 58 x 85 footprint plus the 15 mm tie extension below it; the clips stand 7.5 mm off the PSU face
    assert (L, W, EXT) == (58, 85, 15)
    assert np.allclose(mount.bounds, [[-L / 2, -W / 2 - EXT, 0], [L / 2, W / 2, CLIP_TOP]], atol=0.05)
    assert T <= 2.5


def test_volume_is_frame_plus_two_clips(mount):
    clips = 2 * 4488.0
    assert clips * 0.9 < mount.volume < clips + 0.8 * L * (W + EXT) * T


def test_centre_is_open(mount):
    assert first_z(mount, 0, 0) is None
    assert first_z(mount, 0, W / 2 - P["rim_w"] / 2) is not None  # the rim


def test_two_diagonal_screw_holes(mount):
    dx, dy = P["hole_dx"] / 2, P["hole_dy"] / 2
    assert first_z(mount, -dx, -dy) is None and first_z(mount, dx, dy) is None
    # the other diagonal is solid: the PSU has only two holes
    assert np.isclose(first_z(mount, -dx, dy), T) and np.isclose(first_z(mount, dx, -dy), T)
    assert 3.3 <= P["hole_d"] <= 3.6  # M3, easy slip fit


def test_clips_stand_on_the_frame_with_filled_screw_holes(mount):
    for sx in (-1, 1):
        x = sx * P["clip_x"]
        assert first_z(mount, x, 5) > T  # the shelf under the rail flange stands above the frame
        # the clip's two heat-insert holes are filled: its hook (clip x = 5) and shelf (clip x = 56) are solid
        for y in (5 - 27.05, 56 - 27.05):
            assert first_z(mount, x, y) is not None


def test_zip_tie_slot_pairs_with_underside_chamfers(mount):
    gap, tw, tt, c = P["tie_gap"], P["tie_w"], P["tie_t"], P["tie_c"]
    assert tw >= 5.2  # a standard 4.8 mm tie
    for x in TIE_XS:
        for s in (-1, 1):
            y = TIE_Y + s * gap / 2
            assert first_z(mount, x, y) is None  # slot through the plate
            # the web between the pair stands, so the tie loops under it
            assert np.isclose(first_z(mount, x, TIE_Y), T)
            # outer-edge chamfer: just outside the slot the plate is cut away at the underside, still solid above
            assert first_z(mount, x, y + s * (tt / 2 + c * 0.25)) is not None
            h = ray_hits(mount, (x, y + s * (tt / 2 + c * 0.25), -5), (0, 0, 1))
            assert h[0][2] > 0.3  # underside cut, not the flat z = 0 face
