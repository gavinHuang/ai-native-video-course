#!/usr/bin/env python3
"""Measure motion cadence: are the frame-to-frame steps even? (C09·M04 frame-rate conversion)

  python cadence.py clip_24fps.mp4

A clip with smooth motion has similar changes between all neighbour frames. A frame-rate conversion by
duplicating frames (for example 16 -> 24 fps) makes a pattern of "no change" frames: the motion stutters
(judder). Frame blending makes ghost images. Motion interpolation makes even steps, with artifacts at edges
and fast motion. The tool reports:
  duplicate_pct : share of frame steps with almost no change (repeated frames)
  step_cv       : spread of the step sizes (standard deviation / mean). Low = even motion.
Needs ffmpeg and numpy.
"""
import argparse
import json
import subprocess
import sys

import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip")
    ap.add_argument("--width", type=int, default=160)
    a = ap.parse_args()
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                          "-of", "json", a.clip], capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    h = max(2, round(int(s["height"]) * a.width / int(s["width"]) / 2) * 2)
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", a.clip, "-vf", f"scale={a.width}:{h}", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                       capture_output=True)
    f = np.frombuffer(r.stdout, np.uint8).reshape(-1, h, a.width).astype(np.float32)
    if len(f) < 3:
        sys.exit("clip too short")
    steps = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    moving = steps[steps > 0.05]
    dup = float((steps < 0.25 * np.median(steps[steps > 0.05] if moving.size else steps + 1)).mean())
    rep = {"clip": a.clip, "fps": s["r_frame_rate"], "frames": int(len(f)), "mean_step": round(float(steps.mean()), 3),
           "duplicate_pct": round(100 * dup, 1), "step_cv": round(float(steps.std() / (steps.mean() + 1e-9)), 3)}
    print(json.dumps(rep))


if __name__ == "__main__":
    main()
