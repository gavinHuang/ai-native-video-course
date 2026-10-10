#!/usr/bin/env python3
"""Make a seamless ambience loop, and measure the loop point (C06·M04). Needs ffmpeg and numpy.

  python loop_audio.py rain_90s.wav --out rain_loop.wav --xfade 2.0      # crossfade the end into the start
  python loop_audio.py rain_loop.wav --check                             # measure the join of an existing loop

How it works: the last --xfade seconds are faded out and mixed over the first --xfade seconds, which are
faded in (equal power). The result is shorter by --xfade seconds and plays end-to-start without a click.

The check compares the level change across the loop point with the normal level change between
neighbouring 10 ms blocks inside the file (like join_check.py does for video). Ratio about 1 = seamless;
above 3 = an audible step. It also reports the sample jump at the join (a click).
"""
import argparse
import subprocess
import sys

import numpy as np


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", "48000", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def save(path, x):
    p = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", "2", "-ar", "48000", "-i", "-",
                        "-c:a", "pcm_s24le", path], input=x.astype(np.float32).tobytes())
    if p.returncode:
        sys.exit("ffmpeg could not write the file")


def check(x, sr=48000):
    blk = sr // 100  # 10 ms
    n = len(x) // blk
    rms = np.sqrt((x[: n * blk].reshape(n, blk, 2) ** 2).mean(axis=(1, 2)) + 1e-12)
    db = 20 * np.log10(rms)
    inside = np.median(np.abs(np.diff(db)))
    join = abs(db[0] - db[-1])
    jump = float(np.abs(x[0] - x[-1]).max())
    typical = float(np.median(np.abs(np.diff(x, axis=0)).max(axis=1)))
    return {"level_step_inside_db": round(float(inside), 2), "level_step_join_db": round(float(join), 2),
            "ratio": round(float(join / (inside or 1e-6)), 2), "sample_jump": round(jump, 4),
            "typical_sample_step": round(typical, 4),
            "click": bool(jump > 8 * typical + 1e-4)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio")
    ap.add_argument("--out")
    ap.add_argument("--xfade", type=float, default=2.0)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    x = load(a.audio)
    sr = 48000
    if not a.check:
        n = int(a.xfade * sr)
        if len(x) < 3 * n:
            sys.exit("the file must be at least 3 times as long as the crossfade")
        t = np.linspace(0, np.pi / 2, n, dtype=np.float32)[:, None]
        head, tail = x[:n], x[-n:]
        mixed = tail * np.cos(t) + head * np.sin(t)  # equal-power crossfade: tail fades out, head fades in
        x = np.concatenate([mixed, x[n:-n]])
        if a.out:
            save(a.out, x)
            print(f"wrote {a.out}: {len(x) / sr:.2f} s")
    rep = check(x)
    ok = rep["ratio"] <= 3 and not rep["click"]
    print({**rep, "result": "SEAMLESS" if ok else "AUDIBLE JOIN"})
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
