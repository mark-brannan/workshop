"""Tests for the BME688 louvred screen: bounding boxes, volume windows, feature counts, what the slats block and pass, no part overlapping another."""

import math
import re
import tempfile
from pathlib import Path

import pytest
import trimesh
from shop.scad import OpenSCAD, find_openscad
from shop.testing import ray_hits

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")


def params(*files) -> dict[str, float]:
    out = {}
    for f in files:
        out |= {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*(-?[\d.]+)\s*;", (HERE / f).read_text(), re.M)}
    return out


P = params("model.scad", "assembly.scad")
OUT_W = P["in_w"] + 2 * P["louv_run"]
Y_LO, Y_HI = -P["floor_t"], P["in_h"] + P["roof_t"]
BODY_H = P["plate_t"] + P["in_d"]
SLAT_V = P["louv_t"] / math.cos(math.radians(45))
SPAN = Y_HI - Y_LO - 2 * P["louv_run"] + 2 * P["bite"] - P["louv_run"] - SLAT_V
N_SLAT = math.ceil(SPAN / P["louv_pitch"]) + 1
PITCH = SPAN / (N_SLAT - 1)
Z_AIR = BODY_H - 3                                            # above the pads and pegs
SEATS = [(sx * P["hole_dy"] / 2, P["board_y"] + sy * P["hole_dx"] / 2) for sx in (-1, 1) for sy in (-1, 1)]
PILOTS = [(sx * (P["in_w"] + P["louv_run"]) / 2, y) for sx in (-1, 1) for y in (Y_LO + P["louv_run"] / 2, Y_HI - P["louv_run"] / 2)]


def run(scad: str, *defs: str) -> trimesh.Trimesh:
    osc = OpenSCAD()
    with tempfile.TemporaryDirectory() as d:
        stl = Path(d) / "m.stl"
        args = [a for kv in defs for a in ("-D", kv)]
        osc.run(HERE / scad, stl, *args)
        mesh = trimesh.load(stl)
    osc.cleanup()
    return mesh


@pytest.fixture(scope="module")
def body():
    return run("model.scad")


@pytest.fixture(scope="module")
def cover():
    return run("part-cover.scad")


def test_body_bounding_box_and_volume(body):
    assert body.extents == pytest.approx([OUT_W, Y_HI - Y_LO, BODY_H], abs=0.05)
    assert body.is_watertight
    assert 11500 < body.volume < 16000


def test_cover_bounding_box_and_volume(cover):
    post_l = P["in_d"] - P["pad_h"] - P["pcb_t"] - P["press_gap"]
    assert cover.extents == pytest.approx([OUT_W, Y_HI - Y_LO, P["cover_t"] + post_l], abs=0.05)
    assert cover.is_watertight
    assert 3800 < cover.volume < 5200


def test_slat_count_each_side(body):
    for sx in (-1, 1):       # up the middle of a louvred wall: a post, every slat, a post
        hits = ray_hits(body, [sx * (P["in_w"] + P["louv_run"]) / 2, Y_LO - 5, P["plate_t"] + 5], [0, 1, 0])   # under the pilot holes
        assert len(hits) == 2 * (N_SLAT + 2)


def test_no_straight_line_in_from_the_side(body):
    y = Y_LO + 0.3
    while y < Y_HI:
        for sx in (-1, 1):
            assert ray_hits(body, [0, y, Z_AIR], [sx, 0, 0]), f"open at y={y:.1f}"
        y += 0.5


def test_air_passes_between_the_slats(body):
    run_ = P["louv_run"]
    for k in range(N_SLAT - 1):          # down and out through the middle of each gap
        y_out = Y_LO + run_ - P["bite"] + k * PITCH + (SLAT_V + PITCH) / 2
        for sx in (-1, 1):
            start = [sx * (P["in_w"] / 2 - 1), y_out + run_ + 1, Z_AIR]
            assert not ray_hits(body, start, [sx, -1, 0]), f"gap {k} is closed"


def test_holes_and_notch(body):
    for y in (P["mount_lo_y"], P["mount_hi_y"]):                               # bulkhead screws, through the back plate
        assert not ray_hits(body, [0, y, -5], [0, 0, 1])
    for x, y in PILOTS:                                                        # cover screw pilots, blind from the top
        hits = ray_hits(body, [x, y, BODY_H + 5], [0, 0, -1])
        assert hits[0][2] == pytest.approx(BODY_H - P["pilot_depth"], abs=0.05)
    notch_z = BODY_H - P["notch_depth"] + P["notch_w"] / 2
    assert not ray_hits(body, [0, 5, notch_z], [0, -1, 0]), "no way through the floor"
    assert not ray_hits(body, [0, -P["floor_t"] / 2, notch_z], [0, 0, 1]), "the notch is closed toward the cover"
    assert ray_hits(body, [P["notch_w"] / 2 + 1, 5, notch_z], [0, -1, 0])
    assert P["notch_w"] - P["cable_d"] >= 1


def test_pegs_on_the_adafruit_pattern(body):
    seat_z = P["plate_t"] + P["pad_h"]
    for x, y in SEATS:
        top = ray_hits(body, [x, y, BODY_H + 5], [0, 0, -1])[0][2]
        assert top == pytest.approx(seat_z + P["peg_h"], abs=0.05)
        shoulder = ray_hits(body, [x + P["pad_d"] / 2 - 0.5, y, BODY_H + 5], [0, 0, -1])[0][2]
        assert shoulder == pytest.approx(seat_z, abs=0.05)
    assert P["peg_d"] < 2.5 and P["peg_h"] > P["pcb_t"]


def test_cover_posts_reach_the_board(cover):
    for x, y in SEATS:       # just outside the peg socket, on the post's rim
        tip = ray_hits(cover, [x + (P["peg_d"] + 0.8) / 2 + 0.3, y, 50], [0, 0, -1])[0][2]
        board_top = P["plate_t"] + P["pad_h"] + P["pcb_t"]
        assert 0 < (BODY_H + P["cover_t"] - tip) - board_top <= 0.5
    for x, y in PILOTS:
        assert not ray_hits(cover, [x, y, -5], [0, 0, 1])


def test_no_component_overlaps_another():
    clash = run("assembly.scad", 'show="clash"')
    assert clash.volume - 1.0 == pytest.approx(0, abs=1e-3)     # only the 1 mm3 marker is left


def test_bulkhead_screws_clear_the_board_and_the_walls():
    board_lo, board_hi = P["board_y"] - P["board_l"] / 2, P["board_y"] + P["board_l"] / 2
    r = P["mount_head_d"] / 2
    assert P["mount_hi_y"] - r >= board_hi + 1 and P["mount_hi_y"] + r <= P["in_h"] - 1
    assert P["mount_lo_y"] + r <= board_lo - 1 and P["mount_lo_y"] - r >= 1
    assert board_lo - P["plug_out"] - P["lead_out"] >= 2, "no room under the plug for the wires to turn"
