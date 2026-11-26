"""A warning for the build log, never a failure: what OrcaSlicer itself says when it slices the 3MF.

The slicer is the judge of what prints. Our own checks read the mesh (closed solid, flat
overhangs); Orca reads the layers, and catches what they miss: a feature standing on a root
narrower than one line, which Orca reports as "floating regions".

Only a 3MF that carries saved Orca settings (``Metadata/project_settings.config``, written once
the user saves the project in the GUI) can be sliced headless; the rest are skipped, as is a box
with no ``orca-slicer`` on PATH. Each slice runs in a throwaway directory with its own
``--datadir``, so it never touches the GUI's config.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

SETTINGS = "Metadata/project_settings.config"


def has_settings(threemf: Path | str) -> bool:
    try:
        with zipfile.ZipFile(threemf) as z:
            return SETTINGS in z.namelist()
    except (zipfile.BadZipFile, FileNotFoundError):
        return False


def messages(result: dict) -> list[str]:
    """Orca's result.json → its warnings and, on a failed slice, its error, each once."""
    out: list[str] = []
    if result.get("return_code", 0) != 0:
        out.append(f"Orca could not slice it: {result.get('error_string', '').strip()}")
    for p in result.get("sliced_plates") or []:
        out.append(p.get("warning_message", ""))
    for w in result.get("warnings") or []:
        out.append(w.get("text", ""))
    seen: list[str] = []
    for m in (m.strip() for m in out):
        if m and m not in seen:
            seen.append(m)
    return seen


def warnings(threemf: Path | str, timeout: float = 300) -> list[str]:
    exe = shutil.which("orca-slicer")
    if exe is None or not has_settings(threemf):
        return []
    with tempfile.TemporaryDirectory(prefix="orcacheck-") as tmp:
        try:
            subprocess.run([exe, "--datadir", str(Path(tmp) / "dd"), "--slice", "0", "--outputdir", tmp,
                            str(Path(threemf).resolve())], cwd=tmp, capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return [f"Orca slice did not finish in {timeout:.0f}s"]
        res = Path(tmp) / "result.json"
        if not res.exists():
            return ["Orca slice wrote no result.json"]
        return [f"Orca: {m}" for m in messages(json.loads(res.read_text()))]
