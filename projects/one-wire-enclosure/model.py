"""Gland layout for the 63 x 58 x 35 ABS box (black or clear lid): 6 probe glands + 1 master.

Outer size and the 39 mm clear wall between corner columns are the vendor's.
Every other number is read off vendor photos and is a GUESS until the box is
in calipers (see README). Shares its box numbers with projects/small-box-sensors/box.scad.
"""
from dataclasses import dataclass
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.gridspec import GridSpec


@dataclass
class Box:
    L: float = 63.0          # outer, vendor
    W: float = 58.0          # outer, vendor
    H: float = 35.0          # outer, vendor
    clear: float = 39.0      # straight wall between corner columns, both walls, vendor
    lid: float = 8.5         # lid height, photo
    wall: float = 2.5        # photo (vendor 53 inside across W)
    floor: float = 3.0       # photo
    groove: float = 4.5      # gasket band under the seam, photo
    boss_pitch: float = 41.0 # floor screw bosses, centred on the short walls, photo
    boss_d: float = 6.0
    boss_h: float = 4.0      # above the inside floor

    @property
    def z_top(self):         # highest z (from outer base) a nut may reach on the plain wall
        return self.H - self.lid - self.groove

    def col(self, wall_len):  # corner column width along a wall, from the outer corner
        return (wall_len - self.clear) / 2

    @property
    def boss_gap(self):      # inside wall face to boss edge
        return (self.L - 2 * self.wall) / 2 - self.boss_pitch / 2 - self.boss_d / 2


# name: (hole dia, nut across corners, nut thickness, inside body dia, inside body depth past the wall)
# PG7: nut 15 AF / 17 AC, ~5 thick, thread ~8 long. SP13: rear body ~13 dia x ~15 deep, nut unmeasured.
# M8: nut 11.5-13 across corners (13 used), clamps 2-5 cable; probe cable 3.5 (owner, caliper)
PARTS = {"M8": (8.3, 13.0, 5.0, 8.3, 5.5), "PG7": (12.5, 17.0, 5.0, 12.5, 5.5), "SP13": (13.0, 17.0, 3.0, 13.0, 15.0)}


def layout(b: Box):
    """wall -> (length, has_boss, [(part, x from the outer corner, z from the outer base)])"""
    L, W = b.L, b.W
    return {
        "long A": (L, False, [("M8", L/2 - 10, 12.5), ("M8", L/2 + 10, 12.5)]),
        "long B": (L, False, [("M8", L/2 - 10, 12.5), ("M8", L/2 + 10, 12.5)]),
        "short A": (W, True, [("M8", W/2 - 10, 12.5), ("M8", W/2 + 10, 12.5)]),
        "short B (master)": (W, True, [("SP13", W/2 + 10, 12.5)]),
    }


def _circle_rect_gap(cx, cy, r, x0, x1, y0, y1):
    dx = max(x0 - cx, 0, cx - x1); dy = max(y0 - cy, 0, cy - y1)
    return math.hypot(dx, dy) - r


def margins(b, wall_len, has_boss, items):
    """Smallest clearance (mm) to each obstacle; negative = collision."""
    col = b.col(wall_len)
    m = {"column": 99, "floor": 99, "gasket": 99, "next": 99, "boss": 99}
    bx0, bx1 = wall_len/2 - b.boss_d/2, wall_len/2 + b.boss_d/2
    btop = b.floor + b.boss_h
    for i, (p, x, z) in enumerate(items):
        _, nut, nut_t, body_d, body_l = PARTS[p]
        r = nut / 2
        m["column"] = min(m["column"], x - r - col, wall_len - col - x - r)
        m["floor"] = min(m["floor"], z - r - b.floor)
        m["gasket"] = min(m["gasket"], b.z_top - z - r)
        for q, y, zz in items[:i]:
            m["next"] = min(m["next"], math.hypot(x - y, z - zz) - r - PARTS[q][1] / 2)
        if has_boss:
            # nut and inside body only reach the boss if they stand deeper than the boss gap
            for rad, depth in ((r, nut_t), (body_d / 2, body_l)):
                g = _circle_rect_gap(x, z, rad, bx0, bx1, 0, btop)
                if depth > b.boss_gap:
                    m["boss"] = min(m["boss"], g)
    return m


def ok(m):
    return min(m.values()) >= 0


def elevation(ax, b, L, has_boss, items, title):
    col = b.col(L)
    ax.add_patch(Rectangle((0, 0), L, b.floor, color="#bbb"))
    ax.add_patch(Rectangle((0, b.H - b.lid), L, b.lid, color="#ddd"))
    ax.text(L/2, b.H - b.lid/2, "LID", ha="center", va="center", color="#888", fontsize=8)
    ax.add_patch(Rectangle((0, b.z_top), L, b.groove, color="#f3d9a4"))
    ax.text(L/2, b.z_top + b.groove/2, "gasket band", ha="center", va="center", fontsize=7, color="#a77")
    for x0 in (0, L - col):
        ax.add_patch(Rectangle((x0, 0), col, b.H - b.lid, color="#bbb", alpha=.8))
    if has_boss:
        ax.add_patch(Rectangle((L/2 - b.boss_d/2, b.floor), b.boss_d, b.boss_h, color="#7d3c98", alpha=.6))
        ax.text(L/2, b.floor + b.boss_h + .4, f"floor boss, {b.boss_gap:.1f} in", ha="center", fontsize=6, color="#7d3c98")
    m = margins(b, L, has_boss, items)
    c = "#1e8449" if ok(m) else "#c0392b"
    for p, x, z in items:
        hd, nd, *_ = PARTS[p]
        ax.add_patch(Circle((x, z), nd/2, fill=False, ls="--", ec=c, lw=1.2))
        ax.add_patch(Circle((x, z), hd/2, fc=c, alpha=.35, ec=c))
        ax.text(x, z, f"{p}\nz{z:g}", ha="center", va="center", fontsize=6)
    worst = min(m, key=m.get)
    ax.set_xlim(-1, L + 1); ax.set_ylim(-1, b.H + 1); ax.set_aspect("equal")
    ax.set_title(f"{title}\nworst: {worst} {m[worst]:+.1f} mm", fontsize=8, color=c)
    ax.set_xlabel("mm along wall from the outer corner", fontsize=7)
    return m


def main(path):
    b = Box()
    lay = layout(b)
    fig = plt.figure(figsize=(16, 8.5))
    gs = GridSpec(2, 4, figure=fig)
    report = {}
    for k, (name, (L, boss, items)) in enumerate(lay.items()):
        if name == "long B":
            continue
        t = {"long A": "Long walls A and B: 2 x M8 at +/-10",
             "short A": "Short wall A: 2 x M8 at +/-10",
             "short B (master)": "Short wall B: SP13 10 off centre"}[name]
        report[name] = elevation(fig.add_subplot(gs[0, len(report)]), b, L, boss, items, t)
    report["long B"] = margins(b, *lay["long B"])
    # the earlier layout, re-checked against this box
    W = b.W
    old = [
        (b.L, False, [("PG7", b.L/2 - 10, 12.5), ("PG7", b.L/2 + 10, 12.5)], "PG7 instead, long wall: 1 mm to the columns"),
        (W, True, [("PG7", W/2 - 9.5, 13.0), ("PG7", W/2 + 9.5, 13.0)], "PG7 instead, short A: 0.5 mm to the gasket band"),
        (W, True, [("SP13", W/2, 12.5)], "Fails: a centred SP13 body hits the boss"),
    ]
    for i, (L, boss, items, t) in enumerate(old):
        elevation(fig.add_subplot(gs[1, i]), b, L, boss, items, t)
    ax = fig.add_subplot(gs[0:2, 3])
    ax.axis("off")
    rows = [[n] + [f"{m[k]:+.1f}" if m[k] < 90 else "-" for k in ("column", "floor", "gasket", "next", "boss")] for n, m in report.items()]
    tb = ax.table(cellText=rows, colLabels=["wall", "column", "floor", "gasket", "next nut", "boss"], loc="center", cellLoc="center")
    tb.auto_set_font_size(False); tb.set_fontsize(8); tb.scale(1, 1.6)
    ax.set_title("Clearance, mm (nut corners; photo guesses)", fontsize=9)
    fig.suptitle("One-wire enclosure 63 x 58 x 35, 6 x M8 + SP13 (39 mm clear wall, floor bosses on the short walls). "
                 "Green fits, red fails. Dashed = nut corners, solid = hole. z from the outer base.", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    return b, lay, report


if __name__ == "__main__":
    _, _, rep = main("projects/one-wire-enclosure/out/holes.png")
    for n, m in rep.items():
        print(n, {k: round(v, 2) for k, v in m.items() if v < 90})
