"""Tests for the probe holder: bounding box, volume window, screw holes and reach, fins to the plate, the slot open from above, solid behind the tip, no flat overhangs."""

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
    assert 85_000 < holder.volume < 100_000  # 93.3 cm^3 as built


def test_two_screw_holes_clear_and_reachable(holder):
    # a driver from the front meets nothing on its way through the hole: the screws sit above the cradle
    for x, z in SCREWS:
        assert len(ray_hits(holder, (x, -300, z), (0, 1, 0))) == 0


def test_screws_high(holder):
    # the pull-out load is greatest at the top: the screws sit in the top fifth of the plate
    top = holder.bounds[1][2]
    assert all(z > 0.8 * top for _, z in SCREWS)


def test_side_walls_reach_the_plate(holder):
    # just in front of the plate, high up, a ray across meets both fins (two faces each) and nothing else
    assert len(ray_hits(holder, (100, Y_PF - 1, 95), (-1, 0, 0))) == 4


def test_probe_slot_open_from_above(holder):
    # straight down the slot centre at the probe's point: nothing until the V floor, about at the cradle point height
    h = ray_hits(holder, (0, -20 * math.sin(TILT), 75), (0, 0, -1))  # through the slot at the probe frame (u 0, w 0, v 20)
    assert len(h) and P["plate_pt"] + 5 < h[0][2] < P["plate_pt"] + 25


def test_no_flat_overhangs(holder):
    n, c = holder.face_normals, holder.triangles_center
    bad = (n[:, 2] < -math.cos(math.radians(44.5))) & (c[:, 2] > 1.6)  # not the plate foot's 1.5 mm edge round on the bed
    # the two 3 mm corner rounds of the quarter circle pass through flat for a few mm: about 27 mm^2 in all
    assert holder.area_faces[bad].sum() < 35


def _world(u, v, w):
    # probe frame (u across, v up the face, w through it, +w the support wall) to world, as placed() in model.scad
    z_low = -K * math.cos(TILT) - (SLOT / 2 + P["wall"]) * math.sin(TILT)
    y, z = -w, v
    return (u, y * math.cos(TILT) - z * math.sin(TILT), y * math.sin(TILT) + z * math.cos(TILT) + P["plate_pt"] - z_low)


def test_solid_behind_the_tip(holder):
    # from the gap at the probe's machined face, near the point, toward the wall: solid from within the fit clearance to the plate's back
    w_face = -P["probe_t"] / 2 + P["pocket_d"] + P["fit_t"]  # the machined face, the probe resting on the support wall
    h = ray_hits(holder, _world(0, 3, w_face - 0.5), (0, 1, 0))
    assert len(h) == 2
    assert np.linalg.norm(np.array(h[0]) - _world(0, 3, w_face - 0.5)) < 2.5
    assert np.isclose(h[1][1], Y_PF + P["plate_t"], atol=0.05)
