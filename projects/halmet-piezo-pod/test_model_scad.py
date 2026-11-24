"""Tests for the HALMET piezo pod box and lid: bounding box, volume window, feature counts."""

import re
from pathlib import Path

import numpy as np
import pytest
import trimesh
from shop.scad import build_scad, find_openscad
from shop.testing import TURNS, ray_hits, seated_overlap

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")

P = {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*([-\d.]+)\s*;", (HERE / "model.scad").read_text(), re.M)}
OUT_W = P["in_w"] + 2 * P["wall"]
OUT_L = P["in_l"] + 2 * P["wall"]
SEAT_Z = P["floor_t"] + P["plinth_h"]
INSERT_DEPTH = P["insert_l"] + 0.8
COL_R = P["insert_hole_d"] / 2 + P["insert_wall"]
EAR_A = np.arcsin((P["in_w"] / 2 - P["ear_tip_gap"] - P["ear_r"]) / (P["ear_span"] / 2 - P["ear_r"]))
EAR_XY = [(s * -np.sin(EAR_A) * P["ear_pitch"] / 2, s * np.cos(EAR_A) * P["ear_pitch"] / 2) for s in (-1, 1)]
LEDGE_Z = SEAT_Z + P["mod_h"] + P["buzz_clear"]
DEPTH = LEDGE_Z + P["buzzer_h"] - P["proud"] - P["lid_t"]
TAB_Y = OUT_L / 2 + P["tab_reach"]
def build(tmp_path_factory, src, name):
    d = tmp_path_factory.mktemp(name)
    for f in ("model.scad", "part-lid.scad"):
        (d / f).write_text((HERE / f).read_text())
    return trimesh.load(build_scad(d / src, d, name, render=False)["stl"])


@pytest.fixture(scope="module")
def box(tmp_path_factory):
    return build(tmp_path_factory, "model.scad", "box")


@pytest.fixture(scope="module")
def lid(tmp_path_factory):
    return build(tmp_path_factory, "part-lid.scad", "lid")


def test_box_bounds_volume(box):
    assert box.is_watertight
    assert np.allclose(box.bounds, [[-OUT_W / 2, -TAB_Y - P["tab_r"], 0], [OUT_W / 2, TAB_Y + P["tab_r"], DEPTH]], atol=0.05)
    assert 14_000 < box.volume < 28_000


def test_lid_bounds_volume(lid):
    assert lid.is_watertight
    assert np.allclose(lid.bounds[:, :2], [[-OUT_W / 2, -OUT_L / 2], [OUT_W / 2, OUT_L / 2]], atol=0.05)
    assert np.isclose(lid.bounds[1][2], P["lid_t"] + P["skirt_h"], atol=0.05)
    assert 2_500 < lid.volume < 7_000


def test_stack_fits():
    assert P["plinth_h"] > P["pin_out"]  # pins clear of the pocket floor
    for x, y in EAR_XY:
        assert abs(x) - COL_R > P["mod_w"] / 2 + 1  # bosses clear the module's sides
    c = P["ear_span"] / 2 - P["ear_r"]
    assert c * np.sin(EAR_A) + P["ear_r"] <= P["in_w"] / 2 - 1  # ear tips clear the long walls
    assert c * np.cos(EAR_A) + P["ear_r"] < P["in_l"] / 2 - 1
    assert P["ledge_reach"] - (P["in_w"] / 2 - P["buzzer_d"] / 2) >= 1.5  # flange edge overlaps the ledges
    assert LEDGE_Z + P["ear_t"] + 2.5 < DEPTH  # M3 heads inside, under the lid
    assert 2 <= P["proud"] <= 4  # ~3 of the buzzer's housing shows above the lid (owner)
    assert P["hole_pitch"] / 2 + P["hole_d"] / 2 < P["mod_w"] / 2  # screw holes inside the board's edges
    assert P["ear_span"] < P["in_l"]
    assert P["in_w"] - P["buzzer_d"] >= 6  # room for the leads leaving the buzzer's side
    assert P["body_hole_d"] > P["buzzer_d"]
    assert abs(P["hole_x"]) - P["hole_w"] / 2 > P["tab_base"] - 0.5  # ...and of the tab


def test_seat_pocket_and_pilots(box):
    pocket_y = -P["mod_l"] / 2 + P["pocket_gap"] + P["pocket_l"] / 2
    hole_e = P["hole_gap"] + P["hole_d"] / 2
    assert np.isclose(ray_hits(box, (0, pocket_y, DEPTH + 5), (0, 0, -1))[0][2], P["floor_t"], atol=0.05)
    assert np.isclose(ray_hits(box, (0, 0, DEPTH + 5), (0, 0, -1))[0][2], SEAT_Z, atol=0.05)
    for s in (-1, 1):
        hit = ray_hits(box, (s * P["hole_pitch"] / 2, P["mod_l"] / 2 - hole_e, DEPTH + 5), (0, 0, -1))[0][2]
        assert np.isclose(hit, SEAT_Z - P["m25_depth"], atol=0.05)  # blind, deep enough for a longer M2.5


def test_insert_columns_at_ear_holes(box):
    for x, y in EAR_XY:
        hits = ray_hits(box, (x, y, DEPTH + 5), (0, 0, -1))
        assert np.isclose(hits[0][2], LEDGE_Z - INSERT_DEPTH, atol=0.05)  # blind insert hole in the column top
        rim = ray_hits(box, (x + COL_R - 0.5, y, DEPTH + 5), (0, 0, -1))[0][2]
        assert np.isclose(rim, LEDGE_Z, atol=0.05)
        inner = x - np.sign(x) * (COL_R - 0.5)  # the boss edge toward the module
        hits = ray_hits(box, (inner, y, DEPTH + 5), (0, 0, -1))
        assert np.isclose(hits[0][2], LEDGE_Z, atol=0.05)
        assert hits[1][2] > LEDGE_Z - INSERT_DEPTH - P["insert_floor"] - 0.6  # boss hangs off the wall
        assert np.isclose(hits[2][2], P["floor_t"], atol=0.05)  # floor clear under it, room for ferrules


def test_seat_ledges_mid_wall(box):
    for s in (-1, 1):
        assert np.isclose(ray_hits(box, (s * (P["in_w"] / 2 - 1), 0, DEPTH + 5), (0, 0, -1))[0][2], LEDGE_Z, atol=0.05)
        assert ray_hits(box, (s * (P["in_w"] / 2 - P["ledge_reach"] - 0.5), 0, DEPTH + 5), (0, 0, -1))[0][2] < LEDGE_Z - 5


TIES = [(-13, -21.5, 0), (-13, 5, 0), (13, -21.5, 0)]  # A 12 V pair, B signal, C buzzer leads


def test_tie_staples_closed(box):
    peak = P["floor_t"] + P["tie_gap"]
    zt = P["floor_t"] + P["tie_gap"] / 2
    for x, y, a in TIES:
        hits = ray_hits(box, (x, y, peak + P["tie_deck_t"] + 1), (0, 0, -1))[:3]  # B sits under a seat ledge
        assert np.isclose(hits[0][2], peak + P["tie_deck_t"], atol=0.05)
        assert np.isclose(hits[1][2], peak, atol=0.05)  # tunnel roof
        assert np.isclose(hits[2][2], P["floor_t"], atol=0.05)
        u = np.array([np.cos(np.radians(a)), np.sin(np.radians(a)), 0])  # the way the tie runs
        v = np.array([-u[1], u[0], 0])
        for dv in (-P["tie_span"] / 2 + 0.3, P["tie_span"] / 2 - 0.3):  # tunnel open end to end
            start = np.array([x, y, zt]) + dv * v - (P["tie_deck_w"] / 2 + 0.5) * u
            through = ray_hits(box, tuple(start), tuple(u))
            assert np.dot(through[0] - start, u) > P["tie_deck_w"] + 1
        for sv in (-1, 1):  # closed: a pier each side of the tunnel
            side = np.array([x, y, zt]) + sv * (P["tie_span"] / 2 + P["tie_pier"] / 2) * v + (P["tie_deck_w"] / 2 + 0.5) * u
            assert np.dot(ray_hits(box, tuple(side), tuple(-u))[0] - side, -u) < 0.6


def test_lid_has_only_the_body_hole(lid):
    for x, y in EAR_XY:
        assert len(ray_hits(lid, (x, y, -1), (0, 0, 1))) == 2  # no screw holes: the buzzer screws are inside


def test_two_tab_holes_through(box):
    for s in (-1, 1):
        assert len(ray_hits(box, (0, s * TAB_Y, -1), (0, 0, 1))) == 0


def test_mousehole_at_floor_terminal_end(box):
    z = P["floor_t"] + 1
    hits = ray_hits(box, (P["hole_x"], -OUT_L, z), (0, 1, 0))
    assert hits[0][1] > -P["in_l"] / 2 + 1  # passes the terminal-end wall at its foot
    above = P["floor_t"] + P["hole_side"] + P["hole_w"] / 2 + 0.5
    assert ray_hits(box, (P["hole_x"], -OUT_L, above), (0, 1, 0))[0][1] < -P["in_l"] / 2  # wall above the roof


TIP_Y = (P["ear_span"] / 2 - P["ear_r"]) * np.cos(EAR_A) - P["ear_r"]  # ear tip's near edge along Y
FINGER_HI = P["in_l"] / 2 - P["in_r"] - P["finger_end"]
FINGER_LO = -(TIP_Y - P["ear_clear"])
# +X wall: finger over [FINGER_LO, FINGER_HI]; -X wall: the same turned 180°


def test_finger_strain():
    # cantilever: strain = 1.5 t y / L^2, y = how far the ridge must push the finger in
    y = P["snap_d"] - P["skirt_gap"]
    assert 1.5 * P["skirt_t"] * y / P["snap_z"] ** 2 < 0.035  # PETG, repeated snaps
    assert P["snap_d"] + 0.1 < P["groove_d"] + P["skirt_gap"]  # finger springs fully back in the pocket
    assert P["groove_d"] <= P["wall"] - 1


def test_one_long_finger_each_long_wall(lid):
    x = P["in_w"] / 2 - P["skirt_gap"] + P["snap_d"] / 2
    z = P["lid_t"] + P["snap_z"]
    for sx in (-1, 1):
        hits = ray_hits(lid, (sx * x, -50, z), (0, 1, 0))
        assert len(hits) == 2  # one continuous ridge
        lo, hi = sorted((-sx * FINGER_LO, -sx * FINGER_HI))  # print pose: the installed layout mirrored in X
        assert np.isclose(hits[0][1], lo, atol=0.05) and np.isclose(hits[1][1], hi, atol=0.05)
    assert FINGER_HI - FINGER_LO > 30  # long: holds along most of the wall


def test_fingers_clear_the_ear_tips():
    # the ear on the +X wall sits at -Y; its tip spans |y| >= TIP_Y and reaches within ear_tip_gap of the wall
    for ex, ey in EAR_XY:
        sx = 1 if ex > 0 else -1
        lo, hi = sorted((sx * FINGER_LO, sx * FINGER_HI))
        assert not (lo - P["ear_clear"] + 0.01 < ey < hi + P["ear_clear"] - 0.01)
        tip_cy = abs(ey) / (P["ear_pitch"] / 2) * (P["ear_span"] / 2 - P["ear_r"])  # tip centre lies further out than the hole
        assert tip_cy - P["ear_r"] - P["ear_clear"] >= -FINGER_LO - 0.01


def test_pockets_line_up_with_ridges(box):
    z = DEPTH - P["snap_z"]
    for sx in (-1, 1):
        mid = sx * (FINGER_LO + FINGER_HI) / 2
        hit = ray_hits(box, (0, mid, z), (sx, 0, 0))[0]
        assert np.isclose(abs(hit[0]), P["in_w"] / 2 + P["groove_d"], atol=0.05)
        plain = ray_hits(box, (0, -sx * 20, z), (sx, 0, 0))[0]
        assert np.isclose(abs(plain[0]), P["in_w"] / 2, atol=0.05)  # no groove by the ear


def test_body_hole_through_lid(lid):
    assert len(ray_hits(lid, (0, 0, -1), (0, 0, 1))) == 0


def test_end_stops_key_the_lid_lengthwise(lid):
    # a stiff rib across each end wall, 0.2 off it: the lid can't slide along the box (owner)
    z = P["lid_t"] + P["stop_h"] / 2
    face = P["in_l"] / 2 - P["stop_gap"]
    for x in (-P["in_w"] / 2 + P["in_r"] + 0.5, 0, P["in_w"] / 2 - P["in_r"] - 0.5):
        hits = ray_hits(lid, (x, -50, z), (0, 1, 0))
        assert np.isclose(hits[0][1], -face, atol=0.05) and np.isclose(hits[-1][1], face, atol=0.05)
    assert face - P["stop_t"] > FINGER_HI + 0.5  # stops don't join the fingers, which still bend from the lid alone
    assert P["stop_h"] < DEPTH - (LEDGE_Z + P["ear_t"] + 2)


# A hand turns the printed lid over; it cannot mirror it. Both turns (about Y and about X) give the same pose here.
@pytest.mark.parametrize("flip", TURNS)
def test_printed_lid_turned_over_fits_printed_box(box, lid, flip, tmp_path):
    # on the meshes that get printed, in the pose they are used: no lid material inside the box, and the
    # fingers clear the buzzer's ear tips. A lid that only fits as its mirror image fails here.
    place = f'translate([0, 0, {DEPTH + P["lid_t"]}]) {TURNS[flip]}'
    assert seated_overlap(tmp_path, box, lid, place) < 0.01
    assert seated_overlap(tmp_path, box, lid, place, mirror="[1, 0, 0]") > 1  # the test sees the mirror image
    seated = lid.copy()
    seated.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [0, 1, 0] if flip == "about Y" else [1, 0, 0]))
    seated.apply_translation([0, 0, DEPTH + P["lid_t"]])
    for ex, ey in EAR_XY:  # nothing hangs down at the ear tip, by the wall
        x = np.sign(ex) * (P["in_w"] / 2 - P["skirt_gap"] - P["skirt_t"] / 2)
        assert len(ray_hits(seated, (x, ey, 0), (0, 0, 1))) == 2  # the lid plate only
