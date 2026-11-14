"""``shop gauge``: the generated part-gauge.scad slices a model thin and keeps its through-holes."""

import pytest
import trimesh
from shop.gauge import MARK, write_gauge
from shop.scad import build_scad, find_openscad
from shop.testing import ray_hits

# a 40 x 30 x 3 plate, a 2 mm wall round it 10 tall, one 4 mm through-hole at (10, 5)
MODEL = """
module part() difference() {
    union() {
        translate([-20, -15, 0]) cube([40, 30, 3]);
        difference() { translate([-22, -17, 0]) cube([44, 34, 13]); translate([-20, -15, -1]) cube([40, 30, 15]); }
    }
    translate([10, 5, -1]) cylinder(d = 4, h = 5, $fn = 32);
}
part();
"""


def top_z(mesh, x, y):
    h = ray_hits(mesh, (x, y, 50), (0, 0, -1))
    return h[0][2] if len(h) else None


def test_refuses_a_hand_written_gauge_and_rewrites_its_own(tmp_path):
    (tmp_path / "model.scad").write_text(MODEL)
    (tmp_path / "part-gauge.scad").write_text("// by hand\n")
    with pytest.raises(FileExistsError):
        write_gauge(tmp_path, "part", 1.5, 8)
    (tmp_path / "part-gauge.scad").unlink()
    write_gauge(tmp_path, "part", 1.5, 8)
    text = write_gauge(tmp_path, "part();", 1.5).read_text()  # its own file: overwritten
    assert text.startswith(MARK) and "z_wall = -1;" in text and "gauge_slice() part();" in text


def test_needs_a_model(tmp_path):
    with pytest.raises(FileNotFoundError):
        write_gauge(tmp_path, "part", 1.5)


@pytest.mark.skipif(find_openscad() is None, reason="openscad not found")
@pytest.mark.parametrize("z_wall, top", [(8, 3), (None, 1)])
def test_gauge_is_thin_and_keeps_the_hole(tmp_path, z_wall, top):
    (tmp_path / "model.scad").write_text(MODEL)
    g = trimesh.load(build_scad(write_gauge(tmp_path, "part", 1.5, z_wall), tmp_path, "gauge", render=False)["stl"])
    assert g.is_watertight and g.body_count == 1
    assert g.bounds[1][2] == pytest.approx(top, abs=0.02)
    assert top_z(g, 0, 0) == pytest.approx(1, abs=0.02)  # plate
    assert top_z(g, 10, 5) is None  # the hole, through
    assert top_z(g, 21, 0) == pytest.approx(top, abs=0.02)  # the wall, or the bare plate edge
    assert top_z(g, 10 + 2.5, 5) == pytest.approx(1, abs=0.02)  # just outside the 4 mm hole
