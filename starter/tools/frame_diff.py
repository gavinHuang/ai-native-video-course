#!/usr/bin/env python3
"""Measure what an edit changed. Use it after every instruction edit, inpaint, or upscale.

  python frame_diff.py before.png after.png --heatmap diff.png
  python frame_diff.py before.png after.png --mask mask.png        # report change inside / outside the mask
  python frame_diff.py before.png after.png --box 120,80,300,260   # the area that should change (x0,y0,x1,y1)

Output: mean absolute difference (0–255), the share of pixels that changed by more than --tol,
and the bounding box of the changed area. If the after image has another size, it is resized
to the before size first (and the report says so).

Pass rule outside the allowed area (defaults, calibrated on 2026-10-04 tests):
  - changed pixels <= 1 %, mean absolute difference <= 3.0 (a JPEG re-save at quality 90 gives about 0.8);
  - signed mean shift of each RGB channel, saturation, and brightness <= 1.5.
The signed shifts catch global color drift (warmer, more saturated) that compression noise does not cause.
"""
import argparse
import json
import sys

import numpy as np
from PIL import Image


def load(path, size=None):
    im = Image.open(path).convert("RGB")
    if size and im.size != size:
        im = im.resize(size, Image.LANCZOS)
    return np.asarray(im).astype(np.int16)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--mask", help="white = area that may change")
    ap.add_argument("--box", help="x0,y0,x1,y1 of the area that may change")
    ap.add_argument("--tol", type=int, default=12, help="per-channel change that counts as 'changed' (0–255)")
    ap.add_argument("--heatmap")
    ap.add_argument("--max-outside", type=float, default=1.0, help="fail if more than this % changed outside")
    ap.add_argument("--max-outside-mean", type=float, default=3.0, help="fail if the mean change outside is larger (0–255)")
    ap.add_argument("--max-shift", type=float, default=1.5,
                    help="fail if the mean signed change outside (per RGB channel, saturation, or brightness) is larger")
    a = ap.parse_args()

    b_img = Image.open(a.before)
    a_img = Image.open(a.after)
    resized = b_img.size != a_img.size
    b = load(a.before)
    x = load(a.after, b_img.size)
    d = np.abs(b - x).max(axis=2)  # largest channel change per pixel
    changed = d > a.tol

    allowed = np.zeros(d.shape, bool)
    if a.mask:
        allowed = np.asarray(Image.open(a.mask).convert("L").resize(b_img.size)) > 127
    if a.box:
        x0, y0, x1, y1 = map(int, a.box.split(","))
        allowed[y0:y1, x0:x1] = True

    ys, xs = np.nonzero(changed)
    report = {
        "size": list(b_img.size),
        "resized_after": resized,
        "mean_abs_diff": round(float(np.abs(b - x).mean()), 2),
        "changed_pct": round(100 * float(changed.mean()), 2),
        "changed_box": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1] if len(xs) else None,
    }
    if allowed.any():
        out = ~allowed
        report["changed_inside_pct"] = round(100 * float(changed[allowed].mean()), 2)
        report["changed_outside_pct"] = round(100 * float(changed[out].mean()), 2) if out.any() else 0.0
        diff = (x - b)[out]
        report["outside_mean_abs_diff"] = round(float(np.abs(diff).mean()), 2) if out.any() else 0.0
        # Signed mean change per channel: shows a global color drift, for example warmer or more saturated.
        report["outside_shift_rgb"] = [round(float(v), 2) for v in diff.mean(axis=0)] if out.any() else [0, 0, 0]
        hb = np.asarray(Image.fromarray(b.astype(np.uint8)).convert("HSV")).astype(np.int16)
        hx = np.asarray(Image.fromarray(x.astype(np.uint8)).convert("HSV")).astype(np.int16)
        report["outside_sat_shift"] = round(float((hx[..., 1] - hb[..., 1])[out].mean()), 2)
        report["outside_value_shift"] = round(float((hx[..., 2] - hb[..., 2])[out].mean()), 2)
    if a.heatmap:
        heat = np.clip(d * 4, 0, 255).astype(np.uint8)
        Image.fromarray(heat, "L").save(a.heatmap)
    print(json.dumps(report, indent=2))
    shifts = report.get("outside_shift_rgb", []) + [report.get("outside_sat_shift", 0), report.get("outside_value_shift", 0)]
    if allowed.any() and (report["changed_outside_pct"] > a.max_outside or
                          report["outside_mean_abs_diff"] > a.max_outside_mean or
                          max(abs(v) for v in shifts) > a.max_shift):
        print("FAIL: the edit changed the area outside the allowed region", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
