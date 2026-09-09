# Module 1 (Quality) — ledger

Append-only. One line per entry, exactly:

    YYYY-MM-DD HH:MM IST — <single sentence, past tense, ends with a period.>

WHAT and WHEN only. The WHY lives in docs/DECISIONS.md.

2026-09-09 20:20 IST — Started Module 1 feasibility slice on branch kavya/module1.
2026-09-09 20:22 IST — Confirmed no MATLAB on the build laptop; Kavya approved the Python/OpenCV fallback for tonight.
2026-09-09 20:28 IST — Installed the Python stack into module1_quality/.venv: numpy 2.5.3, opencv 5.0.0, scikit-image 0.26.0, scipy 1.18.1, matplotlib 3.11.1.
2026-09-09 20:31 IST — Ran env_check.py; all nine MATLAB-function equivalents resolve on this machine.
2026-09-09 20:33 IST — Committed task1: env check and skeleton.
2026-09-09 20:31 IST — Downloaded DRIVE test set (20 fundus images, ~28MB) from the Kaggle mirror andrewmvd/drive-digital-retinal-images-for-vessel-extraction.
2026-09-09 20:32 IST — Chose the 20 DRIVE test images as tonight's good set, taken as-is rather than hand-picked by eye.
2026-09-09 20:33 IST — Generated 6 synthetic degradations (blur, dark, vignette, jpeg, partial, overexp), one per image, into data/degraded/.
2026-09-09 20:34 IST — Committed task2: DRIVE corpus and 6 synthetic degradations.
2026-09-09 20:36 IST — Committed task3: preprocess.py with FOV crop and circular mask.
2026-09-09 20:40 IST — Hardcoded UNTUNED quality thresholds: blur 250/420, illum CoV 0.45/0.20, coverage 0.90/0.965, exposure 42/200 and 70-185, blockiness 1.55/1.20.
2026-09-09 20:42 IST — Added two scores beyond the plan's three (exposure, JPEG blockiness) so global under/over-exposure and compression are caught.
2026-09-09 20:43 IST — Adjusted by eye after the first run: strengthened the vignette and overexp degradations and moved blockiness to full-res and coverage into preprocess, so all 6 degraded images now land on reject and no clean image does.
2026-09-09 20:45 IST — Committed task4: assessQuality.py with 4 scores and 3-way decision.
2026-09-09 20:47 IST — Hardcoded UNTUNED enhancement settings: CLAHE clip 2.0 tile 8, flat-field sigma 55, denoise strength 3.
2026-09-09 20:48 IST — Verified enhancement raises the sharpness score on all 10 test images, so the denoise strength was left light and not reduced further.
2026-09-09 20:49 IST — Committed task5: enhance.py with staged pipeline and before/after scores.
2026-09-09 20:52 IST — Exported three figures (fig1 reject+feedback, fig2 enhance before/after, fig3 score scatter) at 2600-3000px wide with baked-in captions.
2026-09-09 20:53 IST — Committed task6: three figures and figure README.
2026-09-09 20:56 IST — Committed task7: recording script and demo.py.
2026-09-09 20:57 IST — Committed task8: plain-English explainer.
2026-09-09 21:00 IST — Finished all eight tasks with time to spare; spent the remainder on smoke tests, a requirements.txt, and the module README (no new scope).
2026-09-09 21:02 IST — Added tests/test_module1.py (the section-10 "runtests before merge" gate); all 13 checks pass.
2026-09-09 21:03 IST — Committed task9: smoke tests, requirements.txt, module README.

