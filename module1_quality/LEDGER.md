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

