# Module 1 - environment check

Run: 2026-09-09 20:31 IST  ·  build laptop (Kavya's)

## MATLAB

MATLAB is **not installed** on this laptop. Per the build prompt this is a
stop-and-ask point; Kavya approved the Python/OpenCV fallback for the
9 Sep feasibility slice (see DECISIONS.md D0). Image Processing Toolbox,
Computer Vision Toolbox, Deep Learning Toolbox, Medical Imaging Toolbox:
**none present** (no MATLAB).

## Python stack (stands in for Image Processing Toolbox tonight)

| Component | Version |
|---|---|
| python | 3.14.6 |
| platform | Windows-11-10.0.26200-SP0 |
| numpy | 2.5.3 |
| opencv | 5.0.0 |
| scikit-image | 0.26.0 |
| scipy | 1.18.1 |
| matplotlib | 3.11.1 |

## MATLAB function equivalents - do they run here?

| MATLAB function (from prompt) | Python equivalent | Runs? | Note |
|---|---|---|---|
| `adapthisteq` | `cv2.createCLAHE().apply` | yes |  |
| `imflatfield` | `large-sigma background division (cv2.GaussianBlur)` | yes |  |
| `imnlmfilt` | `cv2.fastNlMeansDenoising` | yes |  |
| `rgb2lab` | `skimage.color.rgb2lab` | yes |  |
| `lab2rgb` | `skimage.color.lab2rgb` | yes |  |
| `imfilter` | `cv2.filter2D` | yes |  |
| `fspecial('laplacian')` | `cv2.Laplacian` | yes |  |
| `regionprops` | `skimage.measure.regionprops` | yes |  |
| `imbinarize` | `skimage.filters.threshold_otsu` | yes |  |

**All equivalents resolve: yes.**

Status: FEASIBILITY SLICE - untuned, not validated.
