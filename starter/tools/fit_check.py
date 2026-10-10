#!/usr/bin/env python3
"""Check that voice lines fit their time slots (C06·M01 voice-over, C06·M02 dubbing, C15·M02 localization).

  python fit_check.py slots.json --audio-dir vo_es/ [--tol 10]

slots.json: one entry per line, with the slot from the picture (the original timing):
  [{"id": "L01", "start": 0.40, "end": 3.10, "text": "Every photo showed tomorrow."},
   {"id": "L02", "start": 3.60, "end": 5.20, "text": "Except mine.", "text_target": "Excepto la mía."}]
  ("text_target" is the translated line; the tool uses it for the speaking rate and the cut estimate.)
Audio: <audio-dir>/<id>.wav (any format ffmpeg reads; leading and trailing silence is ignored).

For each line it reports the speech length, the slot length, and the difference in %. A line passes when
it is no more than --tol % longer than its slot (default 10 %) and not more than 25 % shorter.
It also reports the speaking rate (characters per second), so you can set limits for the translator.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def speech_span(path, noise_db=-40, min_sil=0.15):
    """Return (start, end) of speech in seconds, ignoring leading and trailing silence."""
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                               capture_output=True, text=True, check=True).stdout)
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-af", f"silencedetect=noise={noise_db}dB:d={min_sil}",
                        "-f", "null", "-"], capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    s, e = 0.0, dur
    if starts and starts[0] <= 0.01 and ends:
        s = ends[0]
    if starts and (len(ends) < len(starts) or ends[-1] >= dur - 0.01):
        e = starts[-1]
    return s, max(s, e)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slots")
    ap.add_argument("--audio-dir", required=True)
    ap.add_argument("--tol", type=float, default=10.0, help="max % longer than the slot")
    ap.add_argument("--short", type=float, default=25.0, help="max % shorter than the slot")
    a = ap.parse_args()
    slots = json.loads(Path(a.slots).read_text())
    fails = 0
    print(f"{'id':6} {'slot s':>7} {'speech s':>8} {'diff':>7} {'chars/s':>7}  result")
    for sl in slots:
        f = next(iter(sorted(Path(a.audio_dir).glob(f"{sl['id']}.*"))), None)
        if f is None:
            print(f"{sl['id']:6} {'':>7} {'':>8} {'':>7} {'':>7}  MISSING")
            fails += 1
            continue
        s, e = speech_span(f)
        speech = e - s
        slot = sl["end"] - sl["start"]
        diff = 100 * (speech - slot) / slot
        text = sl.get("text_target") or sl.get("text", "")  # the translated line, if given
        cps = len(text) / speech if speech else 0
        if diff > a.tol:
            res = f"TOO LONG: cut about {len(text) * (1 - slot / speech):.0f} characters, or speed up <= 10 %"
            fails += 1
        elif diff < -a.short:
            res = "TOO SHORT: add a word, or slow down"
            fails += 1
        else:
            res = "ok"
        print(f"{sl['id']:6} {slot:7.2f} {speech:8.2f} {diff:+6.0f}% {cps:7.1f}  {res}")
    print(f"\n{len(slots) - fails} of {len(slots)} lines fit")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
