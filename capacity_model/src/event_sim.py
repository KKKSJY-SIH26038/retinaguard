"""
Purpose: discrete-event simulation of one district's DR-screening image
  queue over a year, to answer "how many graders does a district need".
How it works: images arrive as a Poisson process (randomly, but at a
  steady average rate) during working hours; each of `num_graders`
  graders reviews one image at a time, taking a random amount of time
  averaging `grader_service_minutes_per_image`. Whichever grader frees
  up first takes the next waiting image (first-come-first-served). We
  track, day by day, how many images are backed up and how long people
  wait. A weekly "camp day" can optionally multiply the arrival rate to
  mimic a mobile screening camp.
Does NOT yet: model grader shifts/breaks within a day, model images
  rejected by the quality gate before reaching the queue (see
  gate_value.py for that effect as a separate calc), model multiple
  districts.
UNDERSTOOD-BY:
Status: FEASIBILITY SLICE — untuned, not validated
"""

import math
import csv
import os
import heapq
import numpy as np


def default_params():
    return {
        # Basis: final_plan.md §9 sizing note ("100k patients/yr ~ 400/day").
        "district_population_screened_per_year": 100_000,
        # ASSUMPTION: 2 images/patient (one per eye), per final_plan.md §9 sizing note.
        "images_per_patient": 2,
        # ASSUMPTION, untuned: grounded loosely in final_plan.md §9's
        # t_review = 240s ("without report") grader service time; here
        # expressed in minutes as the mean of an exponential service time.
        "grader_service_minutes_per_image": 4.0,
        "num_graders": 5,
        "working_hours_per_day": 8,
        # ASSUMPTION: ~6 working days/week, accounting for holidays -> ~300/yr.
        "working_days_per_year": 300,
        # Weekly camp-day spike: OFF by default (uniform arrivals).
        "camp_day_spike_enabled": False,
        "camp_day_every_n_days": 7,
        "camp_day_multiplier": 3.0,
        "seed": 42,
    }


def simulate(params):
    """Runs the event-list simulation. Returns (results_dict, daily_rows).

    Arrivals: Poisson process, generated day-by-day so a weekly camp-day
    spike can multiply that day's rate. Service: exponential, mean
    `grader_service_minutes_per_image` — deliberately exponential (not a
    fixed/other distribution) so this simulation satisfies the same
    assumptions as the Erlang-C formula it's checked against in
    erlang_c.py; the plan flags "service time not exponential when
    Erlang-C assumes it is" as a common source of mismatch, so this
    avoids that bug by construction.

    Time axis is cumulative WORKING minutes only (off-hours/weekends are
    not modelled as gaps — see DECISIONS.md). Servers are modelled via
    the standard "earliest-free-server" method: keep a min-heap of the c
    servers' next-free times; each arrival is served by whichever frees
    up soonest, and waits if that time is in the future. This is exact
    for a FIFO, c-identical-server queue.
    """
    rng = np.random.default_rng(params["seed"])

    day_minutes = params["working_hours_per_day"] * 60
    n_days = params["working_days_per_year"]
    total_images_year = (
        params["district_population_screened_per_year"] * params["images_per_patient"]
    )
    base_lambda_per_min = total_images_year / (n_days * day_minutes)
    mu_per_min = 1.0 / params["grader_service_minutes_per_image"]
    c = params["num_graders"]

    server_free_heap = [0.0] * c
    heapq.heapify(server_free_heap)

    daily_rows = []
    all_waits = []
    total_service_minutes_consumed = 0.0
    cumulative_arrivals = 0
    cumulative_departures = 0
    departure_times_sorted = []  # kept sorted via bisect-free simple approach

    day_start = 0.0
    for day_idx in range(n_days):
        day_end = day_start + day_minutes
        is_camp_day = (
            params["camp_day_spike_enabled"]
            and (day_idx % params["camp_day_every_n_days"] == params["camp_day_every_n_days"] - 1)
        )
        day_lambda = base_lambda_per_min * (
            params["camp_day_multiplier"] if is_camp_day else 1.0
        )

        # Generate this day's arrivals via exponential interarrival draws.
        t = day_start
        day_waits = []
        day_arrivals = 0
        day_departures_completed = 0
        while True:
            t += rng.exponential(1.0 / day_lambda)
            if t >= day_end:
                break
            day_arrivals += 1
            cumulative_arrivals += 1

            free_time = heapq.heappop(server_free_heap)
            start_service = max(t, free_time)
            wait = start_service - t
            service_time = rng.exponential(params["grader_service_minutes_per_image"])
            departure = start_service + service_time
            heapq.heappush(server_free_heap, departure)

            all_waits.append(wait)
            day_waits.append(wait)
            total_service_minutes_consumed += service_time
            departure_times_sorted.append(departure)

        day_start = day_end

        # Backlog at end of day = arrivals so far minus departures completed by day_end.
        completed_by_day_end = sum(1 for d in departure_times_sorted if d <= day_end)
        cumulative_departures = completed_by_day_end
        backlog_end_of_day = cumulative_arrivals - cumulative_departures

        daily_rows.append({
            "day": day_idx + 1,
            "is_camp_day": is_camp_day,
            "arrivals": day_arrivals,
            "mean_wait_minutes": float(np.mean(day_waits)) if day_waits else 0.0,
            "p95_wait_minutes": float(np.percentile(day_waits, 95)) if day_waits else 0.0,
            "backlog_end_of_day": backlog_end_of_day,
        })

    total_minutes = n_days * day_minutes
    utilization = total_service_minutes_consumed / (c * total_minutes)

    results = {
        "num_graders": c,
        "offered_load_erlangs": base_lambda_per_min / mu_per_min,
        "mean_wait_minutes": float(np.mean(all_waits)) if all_waits else 0.0,
        "p95_wait_minutes": float(np.percentile(all_waits, 95)) if all_waits else 0.0,
        "utilization": utilization,
        "end_of_year_backlog": daily_rows[-1]["backlog_end_of_day"] if daily_rows else 0,
        "total_images_simulated": cumulative_arrivals,
    }
    return results, daily_rows


def write_daily_csv(daily_rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(daily_rows[0].keys()))
        writer.writeheader()
        writer.writerows(daily_rows)


if __name__ == "__main__":
    p = default_params()
    results, daily = simulate(p)
    print("Baseline (num_graders=%d):" % p["num_graders"], results)

    write_daily_csv(daily, os.path.join(os.path.dirname(__file__), "..", "data", "eventsim_daily.csv"))

    # Sanity checks required by the task spec.
    p_high = dict(p, num_graders=1000)
    r_high, _ = simulate(p_high)
    p_low = dict(p, num_graders=1)
    r_low, d_low = simulate(p_low)
    print("Sanity — c=1000: mean_wait=%.4f min, backlog=%d" % (r_high["mean_wait_minutes"], r_high["end_of_year_backlog"]))
    print("Sanity — c=1:    mean_wait=%.2f min, backlog=%d" % (r_low["mean_wait_minutes"], r_low["end_of_year_backlog"]))
    assert r_high["mean_wait_minutes"] < 0.5, "c=1000 should have near-zero wait"
    assert r_low["end_of_year_backlog"] > 10_000, "c=1 should explode into a large backlog"
    print("Sanity checks passed: high-c queue stays near zero, c=1 explodes.")
