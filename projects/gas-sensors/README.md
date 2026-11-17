# Gas sensors

An air monitor for the boat. It watches three enclosed spaces and says
"something changed in here, go and look": a fuel line starting to weep, an
exhaust joint letting go, a battery locker that smells different from last week.

It reports change against each space's own normal. It does not report
concentrations, and it switches nothing.

Nothing is built yet. This folder is the reference the build starts from.

## What is in here

| File | Read it when |
|---|---|
| [gases.md](gases.md) | Asking "what could be in the air aboard, and what can sense it at all?" |
| [sensors.md](sensors.md) | Choosing, wiring, powering or pricing a sensor part |
| [products.md](products.md) | Asking what finished detectors and monitors exist, and what each one detects |
| [logging-and-validation.md](logging-and-validation.md) | Deciding what to log, or judging whether a detection method works |
| [enclosure-materials.md](enclosure-materials.md) | Choosing a seal, a vent or a case plastic, or asking what silicone does to these sensors |
| This file | Deciding what the system on the boat does and how it is laid out |

## How far to trust a line

The notes come from design sessions on 2026-07-25 and 26, and a check of specs
and prices on 2026-11-17.

| Label | Meaning |
|---|---|
| **Settled** | Decided by the owner. Ask before changing it. |
| **Open** | Deliberately unresolved. Raise it; do not settle it quietly. |
| **Proposed** | A recommendation nobody has accepted yet. A starting point. |
| **Unverified** | A figure from memory or from July, not checked against a datasheet or a listing. |
| **Verified** | Read on a datasheet, a maker's page or a seller's listing on 2026-11-17; the source is listed beside it. |

No sensor here has been on the bench. Check the datasheet for the exact part in
hand before relying on a figure.

## The system

```
 engine space        battery locker        main cabin
 ┌───────────┐       ┌───────────┐       ┌───────────┐
 │ ESP32 node│       │ ESP32 node│       │ ESP32 node│
 └─────┬─────┘       └─────┬─────┘       └─────┬─────┘
       │                   │                   │        link: Open
       └───────────────────┼───────────────────┘
                           ▼
                 Signal K server (HALPI2)
          baselines, states, alerts, history
```

| Piece | What it is | Status |
|---|---|---|
| Hub | The boat's existing Signal K server, on the HALPI2. Baselines, alerts and history live here. | Settled |
| Nodes | One ESP32 board per space, reading its sensors and passing readings to Signal K | Settled |
| Which board | A HALMET and bare ESP32s are on hand. Nothing in the design depends on the board. | Open |
| Link from node to hub | Wi-Fi, a wired bus that also carries power, or a mix | Open |
| A second small computer, such as a Pi Zero | Not planned. Only if something cannot run on the HALPI2 or a node. | Open |
| Display | None yet. Signal K's own dashboards first. | Open |
| Data | Stays on the boat | Settled |

The engine space and battery locker are metal or foil-lined, so Wi-Fi from
inside them is in doubt until tried.

## The three spaces (Settled)

| Space | The question it answers | Sensors live there |
|---|---|---|
| Engine and mechanical space | Is fuel vapour, exhaust or heat drifting away from normal? | MP-4, MP-7, BME688, thermopile, flame flicker, DS18B20; MQ-2 as well if the bilge is open to it |
| Battery locker | Has the air in here changed from its own normal? | BME688, and a DS18B20 on the battery. Heated sensors off. A battery getting warm shows earlier than gas does. |
| Main cabin | What is the boat's air doing right now? | BME688. It is the reference for the other two: is the battery locker up, or is the whole boat damp today? |

A motion sensor, a light sensor and a microphone can ride along in any space
as context: was someone in there, did a hatch open, is a pump or the engine
running.

Another node is only worth having where it answers a question of its own. Each
one costs a box, a power run and a link.

The parts are described in [sensors.md](sensors.md).

## How it decides something changed

Each sensor is compared with its own recent normal. It is not compared with a
fixed threshold or with another unit.

- This avoids the three hard problems of cheap gas sensors: one unit reads
  differently from the next, none of them is calibrated, and all of them drift.
- The price: the system knows *that* something changed, not *what*.
- The cabin node lets it discount whole-boat effects such as humidity, cooking
  or an open hatch.

Each gas channel publishes three things (Settled):

| Output | Form |
|---|---|
| `raw` | The reading, scaled 0 to 1 |
| `baselineDeviation` | How far from normal, signed, in multiples of the usual spread for that space and channel |
| `state` | `conditioning` · `learning` · `normal` · `elevated` · `high` · `fault` |

`elevated` raises an alert and `high` a warning. An alarm takes persistence
and agreement between channels.

How the baseline is learned (the window, how fast it may adapt) is **Open**; it
is the thing the build is meant to find out. It stays behind
`baselineDeviation` and `state` so it can change without touching anything else.

## Signal K paths

Standard measurements go on standard paths. Gas channels go on a branch of
their own. The standard keys are **Unverified** against the current Signal K
specification.

| Data | Path |
|---|---|
| Temperature, humidity, pressure | `environment.inside.{zone}.temperature` · `.relativeHumidity` · `.pressure` (K, ratio, Pa) |
| Battery probe temperature | `electrical.batteries.{id}.temperature` |
| Gas channel | `environment.inside.{zone}.gasSense.{channel}.raw` · `.baselineDeviation` · `.state` |
| Sensor diagnostics | `…gasSense.{channel}.sensor.hoursOfOperation` · `.faultCode` |
| Alerts | `notifications.environment.inside.{zone}.gasSense.{channel}` |

Zones: `engineRoom`, `batteryBay`, `mainCabin`. Channels: `co`, `combustible`,
`lpg`, `voc`.

For example, a damp day with a small fuel weep in the engine space:

```
environment.inside.engineRoom.gasSense.combustible.raw                0.41
environment.inside.engineRoom.gasSense.combustible.baselineDeviation  3.2
environment.inside.engineRoom.gasSense.combustible.state              elevated
environment.inside.mainCabin.gasSense.voc.state                       normal
```

## Rules for the build (Settled)

| Rule | Why |
|---|---|
| No concentration (ppm) readouts from the heated or MOX sensors | They cannot give a trustworthy one; see [sensors.md](sensors.md) |
| No sensors with a shelf life: no electrochemical cells, pellistors or PID lamps | No part to replace every one to three years |
| It reads and reports. It commands nothing, the battery management system included. | Scope |
| Sealed box; the only openings are a PTFE gas vent, a bonded IR window and an ePTFE acoustic vent | Moisture and salt are the main threat |
| Nothing moving on the outside | The same |
| No silicone adhesive, sealant or coating near the sensors | Siloxanes permanently poison MOX and MOS elements |
| Any conformal coat is acrylic, with every sensor opening masked | The same |

## Open questions

| Question | Note |
|---|---|
| Link from node to hub | See the table above |
| Which board in which space | HALMET and ESP32s on hand |
| Baseline internals | What the build is for |
| BME688 or BME690 | See [sensors.md](sensors.md) |
| Log raw BME688 scans, or only what Bosch's library computes | See [logging-and-validation.md](logging-and-validation.md) |
| Signal K standard path keys | Not yet checked against the specification |
| Enclosure, mounts and vents | One box so far: [bme688-halpi2](bme688-halpi2/), a BME688 alone, wired to the HALPI2. Not printed. Parts measured for boxes go in [`parts.md`](../../parts.md). |
