2026-09-09 22:14 IST — Started Task Block B (capacity model); noted hard stop 11:30pm leaves ~76 min, decision gate for Part 2 already passed (8:30pm) so Part 2 is skipped per plan and effort goes to Part 1 only.
2026-09-09 22:15 IST — Checked for Kaggle API and IEEE DataPort credentials; neither found, so no grading-dataset download started and Part 2 is cancelled (also moot: 8:30pm decision gate already passed).
2026-09-09 22:17 IST — Confirmed MATLAB absent on this laptop; Part 1 will be built in Python (numpy/matplotlib, plain-Python Erlang-C) instead of MATLAB, per shared-rules fallback.
2026-09-09 22:17 IST — Created capacity_model/ skeleton (src, data, figs, docs) and docs/DECISIONS.md.
2026-09-09 22:20 IST — Hardcoded grader_service_minutes_per_image=4.0 (ASSUMPTION, untuned) and working_days_per_year=300 (ASSUMPTION) in event_sim.py defaults.
2026-09-09 22:20 IST — Wrote and ran src/event_sim.py; sanity checks passed (c=1000 near-zero wait, c=1 explodes to 164k backlog); baseline c=5 is unstable (utilization 1.11) matching offered load ~5.56 Erlangs.
2026-09-09 22:22 IST — Ran erlang_c.py against event_sim.py at c=3,5,7; c=7 (only stable case) agreed within 1.9%, well under the 10% target; c=3/5 correctly show as overloaded/no-steady-state in both.
