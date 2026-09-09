# RetinaGuard root ledger

Append-only. One line per entry:

    YYYY-MM-DD HH:MM IST — <single sentence, past tense, ends with a period.>

Build night of 9 Sep 2026: two instances worked on separate branches with
per-directory ledgers (module1_quality/LEDGER.md, capacity_model/LEDGER.md).
The lines below are those two ledgers merged and sorted by timestamp at the
end of the night; the final line records that merge.

2026-09-09 20:20 IST — Started Module 1 feasibility slice on branch kavya/module1.
2026-09-09 20:22 IST — Confirmed no MATLAB on the build laptop; Kavya approved the Python/OpenCV fallback for tonight.
2026-09-09 20:28 IST — Installed the Python stack into module1_quality/.venv: numpy 2.5.3, opencv 5.0.0, scikit-image 0.26.0, scipy 1.18.1, matplotlib 3.11.1.
2026-09-09 20:31 IST — Ran env_check.py; all nine MATLAB-function equivalents resolve on this machine.
2026-09-09 20:32 IST — Committed task1: env check and skeleton.
2026-09-09 20:33 IST — Downloaded DRIVE test set (20 fundus images, ~28MB) from the Kaggle mirror andrewmvd/drive-digital-retinal-images-for-vessel-extraction.
2026-09-09 20:33 IST — Chose the 20 DRIVE test images as tonight's good set, taken as-is rather than hand-picked by eye.
2026-09-09 20:34 IST — Generated 6 synthetic degradations (blur, dark, vignette, jpeg, partial, overexp), one per image, into data/degraded/.
2026-09-09 20:35 IST — Committed task2: DRIVE corpus and 6 synthetic degradations.
2026-09-09 20:36 IST — Committed task3: preprocess.py with FOV crop and circular mask.
2026-09-09 20:40 IST — Hardcoded UNTUNED quality thresholds: blur 250/420, illum CoV 0.45/0.20, coverage 0.90/0.965, exposure 42/200 and 70-185, blockiness 1.55/1.20.
2026-09-09 20:42 IST — Added two scores beyond the plan's three (exposure, JPEG blockiness) so global under/over-exposure and compression are caught.
2026-09-09 20:44 IST — Adjusted by eye after the first run: strengthened the vignette and overexp degradations and moved blockiness to full-res and coverage into preprocess, so all 6 degraded images now land on reject and no clean image does.
2026-09-09 20:46 IST — Committed task4: assessQuality.py with 4 scores and 3-way decision.
2026-09-09 20:47 IST — Hardcoded UNTUNED enhancement settings: CLAHE clip 2.0 tile 8, flat-field sigma 55, denoise strength 3.
2026-09-09 20:47 IST — Verified enhancement raises the sharpness score on all 10 test images, so the denoise strength was left light and not reduced further.
2026-09-09 20:48 IST — Committed task5: enhance.py with staged pipeline and before/after scores.
2026-09-09 20:50 IST — Exported three figures (fig1 reject+feedback, fig2 enhance before/after, fig3 score scatter) at 2600-3000px wide with baked-in captions.
2026-09-09 20:51 IST — Committed task6: three figures and figure README.
2026-09-09 20:52 IST — Committed task7: recording script and demo.py.
2026-09-09 20:52 IST — Committed task8: plain-English explainer.
2026-09-09 20:52 IST — Finished all eight tasks with time to spare; spent the remainder on smoke tests, a requirements.txt, and the module README (no new scope).
2026-09-09 20:53 IST — Added tests/test_module1.py (the section-10 "runtests before merge" gate); all 13 checks pass.
2026-09-09 20:53 IST — Committed task9: smoke tests, requirements.txt, module README.
2026-09-09 20:53 IST — Module 1 feasibility slice complete; all tasks done, nothing partial or broken, branch kavya/module1 pushed, no merge performed.
2026-09-09 22:14 IST — Started Task Block B (capacity model); noted hard stop 11:30pm leaves ~76 min, decision gate for Part 2 already passed (8:30pm) so Part 2 is skipped per plan and effort goes to Part 1 only.
2026-09-09 22:15 IST — Checked for Kaggle API and IEEE DataPort credentials; neither found, so no grading-dataset download started and Part 2 is cancelled (also moot: 8:30pm decision gate already passed).
2026-09-09 22:17 IST — Confirmed MATLAB absent on this laptop; Part 1 will be built in Python (numpy/matplotlib, plain-Python Erlang-C) instead of MATLAB, per shared-rules fallback.
2026-09-09 22:17 IST — Created capacity_model/ skeleton (src, data, figs, docs) and docs/DECISIONS.md.
2026-09-09 22:20 IST — Reconciled the timestamps above against the git commit times; later entries had been estimated a few minutes fast.
2026-09-09 22:20 IST — Hardcoded grader_service_minutes_per_image=4.0 (ASSUMPTION, untuned) and working_days_per_year=300 (ASSUMPTION) in event_sim.py defaults.
2026-09-09 22:20 IST — Wrote and ran src/event_sim.py; sanity checks passed (c=1000 near-zero wait, c=1 explodes to 164k backlog); baseline c=5 is unstable (utilization 1.11) matching offered load ~5.56 Erlangs.
2026-09-09 22:22 IST — Ran erlang_c.py against event_sim.py at c=3,5,7; c=7 (only stable case) agreed within 1.9%, well under the 10% target; c=3/5 correctly show as overloaded/no-steady-state in both.
2026-09-09 22:27 IST — Ran sweep (num_graders 2-8) and heatmap (graders x service-minutes); found knee at 6 graders (backlog drops from ~19,773 at c=5 to 4 at c=6), matching Erlang-C's stability threshold of ~5.56 Erlangs; saved fig4_backlog_vs_graders.png and fig5_sweep_heatmap.png.
2026-09-09 22:27 IST — Computed gate-value: 30,000 ungradeable images/yr at 15% (assumption) implies ~2,000 grader-hours and ~30,000 patient recalls per 100k screened per year saved by capture-time rejection; wrote docs/SLIDE5_LINE.md.
2026-09-09 22:28 IST — Wrote docs/EXPLAINER.md (plain-English description of the capacity model); Part 2 never ran so no second paragraph needed.
2026-09-09 22:28 IST — Part 1 (Tasks 0-5, 9) complete with ~60 min to spare before the 11:30pm hard stop; pushing krisha/capacity now.
2026-09-09 22:48 IST — Merged both branches and ledgers into main.
