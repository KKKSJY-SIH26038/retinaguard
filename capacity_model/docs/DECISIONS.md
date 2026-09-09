# DECISIONS — capacity_model

Every hardcoded threshold, parameter, dataset choice, algorithm choice, and
fallback gets a paragraph here: what was chosen, alternatives considered,
why this one, and the words UNTUNED or ASSUMPTION where they apply.

---

## Environment (Task 1)

MATLAB is not installed on this laptop (confirmed by checking `Program
Files`, PATH, and the registry — no `matlab.exe`, no MathWorks registry
keys). Per the shared rules, Part 1 (capacity model) is therefore built in
Python (numpy/matplotlib, plus plain-Python for Erlang-C rather than scipy,
see below) instead of MATLAB. This is an explicit fallback path the plan
allows for tonight's feasibility slice — the real project plan
(`final_plan.md` §9) still calls for a Simulink/SimEvents model built by
hand later, with `eventSim.m` kept only as the insurance fallback (item
5.7). Tonight, the fallback becomes the whole deliverable because the
primary tool isn't available. ASSUMPTION: a laptop with MATLAB + SimEvents
licensed will be available during the actual practice sprint (Phase 2).

Deep Learning Toolbox / resnet18 check is moot tonight: Part 2 (grading
smoke test) never started. The 8:30pm IST decision gate for starting Part 2
had already passed by the time this instance began work (~10:14pm), so
Part 2 was skipped per the plan's own rule, independent of whether a
dataset download would have succeeded.

## Erlang-C cross-check (Task 3)

Ran `erlang_c.py` (closed-form M/M/c) against `event_sim.py` at the
baseline parameters (offered load a = λ/μ = 5.556 Erlangs) for c = 3, 5, 7
graders:

| c | Erlang-C Wq (min) | Sim mean wait (min) | % diff | note |
|---|---|---|---|---|
| 3 | n/a (overloaded) | 61184.8 | n/a | a=5.56 ≥ c=3, no steady state |
| 5 | n/a (overloaded) | 7880.5 | n/a | a=5.56 ≥ c=5, no steady state |
| 7 | 1.309 | 1.285 | 1.9% | agrees, well within the 10% target |

At c=3 and c=5 the offered load (5.556 Erlangs) exceeds the number of
graders, so there is no steady state — the queue grows without bound in
both the formula (undefined/P_wait→1) and the simulation (backlog climbs
all year). That is not a simulation bug, it's the correct behavior for an
understaffed queue. Only c=7 has a finite steady-state comparison, and it
agrees within 1.9%, well inside the ~10% target — this is the evidence
the simulation's core mechanics (Poisson arrivals, exponential service,
c-server FIFO) are implemented correctly. The practical implication:
under tonight's ASSUMPTION parameters, a district doing 100k
screenings/yr needs at least 6-7 graders before wait times are finite at
all — see the sweep in Task 4 for where the knee actually sits.

## Time (whole session)

This instance started at 22:14 IST, leaving ~76 minutes before the 11:30pm
hard stop instead of the ~2 hours Task Block B budgets for Part 1 alone.
Scope was cut accordingly: Task 0 (dataset download check) capped at a few
minutes since no Kaggle/IEEE credentials were found; figures (Task 4) and
the gate-value calc (Task 5) were kept deliberately small/fast rather than
polished, so the core deliverable — a working, cross-checked simulation —
could be finished and committed before the hard stop.
