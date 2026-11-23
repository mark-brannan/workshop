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
Y0 = -W / 2 - (P["front"] - P["wall"])  # knob face
POT_Z = P["floor_t"] + 3 + 1.6 + P["pot_z"]
BOARD_Y = -W / 2 + P["wall"] + P["board"] / 2 + 1


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


# box, as printed and as modelled: floor on the bed, open top up
def test_box_bounds_volume(box):
    assert box.is_watertight and len(box.split()) == 1
    assert np.allclose(box.bounds, [[-W / 2, Y0, 0], [L - W / 2, W / 2, H]], atol=0.05)
    assert 32_000 < box.volume < 46_000


def test_box_air_path_and_four_screw_holes(box):
    assert ray_hits(box, (0, 0, -10), (0, 0, 1)) == []
    for x in (-HOLE, HOLE):
        for y in (-HOLE, HOLE):
            assert ray_hits(box, (x, y, -10), (0, 0, 1)) == []
            assert len(ray_hits(box, (x + 3.5, y, -10), (0, 0, 1))) == 2  # floor around the hole


def test_box_ceilings_only_in_the_two_holes(box):
    # every face steeper than 45 deg downward sits on the bed, or in the crown of the knob or gland hole
    down = box.face_normals[:, 2] < -0.72
    c = box.triangles_center[down]
    c = c[np.abs(c[:, 2]) > 0.01]
    gz = P["floor_t"] + P["fan_t"] / 2
    in_pot = (c[:, 1] < Y0 + P["front"] + 0.01) & (np.hypot(c[:, 0] - POCKET_X, c[:, 2] - POT_Z) < P["pot_bushing"] / 2 + 0.05)
    in_gland = (c[:, 1] > W / 2 - P["wall"] - 0.01) & (np.hypot(c[:, 0] - POCKET_X, c[:, 2] - gz) < P["gland"] / 2 + 0.25)
    assert (in_pot | in_gland).all(), c[~(in_pot | in_gland)][:5]


def test_box_bed_edge_chamfered(box):
    # the outline on the bed sits bed_chamfer inside the wall above it, all four sides
    c = P["bed_chamfer"]
    for z, inset in ((0.02, c - 0.02), (c + 0.5, 0)):
        assert ray_hits(box, (-100, 20, z), (1, 0, 0))[0][0] == pytest.approx(-W / 2 + inset, abs=0.05)
        assert ray_hits(box, (100 + L, 20, z), (-1, 0, 0))[0][0] == pytest.approx(L - W / 2 - inset, abs=0.05)
        assert ray_hits(box, (10, -100, z), (0, 1, 0))[0][1] == pytest.approx(Y0 + inset, abs=0.05)
        assert ray_hits(box, (10, 100, z), (0, -1, 0))[0][1] == pytest.approx(W / 2 - inset, abs=0.05)


def test_box_round_holes_and_gland_web(box):
    # knob on the pocket's centre line, gland behind it on nearly the same axis: one ray along Y passes both walls
    assert ray_hits(box, (POCKET_X, -60, POT_Z), (0, 1, 0)) == []
    for dz in (1, -1):  # round, not a teardrop: closed just past the radius, above and below
        assert ray_hits(box, (POCKET_X, -60, POT_Z + dz * (P["pot_bushing"] / 2 + 0.3)), (0, 1, 0))[0][1] == pytest.approx(Y0, abs=0.05)
    gz, q = P["floor_t"] + P["fan_t"] / 2, P["gland"] / 4
    web = ray_hits(box, (POCKET_X - q, 60, gz + q), (0, -1, 0))  # on the web's line: it fills the hole
    assert web and web[0][1] == pytest.approx(W / 2, abs=0.05)
    assert ray_hits(box, (POCKET_X + q, 60, gz + q), (0, -1, 0))[0][1] < W / 2 - P["wall"] + 0.05  # mirror side open
    assert ray_hits(box, (POCKET_X, 60, gz + P["gland"] / 2 + 0.3), (0, -1, 0))[0][1] == pytest.approx(W / 2, abs=0.05)  # round


def test_box_knob_centred_between_standoffs(box):
    # on the printed mesh: the bushing's centre and the four pilots' centre share one X
    xs = np.arange(POCKET_X - 20, POCKET_X + 20, 0.05)
    open_x = [x for x in xs if not ray_hits(box, (x, -60, POT_Z), (0, 1, 0)) or ray_hits(box, (x, -60, POT_Z), (0, 1, 0))[0][1] > Y0 + P["front"] - 0.05]
    knob_x = (min(open_x) + max(open_x)) / 2
    top = lambda x, y: (ray_hits(box, (x, y, 50), (0, 0, -1)) or [(0, 0, -1)])[0][2]
    found, pads = 0, []
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = POCKET_X + sx * P["board_holes"] / 2, BOARD_Y + sy * P["board_holes"] / 2
            ring = [x for x in np.arange(cx - 4, cx + 4, 0.05) if np.isclose(top(x, cy), P["floor_t"] + 3, atol=0.05)]
            if ring and np.isclose(top(cx, cy), P["floor_t"], atol=0.05):
                found += 1
                pads.append((min(ring) + max(ring)) / 2)
    assert found == 4
    assert abs(knob_x - POCKET_X) < 0.1 and abs(np.mean(pads) - knob_x) < 0.1, (knob_x, pads)


# lid: plate on the bed, collar up
def test_lid_bounds_volume(lid):
    assert lid.is_watertight and len(lid.split()) == 1
    assert np.allclose(lid.bounds, [[-W / 2, Y0, 0], [L - W / 2, W / 2, P["plate_t"] + P["rim_grip"]]], atol=0.05)
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
