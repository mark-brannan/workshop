import math
from pathlib import Path

import pytest
from build123d import Axis, import_step

from shop.testing import load_model

_m = load_model(__file__)
BracketParams = _m.BracketParams
build = _m.build

P = BracketParams()


@pytest.fixture(scope="module")
def part():
    return build(P)


def test_bounding_box(part):
    bb = part.bounding_box()
    assert math.isclose(bb.size.X, P.width, abs_tol=0.01)
    assert math.isclose(bb.size.Y, P.base_depth, abs_tol=0.01)
    assert math.isclose(bb.size.Z, P.wall_height, abs_tol=0.01)
    assert math.isclose(bb.min.X, 0, abs_tol=0.01)
    assert math.isclose(bb.min.Y, 0, abs_tol=0.01)
    assert math.isclose(bb.min.Z, 0, abs_tol=0.01)


def test_hole_count_by_faces(part):
    # Each through hole has one cylindrical bore face (chamfer faces are cones).
    cyls = [f for f in part.faces() if f.geom_type.name == "CYLINDER"]
    bores = [f for f in cyls if math.isclose(f.radius, P.hole_d / 2, abs_tol=1e-6)]
    assert len(bores) == 2 * P.holes_per_leg
    # Fillet on the outside corner is also a cylinder, with a different radius.
    fillets = [f for f in cyls if math.isclose(f.radius, P.outer_fillet, abs_tol=1e-6)]
    assert len(fillets) == 1
    cones = [f for f in part.faces() if f.geom_type.name == "CONE"]
    assert len(cones) == 2 * P.holes_per_leg


def test_hole_axes(part):
    bores = [f for f in part.faces() if f.geom_type.name == "CYLINDER" and math.isclose(f.radius, P.hole_d / 2, abs_tol=1e-6)]
    axes = [f.axis_of_rotation.direction for f in bores]
    along_z = sum(1 for d in axes if math.isclose(abs(d.Z), 1, abs_tol=1e-6))
    along_y = sum(1 for d in axes if math.isclose(abs(d.Y), 1, abs_tol=1e-6))
    assert along_z == P.holes_per_leg
    assert along_y == P.holes_per_leg


def test_volume_sane(part):
    t = P.thickness
    plates = P.width * P.base_depth * t + P.width * P.wall_height * t - P.width * t * t
    hole = math.pi * (P.hole_d / 2) ** 2 * t
    nominal = plates - 2 * P.holes_per_leg * hole
    # fillet removes (1 - pi/4) r^2 * width; chamfers remove a little more
    fillet_loss = (1 - math.pi / 4) * P.outer_fillet**2 * P.width
    lo = nominal - fillet_loss - 2 * P.holes_per_leg * 60  # generous chamfer allowance
    hi = nominal - fillet_loss + 0.01
    assert lo < part.volume < hi, (lo, part.volume, hi)


def test_step_roundtrip(part, tmp_path: Path):
    from shop.export import export_all

    paths = export_all(part, "rt", tmp_path, render=False)
    assert paths["step"].exists() and paths["stl"].exists() and paths["3mf"].exists()
    back = import_step(paths["step"])
    assert math.isclose(back.volume, part.volume, rel_tol=1e-6)
    assert math.isclose(back.bounding_box().size.Z, P.wall_height, abs_tol=0.01)
