"""2D overlay: HALMET board (from KiCad) on the 158x90x60 box floor (photo estimate)."""
import math
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle

GUESS = "#d9730d"
KNOWN = "#1a7f37"
PLATE = "#2f6feb"

# ---- enclosure floor: ALL photo estimates, +/-5 mm ----
FLOOR_L, FLOOR_W = 150.0, 82.0
BOSS_DX, BOSS_PITCH = 140.0, 22.0  # six holed bosses, three per short end
POST_DX, POST_DY = 79.0, 68.5  # four solid posts

# ---- board: from HALMET.kicad_pcb ----
BL, BW = 89.0, 58.0
SLOTS = [(22.75, 51.5), (67.25, 6.5)]


def arc(cx, cy, r, a0, a1, n=16):
    return [
        (cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
         cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
        for i in range(n + 1)
    ]


outline = (
    [(8.5, 0), (80.5, 0)]
    + arc(89, 0, 8.5, 180, 90)
    + [(89, 24.7), (83, 24.7), (83, 51.98), (81.15, 54.74), (80.5, 58), (8.5, 58)]
    + arc(0, 58, 8.5, 0, -90)
    + [(0, 8.5)]
    + arc(0, 0, 8.5, 90, 0)
)
ox, oy = -BL / 2, -BW / 2  # board centred on the floor


def b(p):
    return (p[0] + ox, p[1] + oy)


fig, ax = plt.subplots(figsize=(13, 8), dpi=130)

# floor
ax.add_patch(FancyBboxPatch((-FLOOR_L / 2, -FLOOR_W / 2), FLOOR_L, FLOOR_W,
                            boxstyle="round,pad=0,rounding_size=6", fc="#f4f1e8", ec=GUESS, lw=1.5, ls="--"))
ax.add_patch(FancyBboxPatch((-79, -45), 158, 90, boxstyle="round,pad=0,rounding_size=8",
                            fc="none", ec="#555", lw=1.5))
ax.text(-78, 46.5, "box outside 158 x 90 (vendor)", fontsize=9, color="#555")
ax.text(-74, -39.5, "floor ~150 x 82 (guess)", fontsize=9, color=GUESS)

# plate
PL_L, PL_W = 152.0 - 6, 56.0
plate = FancyBboxPatch((-PL_L / 2, -PL_W / 2), PL_L, PL_W, boxstyle="round,pad=0,rounding_size=4",
                       fc=PLATE, ec=PLATE, alpha=0.13, lw=0)
ax.add_patch(plate)
ax.add_patch(FancyBboxPatch((-PL_L / 2, -PL_W / 2), PL_L, PL_W, boxstyle="round,pad=0,rounding_size=4",
                            fc="none", ec=PLATE, lw=2))
ax.text(-PL_L / 2 + 12, -PL_W / 2 + 1.5, "adapter plate, 3 mm (proposed)", fontsize=9, color=PLATE)

# bosses + plate slots over them
for sx in (-1, 1):
    for k in (-1, 0, 1):
        x, y = sx * BOSS_DX / 2, k * BOSS_PITCH
        ax.add_patch(FancyBboxPatch((x - 4.5, y - 1.7), 9, 3.4, boxstyle="round,pad=0,rounding_size=1.7",
                                    fc="white", ec=PLATE, lw=1.5))
        ax.add_patch(Circle((x, y), 3.2, fc="none", ec=GUESS, lw=1.5))
        ax.add_patch(Circle((x, y), 1.1, fc=GUESS, ec="none"))
for sx in (-1, 1):
    for sy in (-1, 1):
        ax.add_patch(Circle((sx * POST_DX / 2, sy * POST_DY / 2), 2.6, fc="#cfc9b8", ec=GUESS, lw=1.5))
ax.annotate("solid post x4\n(no hole)", (POST_DX / 2, POST_DY / 2), (52, 39.2), fontsize=8, color=GUESS,
            arrowprops=dict(arrowstyle="-", color=GUESS))
ax.annotate("holed boss x6;\nplate slots allow +/-3", (-70, 22), (-77, 31), fontsize=8, color=GUESS,
            arrowprops=dict(arrowstyle="-", color=GUESS))

# board
ax.add_patch(Polygon([b(p) for p in outline], closed=True, fc="#d8f0dc", ec=KNOWN, lw=2, alpha=0.9))
for name, x, y, w, h in [
    ("terminal blocks", 1.0, 33.5, 41.0, 8.0),
    ("terminal blocks", 1.0, 23.2, 37.5, 8.0),
    ("N2K/power block", 1.5, 9.3, 15.5, 8.0),
    ("ESP32", 60.5, 30.0, 25.5, 18.0),
    ("USB", 82.0, 12.5, 6.0, 8.0),
    ("2x10 hdr", 55.0, 48.5, 24.5, 5.2),
    ("2x4", 7.6, 46.0, 10.5, 5.2),
]:
    ax.add_patch(Rectangle(b((x, y)), w, h, fc="white", ec="#666", lw=0.8))
    ax.text(*b((x + w / 2, y + h / 2)), name, ha="center", va="center", fontsize=7, color="#444")
for s in SLOTS:
    c = b(s)
    ax.add_patch(Circle(c, 4.0, fc="none", ec=PLATE, lw=2))  # standoff under board
    ax.add_patch(Circle(c, 1.6, fc="black", ec="none"))
ax.annotate("M3 slot + standoff\nwith heat-set insert", b(SLOTS[0]), (-40, 36), fontsize=8, color=PLATE,
            arrowprops=dict(arrowstyle="-", color=PLATE))
ax.annotate("M3 slot + standoff", b(SLOTS[1]), (20, -37), fontsize=8, color=PLATE,
            arrowprops=dict(arrowstyle="-", color=PLATE))
# rest pads on the other diagonal
for p in [(80.0, 53.0 - 4.5), (6.0, 4.0 + 5.5)]:
    ax.add_patch(Circle(b(p), 2.5, fc="none", ec=PLATE, lw=1.5, ls=":"))
ax.text(*b((44, 3.5)), "HALMET 89 x 58 (KiCad)", ha="center", fontsize=9, color=KNOWN)


def dim(p0, p1, text, off=0.0, color=KNOWN, va="bottom"):
    ax.annotate("", p0, p1, arrowprops=dict(arrowstyle="<->", color=color, lw=1))
    ax.text((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + off, text, ha="center", va=va, fontsize=8, color=color,
            bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85))


s0, s1 = b(SLOTS[0]), b(SLOTS[1])
dim(s0, s1, "63.3 between slots (44.5 across, 45.0 up)")
dim((-70, -30.5), (70, -30.5), "~140 (guess)", color=GUESS, va="top", off=-0.6)
dim((-66, 0), (-66, 22), "~22", color=GUESS)
dim((-39.5, 37.5), (39.5, 37.5), "~79 (guess)", color=GUESS)

# gland wall
for x in (-3, 16, 37, 55):
    ax.add_patch(Rectangle((x - 6, -41), 12, 5, fc="#333", ec="none"))
ax.text(26, -43.8, "PG7 nuts / 13 mm holes on this wall, above the plate", ha="center", fontsize=8, color="#333")

ax.set_xlim(-84, 84)
ax.set_ylim(-50, 50)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("HALMET in the 158x90x60 box, top view, mm.  Green = from Hat Labs' KiCad file.  "
             "Orange = estimated from a product photo, +/-5 mm.  Blue = proposed part.", fontsize=10)
fig.tight_layout()
fig.savefig(sys.argv[1])
