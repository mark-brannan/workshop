"""Tests for the tube-mounted lux sensor head: each printed part's bounding box, volume window and watertightness."""

import tempfile
from pathlib import Path

import pytest
import trimesh
from shop.scad import OpenSCAD, find_openscad

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")

# part view -> (extents x, y, z in mm, volume window in mm^3), measured from the 2026-11-19 build
PARTS = {
    "tray_print": ((46.0, 70.6, 17.9), (14500, 18000)),
    "ring_print": ((40.0, 29.0, 2.0), (1100, 1450)),
    "lid_print": ((62.1, 143.0, 6.0), (31500, 39000)),
    "arm_half": ((62.1, 143.0, 42.0), (66000, 82000)),
    "back_half": ((62.1, 25.0, 48.0), (28000, 35000)),
}


@pytest.mark.parametrize("view", PARTS)
def test_part(view):
    osc = OpenSCAD()
    with tempfile.TemporaryDirectory() as d:
        stl = Path(d) / "m.stl"
        osc.run(HERE / "model.scad", stl, "-D", f'view="{view}"')
        mesh = trimesh.load(stl)
    osc.cleanup()
    extents, (vmin, vmax) = PARTS[view]
    assert mesh.extents == pytest.approx(extents, abs=0.5)
    assert mesh.is_watertight and vmin < mesh.volume < vmax
