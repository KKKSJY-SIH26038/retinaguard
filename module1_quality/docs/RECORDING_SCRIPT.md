# Module 1 - screen recording script (~90 seconds)

Commands only, in order. Run from `module1_quality/`. One terminal, one file
window per step. Total run time well under 90 s; the pauses are for narration.

## Setup (before recording)

```
cd module1_quality
.venv\Scripts\activate
```

## Take 1 - a good image  (~20 s)

```
python src\demo.py data\raw\09_test.png
```
- Terminal prints: `decision : GOOD`, the five scores, no feedback line.  (~2 s)
- One window opens: preprocessed image + 16-cell illumination map, evenly lit.
- Cue: "clean image, all four checks pass, it goes straight to grading."
- Close the window to continue.

## Take 2 - an image that needs enhancement  (~35 s)

```
python src\demo.py data\raw\15_test.png
```
- Terminal prints: `decision : ENHANCE` and the feedback line about uneven
  lighting and slight under-exposure.  (~2 s)
- Window 1: illumination map shows a bright centre, darker edges.
- Window 2 opens (~3 s to compute): original -> CLAHE -> flat-field -> final,
  with `illum CoV 0.33 -> 0.11` in the title.
- Cue: "borderline image, fixed automatically, then graded."
- Close both windows.

## Take 3 - a rejected image  (~30 s)

```
python src\demo.py data\degraded\blur_01_test.png
```
- Terminal prints: `decision : REJECT` and `Image rejected: too blurred.
  Steady the camera and retake.`  (~2 s)
- Window 1: preprocessed image is visibly soft.
- Window 2: enhancement stages - note the final is still soft (enhancement does
  not fix real blur; that is why it was rejected, not enhanced).
- Cue: "unusable image caught at capture, with a specific instruction for the
  camera operator - no wasted grader time, no patient recall."
- Close windows. End recording.

## If a window does not open
`demo.py` uses the default matplotlib backend. If nothing appears, run once:
`python -c "import matplotlib;print(matplotlib.get_backend())"` and set
`MPLBACKEND=TkAgg` before re-running.
