"""1:1 drilling template for the one-wire enclosure: one strip per wall, printed on A4 at 100 %.

Cut each strip along its outline, fold nothing: set its bottom edge on the bench with the box
standing on it, line the strip's left end up with a vertical outer corner, tape it, centre-punch
through each cross, then step-drill to the printed hole size. Positions come from model.layout().
Run from the repo root: uv run python projects/one-wire-enclosure/template.py
"""
import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

sys.path.insert(0, str(Path(__file__).parent))
from model import Box, PARTS, layout  # noqa: E402

MM = 1 / 25.4
PAGE_W, PAGE_H = 210.0, 297.0   # A4, mm
STRIP_H = 30.0                   # below the lid seam (26.5) plus a little


def main(out_dir):
    b = Box()
    walls = [(n, L, items) for n, (L, _, items) in layout(b).items()]
    fig = plt.figure(figsize=(PAGE_W * MM, PAGE_H * MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, PAGE_W); ax.set_ylim(0, PAGE_H); ax.axis("off")
    ax.text(10, PAGE_H - 12, "One-wire enclosure 63 x 58 x 35: drilling template", fontsize=12, weight="bold")
    ax.text(10, PAGE_H - 19, "Print at 100 % (no fit to page). Check the bar: it must measure 50 mm with calipers.",
            fontsize=8)
    ax.plot([10, 60], [PAGE_H - 26] * 2, "k", lw=1.5)
    for x in (10, 60):
        ax.plot([x, x], [PAGE_H - 28, PAGE_H - 24], "k", lw=1.5)
    ax.text(35, PAGE_H - 33, "50 mm", ha="center", fontsize=8)
    ax.text(10, PAGE_H - 42, "Cut out each strip. Box stands on the bench; strip bottom edge on the bench, left end flush with "
            "a vertical outer corner.\nTape, centre-punch each cross, drill the pilot, then step-drill to the printed hole "
            "size. Dashed = nut footprint, keep clear of the dotted lid seam.", fontsize=7, va="top")
    y = PAGE_H - 60
    for name, L, items in walls:
        y0 = y - STRIP_H
        ax.add_patch(Rectangle((10, y0), L, STRIP_H, fill=False, ec="k", lw=0.8))
        seam = b.H - b.lid
        ax.plot([10, 10 + L], [y0 + seam] * 2, ":", color="#a77", lw=0.8)
        col = b.col(L)
        for xx in (col, L - col):  # start of the corner column's curve: nothing may cross this
            ax.plot([10 + xx] * 2, [y0, y0 + seam], ":", color="#c0392b", lw=0.9)
        ax.text(10 + col + 1, y0 + seam - 3, "clear span %g (red dotted = column starts)" % b.clear, fontsize=5, color="#c0392b")
        ax.text(10 + L + 3, y0 + seam, "lid seam (z %.1f)" % seam, fontsize=6, color="#a77", va="center")
        ax.text(10 + L + 3, y0 + 14, f"{name}, {L:g} wide", fontsize=8, weight="bold")
        ax.text(10 + L + 3, y0 + 2, "bottom edge = outer base", fontsize=6, color="#555")
        for p, x, z in items:
            hd, nd, *_ = PARTS[p]
            cx, cy = 10 + x, y0 + z
            ax.add_patch(Circle((cx, cy), hd / 2, fill=False, ec="k", lw=0.8))
            ax.add_patch(Circle((cx, cy), nd / 2, fill=False, ec="#888", lw=0.6, ls="--"))
            ax.plot([cx - 4, cx + 4], [cy, cy], "k", lw=0.6); ax.plot([cx, cx], [cy - 4, cy + 4], "k", lw=0.6)
            ax.text(cx, y0 + 3, f"{p} {hd:g}\nx {x:g}, z {z:g}", ha="center", fontsize=5.5)
        y = y0 - 14
    d = Path(out_dir); d.mkdir(parents=True, exist_ok=True)
    fig.savefig(d / "drill-template.pdf")
    fig.savefig(d / "drill-template.png", dpi=80)


if __name__ == "__main__":
    main(Path(__file__).parent / "out")
