#!/usr/bin/env python3
"""Bar and beat grid for cutting music to picture (C06·M03, C10).

  python bars.py --bpm 112 --sig 4/4 --offset 0.27 --length 30              # bar start times
  python bars.py --bpm 112 --offset 0.27 --snap 6.0,20.1,29.5               # nearest beat / bar for picture events
  python bars.py --detect cue.wav --snap 6.0,20.1                           # estimate BPM and first beat (needs librosa)
  python bars.py --bpm 112 --cut-to 30 --offset 0.27                        # where to end the cue on a bar near 30 s

Facts used: one beat = 60 / BPM seconds; one bar of 4/4 = 4 beats. At 120 BPM a 4/4 bar is 2.0 s.
A music edit sounds right when you cut on a bar line (or at least on a beat) and the picture hit lands on a
strong beat. A difference of more than about 40 ms between a hit and the picture event is easy to notice.
"""
import argparse
import sys


def grid(bpm, beats_per_bar, offset, length):
    beat = 60.0 / bpm
    t, n = offset, 0
    out = []
    while t <= length + 1e-9:
        out.append((n, t, n % beats_per_bar == 0))
        n += 1
        t = offset + n * beat
    return out


def detect(path):
    try:
        import librosa
    except ImportError:
        sys.exit("--detect needs librosa: pip install librosa")
    y, sr = librosa.load(path, sr=None, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")
    tempo = float(tempo[0] if hasattr(tempo, "__len__") else tempo)
    return tempo, (float(beats[0]) if len(beats) else 0.0), len(y) / sr


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--sig", default="4/4")
    ap.add_argument("--offset", type=float, default=0.0, help="time of the first downbeat in the file (s)")
    ap.add_argument("--length", type=float, default=60.0)
    ap.add_argument("--snap", help="comma-separated picture event times (s)")
    ap.add_argument("--cut-to", type=float, help="target end time: find the nearest bar line")
    ap.add_argument("--detect", help="audio file: estimate BPM and the first beat")
    a = ap.parse_args()
    beats_per_bar = int(a.sig.split("/")[0])
    if a.detect:
        bpm, first, dur = detect(a.detect)
        print(f"detected: {bpm:.1f} BPM, first beat at {first:.3f} s, length {dur:.2f} s "
              f"(check by ear: the detector can pick half or double tempo, or a beat that is not the downbeat)")
        a.bpm = a.bpm or bpm
        a.offset = first if a.offset == 0.0 else a.offset
        a.length = dur
    if not a.bpm:
        sys.exit("give --bpm or --detect")
    g = grid(a.bpm, beats_per_bar, a.offset, a.length)
    beat = 60 / a.bpm
    print(f"{a.bpm:.1f} BPM, {a.sig}: beat {beat:.3f} s, bar {beat * beats_per_bar:.3f} s")
    if not a.snap and a.cut_to is None:
        for n, t, down in g:
            if down:
                print(f"bar {n // beats_per_bar + 1:3d}  {t:7.3f} s")
    if a.snap:
        print(f"{'event':>8} {'nearest beat':>12} {'off ms':>7} {'nearest bar':>11} {'off ms':>7}")
        for ev in (float(x) for x in a.snap.split(",")):
            nb = min(g, key=lambda x: abs(x[1] - ev))
            bars = [x for x in g if x[2]]
            nbar = min(bars, key=lambda x: abs(x[1] - ev))
            flag = "" if abs(nb[1] - ev) <= 0.04 else "  <- move the cut or the music"
            print(f"{ev:8.3f} {nb[1]:12.3f} {1000 * (nb[1] - ev):+7.0f} {nbar[1]:11.3f} {1000 * (nbar[1] - ev):+7.0f}{flag}")
    if a.cut_to is not None:
        bars = [x for x in g if x[2]]
        nbar = min(bars, key=lambda x: abs(x[1] - a.cut_to))
        print(f"end the cue on the bar line at {nbar[1]:.3f} s ({1000 * (nbar[1] - a.cut_to):+.0f} ms from {a.cut_to} s); "
              f"start the ending phrase {beat * beats_per_bar * 2:.2f} s (2 bars) earlier")


if __name__ == "__main__":
    main()
