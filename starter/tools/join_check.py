#!/usr/bin/env python3
"""Check a join between two clips, or the join of a loop (C05·M02, C05·M03). Needs ffmpeg and numpy.

  python join_check.py --loop loop.mp4               # last frame -> first frame of the same clip
  python join_check.py clipA.mp4 clipB.mp4           # end of A -> start of B (a chained or matched cut)

The tool reads small grey frames (160 px wide) near the join and compares:
  step_inside : median change between neighbour frames inside the clips (normal motion)
  step_join   : change across the join
  jump_ratio  : step_join / step_inside.  About 1 = seamless. Above 3 = a visible jump.
  color_shift : mean RGB change across the join (a chained clip often drifts warmer or darker)
Result: SEAMLESS, COLOR SHIFT (motion is continuous, color jumps by more than --max-shift), or VISIBLE JUMP.

Calibration (2026-10-04, a photo with a slow push-in, cut at frame 48):
  continuous -> 1.32 SEAMLESS;  warmed second half -> 1.51, shift +6.2/-7.4 -> COLOR SHIFT;
  8 frames skipped -> 6.31 VISIBLE JUMP;  a different shot -> 20.9 VISIBLE JUMP.

A cut between different shots (a real edit cut) has a high ratio on purpose. Use this tool for joins that
must NOT be seen: loops, chained clips, first/last-frame transitions.
"""
import argparse
import json
import subprocess
import sys

import numpy as np

W = 160


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets",
                          "-show_entries", "stream=width,height,nb_read_packets,r_frame_rate", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    num, den = map(int, s["r_frame_rate"].split("/"))
    return int(s["width"]), int(s["height"]), int(s["nb_read_packets"]), num / den


def frames(path, first, count, color=False):
    w, h, n, fps = probe(path)
    hh = max(2, round(h * W / w / 2) * 2)
    first = max(0, min(first, n - count))
    pix = "rgb24" if color else "gray"
    ch = 3 if color else 1
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"select='between(n\\,{first}\\,{first + count - 1})',scale={W}:{hh}",
           "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", pix, "-"]  # ffmpeg 5.1 or newer
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg failed on {path}: {r.stderr.decode(errors='replace')[-600:]}")
    raw = r.stdout
    arr = np.frombuffer(raw, np.uint8).astype(np.float32)
    return arr.reshape(-1, hh, W, ch) if ch == 3 else arr.reshape(-1, hh, W)


def step(a, b):
    return float(np.abs(a - b).mean())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clips", nargs="*")
    ap.add_argument("--loop")
    ap.add_argument("--window", type=int, default=8, help="frames on each side of the join")
    ap.add_argument("--max-ratio", type=float, default=3.0)
    ap.add_argument("--max-shift", type=float, default=4.0, help="largest allowed mean RGB change across the join")
    a = ap.parse_args()
    if a.loop:
        A = B = a.loop
    elif len(a.clips) == 2:
        A, B = a.clips
    else:
        sys.exit("give --loop clip.mp4, or two clips")
    _, _, nA, _ = probe(A)
    end = frames(A, nA - a.window, a.window)
    start = frames(B, 0, a.window)
    inside = [step(end[i], end[i + 1]) for i in range(len(end) - 1)] + \
             [step(start[i], start[i + 1]) for i in range(len(start) - 1)]
    s_in = float(np.median(inside)) or 1e-6
    s_join = step(end[-1], start[0])
    endc = frames(A, nA - 1, 1, color=True)[0]
    startc = frames(B, 0, 1, color=True)[0]
    shift = (startc - endc).reshape(-1, 3).mean(axis=0)
    ratio = s_join / s_in
    if ratio > a.max_ratio:
        result = "VISIBLE JUMP"
    elif float(np.abs(shift).max()) > a.max_shift:
        result = "COLOR SHIFT"  # motion continues, but the color jumps: match the anchor frame (C05·M03)
    else:
        result = "SEAMLESS"
    rep = {"join": f"{A} -> {B}" if A != B else f"loop {A}", "step_inside": round(s_in, 2),
           "step_join": round(s_join, 2), "jump_ratio": round(ratio, 2),
           "color_shift_rgb": [round(float(v), 2) for v in shift], "result": result}
    print(json.dumps(rep, indent=2))
    sys.exit(0 if result == "SEAMLESS" else 1)


if __name__ == "__main__":
    main()
