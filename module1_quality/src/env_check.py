"""
Purpose: verify the Python image-processing stack that stands in for MATLAB's
  Image Processing Toolbox on the 9 Sep feasibility-slice build night.
How it works: imports every library the Module 1 slice needs, prints the
  version of each, then calls a tiny example of every MATLAB function named in
  the build prompt through its Python equivalent to confirm it actually runs on
  this machine. Writes the result to docs/ENV.md so a teammate can quote it.
Does NOT yet: check MATLAB itself (absent on this laptop), check GPU, or
  compare any Python output against MATLAB output.
UNDERSTOOD-BY: (leave blank - a human fills this in)
Status: FEASIBILITY SLICE - untuned, not validated
"""

from __future__ import annotations

import datetime as _dt
import platform
import sys
from pathlib import Path

import cv2
import numpy as np
import scipy
import skimage
from skimage import measure, color, filters

DOCS = Path(__file__).resolve().parents[1] / "docs"


def _mk_test_image() -> np.ndarray:
    """A small synthetic RGB 'fundus-like' disc on black, uint8."""
    h = w = 128
    yy, xx = np.mgrid[0:h, 0:w]
    disc = ((yy - h / 2) ** 2 + (xx - w / 2) ** 2) < (h * 0.45) ** 2
    img = np.zeros((h, w, 3), np.uint8)
    img[..., 0] = (disc * 180).astype(np.uint8)  # red channel bright, like a fundus
    img[..., 1] = (disc * 90).astype(np.uint8)
    img[..., 2] = (disc * 60).astype(np.uint8)
    return img


def check_equivalents() -> list[tuple[str, str, bool, str]]:
    """(matlab_name, python_equivalent, ok, note) for every function in the prompt."""
    img = _mk_test_image()
    green = img[..., 1]
    rows: list[tuple[str, str, bool, str]] = []

    def run(matlab: str, py: str, fn) -> None:
        try:
            fn()
            rows.append((matlab, py, True, ""))
        except Exception as exc:  # noqa: BLE001 - we want the message
            rows.append((matlab, py, False, f"{type(exc).__name__}: {exc}"))

    run("adapthisteq", "cv2.createCLAHE().apply",
        lambda: cv2.createCLAHE(2.0, (8, 8)).apply(green))
    run("imflatfield", "large-sigma background division (cv2.GaussianBlur)",
        lambda: green / (cv2.GaussianBlur(green.astype(np.float32), (0, 0), 25) + 1e-6))
    run("imnlmfilt", "cv2.fastNlMeansDenoising",
        lambda: cv2.fastNlMeansDenoising(green, None, 7, 7, 21))
    run("rgb2lab", "skimage.color.rgb2lab",
        lambda: color.rgb2lab(img))
    run("lab2rgb", "skimage.color.lab2rgb",
        lambda: color.lab2rgb(color.rgb2lab(img)))
    run("imfilter", "cv2.filter2D",
        lambda: cv2.filter2D(green, cv2.CV_64F, np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])))
    run("fspecial('laplacian')", "cv2.Laplacian",
        lambda: cv2.Laplacian(green, cv2.CV_64F))
    run("regionprops", "skimage.measure.regionprops",
        lambda: measure.regionprops(measure.label(green > 30)))
    run("imbinarize", "skimage.filters.threshold_otsu",
        lambda: green > filters.threshold_otsu(green))
    return rows


def main() -> int:
    now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    libs = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy": np.__version__,
        "opencv": cv2.__version__,
        "scikit-image": skimage.__version__,
        "scipy": scipy.__version__,
    }
    try:
        import matplotlib
        libs["matplotlib"] = matplotlib.__version__
    except Exception as exc:  # noqa: BLE001
        libs["matplotlib"] = f"MISSING ({exc})"

    rows = check_equivalents()
    all_ok = all(ok for _, _, ok, _ in rows)

    lines = [
        "# Module 1 - environment check",
        "",
        f"Run: {now} IST  ·  build laptop (Kavya's)",
        "",
        "## MATLAB",
        "",
        "MATLAB is **not installed** on this laptop. Per the build prompt this is a",
        "stop-and-ask point; Kavya approved the Python/OpenCV fallback for the",
        "9 Sep feasibility slice (see DECISIONS.md D0). Image Processing Toolbox,",
        "Computer Vision Toolbox, Deep Learning Toolbox, Medical Imaging Toolbox:",
        "**none present** (no MATLAB).",
        "",
        "## Python stack (stands in for Image Processing Toolbox tonight)",
        "",
        "| Component | Version |",
        "|---|---|",
    ]
    lines += [f"| {k} | {v} |" for k, v in libs.items()]
    lines += [
        "",
        "## MATLAB function equivalents - do they run here?",
        "",
        "| MATLAB function (from prompt) | Python equivalent | Runs? | Note |",
        "|---|---|---|---|",
    ]
    for matlab, py, ok, note in rows:
        lines.append(f"| `{matlab}` | `{py}` | {'yes' if ok else 'NO'} | {note} |")
    lines += [
        "",
        f"**All equivalents resolve: {'yes' if all_ok else 'NO - see table'}.**",
        "",
        "Status: FEASIBILITY SLICE - untuned, not validated.",
        "",
    ]

    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "ENV.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
