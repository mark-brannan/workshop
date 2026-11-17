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
