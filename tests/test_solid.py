"""The closed-solid warning: quiet on a closed mesh, loud on an open or pinched one."""

import trimesh

from shop import solid


def test_closed_box_is_quiet(tmp_path):
    p = tmp_path / "box.stl"
    trimesh.creation.box([10, 10, 10]).export(p)
    assert solid.warnings(p) == []


def test_open_box_warns(tmp_path):
    box = trimesh.creation.box([10, 10, 10])
    box.update_faces(list(range(1, len(box.faces))))     # one triangle gone
    p = tmp_path / "open.stl"
    box.export(p)
    (w,) = solid.warnings(p)
    assert w.startswith("not a closed solid: 3 edges")


def test_boxes_touching_on_an_edge_warn(tmp_path):
    a = trimesh.creation.box([10, 10, 10])
    b = trimesh.creation.box([10, 10, 10])
    b.apply_translation([10, 10, 0])                     # meets a along one vertical edge only
    p = tmp_path / "pinch.stl"
    trimesh.util.concatenate([a, b]).export(p)
    (w,) = solid.warnings(p)
    assert "(4 faces)" in w
