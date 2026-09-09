"""
Purpose: smoke tests for Module 1 - the "runtests before merge" gate from
  final_plan.md section 10, at feasibility-slice depth.
How it works: runs preprocess / assessQuality / enhance on tonight's corpus and
  checks the shapes, the struct fields named in section 10, and the headline
  behaviour (clean image -> good, every degraded image -> not good, enhancement
  lowers the illumination CoV on the uneven clean image).
Does NOT yet: check numerical correctness against MATLAB, or cover edge cases
  beyond a blank frame.
UNDERSTOOD-BY: (leave blank - a human fills this in)
Status: FEASIBILITY SLICE - untuned, not validated
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from preprocess import preprocess, Pp                       # noqa: E402
from assessQuality import assessQuality                     # noqa: E402
from enhance import enhance                                 # noqa: E402

RAW = ROOT / "data" / "raw"
DEG = ROOT / "data" / "degraded"


def _check(name: str, cond: bool) -> bool:
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    return cond


def main() -> int:
    ok = True
    sample = sorted(RAW.glob("*.png"))
    assert sample, "run build_corpus.py first"

    pp = preprocess(sample[0])
    ok &= _check("preprocess returns Pp with section-10 fields",
                 isinstance(pp, Pp) and pp.img512.shape == (512, 512, 3)
                 and pp.fovMask.shape == (512, 512) and "path" in pp.meta)
    ok &= _check("fovMask is binary", set(np.unique(pp.fovMask)).issubset({0, 1}))

    blank = np.zeros((200, 200), np.uint8)
    tmp = RAW / "_test_blank.png"
    import cv2
    cv2.imwrite(str(tmp), blank)
    ppb = preprocess(tmp)
    ok &= _check("blank frame -> fov_detected False, mask all ones",
                 ppb.meta["fov_detected"] is False and ppb.fovMask.min() == 1)
    tmp.unlink()

    q = assessQuality(pp)
    ok &= _check("assessQuality returns section-10 fields",
                 q.decision in {"good", "enhance", "reject"}
                 and hasattr(q.scores, "blur") and hasattr(q.scores, "illum")
                 and hasattr(q.scores, "fov") and isinstance(q.feedback, str))

    n_good = sum(assessQuality(preprocess(p)).decision == "good" for p in sample)
    ok &= _check(f"most clean images pass ({n_good}/{len(sample)} good)",
                 n_good >= len(sample) - 2)

    for p in sorted(DEG.glob("*.png")):
        d = assessQuality(preprocess(p)).decision
        ok &= _check(f"degraded {p.name} -> not good (got {d})", d != "good")

    e = enhance(preprocess(RAW / "15_test.png"))
    ok &= _check("enhance returns all five stages",
                 all(getattr(e, s).shape == (512, 512, 3) for s in
                     ("original", "after_clahe", "after_flatfield",
                      "after_denoise", "final")))
    ok &= _check("enhance lowers illumination CoV on 15_test",
                 e.scores_after.illum < e.scores_before.illum)

    print(f"\n{'ALL PASS' if ok else 'FAILURES ABOVE'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
