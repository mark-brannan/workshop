# K2 Plus printer notes

Facts about the machine we will need again. Each row says how it was learned.
Source of truth for names in `shop printer` (`src/shop/printer.py`). Add new
findings here, dated.

Moonraker: `http://192.168.0.190:4408`, key in `K2PLUS_API_KEY`. If a call fails
with "No route to host" while ping works, retry once (stale ARP entry, 2026-11-14).

## Fans (checked 2026-11-14)

Each fan was run alone with `M106 P<n> S255` on the idle printer; the user said
where the sound came from.

| Name | `M106` | Klipper pin | Where | Tach channel in `fan_feedback` |
|---|---|---|---|---|
| part | P0 | `output_pin fan0` (toolhead board PB15) | toolhead, part cooling | `fan2_speed` (16000 alone) |
| chamber | P1 | `output_pin fan1` (main board PA0) | rear, ventilates the chamber | none read |
| aux | P2 | `output_pin fan2` (main board PB4+PB3) | sides, model cooling | none read |
| hotend | automatic | `heater_fan hotend_fan` (toolhead PB7+PB1) | hotend heat sink, on above 50 C | `fan1_speed` (16000, then 12000) |

- Tach channel numbers do not follow fan numbers. Part is on `fan2_speed`, hotend on `fan1_speed`.
- `fan0_speed`, `fan3_speed`, `fan4_speed` never read nonzero in any test. The config defines tach pins for fan0..fan2 only, so fan3 and fan4 are probably unused (inference).
- fan1 shares pin PA0 with `temperature_fan chamber_fan` (thermostat, target 35 C), so its duty can change on its own.
- Not yet identified or shown by the tool: `heater_fan chamber_fan` (chamber PTC heater fan, runs with the chamber heater; untested because that heater drew no power on 2026-11-12) and `output_pin extruder_fan` (spun 6 s, no tach on any channel; whether it turned is unknown).
- `SET_PIN PIN=fan0` also sets `fan0_en`. `M106` rescales by per-fan minimums (fan0 25, fan1 50, fan2 100 of 255).

## Heating

- Nozzle commanded to 60 C reached 75 C in about 12 s (overshoot, idle, no filament).
- Rear recirculation vents are a manual mod with no sensor: open is normal, closed keeps heat in. Log their state by asking (user, 2026-11-14).
- Chamber heater waits for the bed: with both on, the chamber heater stays at 0% until bed power drops below ~97%, i.e. the bed is near target (2026-11-15 log).
- `temperature_fan chamber_fan` (rear exhaust, target 35 C) runs at 100% once the chamber passes 35 C, during a chamber heat-up too (2026-11-15 log), when the heater is set with `SET_HEATER_TEMPERATURE`. `M141 S<n>` above 40 sets that fan's target to 0, which this firmware treats as off (probe at 13 C, 2026-11-16); above 35 C unconfirmed.
- A long gcode call over Moonraker returns HTTP 504 while Klipper carries on; do not retry it. Gcode sent while a macro waits is queued behind it, heater-off commands included; `/printer/emergency_stop` is the only thing that cut through (firmware_restart and restart requests timed out), and Klipper returned to ready by itself afterwards (2026-11-16).
- Cold start in a 12 C room, vents closed, rear fan off: bed 100 C at 53 min, chamber 50 C at 88 min, 55 C not reached in 40 min of chamber heating (2026-11-16).
- Mains: 110 V; 240 V split phase is available in the shop. Whether this unit accepts 240 V is unread (rating plate) (user, 2026-11-16).
- Fault codes: `key565` bed, `key559` chamber heater, `key564` nozzle, `key558` other heater "not heating at expected rate"; `key519` chamber heater fan reads 0, heater turned off. The screen shows two letters plus 2000 + key, so the bed fault would read as `..2565` (inference). `[verify_heater chamber_heater]` has `check_gain_time: 345600`, so its rate check cannot fire in practice; the bed's is 120 s (read on the printer, 2026-11-16).
- Error history lives in `/mnt/UDISK/creality/userdata/log` (master-server and display-server, back to 17 Sep 2026; app-server to Dec 2025). The printer's BusyBox has no sftp: copy with `ssh ... tar cf -`, and search on the Mac, not on the printer (2026-11-16).
- Bed fault line: `verify_heater heater_bed` needs 1 C gain per 120 s while more than 10 C below target. In a 15-16 C room the bed manages that up to about 100 C (curve fit) and plateaus near 109-110 C. Keep ABS/ASA bed targets at 100 C or below until the room is warmer or the bed's wall power is measured (2026-11-16).
