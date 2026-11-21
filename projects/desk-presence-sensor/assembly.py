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
    ("FRONT: what you see at the desk (+X on the left)", "front", "0,0,300"),
    ("FRONT, see-through: boards behind the face", "front_xray", "0,0,300"),
    ("SIDE, tray cut away: arm and tape LEFT, you RIGHT", "side_xray", "0,0,300"),
]

def main():
    osc = OpenSCAD()
    out = HERE / "out" / "desk-presence-sensor_assembly_views.png"
    with tempfile.TemporaryDirectory() as d:
        pngs = [Path(d) / f"{i}.png" for i in range(len(PANELS))]
        def one(i):
            _, view, eye = PANELS[i]
            osc.run(HERE / "model.scad", pngs[i], "--render", "--autocenter", "--viewall", "--imgsize=900,700",
                    "--colorscheme=Tomorrow", "--projection=ortho", f"--camera={eye},0,0,0", "-D", f'view="{view}"')
        with ThreadPoolExecutor(len(PANELS)) as pool:
            list(pool.map(one, range(len(PANELS))))
        osc.cleanup()
        cmd = ["montage"]
        for p, (label, *_) in zip(pngs, PANELS):
            cmd += ["-label", label, str(p)]
        subprocess.run([*cmd, "-tile", "3x1", "-geometry", "900x700+4+4", "-pointsize", "26", str(out)], check=True)
    print(out)

main()
