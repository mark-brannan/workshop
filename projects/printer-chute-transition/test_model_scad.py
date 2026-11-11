"""Chute transition: bounding box, volume window, unchanged cover, ball only below the square."""

import re
from pathlib import Path

import numpy as np
import pytest
import trimesh
from shop.scad import build_scad, find_openscad
from shop.testing import ray_hits

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")
Z_OPEN = 32.0  # installed frame: ball_h 30 + flare_h 2 + tube_h 0, where the cover's open end sits
TOP = 156.65   # the part is printed ear down; the fixture flips it back to the installed frame
CONE = 11.0    # the inner funnel inside the cover's last run


@pytest.fixture(scope="module")
def part(tmp_path_factory):
    d = tmp_path_factory.mktemp("chute")
    src = d / "model.scad"
    src.write_text((HERE / "model.scad").read_text())
    m = trimesh.load(build_scad(src, d, "part", render=False)["stl"])
    assert np.allclose(m.bounds[0], [-5.7, 21.1, 0], atol=0.1)  # printed ear down: ear face on the bed
    m.vertices = np.c_[m.vertices[:, 0], -m.vertices[:, 1], TOP - m.vertices[:, 2]]
    return m


@pytest.fixture(scope="module")
def cover():
    o = trimesh.load(HERE / "ref" / "chute-cover.stl", process=False)
    o.vertices = np.c_[o.vertices[:, 0], -o.vertices[:, 2], o.vertices[:, 1] + Z_OPEN + 50.6]
    return o


def test_bounds_volume_watertight(part):
    assert part.is_watertight
    assert np.allclose(part.bounds, [[-5.7, -80.9, 0], [69.11, -21.1, TOP]], atol=0.1)
    assert 44000 < part.volume < 50000  # cover 32334 + tube, flare and ball shells


def test_cover_unchanged(part, cover):
    # vertical rays through the cover's region give the same wall crossings as the original
    for x, y in [(10, -50), (24, -40), (30, -72), (45, -30), (60, -40), (20, -26)]:
        a = [h[2] for h in ray_hits(part, (x, y, 300), (0, 0, -1)) if h[2] > Z_OPEN + CONE + 0.5]
        b = [h[2] for h in ray_hits(cover, (x, y, 300), (0, 0, -1)) if h[2] > Z_OPEN + CONE + 0.5]
        assert np.allclose(a, b, atol=0.01), (x, y)
    above = part.vertices[part.vertices[:, 2] > Z_OPEN + CONE + 0.3]
    assert above[:, 2].max() == pytest.approx(cover.vertices[:, 2].max(), abs=0.01)


def test_wider_than_square_only_below_it(part):
    sq = part.vertices[(part.vertices[:, 2] >= Z_OPEN)]
    assert sq[:, 0].min() >= -0.01  # nothing left of the square's x=0 face at or above the cover's open end
    inner = part.vertices[(part.vertices[:, 2] >= Z_OPEN) & (part.vertices[:, 2] <= Z_OPEN + 20)]
    assert inner[:, 0].max() <= 48.5 and inner[:, 1].max() <= -26.9 and inner[:, 1].min() >= -75.1
    ball = part.vertices[part.vertices[:, 2] < 30]
    assert ball[:, 0].min() < -5  # the ball does overhang the square, below it
    assert ball[:, 2].min() == pytest.approx(0, abs=0.01)  # rim on the bed


def test_ball_is_open_through(part):
    # a vertical ray down the ball's axis passes the waist and leaves through the bottom rim: no floor
    hits = [h[2] for h in ray_hits(part, (24.24, -51, 40), (0, 0, -1))]
    assert hits == []
