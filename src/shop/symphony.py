"""Links from workshop projects to the symphony repo (the boat's system docs).

A boat-bound project's README carries one line starting ``Symphony:`` with
links to the symphony paths it plugs into (firmware, wiring, Signal K docs).
``shop symphony`` prints that index; the test fails on a link whose path is
gone from symphony's main, so the cross-links can't rot silently.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from . import build

REPO_URL = "https://github.com/mark-brannan/symphony/"
LINK = re.compile(re.escape(REPO_URL) + r"(?:tree|blob)/main/([^)\s#]*)")
TAG = re.compile(r"^Symphony:\s*(.*)$", re.MULTILINE)


def checkout() -> Path | None:
    """The symphony checkout: $SYMPHONY_DIR, else ~/symphony."""
    p = Path(os.environ.get("SYMPHONY_DIR", Path.home() / "symphony"))
    return p if (p / ".git").exists() else None


def tracked_paths(repo: Path) -> set[str]:
    """Files and directories on symphony's main (origin/main where it exists)."""
    for ref in ("origin/main", "HEAD"):
        r = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "--name-only", ref], capture_output=True, text=True)
        if r.returncode == 0:
            files = set(r.stdout.split())
            dirs = {str(Path(f).parents[i]) for f in files for i in range(len(Path(f).parents) - 1)}
            return files | dirs
    raise RuntimeError(f"{repo}: no origin/main or HEAD")


def links() -> list[tuple[Path, str]]:
    """Every symphony path linked from any workshop markdown file."""
    out = []
    for md in sorted(build.ROOT.rglob("*.md")):
        if any(part.startswith(".") for part in md.relative_to(build.ROOT).parts):
            continue
        out += [(md, m.group(1).rstrip("/")) for m in LINK.finditer(md.read_text(encoding="utf-8"))]
    return out


def index() -> list[tuple[str, str]]:
    """(project, its Symphony: line) for every boat-bound project."""
    rows = []
    for readme in sorted((build.ROOT / "projects").glob("*/README.md")):
        m = TAG.search(readme.read_text(encoding="utf-8"))
        if m:
            rows.append((readme.parent.name, m.group(1)))
    return rows


def main() -> int:
    for slug, line in index():
        print(f"{slug:28s} {', '.join(LINK.findall(line)) or line}")
    return 0
