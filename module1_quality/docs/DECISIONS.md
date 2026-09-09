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
| vignette | gain = clip(1.10 - 2.10 r^2, 0.05, 1.0) | UNTUNED, strengthened after the first run so it clearly fails |
| jpeg | JPEG quality = 15 | UNTUNED, low end of the prompt's "~15" |
| partial | left 25% of width blacked out | matches the prompt |
| overexp | pixel x2.8 + 55, clipped | UNTUNED, strengthened so highlights clip hard |

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
`assessQuality` does NOT rely on this: it locates the nasal side from the optic
disc (the brightest large patch on the retina, which sits nasally). The
`assumed_eye` field is kept only as a documented fallback if disc detection
fails. Vertical labels (superior / inferior) are pure image geometry.

---

## D5 — Quality scores and thresholds (assessQuality.py)

**Scores.** The plan (section 10) names three: `blur`, `illum`, `fov`
(coverage). Two more were added tonight because the corpus's `dark` and
`overexp` images are global-exposure failures and the `jpeg` image is a
compression failure, none of which the three plan scores can see:

| Score | Meaning | Method |
|---|---|---|
| `blur` | sharpness, higher = sharper | variance of a 3x3 Laplacian over FOV pixels |
| `illum` | lighting unevenness, higher = worse | coefficient of variation across 8 sectors x 2 rings = 16 cells |
| `fov` | coverage, 1.0 = full circle | FOV blob area / (pi * expected-radius^2), expected radius = half the longer bounding-box side |
| `exposure` | mean FOV green, 0-255 | added tonight - see above |
| `block` | JPEG blockiness, ~1.0 = clean | mean gradient on the 8px grid / off it, best of 8 phases, on the full-res image | added tonight |

**Thresholds — all UNTUNED, chosen by eye on tonight's 26 images:**

| Threshold | Value | Basis |
|---|---|---|
| `BLUR_REJECT` / `BLUR_GOOD` | 250 / 420 | clean DRIVE images scored 470-1510; the two blur/dark degradations dropped to 105-160 |
| `ILLUM_REJECT` / `ILLUM_GOOD` | 0.45 / 0.20 | clean median ~0.07; one genuinely uneven clean image (15_test) at 0.33 -> enhance; strong vignette at 0.29 |
| `COVERAGE_REJECT` / `COVERAGE_GOOD` | 0.90 / 0.965 | clean ~0.99; the 25%-occluded image at 0.82 |
| `EXPO_DARK_REJECT` | 42 | clean range 61-126; dark degradation at 37 |
| `EXPO_BRIGHT_REJECT` / `EXPO_CLIP_REJECT` | 200 / 0.12 | overexp degradation at 244 mean |
| `EXPO_GOOD_LO` / `EXPO_GOOD_HI` | 70 / 185 | keeps the clean set inside the good band |
| `BLOCK_REJECT` / `BLOCK_GOOD` | 1.55 / 1.20 | clean ~1.05; JPEG-q12 degradation at 3.6 |

**Adjustment made (logged in LEDGER.md):** the first threshold set left
`jpeg_11` and `partial_16` on "good". The blockiness score was moved to the
full-resolution image with an 8-phase grid search (the 512 resize had smeared
the grid), coverage was moved into `preprocess` in original geometry (the
square-pad resize had inflated it), and the vignette/overexp degradations were
strengthened. After that, all 6 degraded images land on reject and no clean
image is rejected. Result table: `docs/QUALITY_TABLE.md`.

**Decision order.** A low sharpness score also results from low contrast in a
dark or unevenly-lit image, so `_decide` checks coverage, blockiness, exposure
and lighting before attributing a failure to blur.

**Feedback strings** are written for a screening technician's screen: they name
the single worst problem, where it is, and the physical action to take.

**Does NOT do:** tune on EyeQ labels, use a learned gradability model, or output
a continuous quality score. `imgEnhanced` is left `None` here and filled by
`enhance.py` in the orchestrator.

---
