"""Tests for model.scad: DXF from the 2D form, STL from the 3 mm extrude.

No mesh/DXF equivalent: sketch area from the B-rep and CIRCLE/ARC entity
counts (OpenSCAD 2021.01 writes every curve as LINE segments). The layer name
and units come from shop.scad.finish_dxf. Replaced by: closed-loop count in
the DXF, ray probes through the holes in the mesh.
"""

import math
import re
from pathlib import Path

import ezdxf
import numpy as np
import pytest
import trimesh
from shop.scad import build_scad, find_openscad
from shop.testing import ray_hits

HERE = Path(__file__).parent
pytestmark = pytest.mark.skipif(find_openscad() is None, reason="openscad not found")


def scad_params(path: Path) -> dict[str, float]:
    head = path.read_text().split("module", 1)[0]
    return {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*([-\d.]+)\s*;", head, re.M)}


P = scad_params(HERE / "model.scad")
L, W, T = P["length"], P["width"], P["thickness"]
HOLES = [(sx * (L / 2 - P["hole_inset"]), sy * (W / 2 - P["hole_inset"])) for sx in (-1, 1) for sy in (-1, 1)]


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    return build_scad(HERE / "model.scad", tmp_path_factory.mktemp("scad"), "plate", two_d=True, render=False)


@pytest.fixture(scope="module")
def mesh(built) -> trimesh.Trimesh:
    return trimesh.load(built["stl"])


def test_bounding_box(mesh):
    lo, hi = mesh.bounds
    assert np.allclose(lo, [-L / 2, -W / 2, 0], atol=0.05)
    assert np.allclose(hi, [L / 2, W / 2, T], atol=0.05)


def test_watertight(mesh):
    assert mesh.is_watertight


def test_volume_sane(mesh):
    holes = 4 * math.pi * (P["hole_d"] / 2) ** 2
    slot = P["slot_length"] * P["slot_width"] + math.pi * (P["slot_width"] / 2) ** 2
    nominal = (L * W - holes - slot) * T
    assert math.isclose(mesh.volume, nominal, abs_tol=2.0), (mesh.volume, nominal)  # $fn faceting slack


def test_holes_through(mesh):
    def n_hits(x, y):
        return len(ray_hits(mesh, (x, y, 10), (0, 0, -1)))

    for x, y in HOLES:
        assert n_hits(x, y) == 0
    for x in (-P["slot_length"] / 2, 0, P["slot_length"] / 2):
        assert n_hits(x, 0) == 0
    assert n_hits(L / 4, W / 4) == 2


def test_dxf_entities(built):
    doc = ezdxf.readfile(built["dxf"])
    ents = list(doc.modelspace())
    # 2021.01 writes every curve as LINE segments; the 2026 nightly writes closed LWPOLYLINEs.
    assert {e.dxftype() for e in ents} <= {"LINE", "LWPOLYLINE"}, {e.dxftype() for e in ents}
    assert all(e.dxf.layer == "cut" for e in ents)  # finish_dxf re-layers OpenSCAD's "0"
    assert doc.header["$INSUNITS"] == 4  # mm

    # Closed loops: outline + 4 holes + slot = 6.
    polys = [e for e in ents if e.dxftype() == "LWPOLYLINE"]
    assert all(e.closed for e in polys)
    parent: dict = {}

    def find(a):
        while parent.setdefault(a, a) != a:
            a = parent[a]
        return a

    xs, ys = [], []
    for e in ents:
        if e.dxftype() == "LINE":
            a, b = (round(e.dxf.start.x, 3), round(e.dxf.start.y, 3)), (round(e.dxf.end.x, 3), round(e.dxf.end.y, 3))
            parent[find(a)] = find(b)
            pts = [a, b]
        else:
            pts = [(x, y) for x, y, *_ in e.get_points()]
        xs += [q[0] for q in pts]
        ys += [q[1] for q in pts]
    loops = len(polys) + len({find(k) for k in parent})
    assert loops == 6, loops
    assert math.isclose(max(xs) - min(xs), L, abs_tol=0.01)
    assert math.isclose(max(ys) - min(ys), W, abs_tol=0.01)
