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
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle

sys.path.insert(0, str(Path(__file__).parent))
from model import Box, PARTS, layout  # noqa: E402

MM = 1 / 25.4
PAGE_W, PAGE_H = 210.0, 297.0   # A4, mm
STRIP_H = 30.0                   # below the lid seam (26.5) plus a little


INSERT = (5.0, 5.0, 4.5)   # brass lid-screw insert: x, y from the outer corner, OD; photo estimate


def base_face(ax, b, x0, y0):
    """Outer face of the floor, 1:1, looking at it from outside; dotted = where the interior stops being flat."""
    L, W, w = b.L, b.W, b.wall
    cx, cy = b.col(L), b.col(W)           # corner column footprint: 12 along the 63 side, 9.5 along the 58 side
    ax.add_patch(Rectangle((x0, y0), L, W, fill=False, ec="k", lw=0.8))
    ax.text(x0, y0 + W + 2, "Base face (outside view), 63 x 58. Red dotted = start of the interior corner columns; "
            "blue = floor bosses", fontsize=6)
    # the cavity: inner rectangle minus the four column blocks
    for sx in (0, 1):
        for sy in (0, 1):
            px = x0 + (L - cx if sx else 0); py = y0 + (W - cy if sy else 0)
            ax.add_patch(Rectangle((px, py), cx, cy, fill=True, fc="#f3e0e0", ec="#c0392b", ls=":", lw=0.9))
            ix = x0 + (L - INSERT[0] if sx else INSERT[0]); iy = y0 + (W - INSERT[1] if sy else INSERT[1])
            ax.add_patch(Circle((ix, iy), INSERT[2] / 2, fc="#d4a017", alpha=.6, ec="#a77"))
    ax.add_patch(Rectangle((x0 + w, y0 + w), L - 2 * w, W - 2 * w, fill=False, ec="#c0392b", ls=":", lw=0.9))
    for dx in (-b.boss_pitch / 2, b.boss_pitch / 2):
        ax.add_patch(Circle((x0 + L / 2 + dx, y0 + W / 2), b.boss_d / 2, fill=False, ec="#2471a3", lw=0.8))
    ax.text(x0 + L / 2, y0 + W / 2 - 8, "floor: flat inside the dotted line, 3 thick", ha="center", fontsize=5.5, color="#555")
    ax.text(x0 + cx / 2, y0 + cy + 1.5, "column %gx%g" % (cx, cy), fontsize=4.5, color="#c0392b")


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
    fig2 = plt.figure(figsize=(PAGE_W * MM, PAGE_H * MM))
    ax2 = fig2.add_axes([0, 0, 1, 1])
    ax2.set_xlim(0, PAGE_W); ax2.set_ylim(0, PAGE_H); ax2.axis("off")
    ax2.text(10, PAGE_H - 12, "Base face, 1:1", fontsize=12, weight="bold")
    base_face(ax2, b, 10, PAGE_H - 100)
    d = Path(out_dir); d.mkdir(parents=True, exist_ok=True)
    with PdfPages(d / "drill-template.pdf") as pdf:
        pdf.savefig(fig); pdf.savefig(fig2)
    fig.savefig(d / "drill-template.png", dpi=80)
    fig2.savefig(d / "drill-base-face.png", dpi=110)


if __name__ == "__main__":
    main(Path(__file__).parent / "out")
