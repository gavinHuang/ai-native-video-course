#!/usr/bin/env python3
"""Scopes and exposure numbers for a frame or a clip (C09·M01, C09·M02). Needs ffmpeg.

  python scopes.py shot.mp4 --at 2.0 --out scopes_S07.png       # waveform + vectorscope + histogram of one frame
  python scopes.py shot.mp4 --stats                             # numbers for the whole clip

Numbers (from ffmpeg signalstats, 8-bit code values, video range 16–235 for luma):
  luma min / max / mean : where the blacks and the whites are
  % near black / white  : share of pixels at or beyond the legal limits (clipped detail)
  saturation mean / max : overall color intensity (0 = grey)
Rules of thumb for Rec.709 web masters: blacks near 16 but not crushed over large areas, whites below 235,
skin tones on the skin-tone line of the vectorscope (about the 11 o'clock direction).
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def stats(path, at=None):
    args = ["ffmpeg", "-hide_banner", "-nostats"]
    if at is not None:
        args += ["-ss", str(at)]
    args += ["-i", path]
    if at is not None:
        args += ["-frames:v", "1"]
    args += ["-vf", "signalstats,metadata=print:file=-", "-f", "null", "-"]
    r = subprocess.run(args, capture_output=True, text=True)
    keys = ("YMIN", "YMAX", "YAVG", "SATAVG", "SATMAX", "YLOW", "YHIGH")
    vals = {k: [] for k in keys}
    for line in r.stdout.splitlines():
        m = re.match(r"lavfi\.signalstats\.(\w+)=([\d.]+)", line)
        if m and m.group(1) in vals:
            vals[m.group(1)].append(float(m.group(2)))
    if not vals["YAVG"]:
        sys.exit(f"no video frames read from {path}")
    out = {"frames": len(vals["YAVG"]),
           "luma_min": min(vals["YMIN"]), "luma_max": max(vals["YMAX"]),
           "luma_mean": round(sum(vals["YAVG"]) / len(vals["YAVG"]), 1),
           "sat_mean": round(sum(vals["SATAVG"]) / len(vals["SATAVG"]), 1), "sat_max": max(vals["SATMAX"]),
           "luma_10pct_low": round(min(vals["YLOW"]), 1), "luma_90pct_high": round(max(vals["YHIGH"]), 1)}
    return out


def clipped(path, at):
    """Share of pixels at the extremes in one frame (from a tiny grey image)."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(at), "-i", path, "-frames:v", "1", "-vf", "scale=320:-2,format=gray",
                        "-f", "rawvideo", "-"], capture_output=True)
    px = r.stdout
    n = len(px) or 1
    return round(100 * sum(1 for b in px if b <= 17) / n, 2), round(100 * sum(1 for b in px if b >= 234) / n, 2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip")
    ap.add_argument("--at", type=float, default=0.0, help="time of the frame (s)")
    ap.add_argument("--out", help="PNG with the frame, the waveform, the vectorscope, and the histogram")
    ap.add_argument("--stats", action="store_true", help="numbers for the whole clip")
    a = ap.parse_args()
    if a.out:
        tmp = Path(tempfile.mkdtemp(prefix="scopes_"))
        fc = ("[0:v]scale=640:-2,split=4[f][w][v][h];"
              "[w]waveform=graticule=green:flags=numbers+dots:scale=digital,scale=640:360[wf];"
              "[v]format=yuv444p,vectorscope=mode=color3:graticule=color:flags=name,scale=360:360[vs];"
              "[h]histogram=display_mode=overlay,scale=280:360[hs];"
              "[vs][hs]hstack[vh];[f]scale=640:360[ff];[ff][wf]hstack[top];[vh]pad=1280:360[bot];[top][bot]vstack")
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a.at), "-i", a.clip, "-frames:v", "1",
                            "-filter_complex", fc, a.out], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"ffmpeg failed: {r.stderr[-600:]}")
        print(f"wrote {a.out}")
    s = stats(a.clip, None if a.stats else a.at)
    if not a.stats:
        s["pct_at_black_16"], s["pct_at_white_235"] = clipped(a.clip, a.at)
    print(json.dumps(s, indent=2))


if __name__ == "__main__":
    main()
