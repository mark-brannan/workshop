"""Preflight and heat soak for a K2 Plus job (``shop watch``).

    shop watch preflight <file.gcode> --plate frosted|pattern|smooth|epoxy --vents closed|open [--cfs] [--fix]
    shop watch soak <file.gcode> [--bed C] [--chamber C] [--bed-min 45] [--chamber-min 33]

Preflight reads only, unless ``--fix`` sends the fixes it names. Soak sends one ``HEAT_HOLD``
and never another, so the macro's own off-timer bounds an unattended soak. Exit 0 pass, 1 fail.
Why each check exists: projects/k2-plus-mods/printer-notes.md.
"""

from __future__ import annotations

import argparse
import re
import shlex
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

from .printer import URL, _key, api, fetch

SAFE_Z = 10.0
HIGH_TEMP = ("ASA", "ABS")
PLATES = {"frosted": 120, "smooth": 120, "pattern": 80, "epoxy": None}  # rated bed C; printer notes, Build plates
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", "root@192.168.0.190"]
CONFIG = "/mnt/UDISK/printer_data/config"
# A firmware update resets these; each marker is a string the patched file holds (printer notes, Stalls).
PATCHES = {
    "chamber check re-arms (verify_heater.py)": ("/usr/share/klipper/klippy/extras/verify_heater.py", "last_target = 0"),
    "pre-home Z lift (sensorless.cfg)": (f"{CONFIG}/sensorless.cfg", "filament_used|float == 0"),
    "heat-hold hook in END_PRINT": (f"{CONFIG}/gcode_macro.cfg", "_HEAT_HOLD_SAVE"),
    "start mesh at job bed temp": (f"{CONFIG}/gcode_macro.cfg", "first_layer_bed_temp"),
}
MACROS = ("HEAT_HOLD", "BED_VIEW")
OBJECTS = [
    "webhooks",
    "print_stats",
    "toolhead",
    "heater_bed",
    "heater_generic chamber_heater",
    "temperature_sensor chamber_temp",
    "box",
    "gcode_macro _HEAT_HOLD_VARS",
]


@dataclass
class Check:
    level: str  # ok, WARN, FAIL
    text: str
    fix: str = ""  # gcode that clears a FAIL


@dataclass
class Job:
    file: str
    material: str
    bed: float
    height: float
    toolchanges: list[str] = field(default_factory=list)

    @property
    def high_temp(self) -> bool:
        return self.material.upper()[:3] in HIGH_TEMP


def job_checks(st: dict, job: Job, plate: str, vents: str, cfs: bool, macros: set[str], patches: dict[str, int] | None) -> list[Check]:
    c: list[Check] = []
    web, ps = st["webhooks"]["state"], st["print_stats"]["state"]
    busy = ps in ("printing", "paused")
    c.append(Check("FAIL" if web != "ready" or busy else "ok", f"printer {web}, job {ps}"))
    c.append(Check("ok", f"file {job.material}, bed {job.bed:.0f}, height {job.height:.1f} mm"))

    th = st["toolhead"]
    z = th["position"][2]
    if "z" not in th["homed_axes"]:
        c.append(Check("WARN", "Z unhomed: bed position unknown; the job's start lowers the bed before XY homing"))
    elif z < SAFE_Z:
        c.append(Check("FAIL", f"Z {z:.2f} below {SAFE_Z:.0f}: homing XY here drags the nozzle", f"G90\nG1 Z{SAFE_Z:.0f} F600\nM400"))
    else:
        c.append(Check("ok", f"Z {z:.1f}"))

    rated = PLATES[plate]
    if rated is None:
        c.append(Check("WARN", f"plate {plate}: no bed rating known, bed {job.bed:.0f}"))
    else:
        c.append(Check("FAIL" if job.bed > rated else "ok", f"plate {plate} rated {rated} C, bed {job.bed:.0f}"))
    if job.high_temp and job.bed > 100:
        c.append(Check("WARN", f"bed {job.bed:.0f} over 100: verify_heater may fault in a cold room"))
    c.append(Check("FAIL" if job.high_temp and vents != "closed" else "ok", f"rear vents {vents}"))

    enable = int(st.get("box", {}).get("enable", -1))
    if cfs:
        c.append(Check("ok" if enable == 1 else "FAIL", f"CFS printing {'on' if enable == 1 else 'off'}", "BOX_ENABLE_CFS_PRINT ENABLE=1"))
    else:
        fix = "BOX_ENABLE_CFS_PRINT ENABLE=0\nSET_FILAMENT_SENSOR SENSOR=filament_sensor ENABLE=0"
        c.append(Check("FAIL" if enable != 0 else "ok", f"spool job, CFS printing {'off' if enable == 0 else 'on'}", fix))
        if job.toolchanges:
            c.append(Check("FAIL", f"spool job but file has tool changes: {'; '.join(job.toolchanges)}"))

    for m in MACROS:
        c.append(Check("ok" if m in macros else "FAIL", f"macro {m}" + ("" if m in macros else " missing: re-copy its .cfg")))
    if patches is None:
        c.append(Check("WARN", "patches unread: ssh to the printer failed"))
    else:
        for name, n in patches.items():
            c.append(Check("ok" if n else "FAIL", f"patch: {name}" + ("" if n else " missing; re-apply")))
    return c


@dataclass
class Soak:
    """Pass once the bed has held target for ``bed_min`` minutes and the chamber is warm."""

    bed: float
    chamber: float
    deadline_s: float
    bed_min: float = 45
    chamber_min: float = 33
    band: float = 2
    since: float | None = None

    def held_min(self, t: float) -> float:
        return 0.0 if self.since is None else (t - self.since) / 60

    def update(self, t: float, st: dict) -> str:
        """Return '' while soaking, 'PASS', or 'FAIL: <why>'."""
        web = st["webhooks"]
        if web["state"] != "ready":
            return f"FAIL: Klipper {web['state']}: {web.get('state_message', '').strip()[:120]}"
        if st["print_stats"]["state"] in ("printing", "paused"):
            return "FAIL: a job started during the soak"
        bed, ch = st["heater_bed"], st["heater_generic chamber_heater"]
        if bed["target"] < self.bed - 0.5 or ch["target"] < self.chamber - 0.5:
            return f"FAIL: targets dropped to bed {bed['target']:.0f}, chamber {ch['target']:.0f} (hold ended or heaters off)"
        if bed["temperature"] >= self.bed - self.band:
            self.since = t if self.since is None else self.since
        else:
            self.since = None
        chamber = st["temperature_sensor chamber_temp"]["temperature"]
        if self.held_min(t) >= self.bed_min and chamber >= self.chamber_min:
            return "PASS"
        if t >= self.deadline_s:
            return f"FAIL: not soaked before the hold ends (bed {self.held_min(t):.0f} min at target, chamber {chamber:.1f} C)"
        return ""


def gcode(script: str) -> None:
    api("/printer/gcode/script", {"script": script}, timeout=60)


def read_job(name: str) -> Job:
    meta = api("/server/files/metadata?filename=" + urllib.parse.quote(name))
    req = urllib.request.Request(f"{URL}/server/files/gcodes/{urllib.parse.quote(name)}", headers={"X-Api-Key": _key()})
    tool = re.compile(rb"^T\d+\b")
    changes = []
    with urllib.request.urlopen(req, timeout=30) as r:
        for n, line in enumerate(r, 1):
            if tool.match(line) and len(changes) < 3:
                changes.append(f"line {n} {line.decode(errors='replace').strip()}")
    return Job(name, meta.get("filament_type", "?"), float(meta.get("first_layer_bed_temp", 0)), float(meta.get("object_height", 0)), changes)


def read_patches() -> dict[str, int] | None:
    cmd = "; ".join(f"echo $(grep -cF -- {shlex.quote(m)} {shlex.quote(f)} 2>/dev/null)" for f, m in PATCHES.values())
    try:
        out = subprocess.run([*SSH, cmd], capture_output=True, text=True, timeout=30, check=True).stdout.split("\n")
    except (OSError, subprocess.SubprocessError):
        return None
    return {name: int(v or 0) for name, v in zip(PATCHES, out)}


def report(checks: list[Check]) -> int:
    for ch in checks:
        print(f"  {ch.level:4s}  {ch.text}" + (f"   fix: {ch.fix.splitlines()[0]}..." if ch.level == "FAIL" and ch.fix else ""))
    fails = sum(ch.level == "FAIL" for ch in checks)
    print(f"preflight {'FAIL (' + str(fails) + ')' if fails else 'PASS'}")
    return 1 if fails else 0


def preflight(a: argparse.Namespace) -> int:
    job = read_job(a.file)
    macros = {o.split(" ", 1)[1] for o in api("/printer/objects/list")["objects"] if o.startswith("gcode_macro ")}
    patches = read_patches()
    print(f"preflight  {a.file}")
    checks = job_checks(fetch(OBJECTS), job, a.plate, a.vents, a.cfs, macros, patches)
    fixes = [ch.fix for ch in checks if ch.level == "FAIL" and ch.fix]
    if not (a.fix and fixes):
        return report(checks)
    for f in fixes:
        print(f"  sent  {f.replace(chr(10), ' / ')}")
        gcode(f)
    return report(job_checks(fetch(OBJECTS), job, a.plate, a.vents, a.cfs, macros, patches))


def soak(a: argparse.Namespace) -> int:
    st = fetch(OBJECTS)
    if st["print_stats"]["state"] in ("printing", "paused"):
        print("soak FAIL: a job is running")
        return 1
    bed = a.bed if a.bed is not None else read_job(a.file).bed
    hold = int(st["gcode_macro _HEAT_HOLD_VARS"]["hold_min"])
    s = Soak(bed, a.chamber, (hold - 10) * 60, a.bed_min, a.chamber_min)
    print(f"soak  bed {bed:.0f}  chamber {a.chamber:.0f}  hold {hold} min  pass: bed {a.bed_min:.0f} min at target, chamber >= {a.chamber_min:.0f} C", flush=True)
    gcode(f"HEAT_HOLD BED={bed:.0f} CHAMBER={a.chamber:.0f}")
    t0, last = time.monotonic(), -1
    while True:
        time.sleep(a.poll)
        t = time.monotonic() - t0
        st = fetch(OBJECTS)
        verdict = s.update(t, st)
        if verdict or int(t // 300) != last:
            last = int(t // 300)
            b, ch = st["heater_bed"], st["temperature_sensor chamber_temp"]
            print(f"  {t / 60:4.0f}m  bed {b['temperature']:.1f}/{b['target']:.0f}  chamber {ch['temperature']:.1f}  at target {s.held_min(t):.0f}m", flush=True)
        if verdict:
            print(f"soak {verdict} at {t / 60:.0f}m", flush=True)
            return 0 if verdict == "PASS" else 1


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="shop watch")
    sub = p.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("preflight")
    pf.add_argument("file")
    pf.add_argument("--plate", required=True, choices=PLATES)
    pf.add_argument("--vents", required=True, choices=("closed", "open"))
    pf.add_argument("--cfs", action="store_true", help="feed from the CFS; default is the spool")
    pf.add_argument("--fix", action="store_true", help="send the fixes the failed checks name, then re-check")
    sk = sub.add_parser("soak")
    sk.add_argument("file")
    sk.add_argument("--bed", type=float, help="default: the file's first-layer bed temperature")
    sk.add_argument("--chamber", type=float, default=50)
    sk.add_argument("--bed-min", type=float, default=45)
    sk.add_argument("--chamber-min", type=float, default=33)
    sk.add_argument("--poll", type=float, default=30)
    a = p.parse_args(argv)
    return preflight(a) if a.cmd == "preflight" else soak(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
