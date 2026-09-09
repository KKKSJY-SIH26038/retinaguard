"""
Purpose: closed-form queueing-theory check on event_sim.py, using the
  textbook Erlang-C formula for a queue with c identical servers.
How it works: given how fast images arrive and how fast one grader can
  review them, Erlang-C is a formula (no simulation, no randomness) that
  predicts the average wait directly from those two numbers and the
  grader count. If our simulation is coded correctly, its average wait
  should land close to what this formula predicts, whenever the formula
  applies. If they disagree a lot, the simulation has a bug.
Does NOT yet: apply when the system is overloaded (more images arriving
  than graders can ever clear) — in that case both the formula and any
  simulation just show an ever-growing queue, so there's nothing finite
  to compare.
UNDERSTOOD-BY:
Status: FEASIBILITY SLICE — untuned, not validated
"""

import math


def erlang_c(lambda_per_min, mu_per_min, c):
    """Returns dict with P_wait, mean wait in queue (minutes), mean queue
    length, or None if the system is overloaded (offered load >= servers,
    i.e. no steady state exists)."""
    a = lambda_per_min / mu_per_min  # offered load, in Erlangs
    if a >= c:
        return None

    sum_terms = sum(a ** k / math.factorial(k) for k in range(c))
    last_term = (a ** c / math.factorial(c)) * (c / (c - a))
    p0 = 1.0 / (sum_terms + last_term)
    p_wait = last_term * p0
    wq_minutes = p_wait / (c * mu_per_min - lambda_per_min)
    lq = lambda_per_min * wq_minutes

    return {"offered_load_erlangs": a, "P_wait": p_wait, "Wq_minutes": wq_minutes, "Lq": lq}


if __name__ == "__main__":
    from event_sim import default_params, simulate

    p = default_params()
    day_minutes = p["working_hours_per_day"] * 60
    n_days = p["working_days_per_year"]
    total_images_year = p["district_population_screened_per_year"] * p["images_per_patient"]
    lam = total_images_year / (n_days * day_minutes)
    mu = 1.0 / p["grader_service_minutes_per_image"]

    print(f"lambda={lam:.4f} img/min, mu={mu:.4f} img/min/grader, offered load a={lam/mu:.3f} Erlangs\n")
    print(f"{'c':>3} | {'Erlang-C Wq (min)':>18} | {'Sim mean wait (min)':>20} | {'%diff':>8} | note")
    print("-" * 80)

    for c in (3, 5, 7):
        ec = erlang_c(lam, mu, c)
        sim_p = dict(p, num_graders=c)
        sim_result, _ = simulate(sim_p)
        sim_wait = sim_result["mean_wait_minutes"]

        if ec is None:
            print(f"{c:>3} | {'n/a (overloaded)':>18} | {sim_wait:>20.1f} | {'n/a':>8} | offered load {lam/mu:.2f} >= c, no steady state — both formula and sim correctly show an exploding queue, not a bug")
        else:
            diff_pct = 100 * abs(sim_wait - ec["Wq_minutes"]) / ec["Wq_minutes"]
            note = "within ~10% (agrees)" if diff_pct <= 10 else "MISMATCH — check sim"
            print(f"{c:>3} | {ec['Wq_minutes']:>18.3f} | {sim_wait:>20.3f} | {diff_pct:>7.1f}% | {note}")
