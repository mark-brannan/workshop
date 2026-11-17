"""1-wire bus board, three compact forms of the one-row board in model.py: the same three nets, six field
terminals and a MASTER, optional 4k7 pull-up (R1, DATA to VCC), two copper layers, no vias, no jumpers.

  two-row    two 9-position blocks back to back, MASTER turned 90 degrees and centred on the right end,
             four M2.5 corner holes (the right pair sit in the pockets beside MASTER)
  ring       MASTER centred on the left side, two 3-position blocks on each other side, four M3 corner holes
  pinwheel   the ring with each side's end tucked against the next side: two M3 holes, the smallest board

Every terminal reads G D V left to right with its wire entry facing you. Board origin is the top-left
corner, y down (KiCad axes). G and V run on top, D on the bottom; plated pads carry every pin to both layers.
Writes out/<form>/ (board, picture, fab set, assembled pictures) and out/layouts.png (all forms, one scale).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from pathlib import Path

from shop.testing import load_model

_m = load_model(__file__)
NET_NAMES, NETS, PITCH, Params, render = _m.NET_NAMES, _m.NETS, _m.PITCH, _m.Params, _m.render

ENTRY = {"U": (0, -1), "D": (0, 1), "L": (-1, 0), "R": (1, 0)}
ANGLE = {"D": 0, "R": 90, "U": 180, "L": 270}      # KiCad footprint rotation; the pin row runs G D V along (ey, -ex)
B3_HALF = 4.05                                      # half of the 8.1 mm body of a 3-position block (maker's diagram)
SCREW = {"M3": (3.2, 5.6), "M2.5": (2.7, 5.0)}      # clearance hole, pan head diameter (ISO 7045)


@dataclass
class LParams(Params):
    screw: str = "M3"
    head_gap: float = 0.1       # copper and bodies stay this far outside the screw head
    stub: float = 2.0           # pin line to a trunk beside it: pad 0.95 + 0.3 clear + half a 1.0 track, rounded up
    link_w: float = 0.6         # V where it squeezes past a screw head or runs to R1
    block_gap: float = 0.1      # between two 3-position bodies side by side: 8.2 pitch for an 8.1 body


class Board:
    def __init__(self, p: LParams, name: str, w: float, h: float):
        self.p, self.name, self.outline = p, name, (0.0, 0.0, w, h)
        self.pads, self.tracks, self.bodies, self.holes, self.silk, self.blocks = [], [], [], [], [], []
        self.resistor = None

    def block(self, ref: str, n: int, cx: float, cy: float, entry: str) -> None:
        """An n-position block whose pin line is centred on (cx, cy), wire entry toward `entry`."""
        p, (ex, ey) = self.p, ENTRY[entry]
        rx, ry = ey, -ex
        for i in range(n):
            s = (i - (n - 1) / 2) * PITCH
            self.pads.append({"ref": ref, "num": i + 1, "net": NETS["GDV"[i % 3]], "x": cx + rx * s, "y": cy + ry * s,
                              "d": p.pad_d, "drill": p.drill, "ex": ex, "ey": ey, "n": n})
        half = B3_HALF if n == 3 else n * PITCH / 2
        xs = [cx - rx * half + ex * p.front_to_pin, cx + rx * half - ex * p.back_to_pin]
        ys = [cy - ry * half + ey * p.front_to_pin, cy + ry * half - ey * p.back_to_pin]
        self.bodies.append((min(xs), min(ys), max(xs), max(ys)))
        self.blocks.append({"ref": ref, "n": n, "entry": entry, "x": cx - rx * (n - 1) / 2 * PITCH,
                            "y": cy - ry * (n - 1) / 2 * PITCH})

    def pair(self, refs: tuple[str, str], cx: float, cy: float, entry: str) -> None:
        """Two 3-position blocks side by side, the first on the left seen from outside."""
        ex, ey = ENTRY[entry]
        d = B3_HALF + self.p.block_gap / 2
        for ref, sgn in zip(refs, (-1, 1)):
            self.block(ref, 3, cx + ey * sgn * d, cy - ex * sgn * d, entry)

    def path(self, pts: list, net: str, layer: str | None = None, w: float | None = None) -> None:
        layer = layer or ("B.Cu" if net == "D" else "F.Cu")
        w = w or (self.p.track_w if net == "D" else self.p.power_w)
        for a, b in zip(pts, pts[1:]):
            if math.dist(a, b) > 1e-6:
                self.tracks.append({"x1": a[0], "y1": a[1], "x2": b[0], "y2": b[1], "layer": layer, "net": NETS[net], "w": w})

    def stubs(self, net: str, out: float, skip: str = "") -> None:
        """A stub from every pin of `net`, `out` mm toward its wire entry (negative: behind the pin)."""
        for q in self.pins(net):
            if q["ref"] == skip:
                continue
            self.path([(q["x"], q["y"]), (q["x"] + q["ex"] * out, q["y"] + q["ey"] * out)], net)

    def pins(self, net: str, refs: str = "J") -> list:
        return [q for q in self.pads if q["net"] == NETS[net] and q["ref"].startswith(refs)]

    def side(self, net: str, entry: str, axis: int = 0) -> list:
        """Sorted x (axis 0) or y (axis 1) of the `net` pins whose wire entry faces `entry`."""
        ex, ey = ENTRY[entry]
        return sorted(q["xy"[axis]] for q in self.pins(net) if (q["ex"], q["ey"]) == (ex, ey))

    def pin(self, ref: str, net: str) -> tuple:
        q = next(q for q in self.pads if q["ref"] == ref and q["net"] == NETS[net])
        return (q["x"], q["y"])

    def r1(self, v: tuple, d: tuple) -> None:
        p = self.p
        for num, (x, y), net in ((1, v, "V"), (2, d, "D")):
            self.pads.append({"ref": "R1", "num": num, "net": NETS[net], "x": x, "y": y, "d": p.r_pad_d, "drill": p.r_drill})
        self.resistor = (v, d)
        self.text((v[0] + d[0]) / 2, (v[1] + d[1]) / 2, "4k7", 0.9, 0 if v[1] == d[1] else 90)

    def text(self, x, y, s, size=1.0, rot=0, layer="F.SilkS") -> None:
        self.silk.append((x, y, s, layer, size, rot))

    def letters(self, out: float, back: float = 3.6, size: float = 1.0) -> None:
        """G D V beside every pin: on top `out` mm toward the wire entry, on the bottom `back` mm behind the pin."""
        for q in self.pads:
            if q["ref"].startswith("J"):
                name = "GDV"[(q["num"] - 1) % 3]
                rot = {(0, 1): 0, (0, -1): 180, (1, 0): 90, (-1, 0): 270}[(q["ex"], q["ey"])]
                self.text(q["x"] + q["ex"] * out, q["y"] + q["ey"] * out, name, size, rot)
                self.text(q["x"] - q["ex"] * back, q["y"] - q["ey"] * back, name, 0.9, rot, "B.SilkS")

    def done(self, titles: tuple, fig: tuple, legend: list) -> dict:
        hole_d, head_d = SCREW[self.p.screw]
        for x, y, line, size in legend:
            self.text(x, y, line, size, 0, "B.SilkS")
        return {"name": self.name, "pads": self.pads, "tracks": self.tracks, "outline": self.outline, "holes": self.holes,
                "bodies": self.bodies, "blocks": self.blocks, "resistor": self.resistor, "silk": self.silk,
                "p": replace(self.p, mount_d=hole_d), "head_d": head_d, "titles": titles, "fig": fig}


def two_row(p: LParams = LParams(screw="M2.5")) -> dict:
    """Rows back to back, entry toward the top and bottom edges; MASTER centred on the right end, entry right."""
    _, head = SCREW[p.screw]
    keep = head / 2 + p.head_gap
    lip, sep, st = 2.2, 3 * PITCH, p.stub          # lip: room for G D V past the entry face
    hx = head / 2 + 0.2                            # left holes: head just inside the board
    xl = hx + keep + p.power_w / 2                 # V link, clear of the left screw heads
    x0 = xl + st                                   # first pin
    yt = lip + p.front_to_pin
    yb = yt + sep
    h = yb + p.front_to_pin + lip
    xm = x0 + 11 * PITCH                           # MASTER's pin column: a one-hole gap for R1 before its body
    w = xm + p.front_to_pin + 3.0
    b = Board(p, "two-row", w, h)
    b.block("J1", 9, x0 + 4 * PITCH, yb, "D")
    b.block("J2", 9, x0 + 4 * PITCH, yt, "U")
    b.block("J3", 3, xm, h / 2, "R")
    yg, yd = yb - st, h / 2
    g = sorted(q["x"] for q in b.pins("G", "J1") + b.pins("G", "J2"))
    for q in b.pins("G", "J1") + b.pins("G", "J2"):
        b.path([(q["x"], q["y"]), (q["x"], yg)], "G")
    b.path([(g[0], yg), (xm, yg), b.pin("J3", "G")], "G")
    d = sorted(q["x"] for q in b.pins("D", "J1"))
    for x in d:
        b.path([(x, yt), (x, yb)], "D")
    b.path([(d[0], yd), b.pin("J3", "D")], "D")
    xr = (x0 + 8.5 * PITCH + xm - p.back_to_pin) / 2             # R1 stands in the gap, its pads on the pin lines
    yvt, yvb = yt - PITCH, yb + PITCH
    for ref, y in (("J1", yvb), ("J2", yvt)):
        for q in b.pins("V", ref):
            b.path([(q["x"], q["y"]), (q["x"], y)], "V")
    b.path([(max(q["x"] for q in b.pins("V", "J1")), yvb), (xl, yvb), (xl, yvt), (xr, yvt), (xr, yt)], "V")
    b.path([(xr, yt), b.pin("J3", "V")], "V", w=p.link_w)
    b.r1((xr, yt), (xr, yb))
    b.path([(xr, yb), (xr, yd)], "D")
    hy = head / 2 + 0.1
    xp = xm - p.back_to_pin + (w - xm + p.back_to_pin) / 2       # middle of the pocket beside MASTER
    b.holes = [(hx, hy), (hx, h - hy), (xp, hy), (xp, h - hy)]
    b.letters(p.front_to_pin + 1.0, back=-1.9)
    for k, x in enumerate((1, 4, 7)):
        b.text(x0 + x * PITCH, yb - 1.9, str(k + 1))
        b.text(x0 + x * PITCH, yt + 1.9, str(6 - k), 1.0, 180)
    b.text(xm + p.front_to_pin + 2.3, h / 2, "MASTER", 1.0, 90)
    return b.done(("Top copper: G down the channel to MASTER, V in front of each row, linked at the left",
                   "Bottom copper: D, one trace down the channel"), (12, 7),
                  [(x0 + 4 * PITCH, h / 2, f"1-WIRE BUS rev {p.rev}  G=GND D=DATA V=+V", 0.9)])


def _square(p: LParams, name: str, w: float) -> tuple:
    b = Board(p, name, w, w)
    a = p.lip + p.front_to_pin                     # pin line, in from the edge
    return b, a, a - p.stub, a + p.stub            # V trunk in front of the pins, G and D behind them


def ring(p: LParams = LParams()) -> dict:
    """MASTER centred on the left; two 3-position blocks on the top, right and bottom; a screw in each corner."""
    depth = p.front_to_pin + p.back_to_pin
    w = 2 * (p.lip + depth + 0.2) + 4 * B3_HALF + p.block_gap
    b, a, v, g = _square(p, "ring", w)
    c = w / 2
    b.pair(("J1", "J2"), c, a, "U")
    b.pair(("J3", "J4"), w - a, c, "R")
    b.pair(("J5", "J6"), c, w - a, "D")
    b.block("J7", 3, a, c, "L")
    _, head = SCREW[p.screw]
    keep = head / 2 + p.head_gap
    k = 1.0                                         # V hugs the board corner, outside the screw head
    hole = k + p.link_w / 2 + keep
    b.holes = [(hole, hole), (w - hole, hole), (hole, w - hole), (w - hole, w - hole)]
    e = p.lip + depth + 0.6                         # where V leaves a side for the corner
    loop = []
    for rot in range(4):                            # one side and the corner after it, turned four times
        pts = [(e, v), (w - e, v), (w - e + 0.8, k), (w - v, k), (w - k, v), (w - k, e - 0.8), (w - v, e)]
        for _ in range(rot):
            pts = [(w - y, x) for x, y in pts]
        b.path(pts[:2], "V")
        loop += pts
    b.path(loop + loop[:1], "V", w=p.link_w)
    b.stubs("V", p.stub)
    m = e + 0.9                                     # G and D cut the corners behind the screws
    octagon = [(m, g), (w - m, g), (w - g, m), (w - g, w - m), (w - m, w - g), (m, w - g), (g, w - m), (g, m)]
    b.path(octagon + octagon[:1], "G")
    b.stubs("G", -p.stub)
    md, mv = b.pin("J7", "D"), b.pin("J7", "V")
    b.path([(g, md[1]), (g, m), *octagon[:5], (b.side("D", "D")[0], w - g)], "D")   # open at the lower left: V comes in there
    b.stubs("D", -p.stub)
    dx = b.side("D", "D")[-1]
    b.r1((dx - p.r_pitch, mv[1]), (dx, mv[1]))
    b.path([mv, (dx - p.r_pitch, mv[1])], "V", "B.Cu", p.link_w)
    b.path([(dx, mv[1]), (dx, w - g)], "D")
    b.letters(-(p.back_to_pin + 0.7), size=0.8)
    far = p.back_to_pin + 2.4                       # terminal numbers, behind each body where they stay readable
    for n, (x, y) in zip("123456", ((c - 4.1, a + far), (c + 4.1, a + far), (w - a - far, c - 4.1), (w - a - far, c + 4.1),
                                    (c + 4.1, w - a - far), (c - 4.1, w - a - far))):
        b.text(x, y, n)
    b.text(a + far, c, "MASTER", 0.9, 90)
    return b.done(("Top copper: V round the outside, past each corner screw; G behind the pins",
                   "Bottom copper: D behind the pins, open at the lower left where V comes in to R1"), (9, 13),
                  [(c, c - 5.0, f"1-WIRE BUS rev {p.rev}", 0.9), (c, c - 3.4, "G=GND D=DATA", 0.9), (c, c - 1.8, "V=+V", 0.9)])


def pinwheel(p: LParams = LParams()) -> dict:
    """The ring with each side slid along until its end meets the next side: no empty corners."""
    depth = p.front_to_pin + p.back_to_pin
    side = 4 * B3_HALF + p.block_gap                # two 3-position blocks
    w = 2 * p.lip + side + depth + 0.2
    b, a, v, g = _square(p, "pinwheel", w)
    c = p.lip + side / 2
    b.pair(("J1", "J2"), c, a, "U")
    b.pair(("J3", "J4"), w - a, c, "R")
    b.pair(("J5", "J6"), w - c, w - a, "D")
    b.block("J7", 3, a, w - p.lip - B3_HALF, "L")
    first, mv, mg, md = (b.side("V", "U")[0], a), b.pin("J7", "V"), b.pin("J7", "G"), b.pin("J7", "D")
    b.path([first, (first[0], v), (w - v, v), (w - v, w - v), (mv[0], w - v), mv], "V")   # open on the left
    b.stubs("V", p.stub, skip="J7")                 # MASTER's V pin sits on the trunk's end
    b.path([(b.side("G", "U")[0], g), (w - g, g), (w - g, w - g), (g, w - g), (g, mg[1])], "G")
    b.stubs("G", -p.stub)
    b.path([(b.side("D", "U")[0], g), (w - g, g)], "D")
    b.path([(w - g, b.side("D", "R", 1)[0]), (w - g, w - g)], "D")
    b.path([(b.side("D", "D")[-1], w - g), (g, w - g), (g, md[1])], "D")
    b.stubs("D", -p.stub)
    _, head = SCREW[p.screw]
    pocket = (p.lip + depth + 0.2 + w - p.lip - 2 * B3_HALF) / 2          # between the top side and MASTER
    b.holes = [(p.lip + depth / 2, pocket), (w / 2 + 1.8, w / 2 + 1.8)]
    yr = p.lip + depth + 0.2 + 2.4                  # R1 lies behind the top side
    dx = b.side("G", "U")[-1] + 0.5
    b.r1((dx - p.r_pitch, yr), (dx, yr))
    yl = g + 1.5                                    # V comes in through the open left, between G and the screw
    b.path([first, (first[0], yl), (dx - p.r_pitch, yl), (dx - p.r_pitch, yr)], "V", w=p.link_w - 0.1)
    b.path([(dx, yr), (dx, g)], "D")
    b.letters(2.2, back=-2.2)                       # both in front of the pins: behind them is the next side
    b.text(b.holes[0][0], b.holes[0][1] + 3.5, "MASTER", 0.8, 0)
    return b.done(("Top copper: V round the outside, open on the left; G behind the pins; V in to R1 past the left screw",
                   "Bottom copper: D behind the pins"), (8, 13), [(w / 2, w / 2 - 0.7, f"1-WIRE {p.rev}", 0.8)])


LAYOUTS = {"two-row": two_row, "ring": ring, "pinwheel": pinwheel}
PICTURE = {"two-row": (2000, 900, 2.2), "ring": (1400, 1400, 1.0), "pinwheel": (1400, 1400, 1.0)}   # width, height, zoom


def to_kicad(b: dict, models: dict | None = None) -> str:
    """`models` (kind -> STEP path, kinds 'terminal3', 'terminal9', 'screw') is for pictures; the fab file has none."""
    p, models = b["p"], models or {}

    def model(kind, scale=1.0):
        return [f'  (model "{models[kind]}" (offset (xyz 0 0 0)) (scale (xyz {scale} {scale} {scale})) (rotate (xyz 0 0 0)))'] \
            if kind in models else []
    o = ['(kicad_pcb (version 20221018) (generator "workshop")', ' (general (thickness 1.6))', ' (paper "A4")',
         ' (layers (0 "F.Cu" signal) (31 "B.Cu" signal) (36 "B.SilkS" user "B.Silkscreen") '
         '(37 "F.SilkS" user "F.Silkscreen") (38 "B.Mask" user) (39 "F.Mask" user) (44 "Edge.Cuts" user) (49 "F.Fab" user))',
         f' (setup (pad_to_mask_clearance {p.mask_expansion}))', ' (net 0 "")']
    o += [f' (net {n} "{NET_NAMES[n]}")' for n in (1, 2, 3)]
    ox, oy = 100.0, 100.0
    for blk in b["blocks"]:
        n = blk["n"]
        o.append(f' (footprint "workshop:ScrewBlock_1x{n}_P2.54mm" (layer "F.Cu") (at {ox + blk["x"]:.3f} {oy + blk["y"]:.3f} {ANGLE[blk["entry"]]})')
        o.append(f'  (fp_text reference "{blk["ref"]}" (at 0 -1.9) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))')
        for i in range(n):
            net = NETS["GDV"[i % 3]]
            o.append(f'  (pad "{i + 1}" thru_hole {"rect" if i == 0 else "circle"} (at {i * PITCH:.3f} 0 {ANGLE[blk["entry"]]}) '
                     f'(size {p.pad_d} {p.pad_d}) (drill {p.drill}) (layers "*.Cu" "*.Mask") (net {net} "{NET_NAMES[net]}"))')
        o += model(f"terminal{n}")
        o.append(' )')
    if b["resistor"]:
        (vx, vy), (dx, dy) = b["resistor"]
        o.append(f' (footprint "workshop:R_Axial_P7.62mm" (layer "F.Cu") (at {ox + vx:.3f} {oy + vy:.3f})')
        o.append('  (fp_text reference "R1" (at 0 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))')
        for num, (px, py), net in ((1, (0.0, 0.0), 3), (2, (dx - vx, dy - vy), 2)):
            o.append(f'  (pad "{num}" thru_hole circle (at {px:.3f} {py:.3f}) (size {p.r_pad_d} {p.r_pad_d}) '
                     f'(drill {p.r_drill}) (layers "*.Cu" "*.Mask") (net {net} "{NET_NAMES[net]}"))')
        o.append(' )')
    for k, (hx, hy) in enumerate(b["holes"]):
        o.append(f' (footprint "workshop:MountingHole_{p.screw}" (layer "F.Cu") (at {ox + hx:.3f} {oy + hy:.3f})')
        o.append(f'  (fp_text reference "H{k + 1}" (at 0 0) (layer "F.SilkS") hide (effects (font (size 1 1) (thickness 0.15))))')
        o.append(f'  (pad "" np_thru_hole circle (at 0 0) (size {p.mount_d} {p.mount_d}) (drill {p.mount_d}) (layers "*.Cu" "*.Mask"))')
        o += model("screw", round(b["head_d"] / 5.6, 3))
        o.append(' )')
    for s in b["tracks"]:
        o.append(f' (segment (start {ox + s["x1"]:.3f} {oy + s["y1"]:.3f}) (end {ox + s["x2"]:.3f} {oy + s["y2"]:.3f}) '
                 f'(width {s["w"]}) (layer "{s["layer"]}") (net {s["net"]}))')
    for bx0, by0, bx1, by1 in b["bodies"]:
        o.append(f' (gr_rect (start {ox + bx0:.3f} {oy + by0:.3f}) (end {ox + bx1:.3f} {oy + by1:.3f}) (layer "F.SilkS") (width 0.12) (fill none))')
    for x, y, text, layer, size, rot in b["silk"]:
        mirror = " (justify mirror)" if layer == "B.SilkS" else ""
        o.append(f' (gr_text "{text}" (at {ox + x:.3f} {oy + y:.3f} {rot}) (layer "{layer}") '
                 f'(effects (font (size {size} {size}) (thickness 0.15)){mirror}))')
    x0, y0, x1, y1 = b["outline"]
    for (a, c, d, e) in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
        o.append(f' (gr_line (start {ox + a:.3f} {oy + c:.3f}) (end {ox + d:.3f} {oy + e:.3f}) (layer "Edge.Cuts") (width 0.1))')
    o.append(')')
    return "\n".join(o) + "\n"


def price(b: dict) -> float:
    x0, y0, x1, y1 = b["outline"]
    return (x1 - x0) * (y1 - y0) / 645.16 * 5       # OSH Park: $5 per square inch buys three boards


def assembled(b: dict, out: Path) -> None:
    """out/assembled-front.png and -back.png: the board with stand-in terminals and screws."""
    from build123d import Compound, export_step
    from shop import pcbfab
    tmp = out / "_assembled"
    tmp.mkdir(exist_ok=True)
    models = {"screw": tmp / "screw.step"}
    export_step(Compound(children=_m.screw_parts()), str(models["screw"]))
    for n in {blk["n"] for blk in b["blocks"]}:
        models[f"terminal{n}"] = tmp / f"terminal{n}.step"
        export_step(Compound(children=_m.terminal_parts(b["p"], n)), str(models[f"terminal{n}"]))
    pcb = tmp / "assembled.kicad_pcb"
    pcb.write_text(to_kicad(b, models))
    for name, rotate in (("front", "-50,0,-25"), ("back", "-50,0,155")):
        if pcbfab.render3d(pcb, tmp / f"{name}.png", rotate, zoom=0.7):
            (tmp / f"{name}.png").replace(out / f"assembled-{name}.png")
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()


def compare(boards: list, path: Path) -> None:
    """Every form at one scale: top copper, bodies, holes with their screw heads, size and price."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle
    col = {1: "#333333", 2: "#1a73e8", 3: "#d93025"}
    widths = [b["outline"][2] - b["outline"][0] + 6 for b in boards]
    fig, axs = plt.subplots(1, len(boards), figsize=(sum(widths) / 9, 5.2), gridspec_kw={"width_ratios": widths})
    for ax, b, wd in zip(axs, boards, widths):
        x0, y0, x1, y1 = b["outline"]
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#2f6b3a", alpha=0.18, ec="k"))
        for s in b["tracks"]:
            ax.plot([s["x1"], s["x2"]], [s["y1"], s["y2"]], color=col[s["net"]], lw=2.6 * s["w"], solid_capstyle="round",
                    alpha=0.9 if s["layer"] == "F.Cu" else 0.55, zorder=2 if s["layer"] == "F.Cu" else 1)
        for bx0, by0, bx1, by1 in b["bodies"]:
            ax.add_patch(Rectangle((bx0, by0), bx1 - bx0, by1 - by0, fc="#1c7a3d", alpha=0.22, ec="#1c3a4d", lw=0.8))
        for q in b["pads"]:
            ax.add_patch(Circle((q["x"], q["y"]), q["d"] / 2, fc="#d9b44a", ec=col[q["net"]], lw=1.2, zorder=3))
        for hx, hy in b["holes"]:
            ax.add_patch(Circle((hx, hy), b.get("head_d", 7.0) / 2, fc="none", ec="#666", ls=":", lw=1))
            ax.add_patch(Circle((hx, hy), b["p"].mount_d / 2, fc="white", ec="k", zorder=3))
        ax.set_title(f'{b.get("name", "one-row")}\n{x1 - x0:.1f} x {y1 - y0:.1f} mm\n${price(b):.2f} for 3', fontsize=10)
        ax.set_xlim(x0 - 3, x0 - 3 + wd); ax.set_ylim(y0 + 34, y0 - 2); ax.set_aspect("equal"); ax.axis("off")
    fig.suptitle("One scale. Black G, red V (top copper), blue D (bottom copper). Dotted ring: screw head or washer.", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=110)


def main() -> None:
    from shop import pcbfab
    root = Path(__file__).parent / "out"
    boards = [_m.build()]
    for name, build in LAYOUTS.items():
        out = root / name
        out.mkdir(parents=True, exist_ok=True)
        b = build()
        pcb = out / f"one-wire-bus-{name}.kicad_pcb"
        pcb.write_text(to_kicad(b))
        render(b, out / f"one-wire-bus-{name}.png")
        print(name, pcbfab.fab(pcb, out / "fab", PICTURE[name]))
        assembled(b, out)
        x0, y0, x1, y1 = b["outline"]
        print(f"  {x1 - x0:.1f} x {y1 - y0:.1f} mm, ${price(b):.2f} for 3")
        boards.append(b)
    compare(boards, root / "layouts.png")


if __name__ == "__main__":
    main()
