#!/usr/bin/env python3
"""Plot identity drift across the shots of a sequence (C05·M03).

  python identity_score.py --ref refs/CHAR-MARA/01_front.png --ref refs/CHAR-MARA/02_34.png \
      seq/S01.mp4 seq/S02.mp4 ... --json drift.json        # starter/tools/identity_score.py
  python drift_plot.py drift.json --out drift.png [--threshold 0.45]

The plot shows the median and minimum identity score per shot, in sequence order, and the threshold.
The text output gives the slope of the median per 10 shots: a negative slope means the identity drifts
as the sequence goes on (typical for chained generations without fresh references).
Needs matplotlib for the PNG; without it, only the text report is printed.
"""
import argparse
import json
import sys
from pathlib import Path


def slope(ys):
    n = len(ys)
    if n < 2:
        return 0.0
    mx = (n - 1) / 2
    my = sum(ys) / n
    num = sum((i - mx) * (y - my) for i, y in enumerate(ys))
    den = sum((i - mx) ** 2 for i in range(n))
    return num / den


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report")
    ap.add_argument("--out", default="drift.png")
    ap.add_argument("--threshold", type=float)
    a = ap.parse_args()
    rep = json.loads(Path(a.report).read_text())
    clips = rep["clips"]
    thr = a.threshold if a.threshold is not None else rep.get("threshold", 0.45)
    names = [Path(c["clip"]).stem for c in clips]
    med = [c["median"] for c in clips]
    mins = [c["min"] if c["min"] is not None else 0 for c in clips]
    s10 = slope(med) * 10
    below = [n for n, m in zip(names, med) if m < thr]
    # The trend uses only the passing shots: one failed shot is a reject, not a drift.
    kept = [m for m in med if m >= thr]
    trend = slope(kept) * 10
    print(f"{len(clips)} shots; median range {min(med):.2f}–{max(med):.2f}")
    print(f"trend of passing shots: {trend:+.3f} per 10 shots (all shots: {s10:+.3f})")
    print(f"below threshold {thr}: {', '.join(below) if below else 'none'}")
    if trend < -0.05:
        print("DRIFT: identity falls along the sequence. Re-anchor with fresh references, or train a LoRA (C14).")
    elif below:
        print("REJECTS: single shots fail, but there is no trend. Regenerate those shots.")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed: no PNG", file=sys.stderr)
        return
    fig, ax = plt.subplots(figsize=(max(6, len(clips) * 0.5), 3.2), dpi=120)
    x = range(len(clips))
    ax.plot(x, med, marker="o", label="median")
    ax.plot(x, mins, marker=".", linestyle=":", label="minimum")
    ax.axhline(thr, color="grey", linewidth=1, linestyle="--", label=f"threshold {thr}")
    ax.set_xticks(list(x))
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=8)
    ax.set_ylim(0, 1)
    ax.set_ylabel("identity (cosine)")
    ax.set_title(f"Identity across the sequence (trend of passing shots {trend:+.3f} / 10 shots)", fontsize=10)
    ax.legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig(a.out)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
