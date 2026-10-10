#!/usr/bin/env python3
"""Null test: do the stems add up to the full mix? (C10·M02 deliverables)

  python null_test.py --mix mix.wav --stems DX.wav MX.wav FX.wav [--max-residual -60]

Stems (dialogue DX, music MX, effects FX) are delivered with the mix so that others can re-mix, dub, or
cut down. They must be full length, start at the same point, and add up to the mix. The test sums the
stems, subtracts the mix, and measures what is left (the residual) relative to the mix:
  below about -60 dB : the stems null (pass)
  above              : something differs: a missing or extra sound, a level change, an effect on the mix bus
                       that is not on the stems, or an offset (the report gives the best offset in samples)
"""
import argparse
import json
import subprocess
import sys

import numpy as np

SR = 48000


def load(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True)
    if r.returncode:
        sys.exit(f"cannot read {path}")
    return np.frombuffer(r.stdout, np.float32).reshape(-1, 2).copy()


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mix", required=True)
    ap.add_argument("--stems", nargs="+", required=True)
    ap.add_argument("--max-residual", type=float, default=-60.0)
    a = ap.parse_args()
    mix = load(a.mix)
    stems = [load(s) for s in a.stems]
    lengths = {s: round(len(x) / SR, 3) for s, x in zip(a.stems, stems)}
    n = min([len(mix)] + [len(s) for s in stems])
    total = sum(s[:n] for s in stems)
    res = total - mix[:n]
    rel = rms_db(res) - rms_db(mix[:n])
    # best offset (only for the report): cross-correlate the first channel over +-50 ms
    best, lag = None, 0
    for l in range(-2400, 2401, 48):
        t = np.roll(total[:, 0], l)
        v = float(np.dot(t[5000:-5000], mix[5000:n - 5000, 0]))
        if best is None or v > best:
            best, lag = v, l
    shifted = np.roll(total, lag, axis=0)
    rel_aligned = rms_db((shifted - mix[:n])[5000:-5000]) - rms_db(mix[5000:n - 5000])
    per_stem = {s: round(float(rms_db(x[:n])), 1) for s, x in zip(a.stems, stems)}
    ok = rel <= a.max_residual and len(set(lengths.values()) | {round(len(mix) / SR, 3)}) == 1
    rep = {"residual_db_rel_mix": round(float(rel), 1), "pass": bool(ok), "mix_s": round(len(mix) / SR, 3), "stem_lengths_s": lengths,
           "stem_levels_dbfs": per_stem, "best_offset_samples": lag,
           "residual_db_after_offset": round(float(rel_aligned), 1)}
    print(json.dumps(rep, indent=2))
    if not ok:
        if len(set(lengths.values()) | {round(len(mix) / SR, 3)}) > 1:
            print("FAIL: the stems and the mix have different lengths (all must be full length from the same start)")
        if rel > a.max_residual:
            print(f"FAIL: residual {rel:.1f} dB (limit {a.max_residual}).")
            if lag and rel_aligned < rel - 6:
                print(f"  The mix is offset by {lag} samples ({1000 * lag / SR:.1f} ms) against the stems; after alignment the residual is "
                      f"{rel_aligned:.1f} dB. Typical cause: a look-ahead limiter or other latency on the mix bus without delay compensation.")
            if rel_aligned > a.max_residual:
                print("  Even after alignment the stems do not null: processing on the mix bus (limiter, compressor, EQ) that is not on the "
                      "stems, or a missing or extra sound. Print the stems through the same bus processing, or deliver the mix without it.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
