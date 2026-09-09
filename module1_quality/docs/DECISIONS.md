# Module 1 (Quality) — decisions

Every hardcoded threshold, parameter, dataset choice, algorithm choice, and
fallback gets a short entry: what was chosen, the alternatives, why this one,
and the word **UNTUNED** or **ASSUMPTION** wherever it applies.

This is a FEASIBILITY SLICE built on the night of Wed 9 Sep 2026 for the
Fri 11 Sep college-round slides and demo video. Nothing here is validated.

---

## D0 — Language: Python instead of MATLAB (this build night only)

**Chosen:** Python 3 with OpenCV / scikit-image / NumPy / Matplotlib.
**Alternative:** MATLAB with Image Processing Toolbox, as the plan specifies.
**Why:** No MATLAB installation exists on the build laptop and installing it
(multi-GB download + license activation) could not complete inside the
6:00pm-11:30pm window. Tonight's deliverable is a feasibility slice for slides
and a demo video, not the prototype. The plan already permits non-MATLAB for
practice work (gate G2, risk R18).
**Constraint honoured:** function names and returned struct/dict field names
match section 10 of `final_plan.md` exactly, so every slide claim stays true.
**MATLAB equivalents** (to be used in Phase 1):

| Tonight (Python) | Plan (MATLAB) |
|---|---|
| `cv2.createCLAHE` on L channel | `adapthisteq` |
| homomorphic / large-sigma background division | `imflatfield` |
| `cv2.fastNlMeansDenoising` | `imnlmfilt` |
| `cv2.Laplacian` variance | `fspecial('laplacian')` + `imfilter` + `var` |
| `skimage.measure.regionprops` | `regionprops` |
| `cv2.cvtColor(..., COLOR_RGB2LAB)` | `rgb2lab` / `lab2rgb` |

**ASSUMPTION:** OpenCV/skimage defaults are close enough to the MATLAB
functions for a feasibility demo. Not verified against MATLAB output.

---
