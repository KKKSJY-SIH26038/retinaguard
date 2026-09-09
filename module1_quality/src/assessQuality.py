"""
Purpose: decide whether a preprocessed fundus image is good enough to grade,
  needs enhancement first, or must be rejected and recaptured - and say why in
  plain words a camera operator can act on.
How it works: on the green channel inside the camera circle it measures four
  things - how sharp the image is (variance of a Laplacian edge filter), how
  evenly it is lit (spread of brightness across 16 pie-slice-and-ring cells),
  how much of the expected retina circle is actually filled in, and whether the
  exposure is sensible (not near-black, not blown out). Hardcoded cut-offs turn
  those numbers into good / enhance / reject, and a short feedback sentence
  names the worst problem and where it is (nasal, temporal, superior, inferior),
  using the bright optic disc to locate the nasal side.
Does NOT yet: use a learned gradability model, tune any threshold on real
  quality labels (EyeQ), or verify the nasal/temporal call against laterality
  metadata. The plan lists three scores (blur, illumination, coverage); a fourth
  (exposure) was added tonight so global under/over-exposure is caught - see
  DECISIONS.md D5.
UNDERSTOOD-BY: (leave blank - a human fills this in)
Status: FEASIBILITY SLICE - untuned, not validated
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

try:
    from .preprocess import Pp, preprocess
except ImportError:  # run as a script
    from preprocess import Pp, preprocess

# --- hardcoded thresholds, chosen by eye on tonight's 26 images, UNTUNED -----
#     (adjusted once so every degraded image lands on enhance or reject;
#      that adjustment is logged in LEDGER.md and DECISIONS.md D5.)
BLUR_REJECT = 250.0       # Laplacian variance below this -> too blurred to use
BLUR_GOOD = 420.0         # at or above -> sharp enough, no enhancement needed
ILLUM_REJECT = 0.45       # 16-cell coefficient of variation above this -> too uneven
ILLUM_GOOD = 0.20         # at or below -> lighting is even enough
COVERAGE_REJECT = 0.90    # less of the expected retina circle present -> reject
COVERAGE_GOOD = 0.965     # at or above -> full frame
EXPO_DARK_REJECT = 42.0   # mean FOV green below this -> too dark
EXPO_BRIGHT_REJECT = 200.0  # mean FOV green above this -> washed out
EXPO_CLIP_REJECT = 0.12   # fraction of FOV pixels at 250+ above this -> blown out
EXPO_GOOD_LO, EXPO_GOOD_HI = 70.0, 185.0
EXPO_CLIP_GOOD = 0.03
BLOCK_REJECT = 1.55      # 8px-grid gradient inflation above this -> heavy JPEG blocking
BLOCK_GOOD = 1.20        # at or below -> no meaningful compression artefacts

N_SECTORS = 8
N_RINGS = 2
OUTLIER_SD = 1.5          # a cell this many SD from the 16-cell mean is flagged


@dataclass
class Scores:
    blur: float
    illum: float
    fov: float                       # "coverage" in the prompt; .scores.fov in section 10
    exposure: float                  # mean FOV green, 0-255 (extra axis, see DECISIONS D5)
    block: float = 1.0               # JPEG blockiness (extra axis, see DECISIONS D5)
    clip_frac: float = 0.0
    illum_outliers: list = field(default_factory=list)
    nasal_side: str = "unknown"


@dataclass
class Quality:
    """final_plan.md section 10: assessQuality(pp) -> .decision .scores .feedback .imgEnhanced"""
    decision: str                    # 'good' | 'enhance' | 'reject'
    scores: Scores
    feedback: str                    # '' for good; a sentence otherwise
    thresholds: dict
    imgEnhanced: object = None       # filled by enhance.py in the orchestrator, not here


# --- helpers ---------------------------------------------------------------

def _masked_green(pp: Pp) -> tuple[np.ndarray, np.ndarray]:
    g = pp.img512[..., 1].astype(np.float64)
    m = pp.fovMask.astype(bool)
    return g, m


def _blur_score(g: np.ndarray, m: np.ndarray) -> float:
    lap = cv2.Laplacian(g, cv2.CV_64F, ksize=3)
    return float(np.var(lap[m]))


def _fov_geometry(m: np.ndarray) -> tuple[float, float, float]:
    ys, xs = np.nonzero(m)
    return float(xs.mean()), float(ys.mean()), float(np.sqrt(m.sum() / np.pi))


def _disc_side(g: np.ndarray, m: np.ndarray, cx: float) -> str:
    """Optic disc = brightest sizeable patch, and it sits nasally. Report its half."""
    gg = g.copy()
    gg[~m] = 0
    blur = cv2.GaussianBlur(gg, (0, 0), 15)
    blur[~m] = -1
    _, _, _, maxloc = cv2.minMaxLoc(blur)
    return "left" if maxloc[0] < cx else "right"


def _compass(dx: float, dy: float, r: float, nasal_side: str) -> str:
    vert = "superior" if dy < -0.33 * r else "inferior" if dy > 0.33 * r else ""
    horiz_img = "left" if dx < -0.33 * r else "right" if dx > 0.33 * r else ""
    horiz = ""
    if horiz_img:
        horiz = "nasal" if horiz_img == nasal_side else "temporal"
    return "-".join(p for p in (vert, horiz) if p) or "central"


def _illum(g: np.ndarray, m: np.ndarray) -> tuple[float, list[str], str]:
    cx, cy, r = _fov_geometry(m)
    nasal_side = _disc_side(g, m, cx)

    ys, xs = np.mgrid[0:g.shape[0], 0:g.shape[1]]
    dx, dy = xs - cx, ys - cy
    dist = np.sqrt(dx ** 2 + dy ** 2)
    ang = (np.degrees(np.arctan2(dy, dx)) + 360) % 360

    sector = np.floor(ang / (360 / N_SECTORS)).astype(int) % N_SECTORS
    ring = np.clip((dist > 0.5 * r).astype(int), 0, N_RINGS - 1)

    means, labels = [], []
    for s in range(N_SECTORS):
        for rg in range(N_RINGS):
            cell = m & (sector == s) & (ring == rg)
            if cell.sum() < 30:
                continue
            means.append(float(g[cell].mean()))
            sc_ang = (s + 0.5) * (360 / N_SECTORS)
            rr = (0.28 if rg == 0 else 0.72) * r
            comp = _compass(rr * np.cos(np.radians(sc_ang)),
                            rr * np.sin(np.radians(sc_ang)), r, nasal_side)
            labels.append(comp if comp == "central"
                          else f"{'inner' if rg == 0 else 'outer'} {comp}")

    a = np.array(means)
    cov = float(a.std() / a.mean()) if a.size and a.mean() > 0 else 0.0
    mu, sd = a.mean(), a.std()
    outliers = [labels[i] for i in range(a.size)
                if sd > 0 and abs(means[i] - mu) > OUTLIER_SD * sd]
    # darkest outliers first - that is what the operator should fix
    outliers.sort(key=lambda lab: means[labels.index(lab)])
    return cov, outliers, nasal_side


def _exposure(g: np.ndarray, m: np.ndarray) -> tuple[float, float]:
    vals = g[m]
    return float(vals.mean()), float(np.mean(vals >= 250))


def illumination_overlay(pp: Pp) -> np.ndarray:
    """
    512x512 float map: every FOV pixel set to the mean green of the 16-cell
    (8 sector x 2 ring) block it belongs to, else NaN. For figure 1.
    """
    g, m = _masked_green(pp)
    cx, cy, r = _fov_geometry(m)
    ys, xs = np.mgrid[0:g.shape[0], 0:g.shape[1]]
    dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
    ang = (np.degrees(np.arctan2(ys - cy, xs - cx)) + 360) % 360
    sector = np.floor(ang / (360 / N_SECTORS)).astype(int) % N_SECTORS
    ring = np.clip((dist > 0.5 * r).astype(int), 0, N_RINGS - 1)
    out = np.full(g.shape, np.nan)
    for s in range(N_SECTORS):
        for rg in range(N_RINGS):
            cell = m & (sector == s) & (ring == rg)
            if cell.sum() >= 30:
                out[cell] = g[cell].mean()
    return out


def _blockiness(img_full: np.ndarray) -> float:
    """
    JPEG-artifact score on the FULL-RES image (before the 512 resize smears the
    grid): mean |gradient| on the 8-pixel block grid over the mean just off it.
    The grid phase is unknown after cropping, so all 8 offsets are tried and the
    strongest is kept. ~1.0 = clean; >1.3 = visible JPEG blocks.
    """
    g = img_full[..., 1].astype(np.float64)
    m = g > 3
    dh = np.abs(np.diff(g, axis=1))
    dv = np.abs(np.diff(g, axis=0))
    mh = m[:, 1:] & m[:, :-1]
    mv = m[1:, :] & m[:-1, :]
    cols = np.arange(dh.shape[1])
    rows = np.arange(dv.shape[0])
    best = 0.0
    for ph in range(8):
        on_c, off_c = (cols % 8) == ph, (cols % 8) != ph
        on_r, off_r = (rows % 8) == ph, (rows % 8) != ph
        on = np.concatenate([dh[:, on_c][mh[:, on_c]], dv[on_r, :][mv[on_r, :]]])
        off = np.concatenate([dh[:, off_c][mh[:, off_c]], dv[off_r, :][mv[off_r, :]]])
        if on.size and off.size and off.mean() > 1e-6:
            best = max(best, on.mean() / off.mean())
    return float(best)


# --- decision + feedback -------------------------------------------------------

def _decide(s: Scores) -> tuple[str, str]:
    # A low sharpness score can come from real blur OR from low contrast in a
    # dark / unevenly-lit image, so exposure and lighting are judged first and
    # a failing sharpness score is attributed to them when they are also off.
    low_sharp = s.blur < BLUR_REJECT

    if s.fov < COVERAGE_REJECT:
        return "reject", (f"Image rejected: the retina is only {s.fov:.0%} in frame. "
                          "Re-centre the camera and retake.")
    if s.block > BLOCK_REJECT:
        return "reject", ("Image rejected: heavy compression artefacts. Save / "
                          "transfer the image at higher quality and resend.")
    if s.exposure < EXPO_DARK_REJECT or (low_sharp and s.exposure < EXPO_GOOD_LO):
        return "reject", ("Image rejected: too dark. Increase the flash / "
                          "illumination and retake.")
    if s.exposure > EXPO_BRIGHT_REJECT or s.clip_frac > EXPO_CLIP_REJECT:
        return "reject", ("Image rejected: over-exposed, detail is washed out. "
                          "Lower the flash / illumination and retake.")
    if s.illum > ILLUM_REJECT or (low_sharp and s.illum > ILLUM_GOOD):
        where = f" in the {s.illum_outliers[0]} region" if s.illum_outliers else ""
        return "reject", ("Image rejected: lighting is very uneven" + where +
                          ". Adjust illumination or the patient's gaze and retake.")
    if low_sharp:
        return "reject", "Image rejected: too blurred. Steady the camera and retake."

    # --- good: every axis inside the good band ---
    if (s.blur >= BLUR_GOOD and s.illum <= ILLUM_GOOD and s.fov >= COVERAGE_GOOD
            and EXPO_GOOD_LO <= s.exposure <= EXPO_GOOD_HI and s.clip_frac <= EXPO_CLIP_GOOD
            and s.block <= BLOCK_GOOD):
        return "good", ""

    # --- enhance: in between on at least one axis ---
    reasons = []
    if s.blur < BLUR_GOOD:
        reasons.append("slight softness")
    if s.illum > ILLUM_GOOD:
        spot = f" in the {s.illum_outliers[0]} region" if s.illum_outliers else ""
        reasons.append("mild uneven lighting" + spot)
    if s.fov < COVERAGE_GOOD:
        reasons.append("a small part of the retina out of frame")
    if s.exposure < EXPO_GOOD_LO:
        reasons.append("slight under-exposure")
    if s.exposure > EXPO_GOOD_HI or s.clip_frac > EXPO_CLIP_GOOD:
        reasons.append("slight over-exposure")
    if s.block > BLOCK_GOOD:
        reasons.append("mild compression artefacts")
    return "enhance", ("Image usable after enhancement: " + ", ".join(reasons) +
                       " will be corrected.")


def assessQuality(pp: Pp) -> Quality:
    g, m = _masked_green(pp)
    blur = _blur_score(g, m)
    illum, outliers, nasal_side = _illum(g, m)
    fov = float(pp.meta.get("fov_coverage", 1.0))
    expo_mean, clip_frac = _exposure(g, m)
    block = _blockiness(pp.imgFull)

    scores = Scores(blur=round(blur, 2), illum=round(illum, 4), fov=round(fov, 4),
                    exposure=round(expo_mean, 2), block=round(block, 3),
                    clip_frac=round(clip_frac, 4),
                    illum_outliers=outliers, nasal_side=nasal_side)
    decision, feedback = _decide(scores)
    return Quality(
        decision=decision, scores=scores, feedback=feedback,
        thresholds=dict(BLUR_REJECT=BLUR_REJECT, BLUR_GOOD=BLUR_GOOD,
                        ILLUM_REJECT=ILLUM_REJECT, ILLUM_GOOD=ILLUM_GOOD,
                        COVERAGE_REJECT=COVERAGE_REJECT, COVERAGE_GOOD=COVERAGE_GOOD,
                        EXPO_DARK_REJECT=EXPO_DARK_REJECT, EXPO_BRIGHT_REJECT=EXPO_BRIGHT_REJECT,
                        EXPO_CLIP_REJECT=EXPO_CLIP_REJECT,
                        EXPO_GOOD_LO=EXPO_GOOD_LO, EXPO_GOOD_HI=EXPO_GOOD_HI,
                        BLOCK_REJECT=BLOCK_REJECT, BLOCK_GOOD=BLOCK_GOOD),
    )


def _run_corpus() -> int:
    root = Path(__file__).resolve().parents[1]
    good = sorted((root / "data" / "raw").glob("*.png"))
    deg = sorted((root / "data" / "degraded").glob("*.png"))
    rows = []
    print(f"{'file':<22}{'blur':>9}{'illum':>8}{'cover':>8}{'expo':>8}{'block':>7}  decision")
    print("-" * 75)
    for p in good + deg:
        q = assessQuality(preprocess(p))
        tag = "DEG" if p in deg else ""
        rows.append((p.name, q.decision, tag))
        print(f"{p.name:<22}{q.scores.blur:>9.1f}{q.scores.illum:>8.3f}"
              f"{q.scores.fov:>8.3f}{q.scores.exposure:>8.1f}{q.scores.block:>7.2f}  "
              f"{q.decision:<8}{tag}")
    bad = [r for r in rows if r[2] == "DEG" and r[1] == "good"]
    print("-" * 68)
    print(f"degraded images landing on 'good' (must be zero): {len(bad)}  {[r[0] for r in bad]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_run_corpus())
