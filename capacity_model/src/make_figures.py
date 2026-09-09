"""
Purpose: sweeps grader count (and, for one figure, service time per
  image) through event_sim.py and exports the two capacity-planning
  figures for the pitch deck.
How it works: reruns the simulation many times with different grader
  counts (and service times), then plots how the backlog and wait time
  change as you add more graders — this is the "how many people do we
  need to hire" chart.
Does NOT yet: sweep bandwidth or the quality-gate reject rate (those are
  Simulink-model concerns per final_plan.md §9, not built tonight).
UNDERSTOOD-BY:
Status: FEASIBILITY SLICE — untuned, not validated
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from event_sim import default_params, simulate

FIG_DIR = os.path.join(os.path.dirname(__file__), "..", "figs")
os.makedirs(FIG_DIR, exist_ok=True)

BASE = default_params()
POP = BASE["district_population_screened_per_year"]
SVC = BASE["grader_service_minutes_per_image"]


def caption(fig, text):
    fig.text(0.5, 0.01, text, ha="center", fontsize=8, color="#444444")


# --- fig4: backlog vs graders ---
graders_range = list(range(2, 9))
backlogs = []
for c in graders_range:
    p = dict(BASE, num_graders=c)
    r, _ = simulate(p)
    backlogs.append(r["end_of_year_backlog"])

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(graders_range, backlogs, marker="o", color="#2a6f97")
ax.set_yscale("log")
ax.set_xlabel("Number of graders")
ax.set_ylabel("End-of-year backlog (images, log scale)")
ax.set_title("Backlog vs grader count")
# mark the knee: first c where backlog stops being enormous (< 1000)
knee = next((c for c, b in zip(graders_range, backlogs) if b < 1000), None)
if knee is not None:
    ax.axvline(knee, color="#e07a5f", linestyle="--")
    ax.text(knee + 0.1, max(backlogs) * 0.5, f"knee ~ {knee} graders", color="#e07a5f")
fig.tight_layout(rect=[0, 0.04, 1, 1])
caption(fig, f"Simulated, population={POP}/yr, service={SVC} min/image (ASSUMPTION), untuned, n=1 run per point")
fig.savefig(os.path.join(FIG_DIR, "fig4_backlog_vs_graders.png"), dpi=200)
plt.close(fig)
print("Saved fig4_backlog_vs_graders.png; knee at", knee, "graders")
print("backlogs:", dict(zip(graders_range, backlogs)))

# --- fig5: heatmap, graders x service-minutes, color = p95 wait (days) ---
service_range = [1, 2, 3, 4, 5]
p95_days = np.zeros((len(service_range), len(graders_range)))
for i, svc in enumerate(service_range):
    for j, c in enumerate(graders_range):
        p = dict(BASE, num_graders=c, grader_service_minutes_per_image=float(svc))
        r, _ = simulate(p)
        p95_days[i, j] = r["p95_wait_minutes"] / 1440.0  # minutes -> calendar days

fig, ax = plt.subplots(figsize=(9, 6))
# cap color scale so one exploding cell doesn't wash out the plot
capped = np.clip(p95_days, 0, 30)
im = ax.imshow(capped, cmap="magma_r", aspect="auto", origin="lower")
ax.set_xticks(range(len(graders_range)))
ax.set_xticklabels(graders_range)
ax.set_yticks(range(len(service_range)))
ax.set_yticklabels(service_range)
ax.set_xlabel("Number of graders")
ax.set_ylabel("Grader service time (minutes/image)")
ax.set_title("95th-percentile wait (days), capped at 30")
cbar = fig.colorbar(im, ax=ax)
cbar.set_label("95th-percentile wait, days (capped at 30)")
fig.tight_layout(rect=[0, 0.04, 1, 1])
caption(fig, f"Simulated, population={POP}/yr, untuned, n=1 run per cell, color capped at 30 days")
fig.savefig(os.path.join(FIG_DIR, "fig5_sweep_heatmap.png"), dpi=200)
plt.close(fig)
print("Saved fig5_sweep_heatmap.png")
