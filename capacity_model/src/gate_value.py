"""
Purpose: turns the quality gate's benefit into one plain-English number
  for the pitch — how much grader time and how many patient recall trips
  get saved if bad photos are caught at the camera instead of at the
  grading desk.
How it works: assumes a fraction of captured images can never be graded
  (too blurry, badly framed, etc. — see Module 1). If nobody catches
  these until a grader opens them, the grader still spends time on each
  one before rejecting it — that time is wasted. If the quality gate
  catches them right after capture instead, that grader time is never
  spent, and the patient can retake the photo on the spot instead of
  being called back later.
Does NOT yet: account for a patient with both eyes ungradeable being
  counted as two "recalls" instead of one — that's a small overcount,
  noted in DECISIONS.md, not fixed tonight.
UNDERSTOOD-BY:
Status: FEASIBILITY SLICE — untuned, not validated
"""

import os
from event_sim import default_params

# ASSUMPTION, per task spec, untuned: fraction of captured images that
# can never be graded regardless of who looks at them.
UNGRADEABLE_RATE = 0.15


def compute(params=None):
    p = params or default_params()
    total_images_per_year = p["district_population_screened_per_year"] * p["images_per_patient"]
    ungradeable_images = UNGRADEABLE_RATE * total_images_per_year

    grader_hours_wasted = ungradeable_images * p["grader_service_minutes_per_image"] / 60.0
    # Saved = the exact same time, simply never spent, if caught at capture instead.
    grader_hours_saved = grader_hours_wasted

    # Per task spec: each ungradeable image reaching grading implies one
    # recall (image-level count, not patient-level — see docstring/DECISIONS.md).
    patients_recalled_avoided = ungradeable_images

    return {
        "population_screened_per_year": p["district_population_screened_per_year"],
        "total_images_per_year": total_images_per_year,
        "ungradeable_images_per_year": ungradeable_images,
        "grader_hours_wasted_per_year": grader_hours_wasted,
        "grader_hours_saved_per_year": grader_hours_saved,
        "patients_recalled_avoided_per_year": patients_recalled_avoided,
    }


if __name__ == "__main__":
    r = compute()
    print(r)

    # Scale to "per 100k screened" for the headline, in case defaults change.
    scale = 100_000 / r["population_screened_per_year"]
    hours_100k = r["grader_hours_saved_per_year"] * scale
    recalls_100k = r["patients_recalled_avoided_per_year"] * scale

    line = (
        f"With a 15% ungradeable rate (assumption), capture-time rejection "
        f"saves ~{hours_100k:,.0f} grader-hours and ~{recalls_100k:,.0f} "
        f"patient recalls per 100k screened per year."
    )
    print("\n" + line)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "SLIDE5_LINE.md"), "w") as f:
        f.write(line + "\n")
