"""1-wire bus board: seven 3-pin terminals in a row, [G D V] each, tied into three nets.
Optional pull-up spot (R1, DATA to VCC) past the MASTER terminal; leave it empty when the master has its own.

Two copper layers, no vias, no jumpers. Plated pads put every pin on both layers:
  G  top    trunk behind the pin row, stub back from each G pad
  V  top    trunk in front of the pin row (under the terminal body), stub forward from each V pad
  D  bottom trunk between the pin row and the G trunk, stub back from each D pad
Terminals: any 3-position 2.54 mm screw block, wire entry facing the front edge. All 21 pins sit on one
2.54 mm grid, blocks butted (body 3 x 2.54); order terminals to match.
D runs on the other layer from the G stubs it passes under.
Writes out/one-row/one-wire-bus-one-row.kicad_pcb (KiCad 7 text format), the .png beside it and, where the box
has KiCad (shop.pcbfab), the rule check, Gerbers and upload zip under out/one-row/fab/.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

PITCH = 2.54


@dataclass
class Params:
    terminals: int = 7          # six field terminals + the master (the last one)
    pins: int = 3               # G, D, V
    pad_d: float = 1.9
    drill: float = 1.3          # typical for 0.9 mm pins; set to the ordered part
    block_pitch: float = 8.2    # AM128-2.54 body is 8.1 wide (maker diagram), 7.8 by calipers: 8.2 clears both; pins 2.54 inside a block, 2.94 across a joint
    end_gap: float = PITCH / 2  # body edge to first pin
    front_to_pin: float = 3.3   # wire-entry face to the pin row (typical; set to the ordered part)
    back_to_pin: float = 3.2    # body depth 6.5 (typical)
    lip: float = 0.5            # board edge past the body's wire-entry face
    track_w: float = 0.5        # DATA
    power_w: float = 1.0        # GND and VCC
    g_off: float = 5.08         # G trunk behind the pin row (y negative = back)
    d_off: float = 2.54         # D trunk (bottom layer) behind the pin row
    v_off: float = 2.54         # V trunk in front of the pin row
    back_margin: float = 3.8    # board edge behind the body
    mount_d: float = 3.2        # M3 clearance
    mount_keepout: float = 3.8  # hole centre to the nearest part: M3 washer radius 3.5 + 0.3
    mount_inset: float = 3.0    # hole centre to the board end
    mount_span_step: float = 5.0  # hole spacing rounds up to a multiple of this
    pullup: bool = True         # R1 footprint, DATA to VCC, past the MASTER terminal
    r_pitch: float = 7.62       # axial resistor, body up to 6.3 x 2.5
    r_pad_d: float = 1.6
    r_drill: float = 0.8
    r_gap: float = 3.5          # last pin to the resistor's centre line
    mask_expansion: float = 0.05  # OSH Park: 2 mil
    rev: str = "A"


NETS = {"G": 1, "D": 2, "V": 3}
NET_NAMES = {1: "GND", 2: "DATA", 3: "VCC"}


def build(p: Params = Params()) -> dict:
    """Pads and tracks in mm, KiCad axes (y down). Pin row at y = 0."""
    pads, tracks = [], []
    for t in range(p.terminals):
        for i, name in enumerate("GDV"):
            x = t * p.block_pitch + i * PITCH
            pads.append({"ref": f"J{t + 1}", "num": i + 1, "net": NETS[name], "x": x, "y": 0.0,
                         "d": p.pad_d, "drill": p.drill})
    by = {n: [q for q in pads if q["net"] == NETS[n]] for n in "GDV"}

    def seg(a, b, layer, net):
        tracks.append({"x1": a[0], "y1": a[1], "x2": b[0], "y2": b[1], "layer": layer, "net": net,
                       "w": p.track_w if net == NETS["D"] else p.power_w})

    yg, yd, yv = -p.g_off, -p.d_off, p.v_off
    for n, y, layer in (("G", yg, "F.Cu"), ("D", yd, "B.Cu"), ("V", yv, "F.Cu")):
        pp = by[n]
        for q in pp:
            seg((q["x"], 0.0), (q["x"], y), layer, NETS[n])
        for a, b in zip(pp, pp[1:]):
            seg((a["x"], y), (b["x"], y), layer, NETS[n])
    bx0 = -p.end_gap
    bx1 = (p.terminals - 1) * p.block_pitch + (p.pins - 1) * PITCH + p.end_gap
    y0, y1 = -(p.back_to_pin + p.back_margin), p.front_to_pin + p.lip
    ym = (y0 + y1) / 2
    right = bx1
    resistor = None
    if p.pullup:
        xr = by["V"][-1]["x"] + p.r_gap
        rv, rd = (xr, ym + p.r_pitch / 2), (xr, ym - p.r_pitch / 2)   # VCC end in front, DATA end behind
        pads.append({"ref": "R1", "num": 1, "net": NETS["V"], "x": rv[0], "y": rv[1], "d": p.r_pad_d, "drill": p.r_drill})
        pads.append({"ref": "R1", "num": 2, "net": NETS["D"], "x": rd[0], "y": rd[1], "d": p.r_pad_d, "drill": p.r_drill})
        seg((by["V"][-1]["x"], yv), (xr, yv), "F.Cu", NETS["V"])
        seg((xr, yv), rv, "F.Cu", NETS["V"])
        seg((by["D"][-1]["x"], yd), (xr, yd), "B.Cu", NETS["D"])
        seg((xr, yd), rd, "B.Cu", NETS["D"])
        resistor = (xr, rv[1], rd[1])
        right = xr + 1.25
    hl, hr = bx0 - p.mount_keepout, right + p.mount_keepout
    grow = math.ceil((hr - hl) / p.mount_span_step - 1e-9) * p.mount_span_step - (hr - hl)
    hl, hr = hl - grow / 2, hr + grow / 2
    x0, x1 = hl - p.mount_inset, hr + p.mount_inset
    holes = [(hl, ym), (hr, ym)]
    bodies = [(t * p.block_pitch - p.end_gap, -p.back_to_pin,
               t * p.block_pitch + (p.pins - 1) * PITCH + p.end_gap, p.front_to_pin) for t in range(p.terminals)]
    return {"pads": pads, "tracks": tracks, "outline": (x0, y0, x1, y1), "holes": holes, "bodies": bodies,
            "resistor": resistor, "p": p}


def silk(b: dict) -> list[tuple]:
    """Silkscreen text: (x, y, text, layer, height, rotation)."""
    p = b["p"]
    x0, y0, x1, y1 = b["outline"]
    out = []
    for t in range(p.terminals):
        for i, name in enumerate("GDV"):
            out.append((t * p.block_pitch + i * PITCH, -p.back_to_pin - 0.9, name, "F.SilkS", 1.0, 0))
        out.append((t * p.block_pitch + PITCH, y0 + 1.1, "MASTER" if t == p.terminals - 1 else str(t + 1), "F.SilkS", 1.0, 0))
    if b["resistor"]:
        xr, yv_, yd_ = b["resistor"]
        out.append((xr, (yv_ + yd_) / 2, "4k7", "F.SilkS", 0.9, 90))
    mid = (p.terminals - 1) * p.block_pitch / 2 + PITCH
    out.append((mid, y0 + 1.5, f"1-WIRE BUS  G=GND  D=DATA  V=+V   rev {p.rev}", "B.SilkS", 1.0, 0))
    return out


def to_kicad(b: dict, models: dict | None = None) -> str:
    """`models` (footprint kind -> STEP path) is for pictures only; the fab file carries none."""
    p = b["p"]
    models = models or {}

    def model(kind):
        return [f'  (model "{models[kind]}" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))'] if kind in models else []
    o = ['(kicad_pcb (version 20221018) (generator "workshop")',
         ' (general (thickness 1.6))', ' (paper "A4")',
         ' (layers (0 "F.Cu" signal) (31 "B.Cu" signal) (36 "B.SilkS" user "B.Silkscreen") '
         '(37 "F.SilkS" user "F.Silkscreen") (38 "B.Mask" user) (39 "F.Mask" user) (44 "Edge.Cuts" user) (49 "F.Fab" user))',
         f' (setup (pad_to_mask_clearance {p.mask_expansion}))', ' (net 0 "")']
    o += [f' (net {n} "{NET_NAMES[n]}")' for n in (1, 2, 3)]
    ox, oy = 100.0, 100.0   # place on the sheet
    for t in range(p.terminals):
        ref = f"J{t + 1}"
        x = ox + t * p.block_pitch
        o.append(f' (footprint "workshop:ScrewBlock_1x3_P2.54mm" (layer "F.Cu") (at {x:.3f} {oy:.3f})')
        o.append(f'  (fp_text reference "{ref}" (at 2.54 -1.9) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))')
        o.append('  (fp_text value "3P 2.54 screw block, wire entry toward +y" (at 2.54 4.6) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))')
        for i, name in enumerate("GDV"):
            shape = "rect" if i == 0 else "circle"
            o.append(f'  (pad "{i + 1}" thru_hole {shape} (at {i * PITCH:.3f} 0) (size {p.pad_d} {p.pad_d}) '
                     f'(drill {p.drill}) (layers "*.Cu" "*.Mask") (net {NETS[name]} "{NET_NAMES[NETS[name]]}"))')
        o += model("terminal")
        o.append(' )')
    if b["resistor"]:
        xr, yv_, yd_ = b["resistor"]
        o.append(f' (footprint "workshop:R_Axial_P7.62mm" (layer "F.Cu") (at {ox + xr:.3f} {oy + yv_:.3f})')
        o.append('  (fp_text reference "R1" (at 0 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))')
        o.append('  (fp_text value "4k7 pull-up, optional" (at 0 0) (layer "F.Fab") hide (effects (font (size 1 1) (thickness 0.15))))')
        o.append(f'  (fp_rect (start -1.25 {(yd_ - yv_) / 2 + 2.7:.3f}) (end 1.25 {(yd_ - yv_) / 2 - 2.7:.3f}) (layer "F.SilkS") (width 0.12) (fill none))')
        for num, yy, net in ((1, 0.0, 3), (2, yd_ - yv_, 2)):
            o.append(f'  (pad "{num}" thru_hole circle (at 0 {yy:.3f}) (size {p.r_pad_d} {p.r_pad_d}) '
                     f'(drill {p.r_drill}) (layers "*.Cu" "*.Mask") (net {net} "{NET_NAMES[net]}"))')
        o.append(' )')
    for k, (hx, hy) in enumerate(b["holes"]):
        o.append(f' (footprint "workshop:MountingHole_M3" (layer "F.Cu") (at {ox + hx:.3f} {oy + hy:.3f})')
        o.append(f'  (fp_text reference "H{k + 1}" (at 0 0) (layer "F.SilkS") hide (effects (font (size 1 1) (thickness 0.15))))')
        o.append(f'  (pad "" np_thru_hole circle (at 0 0) (size {p.mount_d} {p.mount_d}) (drill {p.mount_d}) (layers "*.Cu" "*.Mask"))')
        o += model("screw")
        o.append(' )')
    for s in b["tracks"]:
        o.append(f' (segment (start {ox + s["x1"]:.3f} {oy + s["y1"]:.3f}) (end {ox + s["x2"]:.3f} {oy + s["y2"]:.3f}) '
                 f'(width {s["w"]}) (layer "{s["layer"]}") (net {s["net"]}))')
    bodies = b["bodies"]   # butted bodies: one outline for the row, dividers stopping short of it
    o.append(f' (gr_rect (start {ox + bodies[0][0]:.3f} {oy + bodies[0][1]:.3f}) (end {ox + bodies[-1][2]:.3f} {oy + bodies[-1][3]:.3f}) '
             '(layer "F.SilkS") (width 0.12) (fill none))')
    for bx0, by0, _, by1 in bodies[1:]:
        o.append(f' (gr_line (start {ox + bx0:.3f} {oy + by0 + 0.4:.3f}) (end {ox + bx0:.3f} {oy + by1 - 0.4:.3f}) (layer "F.SilkS") (width 0.12))')
    for x, y, text, layer, size, rot in silk(b):
        mirror = " (justify mirror)" if layer == "B.SilkS" else ""
        o.append(f' (gr_text "{text}" (at {ox + x:.3f} {oy + y:.3f} {rot}) (layer "{layer}") '
                 f'(effects (font (size {size} {size}) (thickness 0.15)){mirror}))')
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
    fig, axs = plt.subplots(2, 1, figsize=b.get("fig", (12, 5)))
    x0, y0, x1, y1 = b["outline"]
    t_top, t_bot = b.get("titles", ("Top copper (front edge, wire entry, at the bottom): G behind the pins, V in front, under the body",
                                   "Bottom copper: D, one trace under the G stubs"))
    for ax, layer, title in ((axs[0], "F.Cu", t_top), (axs[1], "B.Cu", t_bot)):
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#2f6b3a", alpha=0.18, ec="k"))
        for s in b["tracks"]:
            if s["layer"] == layer:
                ax.plot([s["x1"], s["x2"]], [s["y1"], s["y2"]], color=col[s["net"]], lw=5.2 * s["w"], solid_capstyle="round")
        for q in b["pads"]:
            ax.add_patch(Circle((q["x"], q["y"]), q["d"] / 2, fc="#d9b44a", ec=col[q["net"]], lw=1.5))
        for hx, hy in b["holes"]:
            ax.add_patch(Circle((hx, hy), b["p"].mount_d / 2, fc="white", ec="k"))
        for (bx0, by0, bx1, by1) in b["bodies"]:
            ax.add_patch(Rectangle((bx0, by0), bx1 - bx0, by1 - by0, fc="none", ec="#1c3a4d", ls="--", lw=1))
        for x, y, text, lay, size, rot in b.get("silk") or silk(b):
            if lay[0] == layer[0]:
                ax.text(x, y, text, ha="center", va="center", fontsize=7 * size, rotation=rot)
        ax.set_aspect("equal"); ax.invert_yaxis(); ax.set_title(title, fontsize=10); ax.axis("off")
        ax.set_xlim(x0 - 1, x1 + 1); ax.set_ylim(y1 + 1, y0 - 1)
    fig.tight_layout()
    fig.savefig(path, dpi=110)


def terminal_parts(p: Params, pins: int) -> list:
    """Stand-in screw block: pin 1 at the origin, pins along +x, wire entry toward -y (model y is up)."""
    from build123d import Align, Box, Color, Cylinder, Pos
    low = (Align.CENTER, Align.CENTER, Align.MIN)
    w, depth, h = pins * PITCH, p.front_to_pin + p.back_to_pin, 8.5
    yc = (p.back_to_pin - p.front_to_pin) / 2          # the wire-entry face is at -front_to_pin
    body = Pos((pins - 1) * PITCH / 2, yc, 0) * Box(w - 0.1, depth, h, align=low)
    metal = []
    for i in range(pins):
        body -= Pos(i * PITCH, -p.front_to_pin, 1.2) * Box(1.9, 5.0, 2.4, align=low)      # wire entry
        body -= Pos(i * PITCH, 0.6, h - 2.0) * Cylinder(1.0, 2.0, align=low)              # screw well
        metal.append(Pos(i * PITCH, 0.6, h - 2.6) * Cylinder(0.95, 1.6, align=low)
                     - Pos(i * PITCH, 0.6, h - 1.3) * Box(1.9, 0.35, 0.4, align=low))
        metal.append(Pos(i * PITCH, 0, -3.0) * Box(0.7, 0.5, 3.0, align=low))             # pin
        metal.append(Pos(i * PITCH, -p.front_to_pin + 3.0, 1.3) * Box(1.7, 3.0, 2.0, align=low))  # clamp
    body.color = Color(0.10, 0.45, 0.22)
    for part in metal:
        part.color = Color(0.75, 0.75, 0.78)
    return [body, *metal]


def screw_parts() -> list:
    """Stand-in M3 screw on a 7 mm washer."""
    from build123d import Align, Box, Color, Cylinder, Pos, Rot
    low = (Align.CENTER, Align.CENTER, Align.MIN)
    screw = [Cylinder(3.5, 0.5, align=low) - Cylinder(1.6, 0.5, align=low),
             Pos(0, 0, 0.5) * Cylinder(2.8, 2.2, align=low) - Pos(0, 0, 1.7) * Box(3.2, 0.6, 1.0, align=low)
             - Pos(0, 0, 1.7) * Rot(0, 0, 90) * Box(3.2, 0.6, 1.0, align=low),
             Pos(0, 0, -6.0) * Cylinder(1.5, 6.5, align=low)]
    for part in screw:
        part.color = Color(0.75, 0.75, 0.78)
    return screw


def assembled(b: dict, out: Path) -> None:
    """out/one-row/assembled-front.png and -back.png: the board with stand-in terminals (the guessed body) and M3 screws on washers."""
    from build123d import Compound, export_step
    from shop import pcbfab
    p = b["p"]
    tmp = out / "_assembled"
    tmp.mkdir(exist_ok=True)
    export_step(Compound(children=terminal_parts(p, p.pins)), str(tmp / "terminal.step"))
    export_step(Compound(children=screw_parts()), str(tmp / "screw.step"))
    pcb = tmp / "assembled.kicad_pcb"
    pcb.write_text(to_kicad(b, {"terminal": tmp / "terminal.step", "screw": tmp / "screw.step"}))
    for name, rotate in (("front", "-50,0,-25"), ("back", "-50,0,155")):
        if pcbfab.render3d(pcb, tmp / f"{name}.png", rotate):
            (tmp / f"{name}.png").replace(out / f"assembled-{name}.png")
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()


def main() -> None:
    out = Path(__file__).parent / "out" / "one-row"
    out.mkdir(parents=True, exist_ok=True)
    b = build()
    (out / "one-wire-bus-one-row.kicad_pcb").write_text(to_kicad(b))
    render(b, out / "one-wire-bus-one-row.png")
    from shop import pcbfab
    print(pcbfab.fab(out / "one-wire-bus-one-row.kicad_pcb", out / "fab"))
    assembled(b, out)
    x0, y0, x1, y1 = b["outline"]
    print(f"board {x1 - x0:.1f} x {y1 - y0:.1f} mm, {len(b['pads'])} pads, {len(b['tracks'])} track segments")


if __name__ == "__main__":
    main()
