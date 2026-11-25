"""Tests for the probe holder: bounding box, volume window, screw holes and reach, fins to the plate, the point open, ledges over the lip, no flat overhangs."""

import math
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
TILT = math.radians(P["tilt"])
SLOT = P["probe_t"] + 2 * P["fit_t"]
D = P["probe_s"] * math.sqrt(2)
K = (P["fit_v"] + P["wall"]) * math.sqrt(2)
Y_PF = (SLOT / 2 + P["front_t"]) * math.cos(TILT) + K * math.sin(TILT) - 0.5
Z_CUT = P["open_v"] * math.cos(TILT) - SLOT / 2 * math.sin(TILT)  # the open point's cut lands on the bed
SCREW_ZS = [float(z) for z in re.search(r"^screw_zs\s*=\s*\[([^\]]*)\]", (HERE / "model.scad").read_text(), re.M).group(1).split(",")]
SCREWS = [(x, z) for x in (-P["screw_x"], P["screw_x"]) for z in SCREW_ZS]


@pytest.fixture(scope="module")
def holder(tmp_path_factory):
    d = tmp_path_factory.mktemp("holder")
    return trimesh.load(build_scad(HERE / "model.scad", d, "holder", render=False)["stl"])


def test_one_watertight_piece(holder):
    assert holder.is_watertight
    assert len(holder.split(only_watertight=False)) == 1


def test_bounds(holder):
    lo, hi = holder.bounds
    assert np.isclose(lo[2], 0, atol=0.05)
    assert np.isclose(hi[1], Y_PF + P["plate_t"], atol=0.05)  # plate back face is the wall
    assert -50 < lo[1] < -35  # the support wall leans out toward the user
    assert hi[0] < 60 and lo[0] > -60  # the plate under the fins is the widest part



def test_volume_window(holder):
    assert 83_000 < holder.volume < 94_000  # 88.2 cm^3 as built


def test_two_screw_holes_clear_and_reachable(holder):
    # a driver from the front meets nothing on its way through the hole: the screws sit above the cradle
    for x, z in SCREWS:
        assert len(ray_hits(holder, (x, -300, z), (0, 1, 0))) == 0


def test_screws_just_above_the_cradle(holder):
    # the countersink's lower edge clears the cradle's top by a few mm, no more: the plate stays low
    v = holder.vertices
    cradle_top = v[v[:, 1] < Y_PF - 0.2][:, 2].max()
    assert all(0 < z - P["csk_d"] / 2 - cradle_top < 8 for _, z in SCREWS)
    # and the screws are still the plate's top: the plate ends one rim above them
    assert holder.bounds[1][2] < max(SCREW_ZS) + P["csk_d"] / 2 + P["plate_r"] + 0.5


def test_side_walls_reach_the_plate(holder):
    # just in front of the plate, high up, a ray across meets both fins (two faces each) and nothing else
    assert len(ray_hits(holder, (100, Y_PF - 1, 25), (-1, 0, 0))) == 4


def test_point_open_from_above(holder):
    # straight down the slot centre, past the probe's point: nothing at all
    assert len(ray_hits(holder, (0, -20 * math.sin(TILT), 46), (0, 0, -1))) == 0


def test_no_flat_overhangs(holder):
    n, c = holder.face_normals, holder.triangles_center
    bad = (n[:, 2] < -math.cos(math.radians(39.5)))  # the fins' undersides, swept level, lean 41 deg: owner accepts
    bad &= c[:, 2] > 1.6  # not the plate's 1.5 mm edge round on the bed
    # the two 3 mm corner rounds of the quarter circle pass through flat for a few mm: about 37 mm^2 in all, at 44-46 deg
    assert holder.area_faces[bad].sum() < 40


def _world(u, v, w):
    # probe frame (u across, v up the face, w through it, +w the support wall) to world, as placed() in model.scad
    y, z = -w, v
    return (u, y * math.cos(TILT) - z * math.sin(TILT), y * math.sin(TILT) + z * math.cos(TILT) - Z_CUT)


def _pe(s, n):
    # (s along the seated probe's lower-right edge from its point, n inward) to (u, v), as pe() in model.scad
    return (s - n) / math.sqrt(2), (s + n) / math.sqrt(2) - P["fit_v"] * math.sqrt(2)


def _ray_w(holder, u, v, w, sign):
    a, b = np.array(_world(u, v, w)), np.array(_world(u, v, w + sign))
    return a, ray_hits(holder, tuple(a), tuple(b - a))


def test_point_open_through_the_thickness(holder):
    # 7 mm up the probe's edge, through its thickness: nothing toward the user, only the wall plate toward the wall
    u, v = _pe(7, 1)
    assert len(_ray_w(holder, u, v, 0, 1)[1]) == 0
    h = _ray_w(holder, u, v, 0, -1)[1]
    assert len(h) == 2 and np.isclose(h[1][1], Y_PF + P["plate_t"], atol=0.05)


@pytest.mark.parametrize("side", [1, -1])
def test_ledges_lap_the_lip(holder, side):
    # from the lip's face, toward the wall, 1.5 mm in from each edge: the ledge, fit_t away
    u, v = _pe(P["pocket_s"] + 2, 1.5)
    a, h = _ray_w(holder, side * u, v, -P["probe_t"] / 2 + P["fit_t"], -1)
    assert len(h) and np.isclose(np.linalg.norm(np.array(h[0]) - a), P["fit_t"], atol=0.1)
