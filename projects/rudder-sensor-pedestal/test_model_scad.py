"""Rudder sensor pedestal: bounding box, volume window, lead path open, screw holes through."""

import re
import tempfile
from pathlib import Path

import pytest
import trimesh
from shop.scad import OpenSCAD, find_openscad
from shop.testing import ray_hits

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")
P = {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*(-?[\d.]+)\s*;", (HERE / "model.scad").read_text(), re.M)}
UP = [0, 0, 1]


@pytest.fixture(scope="module")
def mesh():
    osc = OpenSCAD()
    with tempfile.TemporaryDirectory() as d:
        stl = Path(d) / "m.stl"
        osc.run(HERE / "model.scad", stl)
        m = trimesh.load(stl)
    osc.cleanup()
    return m


def test_bounds_and_volume(mesh):
    lo, hi = mesh.bounds
    assert hi[0] - lo[0] == pytest.approx(P["base_w"], abs=0.1)
    assert hi[1] - lo[1] == pytest.approx(P["base_d"], abs=0.1)
    assert hi[2] - lo[2] == pytest.approx(P["base_t"] + P["col_h"] + P["plate_t"] + P["lip_h"], abs=0.05)
    assert mesh.is_watertight and 60000 < mesh.volume < 130000


def test_lead_path_open(mesh):
    # straight down the column from the seat, and out the slot at its foot
    assert not ray_hits(mesh, [0, 0, 200], [0, 0, -1]) or ray_hits(mesh, [0, 0, 200], [0, 0, -1])[0][2] < P["base_t"] + 0.1
    assert not ray_hits(mesh, [0, 0, P["base_t"] + 4], [1, 0, 0])


def test_holes_through(mesh):
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (P["base_w"] / 2 - P["screw_inset"]), sy * (P["base_d"] / 2 - P["screw_inset"])
            assert not ray_hits(mesh, [x, y, -5], UP), f"screw hole at {x}, {y}"
        assert not ray_hits(mesh, [sx * P["sensor_hole_pitch"] / 2, 0, 200], [0, 0, -1])[:1] or \
            ray_hits(mesh, [sx * P["sensor_hole_pitch"] / 2, 0, 200], [0, 0, -1])[0][2] < P["base_t"] + P["col_h"] - 7
