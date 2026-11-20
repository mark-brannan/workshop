"""Tests for the heater fan mount: bounding box, volume window and feature counts of each printed part."""

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
SOCK = P["fan"] + 2 * P["fit"]
COLLAR_BORE = P["rim_d"] + 2 * P["collar_fit"]
W = max(SOCK, COLLAR_BORE) + 2 * P["wall"]
L = W + P["divider"] + P["pocket"]
H = P["floor_t"] + P["fan_t"]
POCKET_X = W / 2 - P["wall"] + P["divider"] + P["pocket"] / 2
SPIGOT_D = P["duct_id"] - 0.2 + 2 * P["rib_h"]
SPIGOT_BORE = P["duct_id"] - 0.2 - 2 * P["spigot_wall"]
HOLE = P["fan_holes"] / 2
BOX_DEPTH = W + P["front"] - P["wall"] + P["gusset"]  # knob face to back wall, the box's print height
AXIS_Z = W / 2 + P["front"] - P["wall"]  # fan axis above the bed, box as printed


def build(tmp_path_factory, name):
    d = tmp_path_factory.mktemp(name)
    for f in ("model.scad", f"part-{name}.scad"):
        (d / f).write_text((HERE / f).read_text())
    return trimesh.load(build_scad(d / f"part-{name}.scad", d, name, render=False)["stl"])


@pytest.fixture(scope="module")
def box(tmp_path_factory):
    return build(tmp_path_factory, "box")


@pytest.fixture(scope="module")
def lid(tmp_path_factory):
    return build(tmp_path_factory, "lid")


@pytest.fixture(scope="module")
def spigot(tmp_path_factory):
    return build(tmp_path_factory, "spigot")


@pytest.fixture(scope="module")
def gauge(tmp_path_factory):
    return build(tmp_path_factory, "gauge")


def test_collar_never_overhangs_and_spigot_core_slips_in_duct():
    assert COLLAR_BORE + 2 * P["wall"] <= W + 1e-9
    assert SPIGOT_D - 2 * P["rib_h"] < P["duct_id"]
    assert HOLE * 2 < SOCK and math.hypot(HOLE, HOLE) * 2 > P["fan_bore"]  # screws clear the air path


# box, as printed: knob face on the bed, open top (lid side) toward -Y, floor at y in [-floor_t, 0]
def test_box_bounds_volume(box):
    assert box.is_watertight and len(box.split()) == 1
    assert np.allclose(box.bounds, [[-W / 2, -H, 0], [L - W / 2, 0, BOX_DEPTH]], atol=0.05)
    assert 40_000 < box.volume < 58_000


def test_box_air_path_and_four_screw_holes(box):
    assert ray_hits(box, (0, -50, AXIS_Z), (0, 1, 0)) == []  # open bay, bore through the floor
    for x in (-HOLE, HOLE):
        for z in (AXIS_Z - HOLE, AXIS_Z + HOLE):
            assert ray_hits(box, (x, -50, z), (0, 1, 0)) == []
            assert len(ray_hits(box, (x + 3.5, -50, z), (0, 1, 0))) == 2  # floor around the hole


def test_box_pot_bushing_through_knob_face(box):
    y = -(P["floor_t"] + 3 + 1.6 + P["pot_z"])
    first = ray_hits(box, (POCKET_X - 8, y, -10), (0, 0, 1))[0]
    assert first[2] > BOX_DEPTH - P["wall"] - 0.05  # nothing until the back wall: the hole is open
    assert ray_hits(box, (POCKET_X - 8 + P["pot_bushing"], y, -10), (0, 0, 1))[0][2] < 0.05


def test_box_gland_through_back_wall(box):
    first = ray_hits(box, (POCKET_X, -H / 2, BOX_DEPTH + 10), (0, 0, -1))[0]
    assert first[2] < P["front"] + 0.05  # straight through to the knob wall inside


def test_box_gussets_hold_the_back_wall(box):
    # a 45 deg plate behind each back corner of the fan: a vertical ray through it meets two faces
    z = AXIS_Z + SOCK / 2 + P["gusset"] / 2
    for x in (-SOCK / 2 + P["gusset"] / 2, SOCK / 2 - P["gusset"] / 2):
        hits = [h for h in ray_hits(box, (x, -H / 2, -10), (0, 0, 1)) if P["front"] < h[2] < BOX_DEPTH - P["wall"]]
        assert len(hits) == 2, (x, hits)
    assert ray_hits(box, (0, -H / 2, z), (1, 0, 0)) != []


def test_box_yz_fins_under_the_back_wall(box):
    # just under the back wall, a ray along X crosses each fin as an entry and exit fin_t apart
    z = BOX_DEPTH - P["wall"] - 0.5
    xs = sorted(h[0] for h in ray_hits(box, (-W, -H / 2, z), (1, 0, 0)))
    fins = [a for a, b in zip(xs, xs[1:]) if abs(b - a - P["fin_t"]) < 0.05]
    assert len(fins) == P["fins_fan"] + 2, xs


def test_box_four_board_standoffs(box):
    found = 0
    for x in (-1, 1):
        for zz in (-1, 1):
            cx = POCKET_X + x * P["board_holes"] / 2
            cz = P["front"] - P["wall"] + P["wall"] + P["board"] / 2 + 1 + zz * P["board_holes"] / 2
            ring = ray_hits(box, (cx + 2, -50, cz), (0, 1, 0))
            pilot = ray_hits(box, (cx, -50, cz), (0, 1, 0))
            if ring and np.isclose(ring[0][1], -P["floor_t"] - 3, atol=0.05) and np.isclose(pilot[0][1], -P["floor_t"], atol=0.05):
                found += 1
    assert found == 4


# lid: plate on the bed, collar up
def test_lid_bounds_volume(lid):
    assert lid.is_watertight and len(lid.split()) == 1
    y0 = -W / 2 - (P["front"] - P["wall"])
    assert np.allclose(lid.bounds, [[-W / 2, y0, 0], [L - W / 2, y0 + BOX_DEPTH, P["plate_t"] + P["rim_grip"]]], atol=0.05)
    assert 25_000 < lid.volume < 40_000


def test_lid_collar_bore_and_six_slots(lid):
    z_low = P["plate_t"] + 2  # below the slots
    assert np.isclose(ray_hits(lid, (0, 0, z_low), (1, 0, 0))[0][0], COLLAR_BORE / 2, atol=0.1)
    z_high = P["plate_t"] + P["rim_grip"] - 2
    hit = [bool(ray_hits(lid, (0, 0, z_high), (math.cos(a), math.sin(a), 0))) for a in np.radians(np.arange(0, 360, 0.5))]
    gaps = sum(1 for i in range(len(hit)) if not hit[i] and hit[i - 1])
    assert gaps == P["slots"]


def test_lid_air_path_and_four_screw_holes(lid):
    assert ray_hits(lid, (0, 0, 50), (0, 0, -1)) == []
    for x in (-HOLE, HOLE):
        for y in (-HOLE, HOLE):
            assert ray_hits(lid, (x, y, 50), (0, 0, -1)) == []


# spigot: flange on the bed, spigot up
def test_spigot_bounds_volume(spigot):
    assert spigot.is_watertight and len(spigot.split()) == 1
    assert np.allclose(spigot.bounds[:, :2], [[-W / 2, -W / 2], [W / 2, W / 2]], atol=0.05)
    assert np.isclose(spigot.bounds[1][2], P["plate_t"] + P["spigot_h"], atol=0.1)
    assert 15_000 < spigot.volume < 26_000


def test_spigot_bore_and_rib(spigot):
    assert ray_hits(spigot, (0, 0, 50), (0, 0, -1)) == []
    assert np.isclose(ray_hits(spigot, (0, 0, P["plate_t"] + 5), (1, 0, 0))[0][0], SPIGOT_BORE / 2, atol=0.1)
    zs = np.arange(P["plate_t"] + 1.5, P["plate_t"] + P["spigot_h"] - 1.5, 0.25)
    r = np.array([ray_hits(spigot, (60, 0, z), (-1, 0, 0))[0][0] for z in zs])  # outer radius at each height
    assert np.isclose(r.max(), SPIGOT_D / 2, atol=0.15)
    assert np.isclose(r.min(), SPIGOT_D / 2 - P["rib_h"], atol=0.15)


def test_spigot_rib_is_right_handed(spigot):
    # follow the crest a quarter turn counter-clockwise (seen from the duct end, +Z): a right-hand helix climbs
    def crest_z(angle):
        c, s = math.cos(angle), math.sin(angle)
        zs = np.arange(P["plate_t"] + 2, P["plate_t"] + P["pitch"] + 2, 0.1)
        r = [math.hypot(*ray_hits(spigot, (60 * c, 60 * s, z), (-c, -s, 0))[0][:2]) for z in zs]
        return zs[int(np.argmax(r))]  # crest: the largest outer radius

    z0, z90 = crest_z(0.0), crest_z(math.pi / 2)
    rise = (z90 - z0) % P["pitch"]
    assert np.isclose(rise, P["pitch"] / 4, atol=1.0), (z0, z90)


def test_spigot_four_nut_pockets(spigot):
    for x in (-HOLE, HOLE):
        for y in (-HOLE, HOLE):
            assert ray_hits(spigot, (x, y, 50), (0, 0, -1)) == []
            top = ray_hits(spigot, (x + np.sign(x) * 3, y, 50), (0, 0, -1))[0][2]
            assert np.isclose(top, P["plate_t"] - 1.9, atol=0.05)


def test_gauge_two_rings_small(gauge):
    assert gauge.is_watertight
    assert len(gauge.split()) == 2
    assert gauge.bounds[0][2] == pytest.approx(0, abs=0.01)
    assert 15_000 < gauge.volume < 28_000  # about a quarter of the three parts
