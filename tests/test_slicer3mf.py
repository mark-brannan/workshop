import zipfile
from pathlib import Path

from shop import slicer3mf

MODEL = ('<?xml version="1.0"?><model><resources><object id="1"><mesh><vertices>{v}</vertices>'
         '<triangles><triangle v1="0" v2="1" v3="2"/></triangles></mesh></object></resources>'
         '<build><item objectid="1" transform="1 0 0 0 1 0 0 0 1 5 6 7"/></build></model>')


def verts(*pts):
    return "".join(f'<vertex x="{x}" y="{y}" z="{z}"/>' for x, y, z in pts)


def fresh(path: Path, h: float):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("3D/3dmodel.model", MODEL.format(v=verts((0, 0, 0), (10, 0, 0), (0, 10, h))))


def project(path: Path, h: float):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("3D/3dmodel.model", MODEL.format(v=verts((0, 0, 0), (0, 0, 0), (0, 0, 0))).replace("<mesh>", "<components/><mesh>", 0))
        z.writestr("3D/Objects/o.model", MODEL.format(v=verts((-5, -5, -h / 2), (5, -5, -h / 2), (-5, 5, h / 2))))
        z.writestr(slicer3mf.SETTINGS, '{"layer_height": "0.2"}')


def test_no_project_is_left_alone(tmp_path):
    p = tmp_path / "a.3mf"
    fresh(p, 4)
    assert slicer3mf.read_prior(p) is None
    assert slicer3mf.read_prior(tmp_path / "missing.3mf") is None


def test_unchanged_geometry_keeps_the_users_file(tmp_path):
    p = tmp_path / "a.3mf"
    project(p, 4)
    old = p.read_bytes()
    prior = slicer3mf.read_prior(p)
    fresh(p, 4)
    assert "unchanged" in slicer3mf.carry(prior, p)
    assert p.read_bytes() == old and not (tmp_path / "printed").exists()


def test_changed_geometry_archives_and_grafts(tmp_path):
    p = tmp_path / "a.3mf"
    project(p, 4)
    old = p.read_bytes()
    prior = slicer3mf.read_prior(p)
    fresh(p, 8)
    slicer3mf.carry(prior, p)
    (arch,) = (tmp_path / "printed").glob("a.*.3mf")
    assert arch.read_bytes() == old
    with zipfile.ZipFile(p) as z:
        assert slicer3mf.SETTINGS in z.namelist()  # settings survive
        zs = [v[2] for v in slicer3mf._verts(z.read("3D/Objects/o.model").decode())]
        assert max(zs) - min(zs) == 8 and abs(max(zs) + min(zs)) < 1e-6  # new mesh, recentred
        assert 'transform="1 0 0 0 1 0 0 0 1 5 6 4"' in z.read("3D/3dmodel.model").decode()  # sits on the bed
