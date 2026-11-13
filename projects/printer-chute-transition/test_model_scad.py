"""Chute transition as two prints: the adapter (ball, flare, spigot and lip) and the trimmed cover.
Bounding boxes, volume windows, the cover unchanged above its cut, the slot the cover drops into,
and the adapter printable rim down with no overhang flatter than 45 deg."""

import shutil
from pathlib import Path

import numpy as np
import pytest
import trimesh
from shop.scad import build_scad, find_openscad
from shop.testing import ray_hits

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")
TRIM = 12.0      # cut off the cover's open end
Z_OPEN = 44.0    # installed frame: ball_h 30 + flare_h 14; the slot's floor, where the cover's cut end sits
TOP = 156.65     # installed height, unchanged from the one-piece part
SPIGOT_H, LIP_H = 15.0, 4.0
COVER_WALL = 1.86
CTR = (24.24, -51.0)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    d = tmp_path_factory.mktemp("chute")
    for f in ("model.scad", "part-adapter.scad", "part-cover.scad"):
        shutil.copy(HERE / f, d / f)
    load = lambda n: trimesh.load(build_scad(d / f"part-{n}.scad", d, n, render=False)["stl"])  # noqa: E731
    return {"adapter": load("adapter"), "cover": load("cover")}


@pytest.fixture(scope="module")
def adapter(built):
    return built["adapter"]


@pytest.fixture(scope="module")
def cover(built):
    return built["cover"]


@pytest.fixture(scope="module")
def original():
    return trimesh.load(HERE / "ref" / "chute-cover.stl", process=False)


def installed(m, dz=0.0):
    """Owner's frame (optionally lifted by dz, as the cover part is dropped onto the bed) to the installed frame."""
    v = m.vertices
    return trimesh.Trimesh(np.c_[v[:, 0], -(v[:, 2] + dz), v[:, 1] + Z_OPEN + 50.6 - TRIM], m.faces, process=False)


def test_adapter_bounds_volume_watertight(adapter):
    assert adapter.is_watertight
    assert np.allclose(adapter.bounds, [[-5.68, -80.92, 0], [54.16, -21.08, Z_OPEN + SPIGOT_H]], atol=0.1)
    assert 9000 < adapter.volume < 14000


def test_cover_is_the_original_above_the_cut(cover, original):
    assert cover.is_watertight
    lo = original.bounds[0] + [0, TRIM, -27]
    assert np.allclose(cover.bounds, [lo, original.bounds[1] - [0, 0, 27]], atol=0.01)
    for x, y in [(10, -30), (24, 0), (30, 40), (45, -20), (60, 70), (20, 60), (1, -10)]:
        a = [h[2] + 27 for h in ray_hits(cover, (x, y, 300), (0, 0, -1))]
        b = [h[2] for h in ray_hits(original, (x, y, 300), (0, 0, -1))]
        assert np.allclose(a, b, atol=0.01), (x, y)
    assert installed(cover, 27).bounds[:, 2] == pytest.approx([Z_OPEN, TOP], abs=0.01)


def test_ball_wall_matches_the_segment(adapter):
    # catcherforRing.3mf measures 0.77 to 0.83 through the ball
    xs = sorted(h[0] for h in ray_hits(adapter, (-20, CTR[1], 10.8), (1, 0, 0)))
    assert xs[1] - xs[0] == pytest.approx(0.8, abs=0.03)
    assert CTR[0] - xs[0] == pytest.approx(29.92, abs=0.03)  # the outer profile, which mates, is the original


def test_open_through(adapter):
    assert ray_hits(adapter, (CTR[0], CTR[1], 100), (0, 0, -1)) == []


def test_no_flat_overhang(adapter):
    # printed rim down: every downward-facing surface is within 45 deg of vertical
    n, c, a = adapter.face_normals, adapter.triangles_center, adapter.area_faces
    flat = (n[:, 2] < -np.cos(np.radians(45)) - 1e-3) & (c[:, 2] > 0.01)
    assert a[flat].sum() < 2.0, c[flat][:5]


def test_rim(adapter):
    rim = adapter.vertices[adapter.vertices[:, 2] < 0.01]
    r = np.hypot(rim[:, 0] - CTR[0], rim[:, 1] - CTR[1])
    assert r.max() == pytest.approx(27.5, abs=0.05)  # 27.8 less the 0.3 chamfer
    assert r.min() == pytest.approx(27.0, abs=0.1)


def test_slot_pinches_the_cover_wall(adapter):
    z = Z_OPEN + 2
    xs = lambda y: sorted(h[0] for h in ray_hits(adapter, (-20, y, z), (1, 0, 0)))[:4]  # noqa: E731
    lip_o, lip_i, sp_o, sp_i = xs(-50)
    assert lip_i - lip_o == pytest.approx(1.2, abs=0.02)
    assert sp_o - lip_i == pytest.approx(COVER_WALL + 0.1 + 0.25, abs=0.02)  # the wall plus both clearances
    assert sp_i - sp_o == pytest.approx(1.2, abs=0.02)
    _, lip_i, rib, _ = xs(-38)                                                # through a crush rib
    assert rib - lip_i == pytest.approx(COVER_WALL - 0.05, abs=0.02)         # 0.05 tighter than the wall
    floor = [h[2] for h in ray_hits(adapter, (0.9, -50, 100), (0, 0, -1))]
    assert floor[0] == pytest.approx(Z_OPEN, abs=0.02)                        # the cover's cut end lands here


def test_lip_is_short_and_absent_at_the_panel(adapter):
    v = adapter.vertices
    above = v[v[:, 2] > Z_OPEN + 0.1]
    assert above[:, 1].max() <= -27 + 0.01        # nothing past the plane of the U's open side
    proud = above[(above[:, 0] < -0.05) | (above[:, 0] > 48.53) | (above[:, 1] < -75.05)]
    assert proud[:, 2].max() == pytest.approx(Z_OPEN + LIP_H, abs=0.02)
    assert proud[:, 0].min() == pytest.approx(-1.3, abs=0.02)


def test_spigot_clears_the_cover_everywhere(adapter, cover):
    # the cover's jog must not reach into the spigot's 15 mm: probe both legs and the back at three heights
    c = installed(cover, 27)
    for z in (Z_OPEN + 1, Z_OPEN + 7, Z_OPEN + SPIGOT_H - 2):
        for o, d, ax in [((CTR[0], -45, z), (-1, 0, 0), 0), ((CTR[0], -45, z), (1, 0, 0), 0),
                         ((CTR[0], -65, z), (-1, 0, 0), 0), ((14.0 + 3, CTR[1], z), (0, -1, 0), 1)]:
            a = [abs(h[ax] - o[ax]) for h in ray_hits(adapter, o, d)]
            wall = [abs(h[ax] - o[ax]) for h in ray_hits(c, o, d)]
            assert wall[0] - a[1] == pytest.approx(0.25, abs=0.03), (z, d)   # spigot outer face to cover inner face
