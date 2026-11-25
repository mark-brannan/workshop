"""Tests for the heater fan mount: bounding box, volume window and feature counts of each printed part."""

import math
import re
from pathlib import Path

import numpy as np
import pytest
import trimesh
from shop.scad import build_scad, find_openscad
from shop.testing import ray_hits, seated_overlap

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")

P = {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*([-\d.]+)\s*;", (HERE / "model.scad").read_text(), re.M)}
SOCK = P["fan"] + 2 * P["fit"]
COLLAR_BORE = P["rim_d"] + 2 * P["collar_fit"]
W = max(SOCK, COLLAR_BORE) + 2 * P["wall"]
L = W + P["divider"] + P["pocket"]
FAN_Z = P["floor_t"] + P["flange_t"]  # the fan sits on the spigot's flange
H = FAN_Z + P["fan_t"]
FLANGE = SOCK - 2 * P["flange_fit"]
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
            assert len(ray_hits(box, (x + P["head_d"] / 2 + 0.5, y, -10), (0, 0, 1))) == 2  # floor around the countersink
            rim = ray_hits(box, (x + P["head_d"] / 2 - 0.3, y, -10), (0, 0, 1))[0][2]
            assert 0.2 < rim < 0.4  # 45 deg countersink for the flush head, opening onto the bed


def test_box_ceilings_only_in_the_two_holes(box):
    # every face steeper than 45 deg downward sits on the bed, or in the crown of the knob or gland hole
    down = box.face_normals[:, 2] < -0.72
    c = box.triangles_center[down]
    c = c[np.abs(c[:, 2]) > 0.01]
    gz = P["floor_t"] + P["fan_t"] / 2
    in_pot = (c[:, 1] < Y0 + P["front"] + 0.01) & (np.hypot(c[:, 0] - POCKET_X, c[:, 2] - POT_Z) < P["pot_bushing"] / 2 + 0.05)
    in_gland = (c[:, 1] > W / 2 - P["wall"] - 0.01) & (np.hypot(c[:, 0] - POCKET_X, c[:, 2] - gz) < P["gland"] / 2 + 0.25)
    win_z = P["floor_t"] + 3 + 1.6 + 1  # the LED window's 3 mm top: accepted, the clear fill covers it
    in_win = (c[:, 1] < Y0 + P["front"] + 0.01) & (abs(c[:, 2] - win_z - P["led_win"] / 2) < 0.05) & (abs(c[:, 0] - (POCKET_X + P["board"] / 2 - P["led_x"] + P["led_shift"])) < P["led_win"] / 2 + 0.05)
    assert (in_pot | in_gland | in_win).all(), c[~(in_pot | in_gland | in_win)][:5]


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
    for dx in (-q, q):  # on each web's line, both sides of the crown: the web fills the hole
        web = ray_hits(box, (POCKET_X + dx, 60, gz + q), (0, -1, 0))
        assert web and web[0][1] == pytest.approx(W / 2, abs=0.05)
    assert ray_hits(box, (POCKET_X, 60, gz), (0, -1, 0)) == []  # below the webs: open, out through the knob hole
    assert ray_hits(box, (POCKET_X, 60, gz + P["gland"] / 2 + 0.3), (0, -1, 0))[0][1] == pytest.approx(W / 2, abs=0.05)  # round


LED_X = POCKET_X + P["board"] / 2 - P["led_x"]
WIN_X, WIN_Z = LED_X + P["led_shift"], P["floor_t"] + 3 + 1.6 + 1


def test_box_led_window(box):
    half = P["led_win"] / 2  # square aperture
    assert abs(WIN_X - LED_X) < half - 0.5  # the LED is inside the aperture
    assert ray_hits(box, (WIN_X, -60, WIN_Z), (0, 1, 0))[0][1] > -W / 2 + P["wall"]  # open through the knob wall
    # 0.4 past the aperture's edge the 45 deg chamfer opens 0.4 short of its full depth, square on every side
    for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        hits = ray_hits(box, (WIN_X + dx * (half + 0.4), -60, WIN_Z + dz * (half + 0.4)), (0, 1, 0))
        assert hits[0][1] == pytest.approx(Y0, abs=0.05)
        assert hits[1][1] == pytest.approx(-W / 2 + P["wall"] - (P["led_chamfer"] - 0.4), abs=0.05)
    # just past the chamfer: solid wall right through
    assert ray_hits(box, (WIN_X + half + P["led_chamfer"] + 0.2, -60, WIN_Z), (0, 1, 0))[1][1] == pytest.approx(-W / 2 + P["wall"], abs=0.05)
    # every aperture corner clears the knob skirt by at least 0.5
    for dx in (-half, half):
        for dz in (-half, half):
            assert np.hypot(WIN_X + dx - POCKET_X, WIN_Z + dz - POT_Z) >= P["knob_d"] / 2 + 0.5


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


def test_lid_nut_pockets_in_low_mounds(lid):
    top = P["plate_t"] + P["nut_h"] - P["nut_sink"]  # mound top, level with the top of the nut
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * HOLE, sy * HOLE
            assert np.isclose(ray_hits(lid, (x + 3, y, 50), (0, 0, -1))[0][2], P["plate_t"] - P["nut_sink"], atol=0.05)  # nut seat
            assert np.isclose(ray_hits(lid, (x - sx * 3.5, y - sy * 3.5, 50), (0, 0, -1))[0][2], top, atol=0.05)  # rim round the nut
            mid = ray_hits(lid, (x - sx * 6, y - sy * 6, 50), (0, 0, -1))[0][2]
            assert P["plate_t"] + 0.3 < mid < top - 0.3  # a slope, not a step, fading into the plate
    assert (P["nut_h"] - P["nut_sink"]) / ((P["mound_d"] - P["mound_top"]) / 2) < 0.35  # gentle: under 20 deg


# spigot: flange on the bed, spigot up
def test_spigot_bounds_volume(spigot):
    assert spigot.is_watertight and len(spigot.split()) == 1
    assert np.allclose(spigot.bounds[:, :2], [[-FLANGE / 2, -FLANGE / 2], [FLANGE / 2, FLANGE / 2]], atol=0.05)
    assert np.isclose(spigot.bounds[1][2], P["flange_t"] + P["floor_t"] + P["spigot_h"], atol=0.1)
    assert 12_000 < spigot.volume < 22_000


def test_flange_drops_in_the_socket_and_the_floor_corners_stop_it():
    hole = SPIGOT_D + 2 * P["thread_gap"]
    assert FLANGE < SOCK  # into the fan socket
    assert hole > SPIGOT_D  # the thread passes down through the floor
    assert math.hypot(FLANGE, FLANGE) / 2 - hole / 2 > 10  # the flange's corners land on floor
    assert math.hypot(HOLE, HOLE) - P["head_d"] / 2 > hole / 2 + 2  # screws and countersinks in that floor


def test_the_fans_own_screws_reach_through_the_nut():
    # heads flush in the floor, then flange, fan and lid; the nut on top of the lid has all its threads on
    assert P["screw_l"] >= FAN_Z + P["fan_t"] + P["plate_t"] - P["nut_sink"] + P["nut_h"]


def test_spigot_bore_and_rib(spigot):
    assert ray_hits(spigot, (0, 0, 50), (0, 0, -1)) == []
    assert np.isclose(ray_hits(spigot, (0, 0, P["flange_t"] + 5), (1, 0, 0))[0][0], SPIGOT_BORE / 2, atol=0.1)
    zs = np.arange(P["flange_t"] + 1.5, P["flange_t"] + P["spigot_h"] - 1.5, 0.25)
    r = np.array([ray_hits(spigot, (60, 0, z), (-1, 0, 0))[0][0] for z in zs])  # outer radius at each height
    assert np.isclose(r.max(), SPIGOT_D / 2, atol=0.15)
    assert np.isclose(r.min(), SPIGOT_D / 2 - P["rib_h"], atol=0.15)


def test_spigot_rib_is_right_handed(spigot):
    # follow the crest a quarter turn counter-clockwise (seen from the duct end, +Z): a right-hand helix climbs
    def crest_z(angle):
        c, s = math.cos(angle), math.sin(angle)
        zs = np.arange(P["flange_t"] + 2, P["flange_t"] + P["pitch"] + 2, 0.1)
        r = [math.hypot(*ray_hits(spigot, (60 * c, 60 * s, z), (-c, -s, 0))[0][:2]) for z in zs]
        return zs[int(np.argmax(r))]  # crest: the largest outer radius

    z0, z90 = crest_z(0.0), crest_z(math.pi / 2)
    rise = (z90 - z0) % P["pitch"]
    assert np.isclose(rise, P["pitch"] / 4, atol=1.0), (z0, z90)


def test_spigot_four_screw_holes(spigot):
    for x in (-HOLE, HOLE):
        for y in (-HOLE, HOLE):
            assert ray_hits(spigot, (x, y, 50), (0, 0, -1)) == []


def test_gauge_two_rings_small(gauge):
    assert gauge.is_watertight
    assert len(gauge.split()) == 2
    assert gauge.bounds[0][2] == pytest.approx(0, abs=0.01)
    assert 15_000 < gauge.volume < 28_000  # about a quarter of the three parts


def test_printed_lid_and_spigot_seat_on_printed_box(box, lid, spigot, tmp_path):
    # the printed meshes in the pose they are used: the lid set on the rim; the spigot turned over and dropped
    # into the fan socket, flange on the floor's corners, thread out through the floor. The flange and its holes
    # are square and symmetric, so this cannot tell a part from its mirror image; the thread meets the duct.
    assert seated_overlap(tmp_path, box, lid, f"translate([0, 0, {H}])") < 0.01
    assert seated_overlap(tmp_path, box, spigot, f"translate([0, 0, {FAN_Z}]) rotate([180, 0, 0])") < 0.01
    low = spigot.copy()
    low.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    low.apply_translation([0, 0, FAN_Z])
    assert np.isclose(low.bounds[0][2], -P["spigot_h"], atol=0.1)  # the duct thread hangs clear below the flat bottom
    assert np.isclose(ray_hits(low, (HOLE - 6, HOLE - 6, 20), (0, 0, -1))[-1][2], P["floor_t"], atol=0.05)  # flange on the floor
