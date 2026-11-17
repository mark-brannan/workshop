"""Graph of the 2026-11-16 ABS full-load test (out/2026-11-16-abs-hold.csv)."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

here = Path(__file__).parent
rows = [r for r in csv.DictReader(l for l in open(here / "out/2026-11-16-abs-hold.csv") if not l.startswith("#"))]
t = [float(r["t_s"]) / 60 for r in rows]
col = lambda k: [float(r[k]) for r in rows]
hold = next(float(r["t_s"]) / 60 for r in rows if r["phase"] == "hold")

fig, (a, b) = plt.subplots(2, 1, figsize=(10, 7), sharex=True, height_ratios=[3, 2])
a.plot(t, col("nozzle_C"), color="#7b3fa0", label="nozzle (target 260)")
a.plot(t, col("bed_C"), color="#d62728", label="bed (target 100)")
a.plot(t, col("chamber_C"), color="#1f77b4", label="chamber air (target 50)")
for y, c in ((260, "#7b3fa0"), (100, "#d62728"), (50, "#1f77b4")):
    a.axhline(y, color=c, ls=":", lw=0.8)
a.axvline(hold, color="k", lw=1)
a.text(hold + 1, 170, "soak reached 49 °C\nhold starts: nozzle 260, part fan 30%", fontsize=9)
a.set_ylabel("°C"); a.legend(loc="center right"); a.grid(alpha=0.3)
a.set_title("16 Nov: ABS full load, warm start, room ~12 °C, vents closed, rear fan off throughout")
b.plot(t, col("bed_pwr"), color="#d62728", label="bed power")
b.plot(t, col("nozzle_pwr"), color="#7b3fa0", label="nozzle power")
b.fill_between(t, col("ch_pwr"), color="#1f77b4", alpha=0.3, step="post", label="chamber heater power")
b.axvline(hold, color="k", lw=1)
b.set_ylabel("power (0–1)"); b.set_xlabel("minutes"); b.legend(loc="lower left", ncol=3); b.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(here / "out/2026-11-16-abs-hold.png", dpi=110)
