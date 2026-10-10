#!/usr/bin/env python3
"""Two-pass loudness normalization to a target, with a report (C10·M02). Needs ffmpeg.

  python normalize.py mix.wav --target -14 --tp -1 --out mix_web.wav
  python normalize.py mix.wav --target -23 --tp -1 --out mix_broadcast.wav      # EBU R128 broadcast

Pass 1 measures the integrated loudness (LUFS), the loudness range (LRA), and the true peak.
Pass 2 applies ffmpeg loudnorm with the measured values in linear mode when possible: one gain change for
the whole program, so the mix keeps its dynamics. If the target plus the true-peak limit cannot be reached
with one gain (the peaks would go over), loudnorm switches to dynamic mode; the report says so, and then
you should fix the peaks in the mix (a true-peak limiter on the mix bus) and run it again.
A final pass measures the result.
"""
import argparse
import json
import re
import subprocess
import sys


def measure(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    t = r.stderr
    get = lambda pat: float(re.findall(pat, t)[-1])  # noqa: E731
    return {"I": get(r"I:\s+(-?[\d.]+) LUFS"), "LRA": get(r"LRA:\s+(-?[\d.]+) LU"), "TP": get(r"Peak:\s+(-?[\d.]+) dBFS")}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio")
    ap.add_argument("--target", type=float, default=-14.0)
    ap.add_argument("--tp", type=float, default=-1.0)
    ap.add_argument("--lra", type=float, default=11.0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    before = measure(a.audio)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", a.audio, "-af",
                        f"loudnorm=I={a.target}:TP={a.tp}:LRA={a.lra}:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    flt = (f"loudnorm=I={a.target}:TP={a.tp}:LRA={a.lra}:measured_I={m['input_i']}:measured_LRA={m['input_lra']}:"
           f"measured_TP={m['input_tp']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true:print_format=json")
    r2 = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-y", "-i", a.audio, "-af", flt, "-ar", "48000", "-c:a", "pcm_s24le", a.out],
                        capture_output=True, text=True)
    m2 = json.loads(r2.stderr[r2.stderr.rindex("{"):r2.stderr.rindex("}") + 1])
    after = measure(a.out)
    rep = {"before": before, "after": after, "mode": m2.get("normalization_type"), "target": a.target, "tp_max": a.tp,
           "pass": abs(after["I"] - a.target) <= 1.0 and after["TP"] <= a.tp + 0.1}
    print(json.dumps(rep, indent=2))
    if m2.get("normalization_type") == "dynamic":
        print("NOTE: dynamic mode was used (one gain could not meet the target and the peak limit). "
              "Limit the peaks on the mix bus and run again for a transparent result.")
    sys.exit(0 if rep["pass"] else 1)


if __name__ == "__main__":
    main()
