"""Assembly review sheet for the desk presence sensor: boards against the shell and the lid.

    uv run python projects/desk-presence-sensor/assembly.py   ->  out/desk-presence-sensor_assembly_views.png

Panels: the plate with its boards on the bench, exploded out of the tray, sections at x = 0,
and the translucent tray over the solid plate and boards.
"""
import shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from shop.scad import OpenSCAD

HERE = Path(__file__).parent
PANELS = [
    ("bench: plate and boards, from the back", "open", "60,240,260"),
    ("bench: straight down", "open", "0,0,300"),
    ("exploded: plate and boards out of the tray front", "exploded", "-250,-200,-120"),
    ("section x = 0, from +X", "section", "300,0,0"),
    ("section x = 0, tilted", "section", "300,-120,180"),
    ("translucent tray, assembled", "xray", "120,-160,230"),
]

def main():
    osc = OpenSCAD()
    out = HERE / "out" / "desk-presence-sensor_assembly_views.png"
    with tempfile.TemporaryDirectory() as d:
        pngs = [Path(d) / f"{i}.png" for i in range(len(PANELS))]
        def one(i):
            _, view, eye = PANELS[i]
            osc.run(HERE / "model.scad", pngs[i], "--render", "--autocenter", "--viewall", "--imgsize=900,700",
                    "--colorscheme=Tomorrow", f"--camera={eye},0,0,0", "-D", f'view="{view}"')
        with ThreadPoolExecutor(len(PANELS)) as pool:
            list(pool.map(one, range(len(PANELS))))
        osc.cleanup()
        cmd = ["montage"]
        for p, (label, *_) in zip(pngs, PANELS):
            cmd += ["-label", label, str(p)]
        subprocess.run([*cmd, "-tile", "3x2", "-geometry", "700x544+4+4", "-pointsize", "20", str(out)], check=True)
    print(out)

main()
