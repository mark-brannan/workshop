"""Tests for the BME688 cabin screen: bounding box, volume window, holes, an open air path, no straight line to the chip."""

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
FACE_Z = P["depth"] - P["cover_t"]
ROOF_Y = P["house_h"] / 2 - P["wall"]
CHANNEL_Z = (P["baffle_z"] + P["baffle_t"] + FACE_Z) / 2      # middle of the rising channel
CHIP = [0, P["board_y"], P["plate_t"] + P["pad_h"] + 2.5]     # the chip's top face


def run(part: str) -> trimesh.Trimesh:
    osc = OpenSCAD()
    with tempfile.TemporaryDirectory() as d:
        stl = Path(d) / "m.stl"
        osc.run(HERE / "model.scad", stl, "-D", f'part="{part}"')
        mesh = trimesh.load(stl)
    osc.cleanup()
    return mesh


@pytest.fixture(scope="module")
def body():
    return run("body")


@pytest.fixture(scope="module")
def cover():
    return run("cover")


@pytest.fixture(scope="module")
def assembly():
    return run("assembly")


def test_body_bounding_box(body):
    x, y, z = body.extents
    assert x == pytest.approx(P["plate_w"], abs=0.05)
    assert y == pytest.approx(P["plate_h"], abs=0.05)
    assert z == pytest.approx(P["depth"] + P["roof_over"], abs=0.05)


def test_cover_bounding_box(cover):
    x, y, z = cover.extents
    assert x == pytest.approx(P["plate_w"], abs=0.05)
    assert y == pytest.approx(P["house_h"] / 2 + ROOF_Y - 0.2, abs=0.05)
    assert z == pytest.approx(P["depth"] - P["baffle_z"], abs=0.05)
    assert cover.bounds[0][2] == pytest.approx(0, abs=0.01), "the face is not on the bed"


def test_volume_windows(body, cover):
    assert body.is_watertight and cover.is_watertight
    assert 7500 < body.volume < 10500
    assert 2500 < cover.volume < 4500


def test_mount_and_screw_holes(body, cover):
    for sy in (-1, 1):       # two mount holes at the DIN clip's pitch, through the plate
        assert not ray_hits(body, [0, sy * P["mount_pitch"] / 2, -5], [0, 0, 1])
    pads = [(sx * P["hole_dy"] / 2, P["board_y"] + sy * P["hole_dx"] / 2) for sx in (-1, 1) for sy in (-1, 1)]
    for x, y in pads:        # four pilot holes on the Adafruit pattern, blind: the back stays closed
        hits = ray_hits(body, [x, y, 30], [0, 0, -1])
        assert hits and hits[0][2] == pytest.approx(1, abs=0.05)
    bx = (P["plate_w"] - 2 * P["wall"]) / 2 - P["boss_d"] / 2 + 0.5
    for sx in (-1, 1):       # cover screw holes line up with the body's bosses
        assert not ray_hits(cover, [sx * bx, -P["boss_y"], -5], [0, 0, 1])      # y flips with the cover
        hits = ray_hits(body, [sx * bx, P["boss_y"], 30], [0, 0, -1])
        assert hits[0][2] == pytest.approx(FACE_Z - 8, abs=0.05)


def test_air_path_is_open(assembly):
    up = ray_hits(assembly, [5, -30, CHANNEL_Z], [0, 1, 0])                    # in at the slot, up the channel
    assert up[0][1] == pytest.approx(ROOF_Y, abs=0.05), "the channel is blocked below the roof"
    over = ray_hits(assembly, [0, (P["baffle_top"] + ROOF_Y) / 2, CHANNEL_Z], [0, 0, -1])   # over the baffle
    assert over[0][2] == pytest.approx(P["plate_t"], abs=0.05), "the turn over the baffle is blocked"


def test_nothing_outside_sees_the_chip(assembly):
    for d in ([0, 0, 1], [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, -1],
              [0, -1, 1], [0, -2, 1], [0, -1, 2], [0, 1, 1], [1, -1, 1], [-1, -1, 1], [1, -2, 1], [-1, -2, 1]):
        assert ray_hits(assembly, CHIP, d), f"open line to the chip along {d}"


def test_cable_notch_opens_the_floor(assembly):
    y = P["floor_y"] + P["wall"] + 1                                           # just above the floor, in the chamber
    assert not ray_hits(assembly, [P["notch_x"], y, P["baffle_z"] - 2], [0, -1, 0])
    assert ray_hits(assembly, [-P["notch_x"], y, P["baffle_z"] - 2], [0, -1, 0])[0][1] == pytest.approx(P["floor_y"] + P["wall"], abs=0.05)


# --- overhead variant: plate up under a horizontal panel, floor with one hole, baffle above it ---

OH_CHIP = [0, 0, P["plate_t"] + P["pad_h"] + 2.5]
IN_W = P["plate_w"] - 2 * P["wall"]


@pytest.fixture(scope="module")
def oh_body():
    return run("overhead_body")


@pytest.fixture(scope="module")
def oh_cover():
    return run("overhead_cover")


@pytest.fixture(scope="module")
def oh_assembly():
    return run("overhead_assembly")


def test_overhead_bounding_boxes(oh_body, oh_cover):
    assert oh_body.extents == pytest.approx([P["plate_w"], P["plate_h"], FACE_Z], abs=0.05)
    assert oh_cover.extents == pytest.approx([P["plate_w"], P["house_h"], FACE_Z + P["oh_floor_t"] - P["baffle_z"]], abs=0.05)
    assert oh_cover.bounds[0][2] == pytest.approx(0, abs=0.01), "the floor is not on the bed"


def test_overhead_volume_windows(oh_body, oh_cover):
    assert oh_body.is_watertight and oh_cover.is_watertight
    assert 7500 < oh_body.volume < 10500
    assert 1800 < oh_cover.volume < 2500


def test_overhead_holes(oh_body, oh_assembly):
    for sy in (-1, 1):
        assert not ray_hits(oh_body, [0, sy * P["mount_pitch"] / 2, -5], [0, 0, 1])
    for sx in (-1, 1):       # four blind pilot holes on the Adafruit pattern
        for sy in (-1, 1):
            hits = ray_hits(oh_body, [sx * P["hole_dy"] / 2, sy * P["hole_dx"] / 2, 30], [0, 0, -1])
            assert hits[0][2] == pytest.approx(1, abs=0.05)
    by = P["house_h"] / 2 - P["wall"] - P["boss_d"] / 2 + 0.3
    bx = IN_W / 2 - P["boss_d"] / 2 + 0.5
    for x, y in ((-bx, by), (bx, -by)):      # cover screws reach the bosses' pilots through the floor
        assert ray_hits(oh_assembly, [x, y, 30], [0, 0, -1])[0][2] == pytest.approx(FACE_Z - 8, abs=0.05)


OH_FIN_X = [i * P["oh_fin_pitch"] for i in (-1.5, -0.5, 0.5, 1.5)]
OH_LANE_X = [0, P["oh_fin_pitch"], -P["oh_fin_pitch"]]       # the lanes between the fins


def test_overhead_air_path_is_open(oh_assembly):
    hole = ray_hits(oh_assembly, [0, 0, 30], [0, 0, -1])                       # in at the hole, up to the arch's crown
    assert hole[0][2] == pytest.approx(P["baffle_z"] + P["oh_arch_t"], abs=0.05)
    for x in OH_LANE_X:
        for sy in (-1, 1):
            along = ray_hits(oh_assembly, [x, 0, CHANNEL_Z], [0, sy, 0])       # out along each lane, past the arch's end
            assert abs(along[0][1]) > P["oh_baffle_l"] / 2 + 2
    for sy in (-1, 1):
        across = ray_hits(oh_assembly, [-P["oh_fin_pitch"], sy * P["oh_fin_gap_y"], CHANNEL_Z + 0.5], [1, 0, 0])   # lane to lane through the fin gaps
        assert across[0][0] > P["oh_fin_pitch"] * 1.5
        turn = ray_hits(oh_assembly, [0, sy * (P["oh_baffle_l"] / 2 + 2), CHANNEL_Z], [0, 0, -1])   # up past the arch's end
        assert turn[0][2] == pytest.approx(P["plate_t"], abs=0.05)


def test_overhead_cover_spans_are_short(oh_cover):
    """Floor on the bed: every face that points down steeper than 45 degrees is within 2.5 mm of what holds it up."""
    import numpy as np
    n, c = oh_cover.face_normals, oh_cover.triangles_center
    down = (n[:, 2] < -np.cos(np.radians(45)) - 1e-3) & (c[:, 2] > 0.01)
    w = P["plate_w"] - 2 * P["wall"] - 2 * P["fit"]
    h = P["depth"] - P["cover_t"] - P["baffle_z"]
    r = ((w / 2) ** 2 + h ** 2) / (2 * h)
    foot = ((r - P["oh_arch_t"]) ** 2 - (r - h) ** 2) ** 0.5                # where the arch's inside meets the floor
    edges = [x + s * P["oh_fin_t"] / 2 for x in OH_FIN_X for s in (-1, 1)] + [-foot, foot]
    gaps = [g * P["oh_fin_gap_y"] + s * P["oh_fin_gap"] / 2 for g in (-1, 1) for s in (-1, 1)]
    worst = 0.0
    for x, y, _ in c[down]:
        in_gap = abs(abs(y) - P["oh_fin_gap_y"]) < P["oh_fin_gap"] / 2 and min(abs(x - f) for f in OH_FIN_X) <= P["oh_fin_t"] / 2
        reach = min(abs(y - g) for g in gaps) if in_gap else min(abs(x - e) for e in edges)   # a gap's top spans y; the arch spans x
        worst = max(worst, reach)
    assert worst <= 2.5, f"an unsupported span reaches {worst:.2f} mm from its support"


def test_overhead_nothing_outside_sees_the_chip(oh_assembly):
    for d in ([0, 0, 1], [0, 1, 2], [0, -1, 2], [1, 0, 2], [-1, 0, 2], [0, 1, 1], [0, -1, 1], [1, 0, 1], [-1, 0, 1],
              [0, 3, 1], [0, -3, 1], [1, 3, 1], [-1, -3, 1], [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, -1]):
        assert ray_hits(oh_assembly, OH_CHIP, d), f"open line to the chip along {d}"


def test_overhead_cable_window(oh_assembly):
    z = P["plate_t"] + P["notch_d"] / 2
    assert not ray_hits(oh_assembly, [10, P["win_y"], z], [1, 0, 0])
    assert ray_hits(oh_assembly, [-10, P["win_y"], z], [-1, 0, 0])
