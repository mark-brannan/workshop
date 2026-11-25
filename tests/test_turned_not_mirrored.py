"""A printed part goes from its print pose to where it is used by a turn, never by mirror() (AGENTS.md,
"Asymmetric mating features"). A mirror is no move a hand can make, and it draws a part that only fits as its
own mirror image as if it fitted: halmet-piezo-pod's lid, 67d7673.

Two guards. The first reads the .scad sources for mirror() applied to a printed part. The second wants a fit
test, on the printed meshes, in every project that prints more than one part.
"""

import hashlib
import re
from pathlib import Path

PROJECTS = Path(__file__).resolve().parents[1] / "projects"
MIRROR = re.compile(r"\bmirror\s*\(")
LAST_CALL = re.compile(r"(\w+)\s*\([^()]*\)\s*;\s*(?://.*)?$")
PRINTED_VAR = re.compile(r'^\s*(?:part|view)\s*=\s*"(\w+)"', re.M)
PRINTED_CALL = re.compile(r"^(?!\s*//).*?(\w+)\s*\(\s*\)\s*;", re.M)


def part_files(project: Path) -> list[Path]:
    return [f for f in sorted(project.glob("part-*.scad")) if "gauge" not in f.name]


def printed_names(project: Path) -> set[str]:
    """Modules a project prints: what its part files call, and the part or view names they and the model select."""
    names: set[str] = set()
    for f in [*part_files(project), project / "model.scad"]:
        if not f.exists():
            continue
        text = f.read_text()
        names |= {n.removesuffix("_print") for n in PRINTED_VAR.findall(text)}
        if f.name.startswith("part-"):
            names |= set(PRINTED_CALL.findall(text))
    return names - {"none", "assembly"}


def mirrored_parts(project: Path) -> list[str]:
    names, found = printed_names(project), []
    for f in sorted(project.glob("*.scad")):
        for n, line in enumerate(f.read_text().splitlines(), 1):
            m = MIRROR.search(line)
            call = LAST_CALL.search(line[m.end():]) if m else None
            if call and call.group(1) in names:
                found.append(f"{f.relative_to(project.parent)}:{n}: mirror() on printed part {call.group(1)}()")
    return found


def test_no_printed_part_is_placed_by_mirror():
    found = [hit for project in sorted(PROJECTS.iterdir()) if project.is_dir() for hit in mirrored_parts(project)]
    assert not found, "turn the part over with rotate(), as a hand does; mirror() only builds shape inside a part:\n" + "\n".join(found)


def test_the_guard_sees_a_mirrored_part(tmp_path):
    (tmp_path / "part-lid.scad").write_text("use <model.scad>\nlid();\n")
    (tmp_path / "model.scad").write_text(
        'part = "box";\nmodule slab() cube(1);\nmodule lid() mirror([1, 0, 0]) slab();\n'
        "module lid_on() translate([0, 0, 9]) mirror([0, 0, 1]) color(\"red\") lid();   // in place\n")
    assert [hit.split(": ")[1] for hit in mirrored_parts(tmp_path)] == ["mirror() on printed part lid()"]


def scad_hash(project: Path) -> str:
    return hashlib.sha256(b"".join(f.read_bytes() for f in sorted(project.glob("*.scad")))).hexdigest()[:12]


# Projects that print more than one part and had no fit test on the printed meshes when this guard landed,
# each with the hash of its .scad files that day. The list only shrinks: a project leaves it when its .scad
# changes, and then needs a test that calls shop.testing.seated_overlap. Never add a line; never refresh a hash.
NOT_YET: dict[str, str] = {
    "din-rail-psu-mount": "a014823d787d",
    "gv30-lux-mount": "0b1d195b8b0b",
    "halmet-enclosure-mount": "397fbb8160a7",
    "imu-tray": "14ef6790f43b",
    "lux-capsule": "25c5a0761bce",
    "lux-sensor-mount": "3decb5a5bf5b",
    "lux-tube-cap": "0b5ac7986977",
    "outside-sensor-pod": "8ad47841620b",
    "printer-chute-transition": "1893e4b5f0b2",
    "rudder-angle-sensor": "ee0f31b75e9e",
    "small-box-sensors": "06242b1db715",
}


def test_every_multi_part_project_seats_its_printed_meshes():
    missing, stale = [], []
    for project in sorted(PROJECTS.iterdir()):
        if not project.is_dir() or not part_files(project):
            continue
        if any("seated_overlap(" in t.read_text() for t in project.glob("test_*.py")):
            if project.name in NOT_YET:
                stale.append(project.name)
            continue
        if NOT_YET.get(project.name) != scad_hash(project):
            missing.append(project.name)
    assert not stale, f"has its fit test now; drop from NOT_YET: {stale}"
    assert not missing, (
        "prints more than one part and its .scad changed, or it is new: seat the printed meshes on each other "
        f"with shop.testing.seated_overlap, in the pose they are used: {missing}")
