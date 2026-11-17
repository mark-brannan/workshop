"""Tests for the BME688 pod: bounding box, volume window, feature counts, no part overlapping another, the chip under the vent."""

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


P = params("../../small-box-sensors/box.scad", "model.scad", "assembly.scad")
CEIL = P["box_h"] - P["lid_top"] - P["box_floor"]            # lid underside above the inside floor
POD_H = CEIL - P["lid_gap"] - P["boss_h"]
BLK_L = P["board_l"] + 2 * (P["rim_fit"] + P["rim_t"])
BLK_W = P["board_w"] + 2 * (P["rim_fit"] + P["rim_t"])


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
def pod():
    return run("model.scad")


def test_pod_bounding_box(pod):
    x, y, z = pod.extents
    assert x == pytest.approx(P["plate_l"], abs=0.05)
    assert y == pytest.approx(BLK_W, abs=0.05)
    assert z == pytest.approx(POD_H, abs=0.05)
    assert x <= 58 - 2, "longer than the inside floor"


def test_pod_volume_window(pod):
    assert pod.is_watertight
    assert 9000 < pod.volume < 12500


def test_pod_holes(pod):
    for sx in (-1, 1):       # a boss slot is open across the whole guessed pitch range
        for dx in (-3.5, 0, 3.5):
            assert not ray_hits(pod, [sx * P["boss_pitch"] / 2 + dx, 0, -5], [0, 0, 1])
    for sx in (-1, 1):       # four screw holes on the Adafruit pattern, through the whole block
        for sy in (-1, 1):
            assert not ray_hits(pod, [sx * P["hole_dx"] / 2, P["plate_y"] + sy * P["hole_dy"] / 2, -5], [0, 0, 1])


def test_rim_walls_the_board_in_except_at_the_plug(pod):
    z = P["seat_h"] + 2      # level with the board's parts
    c = [0, P["plate_y"], z]
    assert ray_hits(pod, c, [-1, 0, 0]) and ray_hits(pod, c, [0, 1, 0]) and ray_hits(pod, c, [0, -1, 0])
    assert not ray_hits(pod, c, [1, 0, 0]), "the plug notch is closed"


def test_no_component_overlaps_another():
    clash = run("assembly.scad", 'show="clash"')
    assert clash.volume - 1.0 == pytest.approx(0, abs=1e-3)     # only the 1 mm3 marker is left


def test_chip_sits_under_the_vent():
    chip_top = P["boss_h"] + P["seat_h"] + P["pcb_t"] + P["chip_h"]
    vent_tip = P["box_h"] - P["box_floor"] - P["vent_thread"]
    assert 1 <= vent_tip - chip_top <= 3


def test_screws_and_rim_fit_under_the_lid():
    tip = P["boss_h"] + P["head_h"] + P["stack_screw_l"]
    nut_top = P["boss_h"] + P["seat_h"] + P["pcb_t"] + P["m25_nut_t"]
    assert tip >= nut_top - 0.5, "the screw does not fill the nut"
    assert CEIL - tip >= 2
    assert P["lid_gap"] >= 1


def test_sensor_air_is_a_small_part_of_the_box():
    chamber = (BLK_L - 2 * P["rim_t"]) * (BLK_W - 2 * P["rim_t"]) * (CEIL - P["boss_h"] - P["seat_h"] + P["pad_h"])
    box = 58 * 53 * (P["box_h"] - P["lid_h"] - P["box_floor"])
    assert chamber < box / 10


def test_sp13_nut_seats_on_plain_wall_and_clears_the_pod():
    plain_top = P["box_h"] - P["lid_h"] - P["box_floor"] - P["gasket_step"]
    assert P["sp_z"] + P["sp_nut_af"] / 2 <= plain_top - 0.5 and P["sp_z"] - P["sp_nut_af"] / 2 >= 0.5
    assert abs(P["sp_x"]) + P["sp_nut_af"] / 0.866 / 2 <= P["col_clear"] / 2 - 0.5
    rear = 53 / 2 - P["sp_rear"]                                # how far the socket reaches into the box
    assert rear - (P["plate_y"] + BLK_W / 2) >= 6, "no room to solder the cups"
