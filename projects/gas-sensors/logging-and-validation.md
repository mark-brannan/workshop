# Logging and validation

What to log from the BME688 and the heated sensors, which features survive, and
how to tell whether a detection method works. Read this before designing a
feature, a train/test split or a log format.

The short version: log the raw readings and everything about the device that
took them; compute later; never judge a method on a random split of rows.

## Features

| Use | Avoid |
|---|---|
| Ratios and differences between heater steps within one scan | Absolute resistance |
| Log-resistance | Library-computed "equivalent ppm" values |
| The slope across the heater profile | |
| Change from one scan to the next | |
| This unit's deviation from its own recent normal | Comparison against another unit's values |

Ratios within a scan cancel the unit's own gain and its slow drift, which is
why they survive. Absolute resistance is the worst feature available.

Feed in temperature, humidity and pressure only where they physically drive
the thing being detected, not because they happen to correlate in the data.
Absolute humidity (from temperature and relative humidity) is what a MOX film
responds to. Derive it downstream, not in firmware.

## Collecting data

- The commonest mistake is to record condition A on one day and condition B on
  another. The model learns the day. Mix conditions within a session and
  randomize the order.
- Use more than one unit and more than one day.
- If a condition goes with the day's humidity, the model learns humidity.

## Validation (Settled)

- **Leave one device out, or leave one session out. Nothing else is valid.** A
  random split of rows reports accuracy that does not exist.
- Rows are not independent. The unit of analysis is one device over one
  stretch of time, not one scan. Every split and every statistic works at that
  level.
- Anything worth holding out is a column: device, location, firmware version,
  heater profile, cumulative heater-seconds. Store them, or they cannot be
  rebuilt.

## Store raw, derive later (Settled)

Store the raw ADC values and the part's calibration coefficients, not
compensated values. The compensation maths has changed between driver
versions, the coefficients are what normalizes one unit against another, and
raw-to-compensated cannot be undone.

Compute nothing on the node that can be computed later. Do not average on the
node: an hourly mean destroys the shape of the transient, and the shape is
the information.

### One scan's record

| Scope | Fields |
|---|---|
| Per heater step | Raw gas ADC and range; raw temperature, pressure, humidity ADC; `gas_valid`, `heat_stab`; step index |
| Per scan | Sequence number; uptime; wall-clock time with a `clock_synced` flag; heater profile ID |
| Per boot | Boot ID; power-cycle count; firmware and driver versions; **cumulative heater-seconds** |
| Per device, once | Device UUID; chip and variant ID; the full calibration blob |
| Per profile | The ordered (temperature, duration) list; mode; oversampling and filter settings |

Mark a bad heater step; never drop it.

Cumulative heater-seconds is the sensor's age. Drift follows hours of heating,
not the calendar. It is the field most often forgotten.

Write an explicit record for a gap. A missing row otherwise cannot be told
apart from "device off", "log lost" and "sensor faulted".

### Volume

A 10-step scan about every 10.8 s is about 8,000 scans a day. At about 110
bytes a record that is about 0.9 MB per device per day, uncompressed. Storage
is no constraint.

### Layers

| Layer | Holds | Rule |
|---|---|---|
| Raw | Frames as received, append-only | Never rewritten |
| Normalized | One row per scan; step resistances as a fixed-length list keyed by profile ID | Rebuildable from raw |
| Features | Ratios, deltas, rolling baselines per device | Versioned, disposable, recomputable |

Ingest is idempotent on (device UUID, boot ID, sequence number). The file
format is a free choice.

## Two heater steps that never change (Settled)

Reserve two heater steps as fixed: the same temperature and duration in every
profile, on every device, for good. The other steps can be tuned freely. This
keeps data comparable across devices, profiles and firmware versions. Without
it, a change of profile orphans everything logged before.

## Open: raw scans or the library's output

One July note has the node run Bosch's BSEC2 library and publish its scaled
air-quality value as the `voc` channel's `raw`. This file says to store raw
scans and derive everything else. The two agree only if raw scans are logged
alongside whatever the library publishes. Not decided.
