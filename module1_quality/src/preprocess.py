"""
Purpose: turn any fundus image file into a clean, square, consistently sized
  input for the rest of the pipeline, plus a mask of the real camera circle.
How it works: it reads the file, finds the bright circular region that is the
  camera's field of view (the retina disc) by thresholding the red channel and
  taking the largest blob, crops tightly to that circle, builds a matching
  circular mask so everything outside the retina is ignored, and returns both a
  full-resolution crop and a 512x512 version with the mask applied.
Does NOT yet: correct for tilted or non-circular fields of view, split an image
  that contains two eyes, or use any learned FOV detector - it is a single
  threshold-and-largest-blob rule.
UNDERSTOOD-BY: (leave blank - a human fills this in)
Status: FEASIBILITY SLICE - untuned, not validated
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

# --- hardcoded, chosen by eye tonight, UNTUNED (see DECISIONS.md D3) --------
RED_FOV_THRESHOLD = 20      # red-channel value above which a pixel is "inside the FOV"
OUT_SIZE = 512             # final square size for quality + grading
MIN_FOV_AREA_FRAC = 0.10   # a detected blob smaller than this fraction of the frame is rejected


@dataclass
class Pp:
    """Matches final_plan.md section 10: preprocess(imgPath) -> .img512 .imgFull .fovMask .meta"""
    img512: np.ndarray                     # 512x512x3 uint8, masked
    imgFull: np.ndarray                    # full-res crop to the FOV bounding box, uint8
    fovMask: np.ndarray                    # 512x512 uint8 {0,1}, the FOV circle at output size
    meta: dict = field(default_factory=dict)


def _read_rgb(img_path: str | Path) -> np.ndarray:
    """Always return HxWx3 uint8 RGB. Grayscale input is promoted to 3 channels."""
    bgr = cv2.imread(str(img_path), cv2.IMREAD_UNCHANGED)
    if bgr is None:
        arr = np.asarray(Image.open(img_path))
    else:
        arr = bgr
    if arr.ndim == 2:
        return np.repeat(arr[:, :, None], 3, axis=2).astype(np.uint8)
    if arr.shape[2] == 4:
        arr = arr[:, :, :3]
    if bgr is not None:  # cv2 gave BGR
        arr = arr[:, :, ::-1]
    if arr.dtype != np.uint8:
        arr = cv2.normalize(arr, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return np.ascontiguousarray(arr)


def _detect_fov(rgb: np.ndarray) -> tuple[float, float, float, bool]:
    """
    Return (cx, cy, radius, detected). Threshold the red channel low, take the
    largest connected component, use its centroid and equivalent-circle radius.
    """
    h, w = rgb.shape[:2]
    red = rgb[..., 0]
    binm = (red > RED_FOV_THRESHOLD).astype(np.uint8)
    binm = cv2.morphologyEx(binm, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

    n, labels, stats, centroids = cv2.connectedComponentsWithStats(binm, connectivity=8)
    if n <= 1:
        return w / 2, h / 2, min(h, w) / 2, False
    # component 0 is background
    idx = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    area = stats[idx, cv2.CC_STAT_AREA]
    if area < MIN_FOV_AREA_FRAC * h * w:
        return w / 2, h / 2, min(h, w) / 2, False
    cx, cy = centroids[idx]
    radius = float(np.sqrt(area / np.pi))  # equivalent-circle radius
    return float(cx), float(cy), radius, True


def _circle_mask(shape: tuple[int, int], cx: float, cy: float, r: float) -> np.ndarray:
    yy, xx = np.ogrid[:shape[0], :shape[1]]
    return (((xx - cx) ** 2 + (yy - cy) ** 2) <= r ** 2).astype(np.uint8)


def preprocess(img_path: str | Path) -> Pp:
    rgb = _read_rgb(img_path)
    h0, w0 = rgb.shape[:2]
    cx, cy, r, detected = _detect_fov(rgb)

    if detected:
        x0 = int(max(0, np.floor(cx - r)))
        x1 = int(min(w0, np.ceil(cx + r)))
        y0 = int(max(0, np.floor(cy - r)))
        y1 = int(min(h0, np.ceil(cy + r)))
        if x1 - x0 < 8 or y1 - y0 < 8:      # degenerate crop -> treat as no detection
            detected = False
    if not detected:
        x0, y0, x1, y1 = 0, 0, w0, h0

    crop = rgb[y0:y1, x0:x1]
    ch, cw = crop.shape[:2]

    if detected:
        mask_full = _circle_mask((ch, cw), cx - x0, cy - y0, r)
    else:
        mask_full = np.ones((ch, cw), np.uint8)   # no circle found -> trust the whole frame

    img_full = (crop * mask_full[..., None]).astype(np.uint8)

    img512 = cv2.resize(img_full, (OUT_SIZE, OUT_SIZE), interpolation=cv2.INTER_AREA)
    mask512 = cv2.resize(mask_full, (OUT_SIZE, OUT_SIZE), interpolation=cv2.INTER_NEAREST)
    img512 = (img512 * mask512[..., None]).astype(np.uint8)

    meta = {
        "path": str(img_path),
        "orig_size": (h0, w0),                     # (rows, cols)
        "fov_detected": bool(detected),
        "fov_center_orig": (round(cx, 1), round(cy, 1)),
        "fov_radius_orig": round(r, 1),
        "crop_box_xyxy": (x0, y0, x1, y1),
        "assumed_eye": "right",                    # ASSUMPTION - see DECISIONS.md D4
        "out_size": OUT_SIZE,
        "red_fov_threshold": RED_FOV_THRESHOLD,
    }
    return Pp(img512=img512, imgFull=img_full, fovMask=mask512, meta=meta)


def _demo() -> int:
    raw = Path(__file__).resolve().parents[1] / "data" / "raw"
    samples = sorted(raw.glob("*.png"))[:3]
    if not samples:
        print("no images in data/raw/ - run build_corpus.py first")
        return 1
    for s in samples:
        pp = preprocess(s)
        m = pp.meta
        print(f"{s.name}: detected={m['fov_detected']} "
              f"center={m['fov_center_orig']} r={m['fov_radius_orig']} "
              f"crop={m['crop_box_xyxy']} img512={pp.img512.shape} "
              f"coverage={pp.fovMask.mean():.3f}")
    # edge cases
    import numpy as _np
    blank = _np.zeros((300, 300), _np.uint8)
    tmp = Path(__file__).resolve().parents[1] / "data" / "raw" / "_edge_blank.png"
    cv2.imwrite(str(tmp), blank)
    pp = preprocess(tmp)
    print(f"edge (all-black grayscale): detected={pp.meta['fov_detected']} "
          f"mask_all_ones={bool(pp.fovMask.min() == 1)}")
    tmp.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
