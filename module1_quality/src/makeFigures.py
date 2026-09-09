"""
Purpose: export the three PNGs the slide deck needs from Module 1 - a rejected
  image with its feedback, an enhancement before/after strip, and a scatter of
  all 26 images by decision.
How it works: it runs preprocess / assessQuality / enhance on tonight's corpus
  and draws each figure with matplotlib at ~2500px wide on a white background,
  no default titles, with a small caption baked into the bottom of every image
  stating what it shows, the number of images, and that the thresholds are
  untuned.
Does NOT yet: pick the "best" example automatically in a smart way (a short
  hand-picked list is used), or render at print resolution.
UNDERSTOOD-BY: (leave blank - a human fills this in)
Status: FEASIBILITY SLICE - untuned, not validated
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

try:
    from .preprocess import preprocess
    from .assessQuality import assessQuality, illumination_overlay
    from .enhance import enhance
except ImportError:
    from preprocess import preprocess
    from assessQuality import assessQuality, illumination_overlay
    from enhance import enhance

ROOT = Path(__file__).resolve().parents[1]
RAW, DEG, FIGS = ROOT / "data" / "raw", ROOT / "data" / "degraded", ROOT / "figs"
DECISION_COLOR = {"good": "#2e7d32", "enhance": "#f9a825", "reject": "#c62828"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13,
                     "figure.facecolor": "white", "axes.facecolor": "white"})


def _caption(fig, text: str) -> None:
    import textwrap
    fig.text(0.5, 0.014, "\n".join(textwrap.wrap(text, 120)), ha="center",
             va="bottom", fontsize=10, color="#444444", style="italic")


def _bare(ax) -> None:
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


# --- figure 1 -------------------------------------------------------------

def fig1() -> None:
    src = DEG / "vignette_08_test.png"
    pp = preprocess(src)
    q = assessQuality(pp)
    overlay = illumination_overlay(pp)

    fig, axes = plt.subplots(1, 3, figsize=(18, 7))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.90, bottom=0.14, wspace=0.08)

    axes[0].imshow(pp.img512)
    axes[0].text(0.5, 1.04, "Captured image (rejected)", transform=axes[0].transAxes,
                 ha="center", fontsize=14)
    _bare(axes[0])

    im = axes[1].imshow(overlay, cmap="magma")
    axes[1].text(0.5, 1.04, "Illumination map - 16 cells, mean green",
                 transform=axes[1].transAxes, ha="center", fontsize=14)
    _bare(axes[1])
    cb = fig.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04)
    cb.set_label("mean green (0-255)")

    axes[2].set_facecolor("#12232e")
    axes[2].add_patch(plt.Rectangle((0, 0), 1, 1, transform=axes[2].transAxes,
                                    color="#12232e", zorder=0))
    axes[2].text(0.5, 0.9, "SCREENING STATION", transform=axes[2].transAxes,
                 ha="center", color="#9fb3c8", fontsize=13, family="monospace")
    axes[2].text(0.5, 0.72, "IMAGE REJECTED", transform=axes[2].transAxes,
                 ha="center", color="#ff6b6b", fontsize=22, fontweight="bold")
    import textwrap
    msg = q.feedback.split(": ", 1)[1] if ": " in q.feedback else q.feedback
    msg = msg[0].upper() + msg[1:]
    axes[2].text(0.5, 0.5, "\n".join(textwrap.wrap(msg, 34)),
                 transform=axes[2].transAxes, ha="center", va="center",
                 color="white", fontsize=16)
    axes[2].text(0.5, 0.16,
                 f"blur {q.scores.blur:.0f}   illum CoV {q.scores.illum:.2f}   "
                 f"exposure {q.scores.exposure:.0f}",
                 transform=axes[2].transAxes, ha="center", color="#9fb3c8",
                 fontsize=11, family="monospace")
    _bare(axes[2])

    _caption(fig, "Fig 1  Module 1 quality gate on a synthetic vignetted fundus image "
                  "(n=1 shown; corpus n=26). Thresholds untuned.")
    fig.savefig(FIGS / "fig1_reject_with_feedback.png", dpi=150)
    plt.close(fig)


# --- figure 2 -------------------------------------------------------------

def fig2() -> None:
    src = RAW / "15_test.png"           # the one clean image the gate sends to "enhance"
    e = enhance(preprocess(src))
    stages = [("Original", e.original), ("After CLAHE", e.after_clahe),
              ("After flat-field", e.after_flatfield), ("Final (denoised)", e.final)]
    b, a = e.scores_before, e.scores_after
    sub = [f"blur {b.blur:.0f} | illum {b.illum:.2f}", "L-channel contrast",
           "background evened", f"blur {a.blur:.0f} | illum {a.illum:.2f}"]

    fig, axes = plt.subplots(1, 4, figsize=(20, 6))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.88, bottom=0.16, wspace=0.06)
    for ax, (name, img), s in zip(axes, stages, sub):
        ax.imshow(img)
        ax.text(0.5, 1.05, name, transform=ax.transAxes, ha="center", fontsize=15)
        ax.text(0.5, -0.06, s, transform=ax.transAxes, ha="center", fontsize=12,
                color="#555555")
        _bare(ax)
    _caption(fig, "Fig 2  Enhancement stages on DRIVE 15_test, the one clean image the "
                  "gate routes to 'enhance' (n=1 shown). Illumination CoV "
                  f"{b.illum:.2f} -> {a.illum:.2f}. Settings untuned.")
    fig.savefig(FIGS / "fig2_enhance_before_after.png", dpi=150)
    plt.close(fig)


# --- figure 3 -------------------------------------------------------------

def fig3() -> None:
    good = sorted(RAW.glob("*.png"))
    deg = sorted(DEG.glob("*.png"))
    xs, ys, cs, labels = [], [], [], []
    for p in good + deg:
        q = assessQuality(preprocess(p))
        xs.append(q.scores.blur); ys.append(q.scores.illum)
        cs.append(DECISION_COLOR[q.decision])
        labels.append(p.stem.split("_")[0] if p in deg else None)

    fig, ax = plt.subplots(figsize=(13, 9))
    fig.subplots_adjust(left=0.09, right=0.95, top=0.93, bottom=0.16)
    ax.scatter(xs, ys, c=cs, s=90, edgecolors="black", linewidths=0.6, zorder=3)
    ax.set_xlim(min(xs) * 0.75, max(xs) * 1.7)
    for x, y, lab in zip(xs, ys, labels):
        if lab:
            ha = "right" if x > 2000 else "left"
            dx = -8 if ha == "right" else 8
            ax.annotate(lab, (x, y), textcoords="offset points", xytext=(dx, 6),
                        ha=ha, fontsize=11, fontweight="bold")

    from assessQuality import BLUR_REJECT, BLUR_GOOD, ILLUM_REJECT, ILLUM_GOOD
    for xv, style in [(BLUR_REJECT, "-"), (BLUR_GOOD, "--")]:
        ax.axvline(xv, color="#888888", ls=style, lw=1)
    for yv, style in [(ILLUM_REJECT, "-"), (ILLUM_GOOD, "--")]:
        ax.axhline(yv, color="#888888", ls=style, lw=1)
    ax.text(BLUR_REJECT, ax.get_ylim()[1], " blur reject", va="top", fontsize=9, color="#888")
    ax.text(BLUR_GOOD, ax.get_ylim()[1], " blur good", va="top", fontsize=9, color="#888")

    ax.set_xscale("log")
    ax.set_xlabel("blur score - variance of Laplacian (log scale, higher = sharper)")
    ax.set_ylabel("illumination CoV across 16 cells (higher = more uneven)")
    handles = [plt.Line2D([], [], marker="o", ls="", ms=11, mec="black",
                          mfc=c, label=k) for k, c in DECISION_COLOR.items()]
    ax.legend(handles=handles, loc="upper right", frameon=True)
    _caption(fig, "Fig 3  All 26 images (20 clean DRIVE + 6 synthetic degradations, "
                  "labelled) by blur and illumination, coloured by gate decision. "
                  "Lines = untuned thresholds (solid reject, dashed good). Red points "
                  "inside the clean zone (jpeg, partial, overexp) were rejected on "
                  "axes not plotted here - compression, coverage, exposure.")
    fig.savefig(FIGS / "fig3_score_distribution.png", dpi=200)
    plt.close(fig)


def main() -> int:
    FIGS.mkdir(exist_ok=True)
    fig1(); fig2(); fig3()
    readme = [
        "# Module 1 figures",
        "",
        "| File | Slide | Pixels |",
        "|---|---|---|",
        "| `fig1_reject_with_feedback.png` | quality-gate / recapture-feedback slide | 2700x1050 |",
        "| `fig2_enhance_before_after.png` | enhancement slide | 3000x900 |",
        "| `fig3_score_distribution.png` | 'the gate separates good from bad' slide | 2600x1800 |",
        "",
        "All: white background, no default titles, caption baked in at the bottom, "
        "thresholds untuned. Regenerate with `python src/makeFigures.py`.",
        "",
    ]
    (FIGS / "README.md").write_text("\n".join(readme), encoding="utf-8")
    for f in sorted(FIGS.glob("*.png")):
        print(f"{f.name}: {f.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
