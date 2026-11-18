"""Tests for the GV30 lux add-on: bounding box, volume window and the features of the ring and the arm."""

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
UP, DOWN = [0, 0, 1], [0, 0, -1]
TAB_X0 = P["skirt_ir"] + P["skirt_t"] + 0.5
SCREWS = [(TAB_X0 + P["screw_dx"], s * P["screw_dy"]) for s in (-1, 1)]


def run(part: str) -> trimesh.Trimesh:
    osc = OpenSCAD()
    with tempfile.TemporaryDirectory() as d:
        stl = Path(d) / "m.stl"
        osc.run(HERE / "model.scad", stl, "-D", f'part="{part}"')
        mesh = trimesh.load(stl)
    osc.cleanup()
    return mesh


@pytest.fixture(scope="module")
def ring():
    return run("ring")


@pytest.fixture(scope="module")
def arm():
    return run("arm")


def test_ring(ring):
    lo, hi = ring.bounds
    assert lo[0] == pytest.approx(-P["ring_od"] / 2, abs=0.1) and hi[0] == pytest.approx(TAB_X0 + P["tab_l"], abs=0.1)
    assert hi[2] == pytest.approx(P["ring_t"] + P["tongue_h"], abs=0.05)
    assert ring.is_watertight and 10000 < ring.volume < 15000
    assert not ray_hits(ring, [0, 0, 10], DOWN), "bore clear over the stub"
    # tongue fits the slot with clearance
    sec = ring.section([1, 0, 0], [P["skirt_ir"] + 1, 0, 0])
    assert sec.bounds[1][1] - sec.bounds[0][1] < P["slot_w"]
    for x, y in SCREWS:
        z = ray_hits(ring, [x, y, P["tab_h"] + 5], DOWN)[0][2]
        assert z == pytest.approx(P["tab_h"] - P["insert_h"], abs=0.05), "insert pocket"


def test_lead_path(ring):
    # inboard through the tongue into the cavity, at the lead's height
    z = P["ring_t"] + P["lead_d"] / 2 + 1
    first = ray_hits(ring, [P["skirt_ir"] - P["tongue_in"] - 2, 0, z], [1, 0, 0])[0]
    assert first[0] > TAB_X0, "lead hole runs through the tongue into the tab"
    # and up out of the tab's top to the arm
    assert not ray_hits(ring, [TAB_X0 + 3.5, 0, z], UP)


def test_arm(arm):
    lo, hi = arm.bounds
    assert hi[0] == pytest.approx(P["reach"] + P["head_d"] / 2, abs=0.1)
    assert hi[2] - lo[2] == pytest.approx(P["arm_t"], abs=0.05)
    assert arm.is_watertight and 5000 < arm.volume < 9000
    # sensor pocket: skin on top, open below
    hits = ray_hits(arm, [P["reach"], 0, -5], UP)
    assert hits[0][2] == pytest.approx(P["arm_t"] - P["skin"], abs=0.05)
    for x, y in SCREWS:
        assert not ray_hits(arm, [x, y, -5], UP), "screw hole through"
