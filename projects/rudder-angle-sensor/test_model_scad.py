"""Rudder angle sensor: each printed part's bounding box, volume window and open or closed features, and two other parts sets."""

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
PRINTS = ("body", "cup", "cap", "arm", "spacer")

# part -> (extents x, y, z in mm, volume window in mm^3), from the 2026-11-20 rev 1 build
PARTS = {
    "body": ((50.0, 25.78, 25.0), (9500, 12500)),
    "cup": ((50.0, 25.78, 15.2), (10000, 13500)),
    "cap": ((10.0, 10.0, 7.5), (300, 420)),
    "arm": ((83.7, 23.5, 13.6), (7000, 9500)),
    "spacer": ((12.8, 12.8, 6.0), (220, 300)),
}
# other bearings and boards the model has to survive: a one-line tweak each in the Customizer
ALT = {
    "625 bearing, 5 mm shaft, same board": ["bearing_id=5", "bearing_od=16", "shaft_d=5", "race_od=7.6"],
    "608 bearing, 8 mm shaft, bare 23 mm module": [
        "bearing_id=8", "bearing_od=22", "bearing_w=7", "shaft_d=8", "race_od=12",
        "board_l=23", "board_w=23", "board_r=1", "hole_dx=17", "hole_dy=17", "hole_d=3", "tall=[]", "chip_h=1.75",
    ],
}


def build(view, defines=()):
    osc = OpenSCAD()
    with tempfile.TemporaryDirectory() as d:
        stl = Path(d) / "m.stl"
        osc.run(HERE / "model.scad", stl, "-D", f'view="{view}"', *[a for kv in defines for a in ("-D", kv)])
        mesh = trimesh.load(stl)
    osc.cleanup()
    return mesh


@pytest.fixture(scope="module")
def parts():
    return {p: build(f"{p}_print") for p in PRINTS}


@pytest.mark.parametrize("part", PARTS)
def test_part(parts, part):
    extents, (vmin, vmax) = PARTS[part]
    assert parts[part].extents == pytest.approx(extents, abs=0.3)
    assert parts[part].is_watertight and vmin < parts[part].volume < vmax


def floor_closed(body, floor_t):
    z = sorted(h[2] for h in ray_hits(body, [0, 0, -5], UP))
    return z[0] == pytest.approx(0, abs=0.01) and z[1] == pytest.approx(floor_t, abs=0.01)


def test_magnet_to_chip_gap():
    gap = P["chip_air"] + P["floor_t"] + P["mag_air"]
    assert 0.5 <= gap <= 2.0   # AS5600: 0.5 to 3; ours stays under 2


def test_body_floor_closed_weep_and_bore_open(parts):
    body = parts["body"]
    assert floor_closed(body, P["floor_t"])
    assert not ray_hits(body, [0, 0, P["floor_t"] + P["weep_d"] / 2], [0, -1, 0])   # weep runs out the side
    assert not ray_hits(body, [0, 0, P["floor_t"] + 0.5], UP)                       # chamber and bore open to the top


def test_flange_holes_through_both(parts):
    for name in ("body", "cup"):
        for s in (-1, 1):
            assert not ray_hits(parts[name], [s * P["flange_pitch"] / 2, 0, -5], UP), name


def test_cup_cable_exit_and_pins(parts):
    cup = parts["cup"]
    assert not ray_hits(cup, [0, 0, P["cup_floor"] + P["cable_d"] / 2 + 0.8], [0, 1, 0])
    assert cup.bounds[1][2] == pytest.approx(15.2, abs=0.05)   # cone studs stand 1.6 over the rim
    for sx in (-1, 1):
        for sy in (-1, 1):   # a pin stands in each board hole, its top at the board's top face
            top = max(h[2] for h in ray_hits(cup, [sx * P["hole_dx"] / 2, sy * P["hole_dy"] / 2, -5], UP))
            assert top == pytest.approx(15.2 - 1.6 - P["chip_air"] - P["chip_h"], abs=0.02)


def test_arm_stud_holes_and_bore(parts):
    for r in (0, 40, 50, 60):
        assert not ray_hits(parts["arm"], [r, 0, -5], UP), r


def test_plate_is_five_bodies():
    assert len(build("plate").split(only_watertight=True)) == 5


@pytest.mark.parametrize("name", ALT)
def test_other_parts_sets(name):
    floor_t = P["floor_t"]
    for p in PRINTS:
        mesh = build(f"{p}_print", ALT[name])
        assert mesh.is_watertight and mesh.volume > 100, p
        if p == "body":
            assert floor_closed(mesh, floor_t)
