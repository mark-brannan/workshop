"""Overlay the sump box's traced wing outline on the platform deck: `uv run python projects/shower-sump-platform/wing_overlay.py`.

Reads the deck from model.scad's parameters and the outline from ref/sump-wing-outline.csv; writes out/wing-overlay.png
(wing in yellow, deck in blue, hull line dashed) and prints the least lateral margin of the wing inside the deck."""

import math
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Polygon, Rectangle  # noqa: E402

HERE = Path(__file__).parent
P = {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*(-?[\d.]+)\s*;", (HERE / "model.scad").read_text(), re.M)}


def deck_half_width(y):
    """Half-width of the deck's top face at fore-aft position y (the model's trapezoid, bond gap taken off)."""
    gap = P["bond_gap"] / math.sin(math.radians(P["hull_angle"]))
    a, f = P["w_aft"] / 2 - gap, P["w_fwd"] / 2 - gap
    return a + (f - a) * (y + P["len"] / 2) / P["len"]


def wing():
    rows = [r.split(",") for r in (HERE / "ref" / "sump-wing-outline.csv").read_text().splitlines() if r and r[0] not in "#x"]
    return [(float(x), float(y)) for x, y in rows]


def margins(outline=None):
    """Lateral clearance of each wing point inside the deck edge (negative = sticks out), for points over the deck's length."""
    return [deck_half_width(y) - x for x, y in (outline or wing()) if abs(y) <= P["len"] / 2]


def draw(path):
    bg = "#14181f"
    fig, ax = plt.subplots(figsize=(11, 5.2), facecolor=bg)
    ax.set_facecolor(bg)
    ha, hf, L = deck_half_width(-P["len"] / 2), deck_half_width(P["len"] / 2), P["len"]
    ax.add_patch(Polygon([(-ha, -L / 2), (ha, -L / 2), (hf, L / 2), (-hf, L / 2)], fc="#5f6f90", ec="#cfd6e6", lw=1.5))
    ox, oy = P["opening_x"] if "opening_x" in P else 176, 59
    ax.add_patch(Rectangle((-ox / 2, -oy / 2), ox, oy, fc=bg, ec="#cfd6e6", lw=1))
    for s in (-1, 1):
        pts = [(s * x, y) for x, y in wing()]
        ax.plot([p[0] for p in pts] + [s * 93], [p[1] for p in pts] + [pts[0][1]], color="#ffe066", lw=2.2)
        for y in (25, -34):
            ax.add_patch(Circle((s * 93, y), 4.5, fc="none", ec="#ffe066", lw=1.2))
        ax.add_patch(Circle((s * 100, 0), 2.5, fc="none", ec="#ffe066", lw=1.2))
    ax.set_xlim(-130, 130)
    ax.set_ylim(-62, 60)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"Sump wing outline (yellow) on the deck; least margin {min(margins()):.1f} mm", color="w")
    fig.savefig(path, dpi=130, facecolor=bg)


if __name__ == "__main__":
    out = HERE / "out" / "wing-overlay.png"
    draw(out)
    print(f"{out}\nleast lateral margin of the wing inside the deck: {min(margins()):.2f} mm")
