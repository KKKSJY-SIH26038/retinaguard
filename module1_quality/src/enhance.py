"""
Purpose: clean up a fundus image that the quality gate marked "enhance" (or
  "reject" for a demo), keeping every intermediate step so each can be shown.
How it works: it boosts local contrast on the lightness channel only (CLAHE),
  then evens out slow background brightness changes by dividing out a heavily
  blurred copy of the image (flat-field), then does a light edge-preserving
  denoise, then puts the black border back. It re-scores the result so the
  before/after quality numbers can be shown side by side.
Does NOT yet: fix real blur, fill in a missing part of the retina, remove JPEG
  blocks, or tune any setting on labelled data - the clip limit, flat-field
  sigma and denoise strength are all hardcoded and UNTUNED (DECISIONS.md D6).
UNDERSTOOD-BY: (leave blank - a human fills this in)
Status: FEASIBILITY SLICE - untuned, not validated
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

try:
    from .preprocess import Pp, preprocess
    from .assessQuality import assessQuality
except ImportError:
    from preprocess import Pp, preprocess
    from assessQuality import assessQuality

# --- hardcoded, UNTUNED (see DECISIONS.md D6) ------------------------------
CLAHE_CLIP = 2.0          # modest: visible but not garish
CLAHE_TILE = 8            # 8x8 tiles on the 512px image
FLATFIELD_SIGMA = 55.0    # background blur, ~ 512/9; larger = gentler flattening
DENOISE_H = 3             # non-local-means strength; deliberately light so it does
                          # not soften the image (checked: blur score rises, not falls)


@dataclass
class Enhanced:
    """out = enhance(pp): every stage plus before/after scores."""
    original: np.ndarray
    after_clahe: np.ndarray
    after_flatfield: np.ndarray
    after_denoise: np.ndarray
    final: np.ndarray
    scores_before: object
    scores_after: object
    params: dict


def _clahe_L(rgb: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP, tileGridSize=(CLAHE_TILE, CLAHE_TILE))
    lab[..., 0] = clahe.apply(lab[..., 0])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)


def _flatfield(rgb: np.ndarray, mask: np.ndarray) -> np.ndarray:
    m = mask.astype(bool)
    out = rgb.astype(np.float32)
    for c in range(3):
        ch = out[..., c]
        bg = cv2.GaussianBlur(ch, (0, 0), FLATFIELD_SIGMA)
        target = float(bg[m].mean())
        ch = ch / np.maximum(bg, 1.0) * target
        out[..., c] = ch
    return np.clip(out, 0, 255).astype(np.uint8)


def _denoise(rgb: np.ndarray) -> np.ndarray:
    return cv2.fastNlMeansDenoisingColored(rgb, None, DENOISE_H, DENOISE_H, 7, 21)


def _as_pp(img512: np.ndarray, base: Pp) -> Pp:
    return Pp(img512=img512, imgFull=img512, fovMask=base.fovMask, meta=dict(base.meta))


def enhance(pp: Pp) -> Enhanced:
    mask3 = pp.fovMask[..., None]
    original = pp.img512.copy()

    after_clahe = _clahe_L(original) * mask3
    after_flatfield = _flatfield(after_clahe, pp.fovMask) * mask3
    after_denoise = _denoise(after_flatfield) * mask3
    final = after_denoise.astype(np.uint8)

    return Enhanced(
        original=original,
        after_clahe=after_clahe.astype(np.uint8),
        after_flatfield=after_flatfield.astype(np.uint8),
        after_denoise=after_denoise.astype(np.uint8),
        final=final,
        scores_before=assessQuality(pp).scores,
        scores_after=assessQuality(_as_pp(final, pp)).scores,
        params=dict(CLAHE_CLIP=CLAHE_CLIP, CLAHE_TILE=CLAHE_TILE,
                    FLATFIELD_SIGMA=FLATFIELD_SIGMA, DENOISE_H=DENOISE_H),
    )


def _run() -> int:
    root = Path(__file__).resolve().parents[1]
    deg = sorted((root / "data" / "degraded").glob("*.png"))
    borderline = ["15_test.png", "07_test.png", "04_test.png", "10_test.png"]
    targets = [("DEG", p) for p in deg] + \
              [("border", root / "data" / "raw" / n) for n in borderline]

    print(f"{'image':<22}{'blur b>a':>16}{'illum b>a':>16}{'expo b>a':>16}")
    print("-" * 70)
    better = 0
    for tag, p in targets:
        e = enhance(preprocess(p))
        b, a = e.scores_before, e.scores_after
        moved_ok = (a.illum <= b.illum + 1e-6) and (a.blur >= 0.6 * b.blur)
        better += moved_ok
        print(f"{p.name:<22}{f'{b.blur:.0f} > {a.blur:.0f}':>16}"
              f"{f'{b.illum:.3f} > {a.illum:.3f}':>16}"
              f"{f'{b.exposure:.0f} > {a.exposure:.0f}':>16}   {tag}")
    print("-" * 70)
    print(f"moved in the right direction: {better}/{len(targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_run())
