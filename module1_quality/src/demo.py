"""
Purpose: run one fundus image through Module 1 on screen for the demo video -
  preprocess, quality decision, and (if not "good") the enhancement stages.
How it works: it prints the decision and the operator feedback line to the
  terminal, then opens one matplotlib window showing the original next to the
  16-cell illumination map, and for a non-good image a second window with the
  enhancement stages and the before/after scores.
Does NOT yet: segment, grade, or explain - that is Modules 2-4.
UNDERSTOOD-BY: (leave blank - a human fills this in)
Status: FEASIBILITY SLICE - untuned, not validated
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preprocess import preprocess
from assessQuality import assessQuality, illumination_overlay
from enhance import enhance


def run(img_path: str) -> None:
    pp = preprocess(img_path)
    q = assessQuality(pp)
    print(f"\n  {Path(img_path).name}")
    print(f"  decision : {q.decision.upper()}")
    print(f"  scores   : blur {q.scores.blur:.0f}  illum {q.scores.illum:.2f}  "
          f"coverage {q.scores.fov:.2f}  exposure {q.scores.exposure:.0f}  "
          f"block {q.scores.block:.2f}")
    if q.feedback:
        print(f"  feedback : {q.feedback}")

    fig, ax = plt.subplots(1, 2, figsize=(11, 5.5), num=f"{Path(img_path).name} - quality")
    ax[0].imshow(pp.img512); ax[0].set_title("preprocessed"); ax[0].axis("off")
    ax[1].imshow(illumination_overlay(pp), cmap="magma")
    ax[1].set_title(f"illumination map  |  {q.decision}"); ax[1].axis("off")
    fig.tight_layout()

    if q.decision != "good":
        e = enhance(pp)
        b, a = e.scores_before, e.scores_after
        f2, ax2 = plt.subplots(1, 4, figsize=(18, 5), num=f"{Path(img_path).name} - enhance")
        for x, (name, im) in zip(ax2, [("original", e.original), ("CLAHE", e.after_clahe),
                                       ("flat-field", e.after_flatfield), ("final", e.final)]):
            x.imshow(im); x.set_title(name); x.axis("off")
        f2.suptitle(f"illum CoV {b.illum:.2f} -> {a.illum:.2f}   "
                    f"blur {b.blur:.0f} -> {a.blur:.0f}")
        f2.tight_layout()

    plt.show()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python src/demo.py <image path>")
        raise SystemExit(2)
    run(sys.argv[1])
