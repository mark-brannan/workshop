"""2D overlay: HALMET board (KiCad), box floor (estimates) and the frame (built DXF).

Usage: python overlay.py out/overlay.png   (after a build, which writes the DXF)
"""
import math
import re
import sys
from pathlib import Path

import ezdxf

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle

GUESS = "#d9730d"
KNOWN = "#1a7f37"
PLATE = "#2f6feb"

HERE = Path(__file__).parent
P = {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*([-\d.]+)\s*;", (HERE / "model.scad").read_text(), re.M)}
SCAD = (HERE / "model.scad").read_text()


def L(name):
    """A list parameter from model.scad, e.g. [1, 2] or [[1, 2], [3, 4]]."""
    import json
    return json.loads(re.search(rf"^{name}\s*=\s*(\[.*?\]);", SCAD, re.M).group(1))

# ---- enclosure floor: estimates, see enclosure/README.md ----
FLOOR_L, FLOOR_W = 151.0, 83.0
BOSS_DX, BOSS_PITCH = P["boss_span"], P["boss_pitch"]
POST_DX, POST_DY = P["post_dx"], P["post_dy"]

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
ox, oy = -BL / 2 + P["board_dx"], -BW / 2 + P["board_dy"]


def b(p):
    return (p[0] + ox, p[1] + oy)


fig, ax = plt.subplots(figsize=(13, 8), dpi=130)

# floor
ax.add_patch(FancyBboxPatch((-FLOOR_L / 2, -FLOOR_W / 2), FLOOR_L, FLOOR_W,
                            boxstyle="round,pad=0,rounding_size=6", fc="#f4f1e8", ec=GUESS, lw=1.5, ls="--"))
ax.add_patch(FancyBboxPatch((-79, -45), 158, 90, boxstyle="round,pad=0,rounding_size=8",
                            fc="none", ec="#555", lw=1.5))
ax.text(-78, 46.5, "box outside 158 x 90 (vendor)", fontsize=9, color="#555")
ax.text(-74, 43.2, "floor ~151 x 83 (estimate)", fontsize=9, color=GUESS)

# frame, from the built laser DXF
for e in ezdxf.readfile(HERE / "out" / "halmet-enclosure-mount_scad.dxf").modelspace():
    if e.dxftype() == "LINE":
        ax.plot([e.dxf.start.x, e.dxf.end.x], [e.dxf.start.y, e.dxf.end.y], color=PLATE, lw=1.6)
    elif e.dxftype() == "LWPOLYLINE":
        pts = [(x, y) for x, y, *_ in e.get_points()]
        ax.add_patch(Polygon(pts, closed=e.closed, fc=PLATE, alpha=0.10, ec="none"))
        ax.add_patch(Polygon(pts, closed=e.closed, fc="none", ec=PLATE, lw=1.4, zorder=5))
ax.text(-62, -40.2, f"frame, {P['plate_t']:g} mm (built from model.scad)",
        fontsize=9, color=PLATE)

# bosses + plate slots over them
for sx in (-1, 1):
    for k in (-1, 0, 1):
        x, y = sx * BOSS_DX / 2, k * BOSS_PITCH
        ax.add_patch(Circle((x, y), 3.2, fc="none", ec=GUESS, lw=1.5))
        ax.add_patch(Circle((x, y), 1.1, fc=GUESS, ec="none"))
for sx in (-1, 1):
    for sy in (-1, 1):
        ax.add_patch(Circle((sx * POST_DX / 2, sy * POST_DY / 2), 2.6, fc="#cfc9b8", ec=GUESS, lw=1.5))
ax.annotate("rest post x4, no hole;\npads rest on these", (POST_DX / 2, POST_DY / 2), (50, 40.5), fontsize=8, color=GUESS,
            arrowprops=dict(arrowstyle="-", color=GUESS))
ax.annotate(f"screw boss x6;\nfork slots allow +/-{P['slot_reach']:g}", (-70, 22), (-77, 31), fontsize=8, color=GUESS,
            arrowprops=dict(arrowstyle="-", color=GUESS))

# board
ax.add_patch(Polygon([b(p) for p in outline], closed=True, fc="#d8f0dc", ec=KNOWN, lw=2, alpha=0.35, zorder=4))
for name, x, y, w, h in [
    ("terminal blocks", 1.0, 33.5, 41.0, 8.0),
    ("terminal blocks", 1.0, 23.2, 37.5, 8.0),
    ("N2K/power block", 1.5, 9.3, 15.5, 8.0),
    ("ESP32", 60.5, 30.0, 25.5, 18.0),
    ("USB", 82.0, 12.5, 6.0, 8.0),
    ("2x10 hdr", 55.0, 48.5, 24.5, 5.2),
    ("2x4", 7.6, 46.0, 10.5, 5.2),
]:
    ax.add_patch(Rectangle(b((x, y)), w, h, fc="none", ec="#666", lw=0.8, ls="--", zorder=4))
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
ax.text(*b((44, 1.5)), "HALMET 89 x 58 (KiCad)", ha="center", fontsize=9, color=KNOWN)


def dim(p0, p1, text, off=0.0, color=KNOWN, va="bottom"):
    ax.annotate("", p0, p1, arrowprops=dict(arrowstyle="<->", color=color, lw=1))
    ax.text((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + off, text, ha="center", va=va, fontsize=8, color=color,
            bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85))


s0, s1 = b(SLOTS[0]), b(SLOTS[1])
dim(s0, s1, "63.3 between slots (44.5 across, 45.0 up)")
dim((-BOSS_DX / 2, 31), (BOSS_DX / 2, 31), f"~{BOSS_DX:g} screw bosses", color=GUESS)
dim((-74, 0), (-74, BOSS_PITCH), f"~{BOSS_PITCH:g}", color=GUESS)
dim((-POST_DX / 2, 40), (POST_DX / 2, 40), f"~{POST_DX:g} posts", color=GUESS)
dim((-49, -POST_DY / 2), (-49, POST_DY / 2), f"~{POST_DY:g}", color=GUESS)
dim((60, -P["frame_w"] / 2), (60, P["frame_w"] / 2), f"{P['frame_w']:g} frame", color=PLATE)
for x in L("tie_bar_xs"):
    ax.text(x, P["tie_bar_y"] - 3.4, "tie", ha="center", fontsize=7, color=PLATE)
ax.text(-65.6, -16, "ties", ha="center", fontsize=7, color=PLATE)

# display tier (separate part): flat plate at the rim on four F/F standoffs, two modules
TIER = "#7a3fd1"
x0, x1, y0 = P["tier_x0"], P["tier_x1"], P["tier_y0"]
xc, yc, yb = P["lid_col_x"] - 1, P["lid_col_y"] - 1, P["plate_y_hi"]
ax.add_patch(Polygon([(x0, y0), (x1, y0), (x1, yc), (xc, yc), (xc, yb), (x0, yb)], closed=True, fc="none", ec=TIER,
                     lw=1.6, ls="--", zorder=6))
for c in L("tier_cols"):
    ax.add_patch(Circle(c, P["tier_boss_d"] / 2, fc="none", ec=TIER, lw=1.2, zorder=6))
    ax.add_patch(Circle(c, P["screw_d"] / 2, fc=TIER, ec="none", zorder=6))
OX, OY, OW, OH = P["oled_x"], P["oled_y"], P["oled_w"], P["oled_h"]
SW, SH = P["seg_w"], P["seg_h"]
SY = OY - OH / 2 - P["seg_gap"] - SH / 2
for (cx, cy, w, h, dx, dy, name) in [(OX, OY, OW, OH, P["oled_hole_dx"], P["oled_hole_dy"], "SSD1306"),
                                     (OX, SY, SW, SH, P["seg_hole_dx"], P["seg_hole_dy"], "TM1637 4-digit")]:
    ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, fc="#e8e0f8", ec=TIER, lw=1.5, alpha=0.6, zorder=6))
    for sx in (-1, 1):
        for sy in (-1, 1):
            ax.add_patch(Circle((cx + sx * dx / 2, cy + sy * dy / 2), P["m25_d"] / 2 + 1, fc=TIER, ec="none", zorder=7))
    ax.text(cx, cy, name, ha="center", va="center", fontsize=7.5, color=TIER, zorder=8,
            bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85))
ax.text(x0 + 1, y0 - 3, f"tier (dashed): top at the rim, {P['rim_z']:g} above the floor; M2.5 self-tap posts", fontsize=7,
        color=TIER, bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85))

# light sensor on the tier, in a cradle under the OLED; photocell at the left end, header pins at the right
SENS = "#b8336a"
lx0, ly, ll, lw = P["ldr_x0"], P["ldr_y"], P["ldr_l"], P["ldr_w"]
ax.add_patch(Rectangle((lx0, ly - lw / 2), ll, lw, fc="#f7dbe6", ec=SENS, lw=1.5, ls=":", alpha=0.8, zorder=7))
ax.add_patch(Circle((lx0 + ll - P["ldr_hole_in"], ly), P["screw_d"] / 2, fc=SENS, ec="none", zorder=8))
ax.add_patch(Circle((lx0 - 1, ly), 2.5, fc="#c0392b", ec=SENS, zorder=8))  # photocell
ax.add_patch(Rectangle((lx0 + ll, ly - 3.2), P["ldr_pin_l"], 6.4, fc="#333", ec="none", zorder=8))  # header pins, straight out
ax.text(lx0 + ll / 2, ly - lw / 2 - 1, "LM393 light sensor in a cradle on the tier, under the OLED",
        ha="center", va="top", fontsize=6.5, color=SENS, zorder=9, bbox=dict(fc="white", ec="none", pad=0.5, alpha=0.85))

# USB plug path, reserved from the board edge to the wall
ax.add_patch(Rectangle((36.5, -15.5), 39, 12, fc="none", ec="#888", lw=1, ls="--"))
ax.text(70, -2.5, "USB plug path", ha="right", fontsize=6.5, color="#666")

# lid-screw columns, one per corner, full height (photo, scaled by the boss span)
for sx in (-1, 1):
    for sy in (-1, 1):
        x0, y0 = sx * P["lid_col_x"], sy * P["lid_col_y"]
        ax.add_patch(Rectangle((min(x0, sx * 75.5), min(y0, sy * 41.5)), 75.5 - P["lid_col_x"], 41.5 - P["lid_col_y"],
                               fc=GUESS, ec=GUESS, alpha=0.3, hatch="//"))
ax.text(70, 30.4, "lid screw\ncolumn", ha="center", va="top", fontsize=6.5, color=GUESS)

# gland wall
for x in (-12.7, 9.5, 31.1, 51.3):  # photo positions; nuts 2-3 mm above the floor
    ax.add_patch(Rectangle((x - 8.3, -41.5), 16.6, 4.0, fc="#333", ec="none", alpha=0.85))
ax.text(20, -44.5, "PG7 nuts on this wall; gland-side frame edge chamfered 2 mm", ha="center", fontsize=8,
        color="#333")

ax.set_xlim(-84, 84)
ax.set_ylim(-50, 50)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("HALMET in the 158x90x60 box, top view, mm.  Green = from Hat Labs' KiCad file.  "
             "Orange = estimate (owner + photo).  Blue = the frame as built.", fontsize=10)
fig.tight_layout()
fig.savefig(sys.argv[1])
