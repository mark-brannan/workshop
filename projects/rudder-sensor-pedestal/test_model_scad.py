"""Rudder sensor pedestal: bounding box, volume window, lead path open, screw holes through, nut slots open to the plate's ends."""

import re
import tempfile
from pathlib import Path

import pytest
import trimesh
from shop.scad import OpenSCAD, find_openscad
from shop.testing import ray_hits

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")
NUM = r"^(\w+)\s*=\s*(-?[\d.]+)\s*;"
P = {k: float(v) for k, v in re.findall(NUM, (HERE / "model.scad").read_text(), re.M)}
# the seat is read from the sensor's model: its two flange holes lie square to its arm, so along Y here
S = {k: float(v) for k, v in re.findall(NUM, (HERE.parent / "rudder-angle-sensor" / "model.scad").read_text(), re.M)}
HOLE_Y = S["flange_pitch"] / 2
UNDER = P["base_t"] + P["col_h"]
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


def test_flange_holes_and_nut_slots(mesh):
    assert S["arm_zero"] == 90
    slot_z = UNDER - (P["nut_t"] + P["nut_fit"]) / 2
    for s in (-1, 1):
        # the screw hole runs from the seat down past the nut
        down = ray_hits(mesh, [0, s * HOLE_Y, 200], [0, 0, -1])
        assert down and down[0][2] == pytest.approx(UNDER - P["screw_below"], abs=0.05)
        # the nut slides in from the plate's end and stops centred under the hole
        inward = ray_hits(mesh, [0, s * 100, slot_z], [0, -s, 0])
        assert abs(inward[0][1]) == pytest.approx(HOLE_Y - (P["nut_af"] + P["nut_fit"]) / 2 / 0.8660254, abs=0.05)
        # and is as wide as the nut across its flats, no wider
        across = ray_hits(mesh, [0, s * HOLE_Y, slot_z], [1, 0, 0])
        assert across[0][0] == pytest.approx((P["nut_af"] + P["nut_fit"]) / 2, abs=0.05)
    # the seat's pocket takes the sensor's foot, long side along Y
    lo, hi = mesh.slice_plane([0, 0, UNDER + P["plate_t"] + 1], [0, 0, 1]).bounds
    assert hi[1] - lo[1] == pytest.approx(S["flange_pitch"] + S["flange_hole_d"] + 2 * S["flange_edge"] + 2 * P["rim"], abs=0.1)
