"""Tests for the small-box sensor carrier: bounding box, volume window, feature counts, and no part overlapping another."""

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


P = params("box.scad", "model.scad", "assembly.scad")


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
def carrier():
    return run("model.scad")


def test_carrier_bounding_box(carrier):
    x, y, z = carrier.extents
    assert x == pytest.approx(P["plate_l"], abs=0.05)
    assert z == pytest.approx(P["plate_t"] + P["post_h"], abs=0.05)
    assert y <= 39 - 1, "wider than the clear floor between the corner columns"
    assert x <= 58 - 2, "longer than the inside floor"


def test_carrier_volume_window(carrier):
    assert carrier.is_watertight
    assert 1200 < carrier.volume < 2600


def test_carrier_holes(carrier):
    for sx in (-1, 1):       # a boss slot is open across the whole guessed pitch range
        for dx in (-2, 0, 2):
            assert not ray_hits(carrier, [sx * P["boss_pitch"] / 2 + dx, 0, -5], [0, 0, 1])
    for sx in (-1, 1):       # four screw holes on the Adafruit pattern
        for sy in (-1, 1):
            assert not ray_hits(carrier, [sx * P["hole_dx"] / 2, P["plate_y"] + sy * P["hole_dy"] / 2, -5], [0, 0, 1])


def test_spacer():
    s = run("model.scad", 'part="spacer"')
    assert s.is_watertight
    assert s.extents[2] == pytest.approx(P["spacer_h"], abs=0.05)
    assert len(s.split()) == 2      # two pairs of tubes, the ends open for the plugs


@pytest.mark.parametrize("variant", ["env", "imu"])
def test_no_component_overlaps_another(variant):
    clash = run("assembly.scad", 'show="clash"', f'variant="{variant}"')
    assert clash.volume - 1.0 == pytest.approx(0, abs=1e-3)     # only the 1 mm3 marker is left


def test_stack_fits_under_the_lid():
    top = P["boss_h"] + P["head_h"] + P["stack_screw_l"]
    ceiling = P["box_h"] - P["lid_top"] - P["box_floor"]
    assert ceiling - top >= 2


def test_nuts_seat_on_plain_wall():
    plain_top = P["box_h"] - P["lid_h"] - P["box_floor"] - P["gasket_step"]
    assert P["sp_z"] + P["sp_nut_af"] / 2 <= plain_top - 0.5 and P["sp_z"] - P["sp_nut_af"] / 2 >= 0.5
    assert abs(P["sp_x"]) + P["sp_nut_af"] / 0.866 / 2 <= P["col_clear"] / 2 - 0.5
    assert P["vent_x"] + P["vent_nut_af"] / 0.866 / 2 <= P["col_clear"] / 2 - 0.5
    assert P["vent_x"] - P["sp_x"] >= (P["sp_nut_af"] + P["vent_nut_af"]) / 0.866 / 2 + 1
