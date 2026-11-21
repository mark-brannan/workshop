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
RECESS = max(0.0, P["boss_h"] - P["post_h"])  # underside pocket over each holed boss
T, H = P["plate_t"], P["standoff_h"]  # T: full body thickness
SPAN, PITCH, REACH = P["boss_span"], P["boss_pitch"], P["slot_reach"]
IN = P["slot_in"]  # extra reach on the inner end
DX, DY = P["board_dx"], P["board_dy"]
SLOTS = [(-21.75 + DX, 22.5 + DY), (22.75 + DX, -22.5 + DY)]
RESTS = [(36 + DX, 18 + DY), (-38.5 + DX, -19.5 + DY)]
COLS = LISTS["tier_cols"]
MID = LISTS["mid_cols"]
PADS = COLS + MID
TIER_Z0 = P["tier_pad_h"]                # standoff feet on the plate's pads
TIER_TOP = TIER_Z0 + P["tier_standoff"] + P["tier_t"]
SEG_Y = P["seg_y"]
SEG2_Y = SEG_Y + P["seg_h"] + P["seg_gap"]  # the upper module, where the OLED was
MOD_POSTS = [(P["seg_x"] + sx * P["seg_hole_dx"] / 2, y + sy * P["seg_hole_dy"] / 2)
             for y in (SEG2_Y, SEG_Y) for sx in (-1, 1) for sy in (-1, 1)]
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
def frame(built):
    return trimesh.load(built["stl"])


def top(mesh, x, y):
    h = ray_hits(mesh, (x, y, 50), (0, 0, -1))
    return h[0][2] if h else None


def test_bounds_volume_watertight(frame):
    assert frame.is_watertight
    lo, hi = frame.bounds
    assert np.allclose([lo[0], hi[0]], [-SPAN / 2 - REACH - P["end_ext"], SPAN / 2 + REACH + P["end_ext"]], atol=0.05)
    assert np.isclose(lo[2], 0, atol=0.02) and np.isclose(hi[2], max(T + H, TIER_Z0, T + P["tie_rise"]), atol=0.02)
    back = max(P["plate_y_hi"], *(y + P["tier_boss_d"] / 2 for _, y in PADS))  # straight back edge, bulged by a pad
    assert np.allclose([lo[1], hi[1]], [-P["frame_w"] / 2, back], atol=0.05)
    assert hi[1] <= 83 / 2 - 1  # inside the box floor
    assert VOL_LO < frame.volume < VOL_HI  # mm^3; a solid 144 x 75 x 4 plate is 43200


def test_one_body_lightened(frame):
    assert len(frame.split(only_watertight=False)) == 1  # every post and island joined
    for x, y in [(-30.0, 0.0), (10.0, 0.0), (45.0, 10.0)]:  # open cells under the board and the tier
        assert any(top(frame, x + dx, y + dy) is None for dx in (-3, 0, 3) for dy in (-3, 0, 3))


def test_board_is_89_by_58_slot_pattern():
    (x0, y0), (x1, y1) = SLOTS
    assert np.isclose(x1 - x0, 44.5) and np.isclose(y0 - y1, 45.0)


def test_two_standoffs_with_through_insert_holes(frame):
    for x, y in SLOTS:
        assert top(frame, x, y) is None
        assert np.isclose(top(frame, x + P["insert_d"] / 2 + 0.7, y), T + H, atol=0.02)
        assert P["standoff_d"] - P["insert_d"] >= 3.0  # 1.5 mm wall around the insert


def test_two_rests_level_with_standoffs(frame):
    for x, y in RESTS:
        assert np.isclose(top(frame, x, y), T + H, atol=0.02)


def test_slots_are_closed_pills(frame):
    for sx in (-1, 1):
        for k in (-1, 0, 1):
            x = sx * (SPAN / 2 + REACH + P["slot_d"] / 2 + 0.5)  # just past the outer end
            assert top(frame, x, k * PITCH) is not None  # floor under the relief, not open


def test_six_fork_slots_open_over_the_bosses(frame):
    for sx in (-1, 1):
        for k in (-1, 0, 1):
            y = k * PITCH
            for off in (-REACH - IN, 0, REACH):  # boss anywhere in the stated reach
                assert top(frame, sx * (SPAN / 2 + off), y) is None
            assert np.isclose(top(frame, sx * SPAN / 2, y + 4 if k < 0 else y - 4), T, atol=0.02)  # solid bar beside the boss, clear of the end tie loops


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
            for ox in ((-2, 0, 2) if sy < 0 else (0,)):  # front: post anywhere within its tab; back-left sits beside a through hole
                assert np.isclose(bottom(frame, sx * P["post_dx"] / 2 + ox, sy * P["post_dy"] / 2), 0, atol=0.02)


def test_underside_recessed_over_bosses_flat_on_posts(frame):
    assert RECESS == 1.0  # boss 3.5 over a 2.5 post
    for sx in (-1, 1):
        for k in (-1, 0, 1):
            x, y = sx * SPAN / 2, k * PITCH + (P["slot_d"] / 2 + 1.5)  # beside the slot, over the boss rim
            assert np.isclose(bottom(frame, x, y), RECESS, atol=0.02)


TIE_TOP = T + P["tie_rise"]
X_END = -(SPAN / 2 - REACH - IN - P["screw_d"] / 2 - 3 + SPAN / 2 + REACH + P["end_ext"]) / 2
LOOPS = [(x, P["tie_bar_y"], 1, 0) for x in LISTS["tie_bar_xs"]] + [(X_END, y, 0, 1) for y in LISTS["tie_end_ys"]]  # centre, run direction


def test_tie_staples_worked_from_above(frame):
    assert len(LOOPS) == 8  # six gland-side, two on the left end
    assert P["tie_bar_y"] - (P["tie_w"] / 2 + P["tie_wall"]) - P["tie_foot"] > P["plate_y_lo"]  # foot chamfer stays on the plate, clear of the tab bevel
    assert P["tie_rise"] - P["tie_t"] - P["tie_round"] - P["tie_mouth"] >= 0.4  # roof keeps a flat band between its top round and the mouth flare
    for x, y, ux, uy in LOOPS:
        hits = [h[2] for h in ray_hits(frame, (x, y, 50), (0, 0, -1))]
        assert np.isclose(hits[0], TIE_TOP, atol=0.02)  # flat top
        assert np.isclose(hits[1], T + P["tie_t"], atol=0.02)  # flat roof
        assert np.isclose(hits[2], T, atol=0.02)  # slot floor is the plate top
        z = T + P["tie_t"] / 2  # through the slot along the run: nothing in the way
        through = ray_hits(frame, (x - ux * 10, y - uy * 10, z), (ux, uy, 0))
        assert not any(abs((h[0] - x) * ux + (h[1] - y) * uy) < P["tie_len"] for h in through)
        assert np.isclose(bottom(frame, x, y), 0, atol=0.02)  # underside untouched


def test_board_clear_of_the_left_fork_slots():
    left_edge = -44.5 + DX
    assert left_edge > -(SPAN / 2 - REACH - IN) + P["slot_d"] / 2  # a driver reaches every left screw


def test_plate_has_insert_pads_under_the_tier_and_mid_tier_standoffs(frame):
    assert len(COLS) == 3 and len(MID) == 4
    for x, y in PADS:
        assert np.isclose(top(frame, x + P["insert_d"] / 2 + 0.7, y), TIER_Z0, atol=0.02)
        assert top(frame, x, y) is None  # insert hole runs through, open both ends


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
    for x, y in [*SLOTS, *RESTS, *PADS]:
        assert top(gauge, x, y) is None  # centre holed through
    for x, y in [*SLOTS, *PADS]:
        assert top(gauge, x + P["insert_d"] / 2 + 0.7, y) == pytest.approx(P["gauge_t"] + P["gauge_rise"], abs=0.02)


# Light sensor: an LM393 module in a cradle on the tier, under the OLED, one M3 screw
LDR_X0, LDR_Y, LDR_L, LDR_W = P["ldr_x0"], P["ldr_y"], P["ldr_l"], P["ldr_w"]
LDR_HOLE = (LDR_X0 + LDR_L - P["ldr_hole_in"], LDR_Y)
LDR_Z = TIER_TOP + P["ldr_ledge"]  # module underside
M3_HEX_R = 5.5 / 3 ** 0.5   # tier standoff, 5.5 across flats: corner radius
M25_HEX_R = 5 / 3 ** 0.5    # module standoff, 5 across flats


def test_sensor_fits_under_the_modules_and_clear_of_their_standoffs():
    assert LDR_Z + P["pcb_t"] + P["ldr_part_h"] + 1 <= TIER_TOP + P["mod_standoff"]  # trimpot clears the OLED
    for cx, cy in MOD_POSTS:
        assert abs(cy - LDR_Y) > LDR_W / 2 + M25_HEX_R + 0.3 or cx - M25_HEX_R > LDR_X0 + LDR_L


def test_board_and_straight_pins_clear_the_tier_screw_heads():
    x_end = LDR_X0 + LDR_L
    board = (LDR_X0, LDR_Y - LDR_W / 2, x_end, LDR_Y + LDR_W / 2)
    pins = (x_end, LDR_Y - 3.2, x_end + P["ldr_pin_l"], LDR_Y + 3.2)
    for cx, cy in COLS:  # M3 heads on the tier top: the board clears them in plan
        dx, dy = max(board[0] - cx, 0, cx - board[2]), max(board[1] - cy, 0, cy - board[3])
        assert (dx * dx + dy * dy) ** 0.5 > P["head_d"] / 2 + 0.3
    pin_z = LDR_Z + P["pcb_t"] + 0.94  # right-angle pins run ~1 above the board top
    assert pin_z > TIER_TOP + P["head_h"] + 0.5  # and the pins pass over the back-right head
    assert LDR_X0 >= P["tier_x0"] - 1  # photocell end at the tier's left edge, none of it over the HALMET


def test_photocell_end_clear_of_the_halmet_in_plan():
    assert LDR_X0 - 3.5 > 44.5 + DX - 6  # board edge steps in 6 above the USB tab


def test_centre_prop_through_hole_in_a_solid_island(frame):
    cx, cy = LISTS["support_xy"]
    assert top(frame, cx, cy) is None and bottom(frame, cx, cy) is None  # open top to bottom
    for a in range(0, 360, 45):  # solid ring: insert wall 2 mm out to the standoff diameter, no lattice cell
        r = (P["insert_d"] / 2 + 0.7) if a % 90 == 0 else P["standoff_d"] / 2 - 0.3
        x, y = cx + r * np.cos(np.radians(a)), cy + r * np.sin(np.radians(a))
        assert np.isclose(top(frame, x, y), T, atol=0.02)


# Tier fit gauge: two square plates, hollowed, one per display module
def test_tier_gauge_plates_are_square_hollow_and_holed(tmp_path):
    src = (HERE / "part-tier-gauge.scad").read_text()
    g = params(HERE / "part-tier-gauge.scad")
    (tmp_path / "part-tier-gauge.scad").write_text(src)
    m = trimesh.load(build_scad(tmp_path / "part-tier-gauge.scad", tmp_path, "tg", render=False)["stl"])
    assert m.is_watertight and m.body_count == 2
    parts = sorted(m.split(), key=lambda p: p.extents[0])
    for part, dx, dy in zip(parts, (g["oled_hole_dx"], g["seg_hole_dx"]), (g["oled_hole_dy"], g["seg_hole_dy"])):
        e = part.extents
        pad = g["hole_d"] + 2 * g["margin"]
        assert e == pytest.approx([dx + pad, dy + pad, g["thickness"]], abs=0.02)
        cx, cy = part.bounds.mean(axis=0)[:2]
        assert top(part, cx, cy) is None  # centre cut out
        for sx in (-1, 1):
            for sy in (-1, 1):
                assert top(part, cx + sx * dx / 2, cy + sy * dy / 2) is None  # hole through
        assert top(part, cx + dx / 2 + g["hole_d"] / 2 + g["margin"] / 2, cy) == pytest.approx(g["thickness"], abs=0.02)  # band is solid
    assert g["seg_hole_dx"] == P["seg_hole_dx"] and g["oled_hole_dy"] == P["oled_hole_dy"]  # same numbers as the tier


# Standoff pads in plan against what sits on or near the plate
HALMET = [(8.5, 0), (80.5, 0), *[(89 + 8.5 * np.cos(a), 8.5 * np.sin(a)) for a in np.radians(np.linspace(180, 90, 17))],
          (89, 24.7), (83, 24.7), (83, 51.98), (81.15, 54.74), (80.5, 58), (8.5, 58),
          *[(8.5 * np.cos(a), 58 + 8.5 * np.sin(a)) for a in np.radians(np.linspace(0, -90, 17))], (0, 8.5),
          *[(8.5 * np.cos(a), 8.5 * np.sin(a)) for a in np.radians(np.linspace(90, 0, 17))]]  # HALMET.kicad_pcb, as overlay.py
STANDOFF_R = 6.4 / 2  # M3 hex standoff body, across corners


def keep_out():
    from shapely.geometry import LineString, Point, Polygon, box
    from shapely.ops import unary_union
    ox, oy = -44.5 + DX, -29 + DY
    board = Polygon([(x + ox, y + oy) for x, y in HALMET])
    esp32 = box(60.5 + ox, 30 + oy, 86 + ox, 48 + oy)  # ESP32 module, overhanging the board's right edge
    usb = box(BOARD_RIGHT, -6, 75.5, 6)  # USB plug path to the right wall
    heads = unary_union([LineString([(sx * (SPAN / 2 - REACH - IN), k * PITCH), (sx * (SPAN / 2 + REACH), k * PITCH)]).buffer(P["head_d"] / 2)
                         for sx in (-1, 1) for k in (-1, 0, 1)])  # floor-screw heads anywhere along their fork slots
    ties = unary_union([box(x - P["tie_len"] / 2 - 2, P["tie_bar_y"] - P["tie_w"] / 2, x + P["tie_len"] / 2 + 2, P["tie_bar_y"] + P["tie_w"] / 2)
                        for x in LISTS["tie_bar_xs"]])  # the tunnel and 2 mm either side, where the tie runs
    halmet_posts = unary_union([Point(p).buffer(P["standoff_d"] / 2) for p in SLOTS] + [Point(p).buffer(P["rest_d"] / 2) for p in RESTS])
    return {"board": unary_union([board, esp32]), "usb": usb, "floor heads": heads, "ties": ties, "halmet posts": halmet_posts}


def test_standoff_pads_clear_board_usb_floor_screws_ties_and_each_other():
    from shapely.geometry import Point
    ko = keep_out()
    for c in PADS:
        assert ko["board"].distance(Point(c)) - STANDOFF_R >= 2  # the HALMET lifts out past the standoffs
        pad = Point(c).buffer(P["tier_boss_d"] / 2)
        for name in ("usb", "floor heads", "ties", "halmet posts"):
            assert pad.distance(ko[name]) > 0.5, (c, name)
    for i, a in enumerate(PADS):
        for b in PADS[i + 1:]:
            assert np.hypot(a[0] - b[0], a[1] - b[1]) > P["tier_boss_d"] + 2


# Flat tier (part-tier-row.scad): an OLED and two TM1637s on top, the light sensor in a cradle under the OLED.
# Its own coordinates: plate top at z = 0, the box's X and Y.
ROW_SRC = (HERE / "part-tier-row.scad").read_text()
R = {k: float(v) for k, v in re.findall(r"(?<![\w$])(\w+)\s*=\s*([-\d.]+)\s*;", ROW_SRC)}
RL = lists(HERE / "part-tier-row.scad")
RT, CX = R["plate_t"], R["cx"]
ROW_SCREWS = RL["tier_pts"]
TM_POSTS = [(CX + sx * R["tm_dx"] / 2, y + sy * R["tm_dy"] / 2) for y in RL["tm_y"] for sx in (-1, 1) for sy in (-1, 1)]
OLED_POSTS = [(CX + sx * R["oled_dx"] / 2, R["oled_y"] + sy * R["oled_dy"] / 2) for sx in (-1, 1) for sy in (-1, 1)]
RLDR_HOLE = (R["ldr_x0"] + R["ldr_l"] - R["ldr_hole_in"], R["ldr_y"])
GLAND_TOP = 33  # gland nut tops above the inside floor (owner)


@pytest.fixture(scope="module")
def row(tmp_path_factory):
    d = tmp_path_factory.mktemp("halmet_row")
    (d / "part-tier-row.scad").write_text(ROW_SRC)
    return trimesh.load(build_scad(d / "part-tier-row.scad", d, "row", render=False)["stl"])


def test_row_screws_are_the_frame_standoffs():
    assert ROW_SCREWS == COLS and RT == P["tier_t"]


def test_row_bounds_volume_and_plan_inside_the_box(row):
    assert row.is_watertight and row.body_count == 1
    lo, hi = row.bounds
    assert lo[2] == pytest.approx(-RT, abs=0.02) and hi[2] == pytest.approx(R["ldr_ledge"] + R["pcb_t"], abs=0.02)  # the sensor cradle walls are the tallest thing
    assert hi[0] <= 75.5 - 1 and max(-lo[1], hi[1]) <= 41.5 - 1  # inner walls, 1 mm margin
    tm_edge = CX + R["tm_w"] / 2
    for x, y, _ in row.vertices:  # lid-screw columns: 1 mm clear, the lower-right TM post cut col_gap short instead
        assert x <= P["lid_col_x"] - R["col_gap"] + 0.01 or abs(y) <= P["lid_col_y"] - 1 + 0.01
    assert tm_edge < P["lid_col_x"] - 0.5
    cut = [p for p in TM_POSTS if p[0] + R["tm_boss_d"] / 2 > P["lid_col_x"] - R["col_gap"]]
    for x, y in cut:  # the cut boss keeps two perimeters beside its hole
        assert P["lid_col_x"] - R["col_gap"] - x - R["tm_hole"] / 2 >= 0.8
    assert 5000 < row.volume < 7000  # mm^3; no OLED posts, straight right edge: 5997


def test_row_prints_flat_nothing_below_or_overhanging(row):
    n, c = row.face_normals, row.triangles_center
    down = n[:, 2] < -0.5
    on_bed = np.isclose(c[:, 2], -RT, atol=0.02)
    recess = np.isclose(c[:, 2], -RT + R["ldr_head_h"], atol=0.02) & (
        np.hypot(c[:, 0] - RLDR_HOLE[0], c[:, 1] - RLDR_HOLE[1]) < R["ldr_head_d"] / 2 + 0.01)  # one short bridge
    assert not np.any(down & ~on_bed & ~recess)
    assert row.vertices[:, 2].min() == pytest.approx(-RT, abs=0.01)


def test_row_three_screw_holes_in_solid_islands_clear_of_modules(row):
    from shapely.geometry import Point, box
    boards = [box(CX - R["tm_w"] / 2, y - R["tm_h"] / 2, CX + R["tm_w"] / 2, y + R["tm_h"] / 2) for y in RL["tm_y"]]
    boards.append(box(CX - R["oled_w"] / 2, R["oled_y"] - R["oled_h"] / 2, CX + R["oled_w"] / 2, R["oled_y"] + R["oled_h"] / 2))
    posts = [Point(p).buffer(R["tm_boss_d"] / 2) for p in TM_POSTS] + [Point(p).buffer(R["oled_pad_d"] / 2) for p in OLED_POSTS]
    assert len(ROW_SCREWS) == 3
    for x, y in ROW_SCREWS:
        assert top(row, x, y) is None
        island = Point(x, y).buffer(R["island_d"] / 2)
        assert all(not island.intersects(g) for g in boards + posts)
        for r in (R["tier_hole"] / 2 + 0.3, R["island_d"] / 2 - 0.3, R["head_d"] / 2):
            for a in np.radians(range(0, 360, 20)):
                assert top(row, x + r * np.cos(a), y + r * np.sin(a)) == pytest.approx(0, abs=0.02)  # solid, flat under the head
        assert R["island_d"] >= 8


def test_row_module_holes_and_tm_bosses(row):
    assert len(TM_POSTS) == 8 and len(OLED_POSTS) == 4
    for x, y in TM_POSTS:
        assert top(row, x, y) is None  # holed through
        assert top(row, x - (R["tm_boss_d"] + R["tm_hole"]) / 4, y) == pytest.approx(R["tm_boss_h"], abs=0.02)  # boss wall, on the side away from the lid column
    for x, y in OLED_POSTS:  # plain holes in flat plate, no boss: the OLED stands on standoffs
        assert top(row, x, y) is None
        assert top(row, x - R["oled_hole"] / 2 - 0.5, y) == pytest.approx(0, abs=0.02)


def test_row_oled_clears_the_sensor_stack_and_cell_sees_past_it():
    stack = R["ldr_ledge"] + R["pcb_t"] + R["ldr_part_h"]
    assert R["oled_standoff_h"] >= stack + 2  # trimpot, pin stubs and clearance under the OLED
    assert R["ldr_y"] == R["oled_y"]  # centred under it
    assert R["ldr_x0"] < R["x0"]  # photocell end out past the plate's left edge
    outer = R["ldr_w"] / 2 + R["ldr_fit"] + R["ldr_wall"]  # cradle wall faces, between the OLED's post rows
    assert R["oled_dy"] / 2 - R["oled_pad_d"] / 2 - outer > 0.5


def test_row_sensor_cradle_on_top(row):
    w = R["ldr_w"] + 2 * R["ldr_fit"]
    x0, y = R["ldr_x0"], R["ldr_y"]
    mid = x0 + 16  # past the screw head's clearance, over both ledges
    z_board = R["ldr_ledge"]
    for s in (-1, 1):
        assert top(row, mid, y + s * (w / 2 - 1)) == pytest.approx(z_board, abs=0.02)  # edge ledge
        assert top(row, x0 + R["ldr_l"] / 2, y + s * (w / 2 + R["ldr_wall"] / 2)) == pytest.approx(z_board + R["pcb_t"], abs=0.02)  # wall
        assert top(row, R["x0"] - 0.5, y) is None  # the cell end hangs past the plate: nothing under it
    assert top(row, R["x0"] + 0.5, y - (w / 2 - 1)) == pytest.approx(z_board, abs=0.02)  # the front ledge starts on the plate (the back one starts past the screw head)
    assert x0 + R["ldr_cell_clear"] >= R["x0"] - 0.01  # no ledge starts off the plate (no supports)
    assert top(row, mid, y) is None  # window between the ledges
    assert top(row, *RLDR_HOLE) is None  # M3 up from underneath
    assert top(row, RLDR_HOLE[0] + R["tier_hole"] / 2 + 0.6, y) == pytest.approx(z_board, abs=0.02)  # pad round it
    up = lambda dx: ray_hits(row, (RLDR_HOLE[0] + dx, y, -50), (0, 0, 1))[0][2]
    assert up(2.4) == pytest.approx(-RT + R["ldr_head_h"], abs=0.02)  # head recess in the underside
    assert up(R["ldr_head_d"] / 2 + 0.8) == pytest.approx(-RT, abs=0.02)


def test_row_clears_the_lid_and_the_gland_nuts():
    floor = -P["post_h"]  # z = 0 on the rest posts
    tier_top = TIER_TOP
    lid = P["rim_z"] + P["lid_depth"] + floor
    assert tier_top + R["oled_standoff_h"] + R["pcb_t"] + 1.5 < lid - 1  # OLED glass, 1.5 over its board (guess)
    assert tier_top + R["tm_boss_h"] + 7 < lid - 1  # TM1637 face, 7 above its board's underside
    assert tier_top - RT - floor > GLAND_TOP + 3  # tier underside over the gland nuts

def test_screw_relief_counterbores_on_top(frame):
    for sx in (-1, 1):
        for k in (-1, 0, 1):
            x, y = sx * SPAN / 2, k * PITCH + (P["slot_d"] / 2 + 0.6)  # beside the slot, inside the relief
            assert np.isclose(top(frame, x, y), T - P["relief_h"], atol=0.02)
            xo = sx * (SPAN / 2 + REACH + P["relief_d"] / 2 + 0.3)  # past the relief's outer end: a wall remains
            assert np.isclose(top(frame, xo, k * PITCH), T, atol=0.02)
