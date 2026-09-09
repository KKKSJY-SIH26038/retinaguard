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

## D1 — Image corpus: DRIVE test set as the "good" 20

**Chosen:** the 20 DRIVE test images (Staal et al. 2004), Kaggle mirror
`andrewmvd/drive-digital-retinal-images-for-vessel-extraction`, ~28 MB.
**Alternatives:** DRIVE training set, STARE, APTOS, IDRiD.
**Why:** no account friction via the Kaggle API key already on this laptop;
under 30 MB; DRIVE images come from a real Dutch DR screening programme, which
is the right setting for this project; the test split is small and uniform.
**ASSUMPTION:** the "select 20 visually clean images" step was not done by a
human eye tonight. DRIVE test images are taken as-is because they were curated
for a segmentation benchmark and are uniformly in focus and well framed. A real
run would hand-check them.

## D2 — Six synthetic degradations

One defect per image, applied in `build_corpus.py`, logged in
`data/DEGRADATION_LOG.md`, disclosed as **SYNTHETIC** on the slide.

| Defect | Parameter | Note |
|---|---|---|
| blur | Gaussian sigma = 3.5 | UNTUNED, mid of the prompt's 3-4 range |
| dark | exposure x0.40 | UNTUNED, "reduced ~60%" |
| vignette | gain = clip(1.15 - 0.95 r^2, 0.15, 1.0) | UNTUNED, hand-shaped falloff |
| jpeg | JPEG quality = 15 | UNTUNED, low end of the prompt's "~15" |
| partial | left 25% of width blacked out | matches the prompt |
| overexp | pixel x2.2 + 40, clipped | UNTUNED, chosen so highlights clip |

These are crude stand-ins, not camera-accurate models. Their only job is to make
each failure axis of the quality gate visible in a demo.

---

## D3 — FOV detection and output size (preprocess.py)

**Method:** red channel > 20 -> morphological open -> largest connected
component -> centroid + equivalent-circle radius r = sqrt(area / pi).
**`RED_FOV_THRESHOLD = 20`** — UNTUNED, chosen by eye; the retina disc is far
brighter than the black surround in the red channel so the exact value barely
matters on DRIVE. A real run tunes this per camera.
**`OUT_SIZE = 512`** — matches the grading/quality input size in final_plan.md
section 5.4.
**`MIN_FOV_AREA_FRAC = 0.10`** — UNTUNED; a "largest blob" under 10% of the
frame is treated as a failed detection.
**Alternatives not used tonight:** Hough circle fit, Otsu threshold, a learned
FOV segmenter. The prompt says do not over-engineer this.
**Edge cases handled:** no blob / tiny blob / degenerate crop -> `fov_detected =
False`, mask set to all ones, whole frame trusted; image already cropped tight
-> crop box clamps to the image; image smaller than 512 -> upscaled by resize.
**Known limitation:** equivalent-circle radius slightly under-reads the true
circle when the FOV is clipped top/bottom (as in DRIVE). Acceptable for a demo.

## D4 — Assumed right eye

`meta.assumed_eye = "right"`. **ASSUMPTION.** DRIVE files carry no laterality.
The compass labels in `assessQuality` (nasal / temporal / superior / inferior)
depend on which eye it is; for a left eye, nasal and temporal swap. Tonight
everything is reported as if every image is a right eye. A real run reads
laterality from DICOM or file metadata.

---
