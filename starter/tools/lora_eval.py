#!/usr/bin/env python3
"""Evaluate LoRA checkpoints and choose one (C14·M02, C14·M03).

Render the same eval prompts with the same seeds for every checkpoint:
  eval/
    prompts.json            [{"id": "in01", "kind": "in"}, {"id": "out01", "kind": "out"}, {"id": "nt01", "kind": "no_trigger"}, ...]
    ckpt-0500/in01.png ...   one image per prompt (or a video: .mp4)
    ckpt-1000/...
    flex.csv                optional: checkpoint,prompt,score (1-5 adherence to the prompt, by a person or a calibrated LLM judge)

  python lora_eval.py eval/ --ref refs/CHAR-MARA/01_front.png --ref refs/CHAR-MARA/02_34.png --grid grid.png

Measures per checkpoint:
  fidelity : median identity on trigger prompts ("in" = like the training data, "out" = new clothes, places, styles)
  leakage  : median identity on no-trigger prompts (the character should NOT appear: low is good)
  flex     : mean prompt-adherence score on "out" prompts, from flex.csv (identity alone cannot see overfitting)
Choice rule: among checkpoints with fidelity >= --fidelity-min and leakage <= --leak-max, take the highest flex
(or, without flex.csv, the earliest checkpoint that passes: earlier = less overfit).
"""
import argparse
import csv
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--ref", action="append", required=True)
    ap.add_argument("--fidelity-min", type=float, default=0.5)
    ap.add_argument("--leak-max", type=float, default=0.3)
    ap.add_argument("--grid", help="write a labeled grid image: rows = checkpoints, columns = prompts")
    a = ap.parse_args()
    import cv2
    import numpy as np
    from identity_score import FaceScorer, frames
    root = Path(a.folder)
    prompts = json.loads((root / "prompts.json").read_text())
    kind = {p["id"]: p["kind"] for p in prompts}
    ckpts = sorted(d for d in root.iterdir() if d.is_dir())
    fs = FaceScorer()
    ref = np.mean([fs.embed(cv2.imread(r)) for r in a.ref], axis=0)
    ref /= np.linalg.norm(ref)
    flex = {}
    if (root / "flex.csv").exists():
        for r in csv.DictReader(open(root / "flex.csv")):
            flex.setdefault(r["checkpoint"], []).append(float(r["score"])) if kind.get(r["prompt"]) == "out" else None
    rows = []
    for c in ckpts:
        sc = {"in": [], "out": [], "no_trigger": []}
        for p in prompts:
            f = next(iter(sorted(c.glob(f"{p['id']}.*"))), None)
            if f is None:
                continue
            vals = []
            for _, img in frames(f, 8):
                e = fs.embed(img)
                vals.append(float(np.dot(e.ravel(), ref.ravel())) if e is not None else 0.0)
            sc[p["kind"]].append(statistics.median(vals) if vals else 0.0)
        fid = statistics.median(sc["in"] + sc["out"]) if sc["in"] + sc["out"] else 0.0
        leak = statistics.median(sc["no_trigger"]) if sc["no_trigger"] else 0.0
        fl = round(statistics.mean(flex[c.name]), 2) if c.name in flex else None
        rows.append({"checkpoint": c.name, "fidelity": round(fid, 3), "fidelity_out": round(statistics.median(sc["out"]), 3) if sc["out"] else None,
                     "leakage": round(leak, 3), "flex": fl,
                     "pass": fid >= a.fidelity_min and leak <= a.leak_max})
    print(f"{'checkpoint':14} {'fidelity':>8} {'(out)':>7} {'leakage':>8} {'flex':>5}  pass")
    for r in rows:
        print(f"{r['checkpoint']:14} {r['fidelity']:8.3f} {r['fidelity_out'] if r['fidelity_out'] is not None else '-':>7} "
              f"{r['leakage']:8.3f} {r['flex'] if r['flex'] is not None else '-':>5}  {'yes' if r['pass'] else 'no'}")
    ok = [r for r in rows if r["pass"]]
    if not ok:
        print("\nno checkpoint passes: fix the dataset (C14·M01) or the training settings")
    else:
        best = max(ok, key=lambda r: r["flex"]) if all(r["flex"] is not None for r in ok) else ok[0]
        why = "highest flexibility among passing checkpoints" if best["flex"] is not None else "earliest passing checkpoint"
        print(f"\nchoose {best['checkpoint']} ({why})")
    if a.grid:
        cells, h = [], 160
        for c in ckpts:
            row = []
            for p in prompts:
                f = next(iter(sorted(c.glob(f"{p['id']}.*"))), None)
                img = next(frames(f, 1))[1] if f else np.full((h, h, 3), 40, np.uint8)
                img = cv2.resize(img, (int(img.shape[1] * h / img.shape[0]), h))[:, :h]
                img = cv2.copyMakeBorder(img, 0, 0, 0, max(0, h - img.shape[1]), cv2.BORDER_CONSTANT)
                cv2.putText(img, p["id"], (4, 14), 0, 0.4, (255, 255, 255), 1)
                row.append(img)
            strip = np.hstack(row)
            label = np.zeros((h, 120, 3), np.uint8)
            cv2.putText(label, c.name, (4, h // 2), 0, 0.45, (255, 255, 255), 1)
            cells.append(np.hstack([label, strip]))
        cv2.imwrite(a.grid, np.vstack(cells))
        print(f"wrote {a.grid}")


if __name__ == "__main__":
    main()
