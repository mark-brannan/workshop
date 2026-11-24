"""Load a project's model.py next to its test file without sys.path games.

Each projects/<name>/ has a model.py and a test_model.py; the directories are
not packages, so tests load the sibling module by path under a unique name.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def load_model(test_file: str | Path, name: str = "model") -> ModuleType:
    here = Path(test_file).resolve().parent
    modname = f"{here.name.replace('-', '_')}_{name}"
    spec = importlib.util.spec_from_file_location(modname, here / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod


def ray_hits(mesh, origin, direction) -> list[list[float]]:
    """Points where a ray meets a trimesh mesh, nearest first (Moller-Trumbore, numpy only).

    trimesh's own ray engine needs rtree, which the venv lacks; this is enough
    for probing holes, chamfers and rounds in a test.
    """
    import numpy as np

    o, d = np.asarray(origin, float), np.asarray(direction, float)
    v0, v1, v2 = (mesh.triangles[:, i, :] for i in range(3))
    e1, e2 = v1 - v0, v2 - v0
    p = np.cross(d, e2)
    det = np.einsum("ij,ij->i", e1, p)
    ok = np.abs(det) > 1e-12
    inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
    s = o - v0
    u = np.einsum("ij,ij->i", s, p) * inv
    q = np.cross(s, e1)
    v = np.einsum("ij,j->i", q, d) * inv
    t = np.einsum("ij,ij->i", e2, q) * inv
    hit = ok & (u >= -1e-9) & (v >= -1e-9) & (u + v <= 1 + 1e-9) & (t > 1e-9)
    ts = np.unique(np.round(t[hit], 6))  # shared edges/vertices count once
    return [(o + ti * d).tolist() for ti in ts]


# A hand turns a printed part over; it cannot mirror it. These are the two turns, as OpenSCAD transforms.
TURNS = {"about X": "rotate([180, 0, 0])", "about Y": "rotate([0, 180, 0])"}


def seated_overlap(tmp_path, mate, part, place: str, mirror: str | None = None) -> float:
    """Volume in mm3 that a printed part shares with its mate once it is seated: 0 when it fits.

    ``mate`` and ``part`` are the meshes that get printed, each in its print pose. ``place`` is the
    OpenSCAD move that carries the part from its print pose to where it is used, built from
    ``rotate()`` and ``translate()`` only, never ``mirror()``: the move a hand makes.

    ``mirror`` (an axis such as ``"[1, 0, 0]"``) seats the part's mirror image instead. A fit test
    worth having finds an overlap there for a part that differs from its mirror image; one that
    reads 0 both ways cannot tell the part from its mirror, and needs a check of what engages.
    """
    import trimesh

    from shop.scad import build_scad

    if "mirror" in place:
        raise ValueError(f"place is a hand's move, rotate() and translate() only: {place}")
    tmp_path = Path(tmp_path)
    tag = f"fit{len(list(tmp_path.glob('fit*.scad')))}"
    mate.export(tmp_path / f"{tag}-mate.stl")
    part.export(tmp_path / f"{tag}-part.stl")
    flip = f"mirror({mirror}) " if mirror else ""
    (tmp_path / f"{tag}.scad").write_text(
        f'intersection() {{ import("{tmp_path}/{tag}-mate.stl"); {place} {flip}import("{tmp_path}/{tag}-part.stl"); }}\n')
    try:
        out = build_scad(tmp_path / f"{tag}.scad", tmp_path, tag, render=False)
    except RuntimeError as e:
        if "top level object is empty" in str(e):  # nothing shared: openscad refuses to export nothing
            return 0.0
        raise
    return abs(trimesh.load(out["stl"]).volume)
