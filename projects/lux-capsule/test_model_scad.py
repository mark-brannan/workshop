"""Tests for the tube-top lux capsule: each printed part's bounding box, volume window and watertightness."""

import tempfile
from pathlib import Path

import pytest
import trimesh
from shop.scad import OpenSCAD, find_openscad

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")

# (view, exit) -> (extents x, y, z in mm, volume window in mm^3), measured from the 2026-11-20 build
PARTS = {
    ("cap_print", "center"): ((33.0, 33.0, 12.5), (3953, 4641)),
    ("cap_print", "side"): ((33.0, 33.0, 12.5), (3882, 4557)),
    ("riser_print", "center"): ((25.0, 25.0, 2.5), (332, 390)),
    ("riser_print", "side"): ((25.0, 25.0, 2.5), (313, 368)),
    ("base_print", "center"): ((46.0, 33.0, 12.1), (3704, 4349)),
    ("base_print", "side"): ((46.0, 33.0, 12.1), (3807, 4469)),
}


@pytest.mark.parametrize("view,exit_", PARTS)
def test_part(view, exit_):
    osc = OpenSCAD()
    with tempfile.TemporaryDirectory() as d:
        stl = Path(d) / "m.stl"
        osc.run(HERE / "model.scad", stl, "-D", f'view="{view}"', "-D", f'exit="{exit_}"')
        mesh = trimesh.load(stl)
    osc.cleanup()
    extents, (vmin, vmax) = PARTS[(view, exit_)]
    assert mesh.extents == pytest.approx(extents, abs=0.5)
    assert mesh.is_watertight and vmin < mesh.volume < vmax
