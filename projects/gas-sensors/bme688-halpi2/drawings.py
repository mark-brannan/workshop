"""Drill drawing (connector wall and lid) and the wiring picture. Usage: uv run python drawings.py"""
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

HERE = Path(__file__).parent


def params(*files):
    out = {}
    for f in files:
        out |= {k: float(v) for k, v in re.findall(r"^(\w+)\s*=\s*(-?[\d.]+)\s*;", (HERE / f).read_text(), re.M)}
    return out


P = params("../../small-box-sensors/box.scad", "model.scad", "assembly.scad")
L, W, H = P["box_l"], P["box_w"], P["box_h"]


def hole(ax, cx, cy, d, c, text, at):
    ax.add_patch(Circle((cx, cy), d / 2, fc=c, alpha=.3, ec=c))
    ax.plot([cx - 2, cx + 2], [cy, cy], c, lw=.8); ax.plot([cx, cx], [cy - 2, cy + 2], c, lw=.8)
    ax.annotate(text, (cx, cy), at, ha="center", va="top", fontsize=8, arrowprops=dict(arrowstyle="-", color=c))


def wall(ax):
    lid = P["lid_h"]
    ax.add_patch(Rectangle((0, 0), L, H - lid, fill=False, lw=2))
    ax.add_patch(Rectangle((0, H - lid), L, lid, fill=False, lw=1, ls=":"))
    ax.text(L / 2, H - lid / 2, "lid", ha="center", va="center", color="#888")
    cx, cz = L / 2 - P["sp_x"], P["sp_z"] + P["box_floor"]      # seen from outside, so x is mirrored
    hole(ax, cx, cz, P["sp_hole"], "#2471a3", f"SP13\ndrill {P['sp_hole']:g}\n{cx:.1f} from either end\n{cz:.1f} up from the base", (cx, -5))
    ax.set_xlim(-3, L + 3); ax.set_ylim(-22, H + 2); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("A 63 mm wall, from outside, base down", fontsize=10)


def lid(ax):
    ax.add_patch(FancyBboxPatch((0, 0), L, W, boxstyle="round,pad=0,rounding_size=4", fill=False, lw=2))
    ax.plot([0, L], [W, W], "#2471a3", lw=5, solid_capstyle="butt")
    ax.text(L / 2, W + 2, "the wall with the SP13", ha="center", fontsize=8, color="#2471a3")
    cx, cy = L / 2 + P["chip_dx"], W / 2 + P["plate_y"] + P["chip_dy"]
    hole(ax, cx, cy, P["vent_hole"], "#1e8449",
         f"M6 vent\ndrill {P['vent_hole']:g}\n{cx:.1f} from either short edge\n{W - cy:.1f} from the SP13 edge", (cx, cy - 8))
    ax.set_xlim(-3, L + 3); ax.set_ylim(-3, W + 6); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("The lid, from above", fontsize=10)


def wiring(ax):
    def box(x, y, w, h, label, c):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5", fc=c, ec="#333"))
        ax.text(x + w / 2, y + h - 2.5, label, ha="center", va="top", fontsize=9, weight="bold")
    ax.add_patch(Rectangle((-4, -8), 50, 62, fill=False, ls="--", ec="#888")); ax.text(21, 55.5, "inside the HALPI2", ha="center", fontsize=9, color="#666")
    ax.add_patch(Rectangle((100, -8), 96, 62, fill=False, ls="--", ec="#888")); ax.text(148, 55.5, "inside the sensor box", ha="center", fontsize=9, color="#666")
    box(0, 0, 26, 48, "40-pin header\n(I2C bus 1)", "#d5f5e3")
    box(40, 8, 12, 30, "PG7\ngland", "#eeeeee")
    box(88, 0, 26, 48, "SP13 plug\nand socket\n4 pins", "#d6eaf8")
    box(140, 14, 14, 24, "Qwiic\nplug", "#f5b7b1")
    box(160, 6, 32, 36, "BME688\n0x77", "#e8daef")
    rows = [("3V3", "pin 1", "1", "red", "#c0392b"), ("SDA", "pin 3", "2", "blue", "#2471a3"),
            ("SCL", "pin 5", "3", "yellow", "#d4ac0d"), ("GND", "pin 9", "4", "black", "#222")]
    for i, (sig, pin, n, colour, c) in enumerate(rows):
        y = 27 - i * 6
        ax.plot([26.5, 87.5], [y, y], c, lw=2, zorder=0); ax.plot([114.5, 139.5], [y, y], c, lw=2)
        ax.plot([27.5], [y], "s", color=c, ms=5)
        ax.text(25, y, f"{sig} {pin}", ha="right", va="center", fontsize=8)
        ax.text(101, y, n, ha="center", va="center", fontsize=9)
        ax.text(127, y + 1, colour, ha="center", va="bottom", fontsize=7, color=c)
    ax.text(14, -5, "four single Dupont\nsockets on the pins", ha="center", fontsize=8)
    ax.text(70, 32, "4-core cable, under 300 mm\nplug soldered at the box end", ha="center", fontsize=8)
    ax.text(127, 0, "Qwiic pigtail, cut and\nsoldered to the SP13 cups", ha="center", fontsize=8)
    ax.set_xlim(-6, 198); ax.set_ylim(-10, 60); ax.set_aspect("equal"); ax.axis("off")


fig, axs = plt.subplots(1, 2, figsize=(11, 5))
wall(axs[0]); lid(axs[1])
fig.suptitle("Drill from these only after the box is in calipers: wall, floor and lid thickness are photo estimates", fontsize=10)
fig.tight_layout(); fig.savefig(HERE / "out/drill.png", dpi=120)
fig, ax = plt.subplots(figsize=(12, 4.6))
wiring(ax)
fig.tight_layout(); fig.savefig(HERE / "out/wiring.png", dpi=120)
