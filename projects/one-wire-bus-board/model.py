"""1-wire bus board: seven 3-pin terminals in a row, [G D V] each, tied into three nets.

Two copper layers, no vias, no jumpers. Plated pads put every pin on both layers:
  G  top    trunk above the pin row, stub up from each G pad
  V  top    trunk below the pin row, stub down from each V pad
  D  bottom trunk between the pin row and the G trunk, stub up from each D pad
D runs on the other layer from the G stubs it passes under.
Writes out/one-wire-bus.kicad_pcb (KiCad 7 text format) and out/one-wire-bus.png.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PITCH = 2.54


@dataclass
class Params:
    terminals: int = 7          # six field terminals + the master (the last one)
    pins: int = 3               # G, D, V
    pad_d: float = 1.8
    drill: float = 1.0
    track_w: float = 0.5
    trunk_off: float = 5.08     # G trunk above / V trunk below the pin row
    d_trunk_off: float = 2.54   # D trunk (bottom layer) above the pin row
    margin_x: float = 5.0
    margin_y: float = 5.0
    mount_d: float = 3.2        # M3 clearance
    mount_inset: float = 3.0


NETS = {"G": 1, "D": 2, "V": 3}
NET_NAMES = {1: "GND", 2: "DATA", 3: "VCC"}


def build(p: Params = Params()) -> dict:
    """Pads and tracks in mm, KiCad axes (y down). Pin row at y = 0."""
    pads, tracks = [], []
    for t in range(p.terminals):
        for i, name in enumerate("GDV"):
            x = (t * p.pins + i) * PITCH
            pads.append({"ref": f"J{t + 1}", "num": i + 1, "net": NETS[name], "x": x, "y": 0.0})
    by = {n: [q for q in pads if q["net"] == NETS[n]] for n in "GDV"}
    w = p.track_w

    def seg(a, b, layer, net):
        tracks.append({"x1": a[0], "y1": a[1], "x2": b[0], "y2": b[1], "layer": layer, "net": net, "w": w})

    yg, yd, yv = -p.trunk_off, -p.d_trunk_off, p.trunk_off
    for n, y, layer in (("G", yg, "F.Cu"), ("D", yd, "B.Cu"), ("V", yv, "F.Cu")):
        pp = by[n]
        for q in pp:
            seg((q["x"], 0.0), (q["x"], y), layer, NETS[n])
        for a, b in zip(pp, pp[1:]):
            seg((a["x"], y), (b["x"], y), layer, NETS[n])
    x0, x1 = -p.margin_x, (p.terminals * p.pins - 1) * PITCH + p.margin_x
    y0, y1 = -(p.trunk_off + p.margin_y), p.trunk_off + p.margin_y
    holes = [(x0 + p.mount_inset, y0 + p.mount_inset), (x1 - p.mount_inset, y0 + p.mount_inset),
             (x0 + p.mount_inset, y1 - p.mount_inset), (x1 - p.mount_inset, y1 - p.mount_inset)]
    return {"pads": pads, "tracks": tracks, "outline": (x0, y0, x1, y1), "holes": holes, "p": p}


def to_kicad(b: dict) -> str:
    p = b["p"]
    o = ['(kicad_pcb (version 20221018) (generator "workshop")',
         ' (general (thickness 1.6))', ' (paper "A4")',
         ' (layers (0 "F.Cu" signal) (31 "B.Cu" signal) (36 "B.SilkS" user "B.Silkscreen") '
         '(37 "F.SilkS" user "F.Silkscreen") (38 "B.Mask" user) (39 "F.Mask" user) (44 "Edge.Cuts" user))',
         ' (setup (pad_to_mask_clearance 0))', ' (net 0 "")']
    o += [f' (net {n} "{NET_NAMES[n]}")' for n in (1, 2, 3)]
    ox, oy = 100.0, 100.0   # place on the sheet
    for t in range(p.terminals):
        ref = f"J{t + 1}"
        x = ox + t * p.pins * PITCH
        o.append(f' (footprint "workshop:Terminal_1x3_P2.54mm" (layer "F.Cu") (at {x:.3f} {oy:.3f})')
        o.append(f'  (fp_text reference "{ref}" (at 2.54 -2.8) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))')
        o.append('  (fp_text value "terminal G D V" (at 2.54 2.8) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))')
        o.append(f'  (fp_rect (start -1.4 -1.4) (end {2 * PITCH + 1.4:.2f} 1.4) (layer "F.SilkS") (width 0.12) (fill none))')
        for i, name in enumerate("GDV"):
            shape = "rect" if i == 0 else "circle"
            o.append(f'  (pad "{i + 1}" thru_hole {shape} (at {i * PITCH:.3f} 0) (size {p.pad_d} {p.pad_d}) '
                     f'(drill {p.drill}) (layers "*.Cu" "*.Mask") (net {NETS[name]} "{NET_NAMES[NETS[name]]}"))')
        o.append(' )')
    for k, (hx, hy) in enumerate(b["holes"]):
        o.append(f' (footprint "workshop:MountingHole_M3" (layer "F.Cu") (at {ox + hx:.3f} {oy + hy:.3f})')
        o.append(f'  (fp_text reference "H{k + 1}" (at 0 0) (layer "F.SilkS") hide (effects (font (size 1 1) (thickness 0.15))))')
        o.append(f'  (pad "" np_thru_hole circle (at 0 0) (size {p.mount_d} {p.mount_d}) (drill {p.mount_d}) (layers "*.Cu" "*.Mask")))')
    for s in b["tracks"]:
        o.append(f' (segment (start {ox + s["x1"]:.3f} {oy + s["y1"]:.3f}) (end {ox + s["x2"]:.3f} {oy + s["y2"]:.3f}) '
                 f'(width {s["w"]}) (layer "{s["layer"]}") (net {s["net"]}))')
    x0, y0, x1, y1 = b["outline"]
    for (a, c, d, e) in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
        o.append(f' (gr_line (start {ox + a:.3f} {oy + c:.3f}) (end {ox + d:.3f} {oy + e:.3f}) (layer "Edge.Cuts") (width 0.1))')
    o.append(')')
    return "\n".join(o) + "\n"


def render(b: dict, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle
    col = {1: "#333333", 2: "#1a73e8", 3: "#d93025"}
    fig, axs = plt.subplots(2, 1, figsize=(12, 6.4))
    x0, y0, x1, y1 = b["outline"]
    for ax, layer, title in ((axs[0], "F.Cu", "Top copper: G above the pins, V below"),
                             (axs[1], "B.Cu", "Bottom copper: D, one trace under the G stubs")):
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#2f6b3a", alpha=0.18, ec="k"))
        for s in b["tracks"]:
            if s["layer"] == layer:
                ax.plot([s["x1"], s["x2"]], [s["y1"], s["y2"]], color=col[s["net"]], lw=3.2, solid_capstyle="round")
        for q in b["pads"]:
            ax.add_patch(Circle((q["x"], q["y"]), b["p"].pad_d / 2, fc="#d9b44a", ec=col[q["net"]], lw=1.5))
            ax.text(q["x"], q["y"], "GDV"[q["num"] - 1], ha="center", va="center", fontsize=6, color=col[q["net"]])
        for hx, hy in b["holes"]:
            ax.add_patch(Circle((hx, hy), b["p"].mount_d / 2, fc="white", ec="k"))
        for t in range(b["p"].terminals):
            ax.text((t * 3 + 1) * PITCH, y1 - 1.2, "MASTER" if t == b["p"].terminals - 1 else f"T{t + 1}",
                    ha="center", fontsize=8)
        ax.set_aspect("equal"); ax.invert_yaxis(); ax.set_title(title, fontsize=10); ax.axis("off")
        ax.set_xlim(x0 - 1, x1 + 1); ax.set_ylim(y1 + 1, y0 - 1)
    fig.tight_layout()
    fig.savefig(path, dpi=110)


def main() -> None:
    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    b = build()
    (out / "one-wire-bus.kicad_pcb").write_text(to_kicad(b))
    render(b, out / "one-wire-bus.png")
    x0, y0, x1, y1 = b["outline"]
    print(f"board {x1 - x0:.1f} x {y1 - y0:.1f} mm, {len(b['pads'])} pads, {len(b['tracks'])} track segments")


if __name__ == "__main__":
    main()
