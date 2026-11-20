"""Six labelled OpenSCAD views of one model view, rendered in parallel and montaged into one PNG.

    shop views projects/<slug>/model.scad <view> [out.png] [-D name=value ...]

Sets ``view="<view>"`` and renders with ``--render`` (real geometry and colours, not the preview).
Each camera is a direction only; ``--autocenter --viewall`` frame the model, so any model fits.
The default output is ``out/<slug>_<view>_views.png`` beside the .scad. Without ImageMagick's
``montage`` the six PNGs are kept beside it instead, not failed.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .scad import OpenSCAD

# label -> eye direction (x, y, z) from the model's centre; Z up.
VIEWS = {
    "iso +X+Y": (170, 230, 160),
    "iso -X-Y": (-170, -230, 160),
    "from -Y": (0, -300, 30),
    "from +X": (300, 0, 0),
    "top": (0, 0, 300),
    "bottom": (0, 0, -300),
}


def render_views(scad: Path, view: str, out: Path, defines: list[str] = ()) -> Path:
    osc = OpenSCAD()
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        pngs = [Path(d) / f"{i}_{label.replace(' ', '_')}.png" for i, label in enumerate(VIEWS)]

        def one(i: int) -> None:
            eye = ",".join(map(str, VIEWS[list(VIEWS)[i]]))
            osc.run(scad, pngs[i], "--render", "--autocenter", "--viewall", "--imgsize=900,700",
                    "--colorscheme=Tomorrow", f"--camera={eye},0,0,0", "-D", f'view="{view}"', *defines)

        with ThreadPoolExecutor(len(VIEWS)) as pool:
            list(pool.map(one, range(len(VIEWS))))
        osc.cleanup()
        if shutil.which("montage") is None:
            keep = out.with_suffix("")
            keep.mkdir(exist_ok=True)
            for p in pngs:
                shutil.copy(p, keep / p.name)
            print(f"montage not found; six views kept in {keep}")
            return keep
        cmd = ["montage"]
        for p, label in zip(pngs, VIEWS):
            cmd += ["-label", label, str(p)]
        subprocess.run([*cmd, "-tile", "3x2", "-geometry", "600x467+4+4", "-pointsize", "22", str(out)], check=True)
    return out


def main(argv: list[str]) -> int:
    args, defines, it = [], [], iter(argv)
    for a in it:
        if a == "-D":
            defines += [a, next(it, "")]
        else:
            args.append(a)
    if len(args) not in (2, 3):
        print(__doc__.strip())
        return 2
    scad = Path(args[0]).resolve()
    out = Path(args[2]) if len(args) == 3 else scad.parent / "out" / f"{scad.parent.name}_{args[1]}_views.png"
    print(render_views(scad, args[1], out, defines))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
