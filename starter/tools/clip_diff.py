#!/usr/bin/env python3
"""Compare an edited clip with its source, frame by frame (C05·M05, C09·M03). Needs ffmpeg and numpy.

  python clip_diff.py source.mp4 edited.mp4 --box 600,300,900,700     # area that may change (x0,y0,x1,y1, source pixels)
  python clip_diff.py source.mp4 edited.mp4 --box ... --samples 24 --csv per_frame.csv

For sampled frames it reports, outside the box: mean absolute difference, and the signed mean change of
R, G, B (a relight or a color drift). Inside the box it reports the mean difference (did the edit happen?).
Edit models often change the whole frame a little; this shows where and when.

Pass rule (defaults): outside mean diff <= 4.0 and every outside channel shift <= 2.0 in all sampled frames.
"""
import argparse
import csv
import json
import subprocess
import sys

import numpy as np

W = 320


def info(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets",
                          "-show_entries", "stream=width,height,nb_read_packets", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    return int(s["width"]), int(s["height"]), int(s["nb_read_packets"])


def read(path, n_frames, idx, w_out, h_out):
    sel = "+".join(f"eq(n\\,{i})" for i in idx)
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"select='{sel}',scale={w_out}:{h_out}",
           "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg failed on {path}: {r.stderr.decode(errors='replace')[-500:]}")
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, h_out, w_out, 3).astype(np.float32)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("edited")
    ap.add_argument("--box", help="x0,y0,x1,y1 in source pixels: the area that may change")
    ap.add_argument("--samples", type=int, default=12)
    ap.add_argument("--csv")
    ap.add_argument("--max-mean", type=float, default=4.0)
    ap.add_argument("--max-shift", type=float, default=2.0)
    a = ap.parse_args()
    sw, sh, sn = info(a.source)
    ew, eh, en = info(a.edited)
    n = min(sn, en)
    if sn != en:
        print(f"note: frame counts differ ({sn} vs {en}); comparing the first {n}", file=sys.stderr)
    h_out = max(2, round(sh * W / sw / 2) * 2)
    idx = sorted({round(k * (n - 1) / max(a.samples - 1, 1)) for k in range(a.samples)})
    A = read(a.source, n, idx, W, h_out)
    B = read(a.edited, n, idx, W, h_out)
    mask = np.zeros((h_out, W), bool)
    if a.box:
        x0, y0, x1, y1 = map(int, a.box.split(","))
        sx, sy = W / sw, h_out / sh
        mask[int(y0 * sy):int(y1 * sy), int(x0 * sx):int(x1 * sx)] = True
    rows, fail = [], False
    for i, (fa, fb) in zip(idx, zip(A, B)):
        d = fb - fa
        out = d[~mask]
        row = {"frame": i, "outside_mean": round(float(np.abs(out).mean()), 2),
               "shift_r": round(float(out[:, 0].mean()), 2), "shift_g": round(float(out[:, 1].mean()), 2),
               "shift_b": round(float(out[:, 2].mean()), 2)}
        if mask.any():
            row["inside_mean"] = round(float(np.abs(d[mask]).mean()), 2)
        bad = row["outside_mean"] > a.max_mean or max(abs(row[k]) for k in ("shift_r", "shift_g", "shift_b")) > a.max_shift
        row["ok"] = not bad
        fail |= bad
        rows.append(row)
    if a.csv:
        with open(a.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    worst = max(rows, key=lambda r: r["outside_mean"])
    summary = {"frames_compared": len(rows), "worst_frame": worst["frame"], "worst_outside_mean": worst["outside_mean"],
               "mean_shift_rgb": [round(float(np.mean([r[k] for r in rows])), 2) for k in ("shift_r", "shift_g", "shift_b")],
               "failed_frames": [r["frame"] for r in rows if not r["ok"]],
               "result": "FAIL: the edit changed areas outside the box" if fail else "PASS"}
    if mask.any():
        summary["inside_mean"] = round(float(np.mean([r["inside_mean"] for r in rows])), 2)
    print(json.dumps(summary, indent=2))
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
