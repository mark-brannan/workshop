import zipfile

import pytest

from shop.scad import build_scad, find_openscad

pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not installed")


def objects(tmf):
    return zipfile.ZipFile(tmf).read("3D/3dmodel.model").decode()


def test_one_body_is_named_for_the_part_not_the_tool(tmp_path):
    (tmp_path / "m.scad").write_text("// parts: lid\ncube(10);")
    out = build_scad(tmp_path / "m.scad", tmp_path, "box_scad", render=False, threemf=True)
    assert 'name="lid"' in objects(out["3mf"]) and "OpenSCAD Model" not in objects(out["3mf"])


def test_undeclared_one_body_takes_the_project_name(tmp_path):
    (tmp_path / "m.scad").write_text("cube(10);")
    out = build_scad(tmp_path / "m.scad", tmp_path, "box_scad", render=False, threemf=True)
    assert 'name="box"' in objects(out["3mf"])


def test_bodies_take_declared_names_front_to_back_then_left_to_right(tmp_path):
    (tmp_path / "m.scad").write_text("// parts: front-left, front-right, back\ncube(5);translate([10,0,0])cube(5);translate([0,10,0])cube(5);")
    out = build_scad(tmp_path / "m.scad", tmp_path, "p_scad", render=False, threemf=True)
    m = objects(out["3mf"])
    assert [n in m for n in ("front-left", "front-right", "back")] == [True] * 3 and "3mf_warning" not in out


def test_missing_names_warn_and_fall_back_to_a_numbered_name(tmp_path):
    (tmp_path / "m.scad").write_text("cube(5);translate([10,0,0])cube(5);")
    out = build_scad(tmp_path / "m.scad", tmp_path, "p_scad", render=False, threemf=True)
    assert "declare a name per part" in out["3mf_warning"] and 'name="p-1"' in objects(out["3mf"])

