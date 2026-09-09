# Degradation log - SYNTHETIC images

**These 6 images are synthetic.** They are clean DRIVE test fundus photos
with one deliberate defect applied in software, to show that the quality
gate reacts to each failure mode. They are disclosed as synthetic on the
slide. Source: DRIVE test set (Staal et al. 2004), 565x584 RGB.

| Degraded file | Source | Defect | Exact operation |
|---|---|---|---|
| `blur_01_test.png` | `01_test.png` | blur | gaussian blur, sigma=3.5 (cv2.GaussianBlur, kernel auto) |
| `dark_04_test.png` | `04_test.png` | dark | exposure x0.4 (linear multiply), i.e. reduced ~60% |
| `vignette_08_test.png` | `08_test.png` | vignette | radial darkening: gain = clip(1.10 - 2.10*(r/rmax)^2, 0.05, 1.0) |
| `jpeg_11_test.png` | `11_test.png` | jpeg | JPEG quality=15 then decoded and re-saved as PNG |
| `partial_16_test.png` | `16_test.png` | partial | left 141px (25% of width) set to black |
| `overexp_19_test.png` | `19_test.png` | overexp | exposure raised: pixel*2.8 + 55, then clipped to 255 |
