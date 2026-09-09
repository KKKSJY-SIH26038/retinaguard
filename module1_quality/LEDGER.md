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

