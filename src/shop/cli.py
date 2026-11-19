"""``shop``: the workshop on PATH.

    shop build [projects/<slug> ...]   build every project, or the ones named
    shop gauge projects/<slug> "mount()" <z_plate> [<z_wall>]   a thin fit-check part sliced from the model
    shop doctor                        which shop tools this box has
    shop printer                       K2 Plus status (read-only)
    shop fusion                      the folder to add in Fusion's Scripts panel
    shop symphony                      boat-bound projects and the symphony paths they link
"""

from __future__ import annotations

import subprocess
import sys

from . import build
from .tools import detect

FUSION = build.ROOT / "fusion"


def _fusion_path() -> str:
    try:  # Fusion runs on Windows; from WSL it wants the \\wsl.localhost form
        return subprocess.run(["wslpath", "-w", str(FUSION)], check=True, capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return str(FUSION)


def doctor() -> int:
    print(f"workshop  {build.ROOT}")
    for t in detect():
        print(f"{t.name:11s} {'yes' if t.path else '-  '}  {t.role:22s} {t.path or ''}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    cmd, rest = (args[0], args[1:]) if args else ("help", [])
    if cmd == "build":
        return build.main(["shop build", *rest])
    if cmd == "gauge":
        from . import gauge

        return gauge.main(rest)
    if cmd == "doctor":
        return doctor()
    if cmd == "printer":
        from . import printer

        return printer.main()
    if cmd == "symphony":
        from . import symphony

        return symphony.main()
    if cmd == "fusion":
        base = _fusion_path()
        sep = "\\" if "\\" in base else "/"
        for d in sorted(p for p in FUSION.iterdir() if p.is_dir()):
            print(f"{d.name:12s} {base}{sep}{d.name}")
        return 0
    print(__doc__.strip())
    return 0 if cmd in ("help", "-h", "--help") else 2


if __name__ == "__main__":
    sys.exit(main())
