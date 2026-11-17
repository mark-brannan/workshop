"""Drill drawing for the connector wall and the wiring picture. Usage: uv run python drawings.py"""
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


P = params("box.scad", "model.scad", "assembly.scad")


def drill(ax, vent):
    L, H, fl, lid = P["box_l"], P["box_h"], P["box_floor"], P["lid_h"]
    ax.add_patch(Rectangle((0, 0), L, H - lid, fill=False, lw=2))
    ax.add_patch(Rectangle((0, H - lid), L, lid, fill=False, lw=1, ls=":"))
    ax.text(L / 2, H - lid / 2, "lid", ha="center", va="center", color="#888")
    holes = [("SP13", P["sp_x"], P["sp_z"], P["sp_hole"], "#2471a3")]
    if vent:
        holes.append(("M6 vent", P["vent_x"], P["vent_z"], P["vent_hole"], "#1e8449"))
    for name, x, z, d, c in holes:
        cx, cz = L / 2 - x, z + fl          # seen from outside, so x is mirrored
        ax.add_patch(Circle((cx, cz), d / 2, fc=c, alpha=.3, ec=c))
        ax.plot([cx - 2, cx + 2], [cz, cz], c, lw=.8); ax.plot([cx, cx], [cz - 2, cz + 2], c, lw=.8)
        ax.annotate(f"{name}\ndrill {d:g}\n{cx:.1f} from the left edge\n{cz:.1f} up from the base", (cx, cz), (cx, -13), ha="center", fontsize=8,
                    arrowprops=dict(arrowstyle="-", color=c))
    ax.set_xlim(-3, L + 3); ax.set_ylim(-22, H + 2); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(("BME688 box" if vent else "IMU box") + ": the 63 mm wall, from outside, base down", fontsize=10)


def wiring(ax, sensor, addr):
    def box(x, y, w, h, label, c):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5", fc=c, ec="#333"))
        ax.text(x + w / 2, y + h - 3, label, ha="center", va="top", fontsize=9, weight="bold")
    box(0, 0, 26, 44, "Raspberry Pi\n40-pin header", "#d5f5e3")
    box(46, 0, 22, 44, "SP13 plug\nand socket\n4 pins", "#d6eaf8")
    box(88, 0, 30, 44, "LTC4311\n(upper board)\nheader pads", "#fdebd0")
    box(140, 6, 30, 32, f"{sensor}\n(lower board)\n{addr}", "#e8daef")
    rows = [("3V3", "pin 1", "1", "VIN", "#c0392b"), ("SDA", "pin 3", "2", "SDA", "#2471a3"),
            ("SCL", "pin 5", "3", "SCL", "#d4ac0d"), ("GND", "pin 9", "4", "GND", "#222")]
    for i, (sig, pin, n, pad, c) in enumerate(rows):
        y = 26 - i * 7
        ax.plot([26.5, 45.5], [y, y], c, lw=2); ax.plot([68.5, 87.5], [y, y], c, lw=2)
        ax.text(25, y, f"{sig} {pin}", ha="right", va="center", fontsize=8)
        ax.text(57, y, n, ha="center", va="center", fontsize=9)
        ax.text(89.5, y, pad, ha="left", va="center", fontsize=8)
    ax.plot([118.5, 139.5], [16, 16], "#555", lw=5)
    ax.text(129, 19, "50 mm\nQwiic cable", ha="center", fontsize=8)
    ax.text(36, 31, "4-core cable", ha="center", fontsize=8)
    ax.text(78, 31, "4 soldered\nwires, ~40 mm", ha="center", fontsize=8)
    ax.set_xlim(-3, 174); ax.set_ylim(-4, 48); ax.set_aspect("equal"); ax.axis("off")


fig, axs = plt.subplots(1, 2, figsize=(13, 5))
drill(axs[0], True); drill(axs[1], False)
fig.suptitle("Drill from these only after the box is in calipers: wall and floor thickness are photo estimates", fontsize=10)
fig.tight_layout(); fig.savefig(HERE / "out/drill.png", dpi=120)
fig, axs = plt.subplots(2, 1, figsize=(11, 7.5))
wiring(axs[0], "BME688", "0x77"); wiring(axs[1], "ICM-20948", "0x69")
axs[0].set_title("Environment box", fontsize=10); axs[1].set_title("IMU box", fontsize=10)
fig.tight_layout(); fig.savefig(HERE / "out/wiring.png", dpi=120)
