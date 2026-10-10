#!/usr/bin/env python3
"""Fill dropouts in a dialogue track with room tone (C10·M01). Needs ffmpeg and numpy.

Generated and TTS lines are often joined with digital silence between them. On speakers, the sound of the
room disappears at every gap: viewers hear "holes". Fill them with room tone: the quiet sound of the place.

  python roomtone.py dialogue.wav --tone room_tone.wav --out dialogue_filled.wav
  python roomtone.py dialogue.wav --auto-tone --out dialogue_filled.wav     # take tone from the quietest non-silent part

Gaps: stretches below --floor dBFS longer than --min-gap seconds. Each gap is filled with tone (looped), with
short crossfades, so the joins are smooth. The report gives the gaps found and the level of the tone.
"""
import argparse
import json
import subprocess
import sys

import numpy as np

SR = 48000


def load(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True)
    if r.returncode:
        sys.exit(f"cannot read {path}")
    return np.frombuffer(r.stdout, np.float32).copy()


def save(path, x):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-i", "-", "-c:a", "pcm_s24le", path],
                   input=x.astype(np.float32).tobytes(), check=True)


def db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


def find_gaps(x, floor_db, min_gap, blk=0.01):
    n = int(blk * SR)
    k = len(x) // n
    lev = 20 * np.log10(np.sqrt((x[: k * n].reshape(k, n) ** 2).mean(1)) + 1e-12)
    quiet = lev < floor_db
    gaps, start = [], None
    for i, q in enumerate(list(quiet) + [False]):
        if q and start is None:
            start = i
        if not q and start is not None:
            if (i - start) * blk >= min_gap:
                gaps.append((start * n, i * n))
            start = None
    return gaps, lev


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dialogue")
    ap.add_argument("--tone", help="a recording of the room tone (several seconds)")
    ap.add_argument("--auto-tone", action="store_true")
    ap.add_argument("--out", required=True)
    ap.add_argument("--floor", type=float, default=-70.0, help="level (dBFS) below which audio counts as a dropout")
    ap.add_argument("--min-gap", type=float, default=0.05)
    ap.add_argument("--fade", type=float, default=0.02)
    a = ap.parse_args()
    x = load(a.dialogue)
    gaps, lev = find_gaps(x, a.floor, a.min_gap)
    if a.tone:
        tone = load(a.tone)
    elif a.auto_tone:
        # the quietest 1 s that is not a dropout: usually the room between words
        blk = int(0.01 * SR)
        cand = [(i, v) for i, v in enumerate(lev) if v >= a.floor]
        if not cand:
            sys.exit("no room tone found; give --tone")
        win = 100
        best = min(range(0, max(1, len(lev) - win)), key=lambda i: np.mean(np.where(lev[i:i + win] < a.floor, 0, lev[i:i + win])) if np.all(lev[i:i + win] >= a.floor) else 1e9)
        tone = x[best * blk:(best + win) * blk]
    else:
        sys.exit("give --tone or --auto-tone")
    if len(tone) < SR // 2:
        sys.exit("room tone must be at least 0.5 s")
    if a.auto_tone and db(tone) > -45:
        sys.exit(f"no room tone found: the quietest non-silent second is {db(tone):.1f} dBFS (speech). "
                 "TTS and many generated lines have no room tone, only digital silence. "
                 "Record 30 s of the room, take it from a native-audio clip of the scene, or generate it (C06·M04); then use --tone.")
    y = x.copy()
    f = int(a.fade * SR)
    ramp = np.linspace(0, 1, f, dtype=np.float32)
    for s, e in gaps:
        L = e - s
        reps = int(np.ceil((L + 2 * f) / len(tone)))
        fill = np.tile(tone, reps)[: L + 2 * f]
        fill[:f] *= ramp
        fill[-f:] *= ramp[::-1]
        a0, a1 = max(0, s - f), min(len(y), e + f)
        y[a0:a1] += fill[: a1 - a0]
    save(a.out, y)
    after, _ = find_gaps(y, a.floor, a.min_gap)
    print(json.dumps({"gaps_found": len(gaps), "gap_seconds": round(sum(e - s for s, e in gaps) / SR, 2),
                      "tone_level_dbfs": round(float(db(tone)), 1), "gaps_after": len(after), "out": a.out}))


if __name__ == "__main__":
    main()
