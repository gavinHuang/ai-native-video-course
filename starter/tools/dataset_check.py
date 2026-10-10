#!/usr/bin/env python3
"""Check a LoRA training dataset before you pay for training (C14·M01).

  python dataset_check.py training/mara/ --trigger mrx_mara [--bound "black bob,scar"] [--min-side 768]

Folder: one image per item (png, jpg, webp) with a caption file of the same name (.txt), and a rights.csv:
  file,source,license_or_consent,date
  01_front.png,generated (CHAR-MARA sheet),own,2026-10-04

Checks:
  - every image has a caption, every caption has an image; every caption starts with the trigger word
  - the shorter side is at least --min-side pixels; aspect ratios (for bucketing)
  - blur (variance of the Laplacian; low = soft or out of focus)
  - near duplicates (perceptual difference hash; duplicates over-weight one view)
  - "bound" features: identity features that you want the trigger to carry must NOT be in the captions
    (if the caption says "black bob" on every image, the model learns the bob from the words, not the trigger)
  - every image has a rights line
Exit code 1 if a problem is found. Warnings do not fail.
"""
import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

EXT = {".png", ".jpg", ".jpeg", ".webp"}


def dhash(img, size=8):
    g = img.convert("L").resize((size + 1, size), Image.LANCZOS)
    a = np.asarray(g, dtype=np.int16)
    return (a[:, 1:] > a[:, :-1]).flatten()


def blur_score(img):
    g = np.asarray(img.convert("L").resize((512, int(512 * img.height / img.width))), dtype=np.float32)
    lap = g[1:-1, 1:-1] * -4 + g[:-2, 1:-1] + g[2:, 1:-1] + g[1:-1, :-2] + g[1:-1, 2:]
    return float(lap.var())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--trigger", required=True)
    ap.add_argument("--bound", default="", help="comma-separated identity features that captions must not mention")
    ap.add_argument("--min-side", type=int, default=768)
    ap.add_argument("--blur-min", type=float, default=60.0)
    ap.add_argument("--dup-bits", type=int, default=5, help="max differing hash bits (of 64) for a near duplicate")
    a = ap.parse_args()
    root = Path(a.folder)
    images = sorted(p for p in root.iterdir() if p.suffix.lower() in EXT)
    caps = {p.stem: p for p in root.glob("*.txt")}
    problems, warnings = [], []
    rights = {}
    rp = root / "rights.csv"
    if rp.exists():
        rights = {r["file"]: r for r in csv.DictReader(open(rp))}
    else:
        problems.append("no rights.csv: every training item needs a source and a license or consent (C16)")
    bound = [b.strip().lower() for b in a.bound.split(",") if b.strip()]
    hashes, aspects = [], Counter()
    for p in images:
        img = Image.open(p)
        w, h = img.size
        aspects[f"{w / h:.2f}"] += 1
        if min(w, h) < a.min_side:
            problems.append(f"{p.name}: {w}x{h} is smaller than {a.min_side} px on the short side")
        b = blur_score(img)
        if b < a.blur_min:
            warnings.append(f"{p.name}: looks soft (sharpness {b:.0f} < {a.blur_min:g}); remove it unless softness is the style")
        hashes.append((p.name, dhash(img)))
        if p.stem not in caps:
            problems.append(f"{p.name}: no caption file {p.stem}.txt")
        else:
            text = caps[p.stem].read_text().strip()
            if not text.lower().startswith(a.trigger.lower()):
                problems.append(f"{p.stem}.txt: does not start with the trigger '{a.trigger}'")
            for f in bound:
                if f in text.lower():
                    warnings.append(f"{p.stem}.txt: mentions the bound feature '{f}' (let the trigger carry it)")
            if len(text.split()) < 6:
                warnings.append(f"{p.stem}.txt: very short caption; describe what VARIES (clothes, place, light, shot)")
        if rights and p.name not in rights:
            problems.append(f"{p.name}: no line in rights.csv")
    for stem in caps.keys() - {p.stem for p in images}:
        problems.append(f"{stem}.txt: caption without an image")
    for i in range(len(hashes)):
        for j in range(i + 1, len(hashes)):
            d = int((hashes[i][1] != hashes[j][1]).sum())
            if d <= a.dup_bits:
                warnings.append(f"near duplicates: {hashes[i][0]} and {hashes[j][0]} ({d} of 64 bits differ)")
    print(f"{len(images)} images, {len(caps)} captions; aspect ratios: {dict(aspects)}")
    for w in warnings:
        print("WARN   ", w)
    for p in problems:
        print("PROBLEM", p)
    print(f"{len(problems)} problems, {len(warnings)} warnings")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
