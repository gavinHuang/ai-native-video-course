#!/usr/bin/env python3
"""Validate an LLM paper edit against the transcripts, and turn it into selects (C08·M02).

An LLM can choose and order quotes from long interviews well. It can also invent words, join two
sentences from different places, or "fix" the grammar of a quote. This tool accepts a segment only
if its quote is an exact, contiguous word sequence in the named transcript.

  python papercut.py edit.json --transcripts tr/ --out selects.csv [--pad 0.15]

edit.json (what you ask the LLM to return):
  [{"id": "P01", "file": "interview_a", "quote": "That's my locker.", "reason": "hook"}, ...]
transcripts: tr/<file>.json from transcribe.py (segments with word timestamps).
Output: selects.csv in the format of takes.py, so selects_to_otio.py can build the timeline.
Each line in the CSV gets in/out times from the first and last word (+ --pad seconds, inside the media).
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path


def norm(w):
    return re.sub(r"[^\w']", "", w.lower())


def words_of(tr):
    return [w for s in tr["segments"] for w in s["words"]]


def find(quote, words):
    q = [norm(x) for x in quote.split() if norm(x)]
    seq = [norm(w["w"]) for w in words]
    for i in range(len(seq) - len(q) + 1):
        if seq[i:i + len(q)] == q:
            return i, i + len(q) - 1
    return None


def near_miss(quote, words):
    """How many words of the quote appear in order somewhere? Helps to explain a rejection."""
    q = [norm(x) for x in quote.split() if norm(x)]
    seq = [norm(w["w"]) for w in words]
    best = 0
    for i in range(len(seq)):
        k = 0
        while k < len(q) and i + k < len(seq) and seq[i + k] == q[k]:
            k += 1
        best = max(best, k)
    return best, len(q)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("edit")
    ap.add_argument("--transcripts", required=True)
    ap.add_argument("--media-ext", default=".mp4", help="extension of the media files next to the transcripts")
    ap.add_argument("--out", default="selects.csv")
    ap.add_argument("--pad", type=float, default=0.15, help="seconds before the first and after the last word")
    a = ap.parse_args()
    edit = json.loads(Path(a.edit).read_text())
    cache, ok_rows, rejects, total = {}, [], [], 0.0
    for seg in edit:
        f = seg["file"]
        if f not in cache:
            p = Path(a.transcripts) / f"{f}.json"
            if not p.exists():
                rejects.append((seg["id"], f"no transcript {p}"))
                continue
            cache[f] = words_of(json.loads(p.read_text()))
        words = cache[f]
        hit = find(seg["quote"], words)
        if hit is None:
            k, n = near_miss(seg["quote"], words)
            rejects.append((seg["id"], f"quote not found as spoken ({k} of {n} words match in a row): \"{seg['quote'][:70]}\""))
            continue
        i, j = hit
        t_in = max(0.0, words[i]["start"] - a.pad)
        t_out = words[j]["end"] + a.pad
        total += t_out - t_in
        ok_rows.append({"shot": seg["id"], "take": f"{seg['id']}_{f}", "file": f + a.media_ext,
                        "in": f"{t_in:.2f}", "out": f"{t_out:.2f}", "usable_s": f"{t_out - t_in:.2f}",
                        "note": seg.get("reason", "")})
    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["shot", "take", "file", "in", "out", "usable_s", "note"])
        w.writeheader()
        w.writerows(ok_rows)
    for sid, why in rejects:
        print(f"REJECT {sid}: {why}")
    print(f"{len(ok_rows)} of {len(edit)} segments valid, {total:.1f} s; wrote {a.out}")
    sys.exit(1 if rejects else 0)


if __name__ == "__main__":
    main()
