#!/usr/bin/env python3
"""Match the color of a shot to a reference shot, and write a 3D LUT (.cube) (C09·M02).

  python match_color.py --src S08.mp4 --ref S07.mp4 --out S08_to_S07.cube [--at 1.0] [--strength 0.8]
  ffmpeg -i S08.mp4 -vf lut3d=S08_to_S07.cube S08_matched.mp4          # apply it (or load the .cube in your NLE)

Method: the mean and the spread of each channel in CIE Lab are moved from the source toward the reference
(a statistical color transfer, Reinhard et al. 2001). It is a starting point for a shot match, not a grade:
it matches the overall balance, brightness, and contrast. Check skin and key colors by eye and on scopes after.

Report: the mean color difference (CIE76 Delta E, on the mean Lab values) between the shots before and after.
Delta E below about 2 is hard to see between two shots; above about 5 a cut shows the jump.
"""
import argparse
import json
import subprocess
import sys

import numpy as np

# sRGB <-> Lab (D65), vectorized
M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
MI = np.linalg.inv(M)
WP = np.array([0.95047, 1.0, 1.08883])


def srgb_to_lab(rgb):
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    xyz = c @ M.T / WP
    f = np.where(xyz > (6 / 29) ** 3, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def lab_to_srgb(lab):
    fy = (lab[..., 0] + 16) / 116
    fx = fy + lab[..., 1] / 500
    fz = fy - lab[..., 2] / 200
    f = np.stack([fx, fy, fz], -1)
    xyz = np.where(f > 6 / 29, f ** 3, 3 * (6 / 29) ** 2 * (f - 4 / 29)) * WP
    c = xyz @ MI.T
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def frames(path, at, n=5, w=320):
    """A few frames around 'at' (or across the clip if at is None), as float RGB 0..1."""
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                               capture_output=True, text=True).stdout or 1)
    times = [at] if at is not None else [dur * (k + 0.5) / n for k in range(n)]
    out = []
    for t in times:
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1", "-vf", f"scale={w}:-2",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
        if r.stdout:
            out.append(np.frombuffer(r.stdout, np.uint8).reshape(-1, 3).astype(np.float64) / 255)
    if not out:
        sys.exit(f"no frames from {path}")
    return np.concatenate(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--at", type=float, help="use one frame at this time in both clips (default: 5 frames across each clip)")
    ap.add_argument("--strength", type=float, default=1.0, help="0 = no change, 1 = full match")
    ap.add_argument("--size", type=int, default=33, help="LUT size (33 is standard)")
    a = ap.parse_args()
    S = srgb_to_lab(frames(a.src, a.at))
    R = srgb_to_lab(frames(a.ref, a.at))
    ms, ss = S.mean(0), S.std(0) + 1e-6
    mr, sr = R.mean(0), R.std(0) + 1e-6
    k = a.strength
    scale = 1 + k * (sr / ss - 1)
    shift_to = ms + k * (mr - ms)

    def transform(lab):
        return (lab - ms) * scale + shift_to

    n = a.size
    g = np.linspace(0, 1, n)
    # .cube order: red changes fastest, then green, then blue
    b, gg, r = np.meshgrid(g, g, g, indexing="ij")
    rgb = np.stack([r, gg, b], -1).reshape(-1, 3)
    out = lab_to_srgb(transform(srgb_to_lab(rgb)))
    with open(a.out, "w") as f:
        f.write(f'TITLE "match {a.src} -> {a.ref}"\nLUT_3D_SIZE {n}\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n')
        for v in out:
            f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
    after = transform(S)
    de_before = float(np.linalg.norm(S.mean(0) - mr))
    de_after = float(np.linalg.norm(after.mean(0) - mr))
    rep = {"lut": a.out, "strength": k, "delta_e_mean_before": round(de_before, 2), "delta_e_mean_after": round(de_after, 2),
           "L_mean": [round(ms[0], 1), round(mr[0], 1)], "a_mean": [round(ms[1], 1), round(mr[1], 1)],
           "b_mean": [round(ms[2], 1), round(mr[2], 1)], "L_spread": [round(ss[0], 1), round(sr[0], 1)]}
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
