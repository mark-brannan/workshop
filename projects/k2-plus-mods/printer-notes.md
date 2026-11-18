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
- A chamber target can come from the touchscreen, not the file: before the PETG gauge job the screen sent `M141 S50` (master-server log, 23:55:01 printer time, 2026-11-17), and the 50 C target heated the chamber through the whole start routine. The file's own `M191 S35` turns the heater off, but only after the screen's prep (home, probe, nozzle clean) finishes. Gcode sent during that prep, `M141 S0` included, waits behind it (2026-11-18).
- Bed fault line: `verify_heater heater_bed` needs 1 C gain per 120 s while more than 10 C below target. In a 15-16 C room the bed manages that up to about 100 C (curve fit) and plateaus near 109-110 C. Keep ABS/ASA bed targets at 100 C or below until the room is warmer or the bed's wall power is measured (2026-11-16).

## Stalls

- Start-of-print homing failed with `key22` "No trigger on y after full movement". The job then sat in `printing` at file position 0 with the start macro dead. `CANCEL_PRINT` ran its end macro but left the job in `printing`. `emergency_stop` put Klipper in shutdown, and this time it stayed there. `firmware_restart` over Moonraker timed out. What cleared it: `ssh root@192.168.0.190 /etc/init.d/klipper restart`, ready in under a minute. The first `G28` after that answers "motor parameters are initializing", so retry it about 20 s later. Then X, Y and Z homed normally (Y in ~5 s), so the fault was the motor state, not the mechanics (2026-11-17).
- Right after that fix, the same job paused before layer 1 on `key836` "extrude error, maybe there's a blockage between the connections and the filament sensor" (values `[1, "A"]`, so CFS 1 slot A), and `filament_switch_sensor` read no filament. A feed problem between the CFS and the toolhead, separate from the homing fault (2026-11-17).
- Remote feed work on that `key836` (2026-11-17). The CFS latches its own fault (`EXTRUDE_ERR8` in klippy.log every ~4 s), and while latched every `BOX_*` feed command returns ok and does nothing. `BOX_ERROR_CLEAR` clears it. After the clear, `BOX_EXTRUDE_MATERIAL TNN=T1A` (nozzle hot) is the call that really feeds; `BOX_QUIT_MATERIAL` cuts and retracts. 250 mm of `G1 E` purge brought out only white: the old white strand was still in the toolhead. After `BOX_QUIT_MATERIAL` pulled it, a 1A load still hit `key836` and the toolhead sensor read none, so black never reaches the toolhead. The block is between the CFS hub and the toolhead (unconfirmed). The toolhead `filament_switch_sensor` reports `enabled: False`.
- Air print (2026-11-17): `halmet-enclosure-mount` PETG ran 05:41-07:15 and reported `complete`, but no plastic came out (user). Klipper log: the CFS fault `EXTRUDE_ERR8` had been latched since 04:31 and stayed latched the whole job; the toolhead `filament_sensor` read false at 05:52 and nothing paused, because that sensor is `enabled: False`. The nozzle held 245-260 C under load throughout, so the heater is not the cause. Same block as the `key836` entry above. `BOX_ERROR_CLEAR` at 12:51 cleared the latch (no `EXTRUDE_ERR8` after it).
- Screen load, 15:32-15:44 (2026-11-17): T1A at 250 C, started from the screen (no job in history). Each try, the CFS hub sensor (`Tn_inner_data[T1][filament_sensor][connections]`) read 1, so the filament reached the hub. The CFS then fed for about 8 s, the toolhead `filament_sensor` stayed false, and the firmware retried. After four tries it raised `key836` (values `[1, "A"]`). A reboot at 15:40 changed nothing. `EXTRUDE_ERR8` stayed latched from 15:44 until `BOX_ERROR_CLEAR` at 20:43.
- The toolhead sensor works: it read true during loads on 12, 13, 14 and 16 Nov, and on the 17th at 04:49-05:15 (the white strand). Since `BOX_QUIT_MATERIAL` at 05:15 it has never read true. So the filament gets past the hub but stops before the toolhead sensor: in the hub-to-toolhead tube or in the toolhead inlet above the sensor (inference).
- Tier-gauge PETG print (2026-11-17 20:53): the feed failed the same way, with `key836` at 21:14. After `BOX_ERROR_CLEAR` I sent one `BOX_EXTRUDE_MATERIAL TNN=T1A`, and it failed the same way (21:16). The job was left paused, heaters on.
- Startup timing from that print's klippy.log, room 12 C. It took 20 min from start to the first feed. Home and nozzle to 140: 0.3 min. Bed 19 to 50 C: 4.9 min. Silent, nothing logged: 3.8 min. Nozzle clean: 1.0 min. Z probe and full mesh: 1.4 min. Bed 50 to 70 C: 3.8 min. Silent again before the T0 load: 4.1 min. The mesh is about 1 min of the 20. The two silent gaps (8 min) and the bed heating (9 min) are the time.
- Correction to the row above (2026-11-17, read from klippy.log heater stats and the macros): the two "silent" gaps are the bed still heating. Klipper logs "within range" for the bed 10 C short of target (`[verify_heater heater_bed]` `hysteresis: 10`), so the 4.9 and 3.8 min "bed" times ended at 40 and 60 C, not 50 and 70. In gap 1 the bed went 40 to 48 C; in gap 2, 60 to 68 C. Above about 44 C the PID cuts bed power to 63-90%, so those last degrees are slow. The bed heats 13 to 70 C in about 17 of the 20 min.
- Where the 50 C stop comes from: a print started with auto-levelling makes `virtual_sdcard` run `BED_MESH_CALIBRATE_START_PRINT` before the file's first line. That macro heats the bed with `M190` and meshes at `[custom_macro] default_bed_temp: 50` (in `printer_params.cfg`), or at the bed's current target if that is higher. The file's own `M140 S70` comes later, in `START_PRINT`, so a cold start always meshes at 50 and then heats to 70. The slicer's `M191 S35` waits on nothing: below 40 C it sets the chamber fan target, and the heater target stays 0.
- What a change saves (estimated from this print's heating curve): setting the bed to 70 before the print starts (`M140 S70`) makes the mesh run at 70 instead, with one heat-up instead of two. That saves about 1 min of the 20, and the mesh is taken at print temperature. Only heating the bed earlier, before the job starts, saves real time.
- Changed 2026-11-17: `BED_MESH_CALIBRATE_START_PRINT` in `gcode_macro.cfg` now meshes at the job's first-layer bed temperature (`printer.virtual_sdcard.cur_print_data.metadata.first_layer_bed_temp`) when that is above 50 C. Original kept as `gcode_macro.cfg.bak-20261117`. Undo: copy it back and `RESTART`.
- Forced-feed attempts (2026-11-17 22:36-22:38). The user saw the 1A filament stop 4-6 in short of the extruder, with nothing blocking the tube or the toolhead inlet, so the CFS stops pushing early. `BOX_TN_EXTRUDE` drives only the toolhead extruder (140 mm at 360, from `box.cfg` `Tn_extrude`) and ignores `TNN` and `LENGTH`. `BOX_CTRL_CONNECTION_MOTOR_ACTION ADDR=1` raised `key60` internal error and put Klipper in shutdown, which lost the paused job; it needs more parameters than `ADDR` (unknown which). Recovered with `/etc/init.d/klipper restart`.
