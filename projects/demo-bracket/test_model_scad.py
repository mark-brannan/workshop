"""Mesh-level tests for model.scad: the same checks as test_model.py where an STL allows.

No mesh equivalent: counting bores/fillets/cones by B-rep face type, reading
hole axes from cylinder faces, STEP round trip. Replaced here by ray probes:
a ray down a hole centre hits nothing; a ray just outside the bore lands on
the chamfer cone at the depth a 45 deg chamfer predicts; a ray up through
the outside corner lands on the round at the height a 2 mm arc predicts.
"""

import math
import re
from pathlib import Path

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
T, W, D, H = P["thickness"], P["width"], P["base_depth"], P["wall_height"]
HOLE_X = [W / 2 + (i - (P["holes_per_leg"] - 1) / 2) * P["hole_pitch"] for i in range(int(P["holes_per_leg"]))]


@pytest.fixture(scope="module")
def mesh(tmp_path_factory) -> trimesh.Trimesh:
    paths = build_scad(HERE / "model.scad", tmp_path_factory.mktemp("scad"), "bracket", render=False)
    return trimesh.load(paths["stl"])


hits = ray_hits


def test_bounding_box(mesh):
    lo, hi = mesh.bounds
    assert np.allclose(lo, [0, 0, 0], atol=0.05)
    assert np.allclose(hi, [W, D, H], atol=0.05)


def test_watertight(mesh):
    assert mesh.is_watertight


def test_volume_sane(mesh):
    plates = W * D * T + W * H * T - W * T * T
    hole = math.pi * (P["hole_d"] / 2) ** 2 * T
    nominal = plates - 2 * P["holes_per_leg"] * hole
    fillet_loss = (1 - math.pi / 4) * P["outer_fillet"] ** 2 * W
    lo = nominal - fillet_loss - 2 * P["holes_per_leg"] * 60
    hi = nominal - fillet_loss + 0.5  # +0.5 mm^3: $fn polygons under-cut the holes a little
    assert lo < mesh.volume < hi, (lo, mesh.volume, hi)


def test_holes_through(mesh):
    r_clear = P["hole_d"] / 2 + P["hole_chamfer"] + 0.3
    base_y, wall_z = (D + T) / 2, (H + T) / 2
    for x in HOLE_X:
        assert hits(mesh, (x, base_y, 10), (0, 0, -1)) == []  # base hole, along Z
        assert len(hits(mesh, (x + r_clear, base_y, 10), (0, 0, -1))) == 2  # solid beside it
        assert hits(mesh, (x, -10, wall_z), (0, 1, 0)) == []  # wall hole, along Y
        assert len(hits(mesh, (x + r_clear, -10, wall_z), (0, 1, 0))) == 2


def test_hole_chamfers(mesh):
    probe = 0.5  # radial offset into the chamfer; 45 deg cone -> same depth
    r = P["hole_d"] / 2 + probe
    for x in HOLE_X:
        top = hits(mesh, (x + r, (D + T) / 2, 10), (0, 0, -1))[0][2]
        assert math.isclose(top, T - probe, abs_tol=0.05), top
        outer = hits(mesh, (x + r, -10, (H + T) / 2), (0, 1, 0))[0][1]
        assert math.isclose(outer, probe, abs_tol=0.05), outer


def test_outer_round(mesh):
    r, y = P["outer_fillet"], 0.3
    expect = r - math.sqrt(r * r - (r - y) ** 2)  # arc height above z=0 at this y
    z = hits(mesh, (W / 2, y, -10), (0, 0, 1))[0][2]
    assert math.isclose(z, expect, abs_tol=0.05), (z, expect)
