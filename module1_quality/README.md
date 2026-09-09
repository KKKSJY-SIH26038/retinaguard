# module1_quality — Image Quality Assessment & Enhancement (feasibility slice)

Built the night of Wed 9 Sep 2026 for the Fri 11 Sep college round. This is a
**feasibility slice** for slides and a demo video, not the prototype. MATLAB was
not available on the build laptop, so it is written in Python against
OpenCV / scikit-image, with function names and returned fields matching
section 10 of `../final_plan.md`. See `docs/DECISIONS.md` D0 for the MATLAB
equivalents.

## Scope (WBS 1.1, 1.2, 1.4, 1.6 only)

- `src/preprocess.py` — `preprocess(imgPath)` → FOV crop, circular mask, 512×512
- `src/assessQuality.py` — `assessQuality(pp)` → blur / illumination / coverage
  (+ exposure, blockiness) → good | enhance | reject + operator feedback
- `src/enhance.py` — `enhance(pp)` → CLAHE → flat-field → denoise, every stage kept
- `src/build_corpus.py` — 20 DRIVE images + 6 synthetic degradations
- `src/makeFigures.py` — the three slide figures in `figs/`
- `src/demo.py` — one image end-to-end, for the recording

Not done tonight: 1.3 (threshold tuning on EyeQ), 1.5 (learned gradability),
1.7 (augmentation set).

## Run it

```
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python src\build_corpus.py       # needs a Kaggle API key at ~/.kaggle/kaggle.json
python src\assessQuality.py      # prints the 26-image table
python src\enhance.py            # prints before/after scores
python src\makeFigures.py        # writes figs/
python tests\test_module1.py     # smoke tests
```

## Docs

- `docs/ENV.md` — environment check
- `docs/DECISIONS.md` — every threshold and choice, with UNTUNED / ASSUMPTION
- `docs/QUALITY_TABLE.md`, `docs/ENHANCE_TABLE.md` — result tables
- `docs/RECORDING_SCRIPT.md` — 90-second demo commands
- `docs/EXPLAINER.md` — 200-word whiteboard version
- `LEDGER.md` — what happened and when
