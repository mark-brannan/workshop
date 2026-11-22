"""Tests for the tube-cap lux head: each printed part's bounding box, volume window and watertightness."""

import tempfile
from pathlib import Path

import pytest
import trimesh
from shop.scad import OpenSCAD, find_openscad

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")

# (view, exit) -> (extents x, y, z in mm, volume window in mm^3), measured from the 2026-11-20 build
PARTS = {
    ("body_print", "center"): ((46.0, 46.0, 82.2), (38500, 47500)),
    ("body_print", "side"): ((46.0, 46.0, 102.8), (49500, 60500)),
    ("lid_print", "center"): ((50.0, 50.0, 11.1), (8600, 10500)),
    ("ring_print", "center"): ((40.0, 26.0, 2.0), (600, 800)),
    ("deck_print", "center"): ((39.6, 39.6, 5.2), (3300, 4100)),
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
