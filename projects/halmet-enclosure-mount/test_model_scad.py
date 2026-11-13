"""Tests for the HALMET enclosure frame: bounding box, volume window, feature counts."""

import json
import re
from pathlib import Path

import ezdxf
import numpy as np
import pytest
import trimesh
from shop.scad import build_scad, find_openscad
from shop.testing import ray_hits

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")


def params(path: Path) -> dict[str, float]:
    return {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*([-\d.]+)\s*;", path.read_text(), re.M)}


def lists(path: Path) -> dict[str, list]:
    return {k: json.loads(v) for k, v in re.findall(r"^(\w+)\s*=\s*(\[[-\d.,\s\[\]]*\]);", path.read_text(), re.M)}


P = params(HERE / "model.scad")
LISTS = lists(HERE / "model.scad")
DROP = 0.0  # flat underside resting on the bosses
T, H = P["plate_t"] + DROP, P["standoff_h"]  # T: full body thickness
SPAN, PITCH, REACH = P["boss_span"], P["boss_pitch"], P["slot_reach"]
DX, DY = P["board_dx"], P["board_dy"]
SLOTS = [(-21.75 + DX, 22.5 + DY), (22.75 + DX, -22.5 + DY)]
RESTS = [(36 + DX, 18 + DY), (-38.5 + DX, -19.5 + DY)]
COLS = LISTS["tier_cols"]
TIER_TOP = P["plate_t"] + P["tier_pad"] + P["tier_standoff"] + P["tier_t"]  # Z = 0 is the boss top
TIER_Z0 = TIER_TOP - P["tier_t"] - P["tier_standoff"]  # standoff feet on the plate's pads
SEG_Y = P["oled_y"] - P["oled_h"] / 2 - P["seg_gap"] - P["seg_h"] / 2
MOD_POSTS = [(P["oled_x"] + sx * P["oled_hole_dx"] / 2, P["oled_y"] + sy * P["oled_hole_dy"] / 2)
             for sx in (-1, 1) for sy in (-1, 1)]
MOD_POSTS += [(P["oled_x"] + sx * P["seg_hole_dx"] / 2, SEG_Y + sy * P["seg_hole_dy"] / 2) for sx in (-1, 1) for sy in (-1, 1)]
USB_Y = 16.5 - 29 + DY                    # USB-C centre on the board's right edge
BOARD_RIGHT = 44.5 + DX
VOL_LO, VOL_HI = 23000, 32000  # first hex-plate build: 25789; with the tier pads and sensor seats 29833


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    d = tmp_path_factory.mktemp("halmet")
    src = d / "model.scad"
    src.write_text((HERE / "model.scad").read_text())
    return build_scad(src, d, "frame", two_d=True, render=False)


@pytest.fixture(scope="module")
def tier(tmp_path_factory):
    d = tmp_path_factory.mktemp("halmet_tier")
    for f in ("model.scad", "part-tier.scad"):
        (d / f).write_text((HERE / f).read_text())
    return trimesh.load(build_scad(d / "part-tier.scad", d, "tier", render=False)["stl"])


@pytest.fixture(scope="module")
def frame(built):
    return trimesh.load(built["stl"])


def top(mesh, x, y):
    h = ray_hits(mesh, (x, y, 50), (0, 0, -1))
    return h[0][2] if h else None


def test_bounds_volume_watertight(frame):
    assert frame.is_watertight
    lo, hi = frame.bounds
    assert np.allclose([lo[0], hi[0]], [-SPAN / 2 - REACH, SPAN / 2 + REACH], atol=0.05)
    assert np.isclose(lo[2], 0, atol=0.02) and np.isclose(hi[2], max(T + H, TIER_Z0), atol=0.02)
    assert np.allclose([lo[1], hi[1]], [-P["frame_w"] / 2, P["plate_y_hi"]], atol=0.05)  # straight back edge
    assert hi[1] < 83 / 2  # inside the box floor
    assert VOL_LO < frame.volume < VOL_HI  # mm^3; a solid 144 x 75 x 4.5 plate is 48600


def test_one_body_lightened(frame):
    assert len(frame.split(only_watertight=False)) == 1  # every post and island joined
    for x, y in [(-30.0, 0.0), (10.0, 0.0), (45.0, 10.0)]:  # open cells under the board and the tier
        assert any(top(frame, x + dx, y + dy) is None for dx in (-3, 0, 3) for dy in (-3, 0, 3))


def test_board_is_89_by_58_slot_pattern():
    (x0, y0), (x1, y1) = SLOTS
    assert np.isclose(x1 - x0, 44.5) and np.isclose(y0 - y1, 45.0)


def test_two_standoffs_with_blind_insert_holes(frame):
    for x, y in SLOTS:
        assert np.isclose(top(frame, x, y), T + H - P["insert_depth"], atol=0.02)
        assert T + H - P["insert_depth"] > 0.5
        assert np.isclose(top(frame, x + P["insert_d"] / 2 + 0.7, y), T + H, atol=0.02)
        assert P["standoff_d"] - P["insert_d"] >= 3.2  # 1.6 mm wall around the insert


def test_two_rests_level_with_standoffs(frame):
    for x, y in RESTS:
        assert np.isclose(top(frame, x, y), T + H, atol=0.02)


def test_six_fork_slots_open_over_the_bosses(frame):
    for sx in (-1, 1):
        for k in (-1, 0, 1):
            y = k * PITCH
            for off in (-REACH, 0, REACH):  # boss anywhere in the stated reach
                assert top(frame, sx * (SPAN / 2 + off), y) is None
            assert np.isclose(top(frame, sx * SPAN / 2, y + PITCH / 2 if k < 0 else y - 4), T, atol=0.02)


def test_laser_profile_is_millimetres_on_cut_layer(built):
    doc = ezdxf.readfile(built["dxf"])
    assert doc.header["$INSUNITS"] == 4
    ents = list(doc.modelspace())
    assert ents and {e.dxf.layer for e in ents} == {"cut"}


def bottom(mesh, x, y):
    h = ray_hits(mesh, (x, y, -50), (0, 0, 1))
    return h[0][2] if h else None


def test_pads_cover_the_four_posts(frame):
    for sx in (-1, 1):
        for sy in (-1, 1):
            for ox in (-4, 0, 4):  # post anywhere within 4 mm of post_dx
                assert np.isclose(bottom(frame, sx * P["post_dx"] / 2 + ox, sy * P["post_dy"] / 2), 0, atol=0.02)


def test_underside_flat_over_bosses_and_posts(frame):
    assert DROP == 0
    for sx in (-1, 1):
        for k in (-1, 0, 1):
            x, y = sx * SPAN / 2, k * PITCH + (P["screw_d"] / 2 + 1.5)  # beside the slot, over the boss rim
            assert np.isclose(bottom(frame, x, y), 0, atol=0.02)


def test_tie_slots_chamfered_underneath_on_the_outer_edge(frame):
    for x in LISTS["tie_bar_xs"]:
        outer = x + P["tie_gap"] / 2 + P["tie_t"] / 2  # outer edge of the right-hand slot
        assert np.isclose(bottom(frame, outer + P["tie_c"] / 2, P["tie_bar_y"]), P["tie_c"] / 2, atol=0.05)
        web = x + P["tie_gap"] / 2 - P["tie_t"] / 2 - 0.2  # web side stays square
        assert np.isclose(bottom(frame, web, P["tie_bar_y"]), 0, atol=0.02)


def test_zip_tie_slots_open(frame):
    assert len(LISTS["tie_bar_xs"]) == 6  # six gland-side ties
    pairs = [(x + s * P["tie_gap"] / 2, P["tie_bar_y"]) for x in LISTS["tie_bar_xs"] for s in (-1, 1)]
    x_end = -(SPAN / 2 - REACH - P["screw_d"] / 2 - 3 + SPAN / 2 + REACH) / 2
    pairs += [(x_end, y + s * P["tie_gap"] / 2) for y in (-10.5, 10.5) for s in (-1, 1)]
    for x, y in pairs:
        assert top(frame, x, y) is None
    for x in LISTS["tie_bar_xs"]:  # web between the two slots of a pair carries the tie
        assert np.isclose(top(frame, x, P["tie_bar_y"]), T, atol=0.02)


def test_board_clear_of_the_left_fork_slots():
    left_edge = -44.5 + DX
    assert left_edge > -(SPAN / 2 - REACH) + P["screw_d"] / 2  # a driver reaches every left screw


def test_plate_has_counterbored_pads_under_the_tier_standoffs(frame):
    assert TIER_Z0 == pytest.approx(T + P["tier_pad"])  # standoffs seat on the plate
    for x, y in COLS:
        assert top(frame, x, y) is None  # M3 passes up through
        assert np.isclose(top(frame, x + P["insert_d"] / 2 + 0.7, y), TIER_Z0, atol=0.02)
        assert np.isclose(bottom(frame, x + P["screw_d"] / 2 + 0.6, y), P["head_h"], atol=0.02)  # head counterbore
        assert P["head_d"] < P["tier_boss_d"]


def test_tier_is_a_flat_plate_at_the_rim(tier):
    assert tier.is_watertight and tier.body_count == 1
    lo, hi = tier.bounds
    assert np.isclose(lo[2], TIER_TOP - P["tier_t"] - P["ldr_boss_h"], atol=0.02)  # the sensor's screw boss hangs below
    assert np.isclose(hi[2], TIER_TOP + P["ldr_ledge"] + P["pcb_t"], atol=0.02)  # cradle walls on top
    assert hi[0] < 151 / 2 - 2 and hi[1] <= P["plate_y_hi"] + 0.01  # inside the floor


def test_tier_holes_for_standoff_screws_and_module_screws(tier):
    for x, y in [*COLS, *MOD_POSTS]:
        assert top(tier, x, y) is None
    for x, y in COLS:
        assert np.isclose(top(tier, x + P["screw_d"] / 2 + 0.6, y), TIER_TOP, atol=0.02)  # plate seats on the standoff


def test_tier_clears_lid_column_board_and_usb_plug(tier):
    for v in tier.vertices:
        assert v[0] <= P["lid_col_x"] - 0.5 or v[1] <= P["lid_col_y"] - 0.5
    assert P["tier_x0"] - BOARD_RIGHT >= 2
    for z in (12.0, 15.0):  # USB-C plug path along +X from the board edge
        assert not ray_hits(tier, (BOARD_RIGHT, USB_Y, z), (1, 0, 0)) or ray_hits(tier, (BOARD_RIGHT, USB_Y, z), (1, 0, 0))[0][0] > BOARD_RIGHT + 30


@pytest.fixture(scope="module")
def gauge(tmp_path_factory):
    d = tmp_path_factory.mktemp("halmet_gauge")
    for f in ("model.scad", "part-gauge.scad"):
        (d / f).write_text((HERE / f).read_text())
    return trimesh.load(build_scad(d / "part-gauge.scad", d, "gauge", render=False)["stl"])


def test_gauge_is_a_thin_open_plate_with_the_frame_outline(gauge, frame):
    assert gauge.is_watertight and gauge.body_count == 1
    assert np.allclose(gauge.bounds[:, :2], frame.bounds[:, :2], atol=0.05)
    assert gauge.bounds[1, 2] == pytest.approx(P["gauge_t"] + P["gauge_rise"], abs=0.02)
    assert 4000 < gauge.volume < 9000  # mm^3; first windowed build 6699, solid 1 mm plate 12062


def test_gauge_keeps_fork_slots_and_marks_raised_features_with_holes(gauge):
    for sx in (-1, 1):
        for k in (-1, 0, 1):
            assert top(gauge, sx * SPAN / 2, k * PITCH) is None
            assert top(gauge, sx * SPAN / 2, k * PITCH + (PITCH / 2 if k < 0 else -4)) == pytest.approx(P["gauge_t"], abs=0.02)
    for x, y in [*SLOTS, *RESTS, *COLS]:
        assert top(gauge, x, y) is None  # centre holed through
    for x, y in [*SLOTS, *COLS]:
        assert top(gauge, x + P["insert_d"] / 2 + 0.7, y) == pytest.approx(P["gauge_t"] + P["gauge_rise"], abs=0.02)


# Light sensor: an LM393 module in a cradle on the tier, under the OLED, one M3 screw
LDR_X0, LDR_Y, LDR_L, LDR_W = P["ldr_x0"], P["ldr_y"], P["ldr_l"], P["ldr_w"]
LDR_HOLE = (LDR_X0 + P["ldr_hole_in"], LDR_Y)
LDR_Z = TIER_TOP + P["ldr_ledge"]  # module underside
M25_R = 5 / 3 ** 0.5  # M2.5 hex standoff, 5 across flats: corner radius


def test_cradle_ledges_walls_and_screw_boss(tier):
    w = LDR_W + 2 * P["ldr_fit"]
    mid = LDR_X0 + LDR_L / 2
    for s in (-1, 1):
        assert top(tier, mid, LDR_Y + s * (w / 2 - 1)) == pytest.approx(LDR_Z, abs=0.02)  # edge ledge
        assert top(tier, mid, LDR_Y + s * (w / 2 + P["ldr_wall"] / 2)) == pytest.approx(LDR_Z + P["pcb_t"], abs=0.02)  # wall
    assert top(tier, mid, LDR_Y) == pytest.approx(TIER_TOP, abs=0.02)  # open between the ledges for solder stubs
    assert top(tier, *LDR_HOLE) is None  # pilot through
    assert top(tier, LDR_HOLE[0] + P["ldr_pilot"] / 2 + 1, LDR_HOLE[1]) == pytest.approx(LDR_Z, abs=0.02)
    assert bottom(tier, LDR_HOLE[0] + P["ldr_pilot"] / 2 + 1, LDR_HOLE[1]) == pytest.approx(
        TIER_TOP - P["tier_t"] - P["ldr_boss_h"], abs=0.02)


def test_sensor_fits_under_the_oled_and_sees_the_lid():
    oled_under = TIER_TOP + P["mod_standoff"]
    assert LDR_Z + P["pcb_t"] + P["ldr_part_h"] + 1 <= oled_under  # trimpot clears the OLED by a millimetre
    assert LDR_X0 + LDR_L > P["oled_x"] + P["oled_w"] / 2 + 2  # photocell end out past the OLED's right edge
    for cx, cy in MOD_POSTS[:4]:  # OLED standoffs pass beside the cradle walls
        assert abs(cy - LDR_Y) > LDR_W / 2 + P["ldr_fit"] + P["ldr_wall"] + M25_R
    assert LDR_Y + LDR_W / 2 < P["lid_col_y"]  # board edge clear of the lid-screw column
    assert LDR_X0 > P["tier_x0"]  # whole board on the tier, none over the HALMET


def test_sensor_plug_runs_out_over_the_halmet():
    assert LDR_Z + 3 > T + H + 1.6 + 10  # plug runs out over the HALMET, above its tall parts
    assert LDR_Z + P["pcb_t"] + 2.5 + 1 < TIER_TOP + P["mod_standoff"]  # and under the OLED
