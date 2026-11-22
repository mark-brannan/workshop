"""Flat overhangs in a printable mesh, and how far each spans with nothing under it.

A warning for the build log, never a failure. A flat overhang is a level face looking down, above the bed.
A point on it counts as held when material sits within ``gap`` below it (a modelled breakaway support).
Spans are measured along X and Y only, between anchors: solid beside the face, or a held point.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

MIN_SPAN = 2.0   # shorter than this gets no line (a guess, not a measured K2 number)


class _Near:
    """Vertical queries against only the triangles whose XY box meets a patch's."""

    def __init__(self, level, lo, hi, pad):
        t, n, tl, th = level
        keep = (th >= lo - pad).all(1) & (tl <= hi + pad).all(1)
        self.t, self.n = t[keep], n[keep]

    def heights(self, pts: np.ndarray) -> np.ndarray:
        """For each XY point, the z of every near triangle over it (nan where the triangle is not over it)."""
        if not len(self.t) or not len(pts):
            return np.full((len(pts), 0), np.nan)
        a, b, c = self.t[:, 0, :2], self.t[:, 1, :2], self.t[:, 2, :2]
        def side(p, q):
            return (q[None, :, 0] - p[None, :, 0]) * (pts[:, None, 1] - p[None, :, 1]) - (q[None, :, 1] - p[None, :, 1]) * (pts[:, None, 0] - p[None, :, 0])
        d1, d2, d3 = side(a, b), side(b, c), side(c, a)
        over = ~(((d1 < 0) | (d2 < 0) | (d3 < 0)) & ((d1 > 0) | (d2 > 0) | (d3 > 0)))
        n, v0 = self.n, self.t[:, 0, :]
        z = v0[None, :, 2] - (n[None, :, 0] * (pts[:, None, 0] - v0[None, :, 0]) + n[None, :, 1] * (pts[:, None, 1] - v0[None, :, 1])) / n[None, :, 2]
        return np.where(over, z, np.nan)


def _patches(mesh, flat: np.ndarray) -> list[np.ndarray]:
    """Flat faces grouped by level and touching bounding boxes (cheap, and good enough for a warning)."""
    tris = mesh.triangles[flat]
    groups: list[list[int]] = []
    boxes: list[list[float]] = []
    for i in np.argsort(tris[:, 0, 2]):
        t = tris[i]
        lo, hi, z = t[:, :2].min(0), t[:, :2].max(0), t[0, 2]
        for g, b in zip(groups, boxes):
            if abs(b[4] - z) < 0.01 and lo[0] <= b[2] + 0.01 and hi[0] >= b[0] - 0.01 and lo[1] <= b[3] + 0.01 and hi[1] >= b[1] - 0.01:
                g.append(i)
                b[0], b[1], b[2], b[3] = min(b[0], lo[0]), min(b[1], lo[1]), max(b[2], hi[0]), max(b[3], hi[1])
                break
        else:
            groups.append([i])
            boxes.append([lo[0], lo[1], hi[0], hi[1], z])
    return [tris[g] for g in groups]


def _in_tris(tris: np.ndarray, pts: np.ndarray) -> np.ndarray:
    a, b, c = tris[:, 0, :2], tris[:, 1, :2], tris[:, 2, :2]
    def side(p, q, r):
        return (q[None, :, 0] - p[None, :, 0]) * (r[:, None, 1] - p[None, :, 1]) - (q[None, :, 1] - p[None, :, 1]) * (r[:, None, 0] - p[None, :, 0])
    d1, d2, d3 = side(a, b, pts), side(b, c, pts), side(c, a, pts)
    neg, pos = (d1 < 0) | (d2 < 0) | (d3 < 0), (d1 > 0) | (d2 > 0) | (d3 > 0)
    return (~(neg & pos)).any(axis=1)


def flat_spans(mesh, gap: float = 0.3) -> list[dict]:
    """One entry per flat overhang with an unheld span of MIN_SPAN or more, longest first.

    Each: ``z``, ``span`` (mm), ``at`` (x, y of the span's middle) and ``free`` (True when one end hangs in air).
    """
    flat = (mesh.face_normals[:, 2] < -0.999) & (mesh.triangles_center[:, 2] > 0.05)
    lying = np.abs(mesh.face_normals[:, 2]) > 1e-6          # upright faces never sit over a point
    t = mesh.triangles[lying]
    level = (t, mesh.face_normals[lying], t[:, :, :2].min(1), t[:, :, :2].max(1))
    out = []
    for tris in _patches(mesh, flat) if flat.any() else []:
        z = float(tris[0, 0, 2])
        lo, hi = tris[:, :, :2].min((0, 1)), tris[:, :, :2].max((0, 1))
        step = max(0.25, float((hi - lo).max()) / 60)
        # one cell of margin all round, nudged off the grid so no sample sits on a triangle edge
        xs = np.arange(lo[0] - step / 2, hi[0] + step, step) + 0.0113
        ys = np.arange(lo[1] - step / 2, hi[1] + step, step) + 0.0071
        gx, gy = np.meshgrid(xs, ys, indexing="ij")
        on = _in_tris(tris, np.c_[gx.ravel(), gy.ravel()]).reshape(gx.shape)
        near = _Near(level, lo, hi, 2 * step)
        zs = near.heights(np.c_[gx.ravel(), gy.ravel()])
        with np.errstate(invalid="ignore"):
            held = (((zs < z - 0.005) & (zs > z - gap)).any(1)).reshape(on.shape) & on
        bare = on & ~held
        with np.errstate(invalid="ignore"):
            solid = (np.sum(zs > z - 0.05, axis=1) % 2 == 1).reshape(on.shape)

        def anchored(i, j):
            return bool(held[i, j] or solid[i, j])

        best = None
        for axis in (0, 1):
            m = bare if axis == 0 else bare.T
            for k in range(m.shape[1]):
                col, i = m[:, k], 0
                while i < len(col):
                    if not col[i]:
                        i += 1
                        continue
                    j = i
                    while j < len(col) and col[j]:
                        j += 1
                    ends = [(i - 1, k), (j, k)] if axis == 0 else [(k, i - 1), (k, j)]
                    a, b = (anchored(*e) for e in ends)
                    if a or b:
                        mid = ((i + j - 1) / 2, k) if axis == 0 else (k, (i + j - 1) / 2)
                        cand = {"span": (j - i) * step, "free": not (a and b), "ij": mid, "axis": axis}
                        cell = (int(mid[0]), int(mid[1]))
                        best_here = cand  # a cell's span is its shorter anchored run (a sliver beside a held point is held)
                        other = _cross_run(bare, cell, 1 - axis) * step
                        ends_held = _cross_anchored(bare, cell, 1 - axis, anchored)
                        if other < cand["span"] and (ends_held == 2 or (ends_held == 1 and other < MIN_SPAN)):
                            best_here = None
                        if best_here and (best is None or best_here["span"] > best["span"]):
                            best = best_here
                    i = j
        if best and best["span"] >= MIN_SPAN:
            x = xs[0] + best["ij"][0] * step
            y = ys[0] + best["ij"][1] * step
            out.append({"z": round(z, 2), "span": round(best["span"], 1), "at": (round(float(x), 1), round(float(y), 1)), "free": best["free"]})
    return sorted(out, key=lambda d: -d["span"])


def _run_bounds(bare, cell, axis):
    i, j = cell
    line = bare[:, j] if axis == 0 else bare[i, :]
    p = i if axis == 0 else j
    a = b = p
    while a - 1 >= 0 and line[a - 1]:
        a -= 1
    while b + 1 < len(line) and line[b + 1]:
        b += 1
    return a, b


def _cross_run(bare, cell, axis) -> int:
    a, b = _run_bounds(bare, cell, axis)
    return b - a + 1


def _cross_anchored(bare, cell, axis, anchored) -> int:
    a, b = _run_bounds(bare, cell, axis)
    i, j = cell
    ends = [(a - 1, j), (b + 1, j)] if axis == 0 else [(i, a - 1), (i, b + 1)]
    return sum(bool(anchored(*e)) for e in ends)


def warnings(stl: Path | str) -> list[str]:
    import trimesh

    mesh = trimesh.load(stl)
    if not hasattr(mesh, "face_normals"):
        return []
    lines = [
        f"flat overhang at z {s['z']}: {s['span']} mm unsupported{' (one end free)' if s['free'] else ''}, near x {s['at'][0]} y {s['at'][1]}"
        for s in flat_spans(mesh)
    ]
    return lines[:3] + ([f"and {len(lines) - 3} more flat overhangs, shorter"] if len(lines) > 3 else [])
