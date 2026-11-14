"""Read-only status of the Creality K2 Plus over Moonraker (``shop printer``)."""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

URL = os.environ.get("K2PLUS_URL", "http://192.168.0.190:4408")
KEY_FILE = Path.home() / ".config/secrets/k2plus_api_key.env"
OBJECTS = [
    "webhooks",
    "print_stats",
    "virtual_sdcard",
    "extruder",
    "heater_bed",
    "temperature_sensor chamber_temp",
    "heater_generic chamber_heater",
    "toolhead",
    "filament_switch_sensor filament_sensor",
    "output_pin fan0",
    "output_pin fan1",
    "output_pin fan2",
    "fan_feedback",
    "heater_fan hotend_fan",
]


FANS = ["part", "chamber", "aux"]  # fan0..fan2: toolhead, rear chamber vents, side model cooling
# Tach channel per fan, measured by running each fan alone (2026-11-14). Only the part fan
# reports one (on fan2_speed); chamber and aux gave 0 on every channel at full speed.
# The hotend fan reads on fan1_speed (nozzle at 75 C). fan0, fan3, fan4 never read nonzero.
TACH = {"part": "fan2_speed", "hotend": "fan1_speed"}


def _key() -> str:
    if os.environ.get("K2PLUS_API_KEY"):
        return os.environ["K2PLUS_API_KEY"]
    for line in KEY_FILE.read_text().splitlines():
        if line.startswith("K2PLUS_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"K2PLUS_API_KEY not in the environment or {KEY_FILE}")


def fetch() -> dict:
    query = "&".join(urllib.parse.quote(o) for o in OBJECTS)
    req = urllib.request.Request(f"{URL}/printer/objects/query?{query}", headers={"X-Api-Key": _key()})
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.load(r)["result"]["status"]


def _hm(seconds: float) -> str:
    m = int(seconds // 60)
    return f"{m // 60}h{m % 60:02d}m"


def _temp(o: dict) -> str:
    return f"{o['temperature']:.1f} / {o['target']:.0f} C"


def format_status(s: dict) -> str:
    ps, sd = s["print_stats"], s.get("virtual_sdcard", {})
    meta = sd.get("cur_print_data", {}).get("metadata", {})
    lines = [
        f"printer  {s['webhooks']['state']}",
        f"job      {ps['state']}  {ps['filename'] or '-'}",
    ]
    if ps["filename"]:
        done = ps["print_duration"]
        est = meta.get("estimated_time")
        lines.append(
            f"progress {sd.get('progress', 0) * 100:.0f}%  layer {sd.get('layer', 0)}/{sd.get('layer_count', '?')}"
            f"  {_hm(done)}" + (f" of ~{_hm(est)}" if est else "")
        )
        if meta:
            lines.append(
                f"slicer   {meta.get('filament_type', '?')}  {meta.get('layer_height', '?')} mm layers"
                f"  {meta.get('filament_weight_total', '?')} g  height {meta.get('object_height', '?')} mm"
            )
    lines.append(f"nozzle   {_temp(s['extruder'])}  ({s['extruder']['nozzle_diameter']} mm)")
    lines.append(f"bed      {_temp(s['heater_bed'])}")
    ch = s.get("heater_generic chamber_heater") or {}
    sensor = s.get("temperature_sensor chamber_temp") or {}
    if sensor:
        lines.append(f"chamber  {sensor['temperature']:.1f} C  target {ch.get('target', 0):.0f}  heater {ch.get('power', 0) * 100:.0f}%")
    pos = s["toolhead"]["position"]
    lines.append(f"toolhead x{pos[0]:.1f} y{pos[1]:.1f} z{pos[2]:.2f}  homed {s['toolhead']['homed_axes'] or 'none'}")
    pins = [s.get(f"output_pin fan{i}") for i in range(3)]
    if all(pins):
        tach = s.get("fan_feedback", {})
        lines.append(
            "fans     "
            + "  ".join(f"{FANS[i]} {p['value'] * 100:.0f}%" + (f" ({tach.get(TACH[FANS[i]], '?')} tach)" if FANS[i] in TACH else "") for i, p in enumerate(pins))
            + f"  hotend {s.get('heater_fan hotend_fan', {}).get('speed', 0) * 100:.0f}% ({tach.get(TACH['hotend'], '?')} tach)"
        )
    fs = s.get("filament_switch_sensor filament_sensor")
    if fs:
        lines.append(f"filament {'detected' if fs['filament_detected'] else 'NONE'}")
    return "\n".join(lines)


def main() -> int:
    print(format_status(fetch()))
    return 0
