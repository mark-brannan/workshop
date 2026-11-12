"""Tests for the HALMET enclosure frame: bounding box, volume window, feature counts."""

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


P = params(HERE / "model.scad")
DROP = max(0.0, P["boss_h"] - P["post_h"])
T, H = P["plate_t"] + DROP, P["standoff_h"]  # T: full body thickness
SPAN, PITCH, REACH = P["boss_span"], P["boss_pitch"], P["slot_reach"]
DX, DY = P["board_dx"], P["board_dy"]
SLOTS = [(-21.75 + DX, 22.5 + DY), (22.75 + DX, -22.5 + DY)]
RESTS = [(36 + DX, 18 + DY), (-38.5 + DX, -19.5 + DY)]


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
    assert np.allclose([lo[0], hi[0]], [-SPAN / 2 - REACH, SPAN / 2 + REACH], atol=0.05)
    assert np.isclose(lo[2], 0, atol=0.02) and np.isclose(hi[2], T + H, atol=0.02)
    assert np.isclose(hi[1] - lo[1], P["frame_w"], atol=0.05)
    assert hi[1] - lo[1] < 83 - 4  # inside the box floor width with room to spare
    assert 12000 < frame.volume < 22000  # mm^3; a solid 144 x 75 x 4.5 plate is 48600


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
            assert np.isclose(top(frame, sx * SPAN / 2, y + PITCH / 2 if k < 1 else y + 4), T, atol=0.02)


def test_laser_profile_is_millimetres_on_cut_layer(built):
    doc = ezdxf.readfile(built["dxf"])
    assert doc.header["$INSUNITS"] == 4
    ents = list(doc.modelspace())
    assert ents and {e.dxf.layer for e in ents} == {"cut"}


def bottom(mesh, x, y):
    h = ray_hits(mesh, (x, y, -50), (0, 0, 1))
    return h[0][2] if h else None


def test_pads_rest_on_the_four_posts(frame):
    for sx in (-1, 1):
        for sy in (-1, 1):
            for ox in (-4, 0, 4):  # post anywhere within 4 mm of post_dx
                assert np.isclose(bottom(frame, sx * P["post_dx"] / 2 + ox, sy * P["post_dy"] / 2), 0, atol=0.02)


def test_underside_pocketed_over_the_holed_bosses(frame):
    for sx in (-1, 1):
        for k in (-1, 0, 1):
            x, y = sx * SPAN / 2, k * PITCH + (P["screw_d"] / 2 + 1.5)  # beside the slot, over the boss rim
            assert np.isclose(bottom(frame, x, y), DROP, atol=0.02)
            assert np.isclose(top(frame, x, y), T, atol=0.02)


def test_zip_tie_slots_open(frame):
    pairs = [(x + s * P["tie_gap"] / 2, P["tie_bar_y"]) for x in (-24, 0, 24) for s in (-1, 1)]
    x_end = -(SPAN / 2 - REACH - P["screw_d"] / 2 - 3 + SPAN / 2 + REACH) / 2
    pairs += [(x_end, y + s * P["tie_gap"] / 2) for y in (-10.5, 10.5) for s in (-1, 1)]
    for x, y in pairs:
        assert top(frame, x, y) is None
    for x in (-24, 0, 24):  # web between the two slots of a pair carries the tie
        assert np.isclose(top(frame, x, P["tie_bar_y"]), T, atol=0.02)
