"""Tests for the probe holder: bounding box, volume window, screw holes, the slot open from above, no flat overhangs."""

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
SCREWS = [(x, 10) for x in (-P["screw_x"], P["screw_x"])]


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
    assert hi[0] < 52 and lo[0] > -52  # the quarter-circle body is the widest part



def test_volume_window(holder):
    assert 50_000 < holder.volume < 66_000  # 58.1 cm^3 as built


def test_two_screw_holes_clear_through_plate(holder):
    for x, z in SCREWS:
        assert len(ray_hits(holder, (x, Y_PF - 40, z), (0, 1, 0))) == 0


def test_probe_slot_open_from_above(holder):
    # straight down the slot centre at the probe's point: nothing until the V floor, about at the cradle point height
    h = ray_hits(holder, (0, -20 * math.sin(TILT), 150), (0, 0, -1))  # through the slot at the probe frame (u 0, w 0, v 20)
    assert len(h) and P["plate_pt"] - 12 < h[0][2] < P["plate_pt"] + 12


def test_no_flat_overhangs(holder):
    n, c = holder.face_normals, holder.triangles_center
    bad = (n[:, 2] < -math.cos(math.radians(44.5))) & (c[:, 2] > 1.6)  # not the plate foot's 1.5 mm edge round on the bed
    # the two 3 mm corner rounds of the quarter circle pass through flat for a few mm: 2 x 2.2 mm^2 triangles each
    assert holder.area_faces[bad].sum() < 25
