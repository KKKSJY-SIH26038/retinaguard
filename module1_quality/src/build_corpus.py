"""
Purpose: build tonight's image corpus for the Module 1 feasibility slice - 20
  "good" fundus images plus 6 deliberately damaged copies, one damage each.
How it works: it reads the 20 DRIVE test fundus photos, saves them as PNGs in
  data/raw/, then takes 6 of them and applies one synthetic defect to each
  (blur, darkening, vignette, heavy JPEG, a blacked-out slice, over-exposure)
  and saves those in data/degraded/. Every defect and its exact settings is
  written to data/DEGRADATION_LOG.md. The degraded images are SYNTHETIC and are
  labelled as such on every slide.
Does NOT yet: hand-pick the "good" set by eye (DRIVE test images are used as-is
  because they were curated for a segmentation benchmark), and does not model
  real-camera defects - these are crude stand-ins for a demo.
UNDERSTOOD-BY: (leave blank - a human fills this in)
Status: FEASIBILITY SLICE - untuned, not validated
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DRIVE_TEST = ROOT / "data" / "_dl" / "DRIVE" / "test" / "images"
RAW = ROOT / "data" / "raw"
DEG = ROOT / "data" / "degraded"

# 6 source images (by DRIVE test id) and the single defect applied to each.
DEGRADE_PLAN = {
    "01_test": "blur",
    "04_test": "dark",
    "08_test": "vignette",
    "11_test": "jpeg",
    "16_test": "partial",
    "19_test": "overexp",
}


def _read(path: Path) -> np.ndarray:
    """RGB uint8. cv2 first (BGR->RGB); PIL fallback for awkward TIFFs."""
    bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if bgr is not None:
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return np.asarray(Image.open(path).convert("RGB"))


def _write(path: Path, rgb: np.ndarray) -> None:
    cv2.imwrite(str(path), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))


def _fov_mask(rgb: np.ndarray) -> np.ndarray:
    """Rough circular field-of-view mask: red channel above a low threshold."""
    red = rgb[..., 0]
    return (red > 20).astype(np.uint8)


# --- the six defects -------------------------------------------------------

def deg_blur(rgb, log):
    sigma = 3.5
    log.append(f"gaussian blur, sigma={sigma} (cv2.GaussianBlur, kernel auto)")
    return cv2.GaussianBlur(rgb, (0, 0), sigma)


def deg_dark(rgb, log):
    factor = 0.40  # keep 40% of exposure -> reduced ~60%
    log.append(f"exposure x{factor} (linear multiply), i.e. reduced ~60%")
    return np.clip(rgb.astype(np.float32) * factor, 0, 255).astype(np.uint8)


def deg_vignette(rgb, log):
    h, w = rgb.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt((yy - h / 2) ** 2 + (xx - w / 2) ** 2)
    r = r / r.max()
    falloff = np.clip(1.10 - 2.10 * r ** 2, 0.05, 1.0)  # 1.0 centre -> ~0.3 FOV edge
    log.append("radial darkening: gain = clip(1.10 - 2.10*(r/rmax)^2, 0.05, 1.0)")
    return np.clip(rgb.astype(np.float32) * falloff[..., None], 0, 255).astype(np.uint8)


def deg_jpeg(rgb, log):
    quality = 15
    ok, buf = cv2.imencode(".jpg", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR),
                           [cv2.IMWRITE_JPEG_QUALITY, quality])
    log.append(f"JPEG quality={quality} then decoded and re-saved as PNG")
    return cv2.cvtColor(cv2.imdecode(buf, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)


def deg_partial(rgb, log):
    h, w = rgb.shape[:2]
    cut = int(round(0.25 * w))
    out = rgb.copy()
    out[:, :cut] = 0  # black out the leftmost 25%
    log.append(f"left {cut}px ({cut / w:.0%} of width) set to black")
    return out


def deg_overexp(rgb, log):
    gain, bias = 2.8, 55
    log.append(f"exposure raised: pixel*{gain} + {bias}, then clipped to 255")
    return np.clip(rgb.astype(np.float32) * gain + bias, 0, 255).astype(np.uint8)


DEFECTS = {
    "blur": deg_blur, "dark": deg_dark, "vignette": deg_vignette,
    "jpeg": deg_jpeg, "partial": deg_partial, "overexp": deg_overexp,
}


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    DEG.mkdir(parents=True, exist_ok=True)

    tifs = sorted(DRIVE_TEST.glob("*.tif"))
    if len(tifs) < 20:
        print(f"ERROR: expected >=20 DRIVE test images, found {len(tifs)} in {DRIVE_TEST}")
        return 1

    good_ids = []
    for tif in tifs[:20]:
        stem = tif.stem  # e.g. 01_test
        rgb = _read(tif)
        _write(RAW / f"{stem}.png", rgb)
        good_ids.append(stem)

    log_lines = [
        "# Degradation log - SYNTHETIC images",
        "",
        "**These 6 images are synthetic.** They are clean DRIVE test fundus photos",
        "with one deliberate defect applied in software, to show that the quality",
        "gate reacts to each failure mode. They are disclosed as synthetic on the",
        "slide. Source: DRIVE test set (Staal et al. 2004), 565x584 RGB.",
        "",
        "| Degraded file | Source | Defect | Exact operation |",
        "|---|---|---|---|",
    ]
    for src_id, kind in DEGRADE_PLAN.items():
        src = RAW / f"{src_id}.png"
        if not src.exists():
            print(f"ERROR: source {src} not in the good set")
            return 1
        rgb = _read(src)
        notes: list[str] = []
        out = DEFECTS[kind](rgb, notes)
        # keep background black outside the original FOV
        out = out * _fov_mask(rgb)[..., None]
        out_name = f"{kind}_{src_id}.png"
        _write(DEG / out_name, out.astype(np.uint8))
        log_lines.append(f"| `{out_name}` | `{src_id}.png` | {kind} | {'; '.join(notes)} |")

    (ROOT / "data" / "DEGRADATION_LOG.md").write_text("\n".join(log_lines) + "\n",
                                                      encoding="utf-8")

    corpus_lines = [
        "# Tonight's corpus",
        "",
        f"- **Good set (n={len(good_ids)}):** DRIVE test images, saved as PNG in `data/raw/`.",
        "  DRIVE test photos are used as-is as the 'good' set: they were curated for a",
        "  vessel-segmentation benchmark, so they are uniformly in-focus and well framed.",
        "  No further hand-selection was done tonight (ASSUMPTION - see DECISIONS.md).",
        f"- **Degraded set (n={len(DEGRADE_PLAN)}):** in `data/degraded/`, one synthetic",
        "  defect each, listed in `DEGRADATION_LOG.md`.",
        "",
        "IDs: " + ", ".join(good_ids),
        "",
        "Status: FEASIBILITY SLICE - untuned, not validated.",
        "",
    ]
    (ROOT / "data" / "CORPUS.md").write_text("\n".join(corpus_lines), encoding="utf-8")

    print(f"good: {len(good_ids)}  degraded: {len(DEGRADE_PLAN)}")
    print("wrote data/raw/, data/degraded/, data/DEGRADATION_LOG.md, data/CORPUS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
