# Outside claims, checked

## 2026-11-20: a chatbot's case that "the ISM330DHCX wins at sea"

Compared the ISM330DHCX, LSM6DSV16X and ICM-42688-P. The spec numbers were mostly real;
the reasoning built on them mostly did not hold.

| Claim | Checks out? | Bears on a boat? |
|---|---|---|
| ISM330DHCX gyro bias instability about 3°/hr | Yes, per ST's blog (5°/hr for its consumer sibling) | Little. Pitch and roll are tied to gravity by the accelerometer and don't wander over a watch |
| Industrial calibration stops the offset shifting with temperature | No. ±0.005 dps/°C in ST's blog, the same figure as the ICM-42688-P datasheet | No. A cabin is well inside every chip's range |
| 9 KB FIFO prevents dropped samples | The size is right | No. It matters only if the host stalls at high sample rates |
| 10-year availability | Yes, from memory of ST's longevity programme; not searched | Somewhat |
| ICM-42688-P is overkill and weaker on drift | Half. Its gyro noise equals the LSM6DSV16X's; its drift is unpublished | No |
| LSM6DSV16X's on-chip fusion is fooled by turns and heel | Misleading. Any 6-axis fusion reads a turn as tilt; the ISM330DHCX has no on-chip fusion; sustained heel is real tilt | Small |

Not confirmed at the time: the LSM6DSV16X's temperature range and bias instability, and
the ISM330DHCX's own noise figure.
