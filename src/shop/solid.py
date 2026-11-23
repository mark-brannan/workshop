"""A warning for the build log, never a failure: the mesh is not a closed solid.

An edge shared by other than two faces means a hole or two sheets touching along a line. A slicer
repairs it quietly, so it shows up nowhere else, and an OpenSCAD model whose mesh changes from build
to build (a minkowski() of non-convex shapes on Manifold, for one) is open on most builds only.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path


def open_edges(mesh) -> list[tuple[int, tuple[float, float, float]]]:
    """(faces on the edge, its midpoint) for every edge not shared by exactly two faces."""
    counts = Counter(map(tuple, mesh.edges_sorted.tolist()))
    v = mesh.vertices
    return [(n, tuple(round(float(c), 2) for c in (v[a] + v[b]) / 2)) for (a, b), n in counts.items() if n != 2]


def warnings(stl: Path | str) -> list[str]:
    import trimesh

    mesh = trimesh.load(stl)
    if not hasattr(mesh, "edges_sorted") or mesh.is_watertight:
        return []
    bad = open_edges(mesh)
    if not bad:
        return []
    n, at = bad[0]
    return [f"not a closed solid: {len(bad)} edges not shared by two faces, first ({n} faces) near x {at[0]} y {at[1]} z {at[2]}"]
