"""Gland layout for the 64 x 57 x 35 black ABS box: 6 probe glands + 1 master.

Outer size is the vendor's. Every other number is read off the vendor photos
and is a GUESS until the box is in calipers (see README).
"""
from dataclasses import dataclass
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.gridspec import GridSpec


@dataclass
class Box:
    L: float = 64.0        # outer, vendor
    W: float = 57.0        # outer, vendor
    H: float = 35.0        # outer, vendor
    lid: float = 8.5       # lid height, photo
    wall: float = 3.0      # photo
    floor: float = 3.0     # photo
    boss: float = 9.5      # corner column, outer corner inward, photo
    groove: float = 4.5    # gasket step under the seam, photo

    @property
    def z_top(self):       # highest usable z on the body wall
        return self.H - self.lid - self.groove

    @property
    def z_mid(self):
        return (self.floor + self.z_top) / 2


# name: (hole dia, nut footprint dia)  -- PG7 15 AF/17 corners; SP13 nut unmeasured; M8 guessed
PARTS = {"PG7": (12.5, 17.0), "SP13": (13.0, 17.0), "M8": (8.3, 11.5)}

# wall -> (length, [(part, x centre from outer corner)])
def layout(b: Box):
    return {
        "long A":  (b.L, [("PG7", b.L/2 - 10), ("PG7", b.L/2 + 10)]),
        "long B":  (b.L, [("PG7", b.L/2 - 10), ("PG7", b.L/2 + 10)]),
        "short A": (b.W, [("PG7", b.W/2 - 8.75), ("PG7", b.W/2 + 8.75)]),
        "short B (master)": (b.W, [("SP13", b.W/2)]),
    }


def check(b, wall_len, items, z):
    """Return list of problems for glands at height z on a wall."""
    bad = []
    lo, hi = b.boss, wall_len - b.boss
    for i, (p, x) in enumerate(items):
        r = PARTS[p][1] / 2
        if x - r < lo or x + r > hi: bad.append((i, "corner column"))
        if z - r < b.floor: bad.append((i, "floor"))
        if z + r > b.z_top: bad.append((i, "gasket step / lid"))
        for j in range(i):
            q, y = items[j]
            if abs(x - y) < r + PARTS[q][1] / 2: bad.append((i, "next gland"))
    return bad


def elevation(ax, b, L, items, z, title, force_bad=()):
    ax.add_patch(Rectangle((0, 0), L, b.floor, color="#bbb"))
    ax.add_patch(Rectangle((0, b.H - b.lid), L, b.lid, color="#ddd"))
    ax.text(L/2, b.H - b.lid/2, "LID", ha="center", va="center", color="#888", fontsize=8)
    ax.add_patch(Rectangle((0, b.z_top), L, b.groove, color="#f3d9a4"))
    ax.text(L/2, b.z_top + b.groove/2, "gasket step", ha="center", va="center", fontsize=7, color="#a77")
    ax.text(L/2, b.floor/2, "floor", ha="center", va="center", fontsize=7)
    for x0 in (0, L - b.boss):
        ax.add_patch(Rectangle((x0, 0), b.boss, b.H - b.lid, color="#bbb", alpha=.8))
    bad = {i for i, _ in check(b, L, items, z)} | set(force_bad)
    for i, (p, x) in enumerate(items):
        hd, nd = PARTS[p]
        c = "#c0392b" if i in bad else "#1e8449"
        ax.add_patch(Circle((x, z), nd/2, fill=False, ls="--", ec=c, lw=1.2))
        ax.add_patch(Circle((x, z), hd/2, fc=c, alpha=.35, ec=c))
        ax.text(x, z, p, ha="center", va="center", fontsize=7)
    ax.set_xlim(-1, L + 1); ax.set_ylim(-1, b.H + 1); ax.set_aspect("equal")
    ax.set_title(title, fontsize=9)
    ax.set_xlabel("mm along wall from the outer corner")


def plan(ax, b):
    ax.add_patch(Rectangle((0, 0), b.L, b.W, fill=False, lw=2))
    ax.add_patch(Rectangle((b.wall, b.wall), b.L - 2*b.wall, b.W - 2*b.wall, fill=False, lw=1))
    for x0 in (0, b.L - b.boss):
        for y0 in (0, b.W - b.boss):
            ax.add_patch(Rectangle((x0, y0), b.boss, b.boss, color="#bbb"))
    lay = layout(b)
    g = lambda p, x, y, ax_: None
    nut_depth = 5.0
    for x in [b.L/2 - 10, b.L/2 + 10]:
        for y, s in ((0, 1), (b.W, -1)):
            ax.add_patch(Rectangle((x - 8.5, y - (0 if s > 0 else nut_depth) + (b.wall if s > 0 else -b.wall) * 0 + (b.wall if s > 0 else -b.wall + 0)),
                                   17, nut_depth, fill=False, ec="#1e8449", ls="--"))
            ax.plot([x - 6.25, x + 6.25], [y, y], color="#1e8449", lw=4)
    for y in [b.W/2 - 8.75, b.W/2 + 8.75]:
        ax.add_patch(Rectangle((b.wall, y - 8.5), nut_depth, 17, fill=False, ec="#1e8449", ls="--"))
        ax.plot([0, 0], [y - 6.25, y + 6.25], color="#1e8449", lw=4)
    ax.add_patch(Rectangle((b.L - b.wall - nut_depth, b.W/2 - 8.5), nut_depth, 17, fill=False, ec="#2471a3", ls="--"))
    ax.plot([b.L, b.L], [b.W/2 - 6.5, b.W/2 + 6.5], color="#2471a3", lw=4)
    ax.text(b.L/2, b.W/2, "inside: 58 x 51\n(boards fit:\npinwheel 24, two-row 42 x 19)", ha="center", va="center", fontsize=8)
    ax.text(0, b.W/2 + 22, "short A\n2 x PG7", ha="right", va="center", fontsize=8, color="#1e8449")
    ax.text(b.L + 1, b.W/2 + 12, "short B\nSP13\nmaster", ha="left", va="center", fontsize=8, color="#2471a3")
    ax.text(b.L/2, b.W + 3, "long A: 2 x PG7", ha="center", fontsize=8, color="#1e8449")
    ax.text(b.L/2, -5, "long B: 2 x PG7", ha="center", fontsize=8, color="#1e8449")
    ax.set_xlim(-14, b.L + 14); ax.set_ylim(-8, b.W + 7); ax.set_aspect("equal")
    ax.set_title("Plan, looking down into the body (lid off)", fontsize=9)


def main(path):
    b = Box()
    lay = layout(b)
    z = b.z_mid
    fig = plt.figure(figsize=(16, 11))
    gs = GridSpec(2, 4, figure=fig, height_ratios=[1.15, 1])
    plan(fig.add_subplot(gs[0, 0:2]), b)
    fail = [("PG7", b.L/2 - 17.5), ("PG7", b.L/2), ("PG7", b.L/2 + 17.5)]
    ax = fig.add_subplot(gs[0, 2:4])
    elevation(ax, b, b.L, fail, z, "FAILS: three PG7 on a long wall (outer two hit the corner columns)")
    # low and high PG7 examples on the same panel
    for zz, lab in ((7.0, "z=7: nut on the floor"), (20.5, "z=20.5: nut in the gasket step")):
        pass
    ax.add_patch(Circle((b.L/2 - 17.5, 7.0), 8.5, fill=False, ec="#c0392b", ls=":"))
    ax.add_patch(Circle((b.L/2 + 17.5, 20.5), 8.5, fill=False, ec="#c0392b", ls=":"))
    ax.text(b.L/2, 3.0 + 0.2, "dotted: same gland at z=7 (floor) or z=20.5 (gasket step)", ha="center", fontsize=7, color="#c0392b", va="bottom")
    elevation(fig.add_subplot(gs[1, 0]), b, b.L, lay["long A"][1], z, "Long wall, x2 (A and B alike): 2 x PG7")
    elevation(fig.add_subplot(gs[1, 1]), b, b.W, lay["short A"][1], z, "Short wall A: 2 x PG7 (tight: 1.75 mm to each column)")
    elevation(fig.add_subplot(gs[1, 2]), b, b.W, lay["short B (master)"][1], z, "Short wall B: SP13 master")
    m8 = [("M8", b.L/2 - 14), ("M8", b.L/2), ("M8", b.L/2 + 14)]
    elevation(fig.add_subplot(gs[1, 3]), b, b.L, m8, z, "Option: M8 minis, 3 per long wall")
    fig.suptitle(f"One-wire enclosure 64 x 57 x 35: 7 holes at z = {z:.1f} mm from the base. "
                 "Green fits, red fails. Dashed = nut footprint, solid = hole. Wall details estimated from photos.", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    return b, lay, z


if __name__ == "__main__":
    main("projects/one-wire-enclosure/out/holes.png")
