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
TIER_Z0 = T + P["tier_boss_h"]            # column feet on the plate's bosses
TIER_TOP = P["rim_z"] - P["boss_h"]       # Z = 0 is the boss top
SEG_Y = P["oled_y"] - P["oled_h"] / 2 - P["seg_gap"] - P["seg_h"] / 2
MOD_POSTS = [(P["oled_x"] + sx * P["oled_hole_dx"] / 2, P["oled_y"] + sy * P["oled_hole_dy"] / 2)
             for sx in (-1, 1) for sy in (-1, 1)]
MOD_POSTS += [(P["oled_x"] + sx * P["seg_hole_dx"] / 2, SEG_Y + sy * P["seg_hole_dy"] / 2) for sx in (-1, 1) for sy in (-1, 1)]
USB_Y = 16.5 - 29 + DY                    # USB-C centre on the board's right edge
BOARD_RIGHT = 44.5 + DX
VOL_LO, VOL_HI = 23000, 29500  # first hex-plate build: 25789


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


def test_plate_has_insert_bosses_under_the_tier_columns(frame):
    for x, y in COLS:
        assert np.isclose(top(frame, x, y), TIER_Z0 - P["insert_depth"], atol=0.02)
        assert np.isclose(top(frame, x + P["insert_d"] / 2 + 0.7, y), TIER_Z0, atol=0.02)


def test_tier_one_body_at_the_rim(tier):
    assert tier.is_watertight
    assert len(tier.split(only_watertight=False)) == 1
    lo, hi = tier.bounds
    assert np.isclose(lo[2], TIER_Z0, atol=0.02)
    assert np.isclose(hi[2], TIER_TOP + P["module_rise"], atol=0.02)
    assert np.isclose(top(tier, P["tier_x0"] + 1, 0), TIER_TOP, atol=0.02)
    assert hi[0] < 151 / 2 - 2 and hi[1] <= P["plate_y_hi"] + 0.01  # inside the floor


def test_tier_columns_land_on_the_bosses_with_driver_access(tier):
    for x, y in COLS:
        assert np.isclose(bottom(tier, x + P["screw_d"] / 2 + 0.5, y), TIER_Z0, atol=0.02)
        assert np.isclose(top(tier, x, y + P["screw_d"] / 2 + 0.5), TIER_Z0 + P["tier_boss_h"], atol=0.02)  # seat, open above
        assert top(tier, x, y) is None  # screw passes through


def test_tier_module_posts_take_m25_self_tappers(tier):
    for x, y in MOD_POSTS:
        assert top(tier, x, y) is None
        assert np.isclose(top(tier, x + P["pilot_d"] / 2 + 0.5, y), TIER_TOP + P["module_rise"], atol=0.02)


def test_tier_clears_lid_column_board_and_usb_plug(tier):
    for v in tier.vertices:
        assert v[0] <= P["lid_col_x"] - 0.5 or v[1] <= P["lid_col_y"] - 0.5
    assert P["tier_x0"] - BOARD_RIGHT >= 2
    for z in (12.0, 15.0):  # USB-C plug path along +X from the board edge
        assert not ray_hits(tier, (BOARD_RIGHT, USB_Y, z), (1, 0, 0)) or ray_hits(tier, (BOARD_RIGHT, USB_Y, z), (1, 0, 0))[0][0] > BOARD_RIGHT + 30
