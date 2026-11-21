"""Assembly review sheet for the desk presence sensor: boards, tray and back plate in the shell.

    uv run python projects/desk-presence-sensor/assembly.py   ->  out/desk-presence-sensor_assembly_views.png

Panels: the front as seen at the desk, the front see-through (boards and tray behind the face),
and a side section through a D1 hook, the tray and the D1 mini, with the USB plug behind it.
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
    ("SIDE, cut through a D1 hook: arm and tape LEFT, you RIGHT", "side_xray", "0,0,300"),
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
