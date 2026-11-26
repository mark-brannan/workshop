import itertools
import zipfile

import pytest
import trimesh

from shop.plate import BED, MARGIN, pack, write_3mf


def boxes(*dims):
    return [(f"b{i}", trimesh.creation.box(extents=d)) for i, d in enumerate(dims)]


def test_parts_land_on_the_bed_inside_the_margin_without_overlap():
    placed = pack(boxes((231, 89, 20), (92, 86, 11), (69, 113, 48), (106, 67, 96), (40, 85, 30), (46, 28, 6)))
    for p in placed:
        lo, hi = p.mesh.bounds
        assert lo[2] == pytest.approx(0)
        assert lo[0] >= MARGIN - 1e-6 and lo[1] >= MARGIN - 1e-6
        assert hi[0] <= BED[0] - MARGIN + 1e-6 and hi[1] <= BED[1] - MARGIN + 1e-6
    for a, b in itertools.combinations(placed, 2):
        (al, ah), (bl, bh) = a.mesh.bounds, b.mesh.bounds
        apart = ah[0] <= bl[0] or bh[0] <= al[0] or ah[1] <= bl[1] or bh[1] <= al[1]
        assert apart, f"{a.name} overlaps {b.name}"


def test_overfull_plate_refuses():
    with pytest.raises(ValueError, match="split the plate"):
        pack(boxes(*[(300, 150, 5)] * 3))


def test_3mf_holds_one_named_object_per_part(tmp_path):
    placed = pack(boxes((20, 20, 5), (30, 10, 5)))
    out = tmp_path / "p.3mf"
    write_3mf(placed, out)
    model = zipfile.ZipFile(out).read("3D/3dmodel.model").decode()
    assert model.count("<object ") == 2 and 'name="b0"' in model and 'name="b1"' in model


def test_placed_parts_keep_their_pose_and_sit_where_asked():
    from shop.plate import place

    a, b = boxes((20, 10, 5), (20, 10, 5))
    placed = place([("a", a[1], (-80, 26)), ("b", b[1], (80, -26))])
    for p, (x, y) in zip(placed, [(-80, 26), (80, -26)]):
        c = p.mesh.bounds.mean(axis=0)
        assert (c[0] - BED[0] / 2, c[1] - BED[1] / 2) == pytest.approx((x, y))
        assert p.mesh.bounds[0][2] == pytest.approx(0)
        assert p.mesh.extents == pytest.approx([20, 10, 5])  # not turned


def test_placing_off_the_bed_refuses():
    from shop.plate import place

    with pytest.raises(ValueError, match="off the bed"):
        place([("a", boxes((20, 10, 5))[0][1], (170, 0))])
