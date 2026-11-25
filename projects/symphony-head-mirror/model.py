"""Outline of the head mirror over the sink, for a shatterproof replacement.

A four-sided plate with no right angles, solved from the owner's tape and
speed-square readings (README). Writes a DXF on LightBurn layer ``cut`` and a
dimensioned PNG, both viewed from the FRONT (the reflective face).

    uv run python projects/symphony-head-mirror/model.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

IN = 25.4
HERE = Path(__file__).parent
OUT = HERE / "out"


@dataclass
class Params:
    # Edges in inches, tape readings (README: which photo).
    top: float = 20 + 3 / 16      # long edge with "AGM 2 21-03" stamped on the back
    wide: float = 10 + 5 / 8      # end with the two touching adhesive pads
    bottom: float = 20 + 1 / 16   # other long edge
    narrow: float = 9 + 7 / 8     # other end; read 9 13/16 and 9 15/16
    corner_deg: float = 85.0      # speed square at the narrow-top corner
    clearance_mm: float = 0.0     # taken off every edge for the replacement; 0 = original size


def corners(p: Params = Params()) -> dict[str, np.ndarray]:
    """Corners in mm, front view, origin at the narrow-top corner, Y up."""
    t = np.radians(p.corner_deg)
    nt = np.array([0.0, 0.0])
    wt = np.array([p.top, 0.0])
    nb = nt + p.narrow * np.array([np.cos(t), -np.sin(t)])
    d = np.linalg.norm(wt - nb)
    x = (d * d + p.wide**2 - p.bottom**2) / (2 * d)
    h = np.sqrt(p.wide**2 - x * x)
    u = (nb - wt) / d
    v = np.array([u[1], -u[0]])
    wb = wt + x * u + h * v
    if wb[1] > 0:
        wb = wt + x * u - h * v
    pts = {"narrow-top": nt, "wide-top": wt, "wide-bottom": wb, "narrow-bottom": nb}
    # Solved as seen from the back (as photographed); the front is its mirror image.
    pts = {k: np.array([-q[0], q[1]]) * IN for k, q in pts.items()}
    lo = np.min(list(pts.values()), axis=0)
    pts = {k: q - lo for k, q in pts.items()}  # bounding box from (0, 0)
    if p.clearance_mm:
        pts = _inset(pts, p.clearance_mm)
    return pts


def _inset(pts: dict[str, np.ndarray], c: float) -> dict[str, np.ndarray]:
    """Move every edge inward by ``c`` mm, keeping its angle."""
    names = list(pts)
    P = [pts[n] for n in names]
    area = sum(P[i][0] * P[(i + 1) % 4][1] - P[(i + 1) % 4][0] * P[i][1] for i in range(4))
    s = 1 if area > 0 else -1
    lines = []
    for i in range(4):
        a, b = P[i], P[(i + 1) % 4]
        d = (b - a) / np.linalg.norm(b - a)
        n = s * np.array([-d[1], d[0]])
        lines.append((a + c * n, d))
    out = {}
    for i, name in enumerate(names):
        (a1, d1), (a2, d2) = lines[i - 1], lines[i]
        t = np.linalg.solve(np.column_stack([d1, -d2]), a2 - a1)
        out[name] = a1 + t[0] * d1
    return out


def angles(pts: dict[str, np.ndarray]) -> dict[str, float]:
    P = list(pts.values())
    res = {}
    for i, name in enumerate(pts):
        a, b = P[i - 1] - P[i], P[(i + 1) % 4] - P[i]
        res[name] = float(np.degrees(np.arccos(a @ b / np.linalg.norm(a) / np.linalg.norm(b))))
    return res


def write_dxf(pts: dict[str, np.ndarray], path: Path) -> None:
    import ezdxf

    doc = ezdxf.new("R2010", units=ezdxf.units.MM)
    doc.layers.add("cut", color=5)
    doc.modelspace().add_lwpolyline([tuple(q) for q in pts.values()], close=True, dxfattribs={"layer": "cut"})
    doc.saveas(path)


def write_png(pts: dict[str, np.ndarray], path: Path, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fg, bg, dim = "#e8e8e8", "#1e1f22", "#7fb3ff"
    names = list(pts)
    P = np.array([pts[n] for n in names])
    ang = angles(pts)
    fig, ax = plt.subplots(figsize=(13, 7.5), facecolor=bg)
    ax.set_facecolor(bg)
    ax.fill(*np.vstack([P, P[:1]]).T, color="#3a4a5a", ec=fg, lw=2)
    c = P.mean(axis=0)
    for i in range(4):
        a, b = P[i], P[(i + 1) % 4]
        m = (a + b) / 2
        L = np.linalg.norm(b - a)
        off = (m - c) / np.linalg.norm(m - c) * 22
        rot = np.degrees(np.arctan2(b[1] - a[1], b[0] - a[0]))
        rot = rot - 180 if abs(rot) > 90 else rot
        ax.text(*(m + off), f'{L:.1f} mm  ({L / IN:.2f}")', color=dim, ha="center", va="center", rotation=rot, fontsize=12)
    for n, q in zip(names, P):
        off = (q - c) / np.linalg.norm(q - c) * 30
        ax.text(*(q + off), f"{n}\n{ang[n]:.1f}°", color=fg, ha="center", va="center", fontsize=10)
        ax.plot(*q, "o", color=dim)
    for a, b in ((P[0], P[2]), (P[1], P[3])):
        ax.plot(*np.array([a, b]).T, ls=":", color="#888")
        m = a + (b - a) * 0.3 + np.array([0, 8])
        ax.text(*m, f"diagonal {np.linalg.norm(b - a):.1f}", color="#aaa", fontsize=9, ha="center")
    ax.text(c[0], c[1] - 20, "FRONT (reflective face) toward you", color=fg, ha="center", fontsize=11)
    ax.set_title(title, color=fg, pad=34)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(path, dpi=110, facecolor=bg, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    slug = HERE.name
    orig = corners()
    write_dxf(orig, OUT / f"{slug}.dxf")
    write_png(orig, OUT / f"{slug}.png", "Head mirror, original size (front view, mm)")
    for n, q in orig.items():
        print(f"{n:14s} x={q[0]:8.1f}  y={q[1]:8.1f}  angle={angles(orig)[n]:.1f}")


if __name__ == "__main__":
    main()
