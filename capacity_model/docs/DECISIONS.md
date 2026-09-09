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

## Time (whole session)

This instance started at 22:14 IST, leaving ~76 minutes before the 11:30pm
hard stop instead of the ~2 hours Task Block B budgets for Part 1 alone.
Scope was cut accordingly: Task 0 (dataset download check) capped at a few
minutes since no Kaggle/IEEE credentials were found; figures (Task 4) and
the gate-value calc (Task 5) were kept deliberately small/fast rather than
polished, so the core deliverable — a working, cross-checked simulation —
could be finished and committed before the hard stop.
