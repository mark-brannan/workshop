"""Preflight and heat soak for a K2 Plus job (``shop watch``).

    shop watch preflight <file.gcode> --plate frosted|pattern|smooth|epoxy --vents closed|open [--cfs] [--fix]
    shop watch soak <file.gcode> --plate ... [--over-rating] [--bed C] [--chamber C] [--bed-min 45] [--chamber-min 33]
    shop watch upload <local.gcode> [--cfs]   send a sliced file; a spool job loses its tool changes
    shop watch start <file.gcode> --plate ... --vents ... [--cfs]
    shop watch frame <layer> <out.jpg>   the camera frame after that layer, during or after a job
    shop watch next <file.gcode> --plate ... --vents ... [--cfs] [--frames DIR] [--taper-from 60] [--taper-to 70] [--no-taper]

Start re-runs preflight, re-sends the feed setting the screen undoes on idle, and starts the job.
Next blocks until the next checkpoint frame (after layers 2, 10, 50, then every 100), the job's
end or a fault, tapering speed (M220) on a tall part as it goes. Before layer 1 it restarts
Klipper and the job on a known fault, at most twice; after layer 1 it never touches the job.
Exit 0 frame ready, 3 job ended, 1 fault for the user. It never cancels a print.
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
from pathlib import Path
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
        c.append(Check("ok" if enable == 1 else "FAIL", f"CFS printing {'on' if enable == 1 else 'off'}", feed_gcode(True)))
    else:
        c.append(Check("FAIL" if enable != 0 else "ok", f"spool job, CFS printing {'off' if enable == 0 else 'on'}", feed_gcode(False)))
        if job.toolchanges:
            c.append(Check("FAIL", f"spool job but file has tool changes: {'; '.join(job.toolchanges)}; start strips them"))

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


def feed_gcode(cfs: bool) -> str:
    return "BOX_ENABLE_CFS_PRINT ENABLE=1" if cfs else "BOX_ENABLE_CFS_PRINT ENABLE=0\nSET_FILAMENT_SENSOR SENSOR=filament_sensor ENABLE=0"


def preflight(a: argparse.Namespace, fix: bool | None = None) -> int:
    job = read_job(a.file)
    if job.high_temp and (a.plate is None or a.vents is None):
        print(f"preflight: {job.material} job needs --plate and --vents; they are not guessed for it")
        return 1
    a.plate, a.vents = a.plate or "pattern", a.vents or "open"
    macros = {o.split(" ", 1)[1] for o in api("/printer/objects/list")["objects"] if o.startswith("gcode_macro ")}
    patches = read_patches()
    print(f"preflight  {a.file}")
    checks = job_checks(fetch(OBJECTS), job, a.plate, a.vents, a.cfs, macros, patches)
    fixes = [ch.fix for ch in checks if ch.level == "FAIL" and ch.fix]
    strip = bool(job.toolchanges) and not a.cfs
    if not ((a.fix if fix is None else fix) and (fixes or strip)):
        return report(checks)
    for f in fixes:
        print(f"  sent  {f.replace(chr(10), ' / ')}")
        gcode(f)
    if strip:
        restrip(a.file)
        print("  sent  tool changes stripped from the file on the printer")
        job = read_job(a.file)
    return report(job_checks(fetch(OBJECTS), job, a.plate, a.vents, a.cfs, macros, patches))


def started(st: dict, name: str) -> bool:
    ps = st["print_stats"]
    return ps["state"] == "printing" and ps.get("filename") == name


def start(a: argparse.Namespace) -> int:
    if preflight(a, fix=True):
        print("start refused: preflight failed")
        return 1
    gcode(feed_gcode(a.cfs))  # the screen turns CFS printing back on when the printer goes idle
    if int(fetch(["box"])["box"].get("enable", -1)) != int(a.cfs):
        print("start refused: CFS setting did not hold; set the screen's CFS switch and retry")
        return 1
    try:
        api("/printer/print/start?filename=" + urllib.parse.quote(a.file), {})
    except TimeoutError:  # Moonraker answers late while the start mesh runs; the poll below decides
        print("  start request timed out; checking whether it is printing")
    for _ in range(12):
        time.sleep(5)
        if started(fetch(["print_stats"]), a.file):
            print(f"start  {a.file} printing")
            return 0
    print(f"start FAIL: {a.file} not printing 60 s after start")
    return 1


TOOLCHANGE = re.compile(rb"^T\d+\b")


def spool_gcode(data: bytes) -> bytes:
    """The file without its tool-change lines: on a spool job a ``T0`` sends the feed to the CFS."""
    return b"".join(ln for ln in data.splitlines(keepends=True) if not TOOLCHANGE.match(ln))


def put(name: str, data: bytes) -> None:
    boundary = "shopwatch" + str(time.time_ns())
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{name}"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n").encode() + data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(f"{URL}/server/files/upload", data=body, headers={
        "X-Api-Key": _key(), "Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        r.read()


def restrip(name: str) -> None:
    """Strip the tool changes from the copy already on the printer."""
    req = urllib.request.Request(f"{URL}/server/files/gcodes/{urllib.parse.quote(name)}", headers={"X-Api-Key": _key()})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    put(name, spool_gcode(data))


def upload(a: argparse.Namespace) -> int:
    src = Path(a.file)
    data = src.read_bytes()
    if not a.cfs:
        data = spool_gcode(data)
    put(src.name, data)
    print(f"upload {src.name}: {len(data)} bytes" + ("" if a.cfs else ", tool changes stripped for the spool"))
    return 0


def soak(a: argparse.Namespace) -> int:
    st = fetch(OBJECTS)
    if st["print_stats"]["state"] in ("printing", "paused"):
        print("soak FAIL: a job is running")
        return 1
    bed = a.bed if a.bed is not None else read_job(a.file).bed
    rated = PLATES[a.plate]
    if rated is not None and bed > rated and not a.over_rating:
        print(f"soak FAIL: bed {bed:.0f} over the {a.plate} plate's {rated} C rating; --over-rating to accept")
        return 1
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


def frame(a: argparse.Namespace) -> int:
    # Frame n is the state after layer n-1 (printer notes, Camera); decoded on the printer, which has ffmpeg.
    src = "/mnt/UDISK/timelapse/main_output.h264"
    # rm first: a frame not yet encoded writes nothing and exits 0, and cat would send the last job's frame.
    cmd = f"rm -f /tmp/watch.jpg && ffmpeg -v error -i {src} -vf 'select=eq(n\\,{a.layer + 1})' -frames:v 1 -y /tmp/watch.jpg && cat /tmp/watch.jpg"
    r = subprocess.run([*SSH, cmd], capture_output=True, timeout=120)
    if r.returncode or not r.stdout.startswith(b"\xff\xd8"):
        print(f"frame FAIL: no frame after layer {a.layer} ({r.stderr.decode(errors='replace').strip()[-200:]})")
        return 1
    with open(a.out, "wb") as f:
        f.write(r.stdout)
    print(f"frame  after layer {a.layer} -> {a.out}")
    return 0


CHECKPOINTS = (2, 10, 50)
EVERY = 100
RECOVERABLE = ("key22", "key798", "key559", "key852")  # printer notes, Stalls and Heating
MAX_RECOVERIES = 2
WATCH_OBJECTS = ["webhooks", "print_stats", "virtual_sdcard", "gcode_move"]
KEY = re.compile(r"\bkey\d+\b")


def checkpoint_due(layer: int, done: set[int], every: int = EVERY) -> int | None:
    """The newest checkpoint whose frame exists at ``layer`` (frames trail by one), if newer than any done."""
    passed = [c for c in CHECKPOINTS if c < layer] + list(range(every, layer, every))
    latest = max(passed, default=None)
    return latest if latest is not None and latest > max(done, default=0) else None


def taper_pct(z: float, height: float, start: float = 60, end: int = 70) -> int:
    """Speed factor for a tall part: 100% up to ``start`` mm, falling linearly to ``end``% at the top."""
    if height <= start or z <= start:
        return 100
    return round(100 - (100 - end) * min(1.0, (z - start) / (height - start)))


def fault_keys(st: dict, store: list[dict], since: float) -> list[str]:
    """Creality fault codes in the state messages and the console since ``since`` (epoch)."""
    text = [st["webhooks"].get("state_message", ""), st["print_stats"].get("message", "")]
    text += [e.get("message", "") for e in store if e.get("time", 0) > since]
    return sorted({k for t in text for k in KEY.findall(t)})


def layer_of(st: dict) -> int:
    sd, info = st.get("virtual_sdcard", {}), st["print_stats"].get("info") or {}
    return int(sd.get("layer") or info.get("current_layer") or 0)


def recoverable(keys: list[str], layer: int, recoveries: int) -> bool:
    return bool(keys) and layer < 1 and recoveries < MAX_RECOVERIES and all(k in RECOVERABLE for k in keys)


def restart_klipper() -> bool:
    """Restart Klipper over ssh; True once it is ready and still ready a minute later (printer notes, key798)."""
    subprocess.run([*SSH, "/etc/init.d/klipper restart"], capture_output=True, timeout=60)
    for _ in range(2):
        for _ in range(36):
            time.sleep(5)
            try:
                if fetch(["webhooks"])["webhooks"]["state"] == "ready":
                    break
            except OSError:
                pass
        else:
            return False
        time.sleep(60)
    return fetch(["webhooks"])["webhooks"]["state"] == "ready"


def running_file() -> str | None:
    ps = fetch(["print_stats"])["print_stats"]
    return ps.get("filename") if ps["state"] in ("printing", "paused") and ps.get("filename") else None


def next_(a: argparse.Namespace) -> int:
    a.file = running_file()
    if a.file is None:
        print("watch FAULT: no job is printing")
        return 1
    print(f"watching {a.file}")
    frames = Path(a.frames or Path.home() / ".local/state/print-watch" / Path(a.file).stem)
    frames.mkdir(parents=True, exist_ok=True)
    done = {int(f.stem.split("-")[1]) for f in frames.glob("layer-*.jpg")}
    rec_file = frames / "recoveries"
    recoveries = int(rec_file.read_text()) if rec_file.exists() else 0
    height = read_job(a.file).height
    since, sent, stall, misses, last = None, None, (None, time.monotonic()), 0, 0
    while True:
        try:
            st = fetch(WATCH_OBJECTS)
            store = api("/server/gcode_store?count=100")["gcode_store"]
        except OSError as e:
            misses += 1
            if misses >= 10:
                print(f"watch FAULT: printer unreachable for {misses} polls ({e})")
                return 1
            time.sleep(a.poll)
            continue
        misses = 0
        if since is None:  # the printer's clock, not ours: only console lines after this call count
            since = max((e.get("time", 0) for e in store), default=0)
        ps, layer = st["print_stats"], layer_of(st)
        last = max(layer, last)  # the printer zeroes the layer on completion
        if ps.get("filename") and ps["filename"] != a.file:
            print(f"watch FAULT: the printer is on {ps['filename']}, not {a.file}")
            return 1
        keys = fault_keys(st, store, since)
        dead = st["webhooks"]["state"] != "ready" or ps["state"] in ("error", "paused", "cancelled")
        pos = st["virtual_sdcard"].get("file_position")
        if pos != stall[0]:
            stall = (pos, time.monotonic())
        stalled = layer < 1 and ps["state"] == "printing" and time.monotonic() - stall[1] > a.stall_min * 60
        if keys or dead or stalled:
            why = ", ".join(keys) or (f"stalled {a.stall_min:.0f} min before layer 1" if stalled else f"Klipper {st['webhooks']['state']}, job {ps['state']}")
            if not recoverable(keys, layer, recoveries):
                print(f"watch FAULT at layer {layer}: {why}; {st['webhooks'].get('state_message', '').strip()[:160]}")
                return 1
            if a.plate is None or a.vents is None:
                print(f"watch FAULT at layer {layer}: {why}; a restart needs --plate and --vents, none given; touching nothing")
                return 1
            recoveries += 1
            rec_file.write_text(str(recoveries))
            print(f"watch RECOVER {recoveries}/{MAX_RECOVERIES}: {why} before layer 1; restarting Klipper and the job", flush=True)
            if not restart_klipper():
                print("watch FAULT: Klipper not ready after restart")
                return 1
            if start(a):
                print("watch FAULT: job did not restart")
                return 1
            since, sent, stall = None, None, (None, time.monotonic())
            continue
        if ps["state"] == "complete" or (ps["state"] == "standby" and not ps.get("filename")):
            print(f"watch DONE: job {ps['state']} at layer {last}")
            return 3
        if a.taper and ps["state"] == "printing":
            pct = taper_pct(st["gcode_move"]["gcode_position"][2], height, a.taper_from, a.taper_to)
            if pct != round(st["gcode_move"]["speed_factor"] * 100) and pct != sent:
                gcode(f"M220 S{pct}")
                sent = pct
                print(f"  taper  Z {st['gcode_move']['gcode_position'][2]:.1f} of {height:.1f}: speed {pct}%", flush=True)
        c = checkpoint_due(layer, done)
        if c is not None:
            out = frames / f"layer-{c:04d}.jpg"
            if frame(argparse.Namespace(layer=c, out=str(out))) == 0:
                print(f"watch CHECKPOINT layer {c} of {st['virtual_sdcard'].get('layer_count', '?')}: {out}")
                return 0
        time.sleep(a.poll)


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="shop watch")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("preflight", "start", "next"):
        pf = sub.add_parser(name)
        watching = name == "next"  # a running job needs them only for a pre-layer-1 restart
        if not watching:  # next watches whatever is printing
            pf.add_argument("file")
        pf.add_argument("--plate", choices=PLATES, help="default for a PETG job: pattern; required for ASA/ABS")
        pf.add_argument("--vents", choices=("closed", "open"), help="default for a PETG job: open; required for ASA/ABS")
        pf.add_argument("--cfs", action="store_true", help="feed from the CFS; default is the spool")
        pf.add_argument("--fix", action="store_true", help="send the fixes the failed checks name, then re-check")
        if name == "next":
            pf.add_argument("--frames", help="where frames go; default ~/.local/state/print-watch/<file stem>")
            pf.add_argument("--no-taper", dest="taper", action="store_false")
            pf.add_argument("--taper-from", type=float, default=60, help="mm where the speed taper starts")
            pf.add_argument("--taper-to", type=int, default=70, help="speed %% at the part's top")
            pf.add_argument("--poll", type=float, default=30)
            pf.add_argument("--stall-min", type=float, default=20, help="minutes at one file position before layer 1")
    sk = sub.add_parser("soak")
    sk.add_argument("file")
    sk.add_argument("--plate", required=True, choices=PLATES)
    sk.add_argument("--over-rating", action="store_true", help="accept a bed above the plate's rating")
    sk.add_argument("--bed", type=float, help="default: the file's first-layer bed temperature")
    sk.add_argument("--chamber", type=float, default=50)
    sk.add_argument("--bed-min", type=float, default=45)
    sk.add_argument("--chamber-min", type=float, default=33)
    sk.add_argument("--poll", type=float, default=30)
    up = sub.add_parser("upload")
    up.add_argument("file")
    up.add_argument("--cfs", action="store_true", help="keep tool changes for a CFS job")
    fr = sub.add_parser("frame")
    fr.add_argument("layer", type=int)
    fr.add_argument("out")
    a = p.parse_args(argv)
    return {"preflight": preflight, "upload": upload, "start": start, "soak": soak, "frame": frame, "next": next_}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
