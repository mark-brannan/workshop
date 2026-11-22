"""The flat-overhang warning: a bare bridge is reported at its length, a held one is not."""

import trimesh
from shop.overhang import flat_spans


def portal(prop: bool):
    """Two legs and a beam bridging 10 between them, as one solid; optionally a block one layer under the beam."""
    outline = [(-7, 0), (-5, 0), (-5, 10), (5, 10), (5, 0), (7, 0), (7, 12), (-7, 12)]
    caps = [(0, 1, 2), (0, 2, 7), (2, 3, 7), (3, 6, 7), (3, 4, 5), (3, 5, 6)]
    verts = [(x, y, z) for y in (-1, 1) for x, z in outline]
    faces = [(c, b, a) for a, b, c in caps] + [(a + 8, b + 8, c + 8) for a, b, c in caps]
    for i in range(8):
        j = (i + 1) % 8
        faces += [(i, j, j + 8), (i, j + 8, i + 8)]
    solid = trimesh.Trimesh(verts, faces)
    solid.fix_normals()
    assert solid.is_watertight
    if not prop:
        return solid
    block = trimesh.creation.box((9.6, 1.6, 9.8), trimesh.transformations.translation_matrix((0, 0, 4.9)))
    return trimesh.util.concatenate([solid, block])


def test_bare_bridge_is_reported_at_its_length():
    (s,) = flat_spans(portal(False))
    assert abs(s["span"] - 10) < 0.5 and s["z"] == 10 and not s["free"]


def test_bridge_resting_on_a_modelled_support_is_quiet():
    assert flat_spans(portal(True)) == []
