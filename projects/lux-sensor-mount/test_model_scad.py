"""Tests for the tube-mounted lux sensor head (rev 10): each printed part's bounding box, volume window and watertightness."""

import tempfile
from pathlib import Path

import pytest
import trimesh
from shop.scad import OpenSCAD, find_openscad

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")

# part view -> (extents x, y, z in mm, volume window in mm^3), measured from the 2026-11-19 rev 10 build
PARTS = {
    "front_print": ((60.1, 48.0, 24.6), (20000, 25500)),
    "aft_print": ((60.1, 48.0, 94.5), (64000, 80000)),
    "cup_print": ((41.0, 25.2, 15.9), (5400, 6900)),
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
