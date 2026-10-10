#!/usr/bin/env python3
"""Transcribe a clip with word timestamps; write a transcript, captions, and dub slots (C06·M02, C08, C15·M02).

  pip install faster-whisper            # open Whisper models (MIT); CPU works, a GPU is faster
  python transcribe.py clip.mp4 --model small --lang en --out tr/
  # -> tr/clip.json (segments + words), tr/clip.srt (captions), tr/clip.slots.json (one slot per line, for fit_check.py)

Tips from the tests in C06·M02:
  - Clean speech: even the tiny model makes almost no errors. In noise, larger models are much better:
    at 0 dB signal-to-noise ratio, small had 0 % word errors where base had 25 %.
  - Split the voice from music and effects first (stems.py), then transcribe the dialogue stem.
  - Always read the transcript: names and product terms are the most common errors. Use --prompt with
    the names and terms to help the model.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def load16k(path):
    import numpy as np
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                       capture_output=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg could not read {path}")
    return np.frombuffer(r.stdout, np.float32).copy()


def srt_time(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"


def wrap2(text, max_chars):
    """Break a caption into at most 2 lines, at the space nearest the middle."""
    if len(text) <= max_chars:
        return text
    spaces = [i for i, c in enumerate(text) if c == " "]
    if not spaces:
        return text
    # the break that makes the longer of the two lines as short as possible
    cut = min(spaces, key=lambda i: max(i, len(text) - i - 1))
    return text[:cut].strip() + "\n" + text[cut:].strip()


def make_captions(segments, max_chars, min_dur=1.0):
    """Captions of at most 2 lines x max_chars. Prefer breaks after punctuation or at pauses.
    A short last piece (under min_dur or under 15 characters) is merged into the caption before it."""
    words = [w for s in segments for w in (s["words"] or [{"w": s["text"], "start": s["start"], "end": s["end"]}])]
    limit = 2 * max_chars
    caps, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        text = " ".join(x["w"] for x in cur)
        nxt = words[i + 1] if i + 1 < len(words) else None
        pause = nxt is not None and nxt["start"] - w["end"] > 0.3
        punct = w["w"].endswith((".", "?", "!", ",", ";", ":"))
        too_long = nxt is not None and len(text + " " + nxt["w"]) > limit
        if too_long and not (punct or pause):
            # break at the last punctuation or pause inside the caption, if it is not too early
            for k in range(len(cur) - 1, 0, -1):
                head = " ".join(x["w"] for x in cur[:k])
                gap = cur[k]["start"] - cur[k - 1]["end"] > 0.3
                if (cur[k - 1]["w"].endswith((".", "?", "!", ",", ";", ":")) or gap) and len(head) >= 0.3 * limit:
                    caps.append(cur[:k])
                    cur = cur[k:]
                    break
            else:
                caps.append(cur)
                cur = []
            continue
        if nxt is None or too_long or ((punct or pause) and len(text) >= 0.4 * limit):
            caps.append(cur)
            cur = []
    merged = []
    for c in caps:
        dur = c[-1]["end"] - c[0]["start"]
        txt = " ".join(x["w"] for x in c)
        if merged and (dur < min_dur or len(txt) < 15):
            prev = merged[-1]
            if len(" ".join(x["w"] for x in prev + c)) <= limit:
                merged[-1] = prev + c
                continue
            # move words from the previous caption so that this one is long enough
            while len(prev) > 1 and (c[-1]["end"] - c[0]["start"] < min_dur or len(" ".join(x["w"] for x in c)) < 15):
                c.insert(0, prev.pop())
        merged.append(c)
    return [(c[0]["start"], c[-1]["end"], wrap2(" ".join(x["w"] for x in c), max_chars)) for c in merged]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip")
    ap.add_argument("--model", default="small", help="tiny, base, small, medium, large-v3, ...")
    ap.add_argument("--lang", help="language code, for example en; default: detect")
    ap.add_argument("--prompt", help="names and terms that the audio contains, for example 'Mara, Leo, locker'")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--out", default=".")
    ap.add_argument("--max-chars", type=int, default=42, help="maximum characters per caption line")
    a = ap.parse_args()
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("pip install faster-whisper")
    model = WhisperModel(a.model, device=a.device, compute_type="int8" if a.device in ("cpu", "auto") else "float16")
    # Pass decoded samples (not the path): this avoids PyAV version problems in shared environments.
    segs, info = model.transcribe(load16k(a.clip), language=a.lang, word_timestamps=True, initial_prompt=a.prompt)
    segs = list(segs)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = Path(a.clip).stem
    data = {"language": info.language, "model": a.model,
            "segments": [{"id": f"L{i + 1:02d}", "start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                          "words": [{"w": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2),
                                     "p": round(w.probability, 2)} for w in (s.words or [])]}
                         for i, s in enumerate(segs)]}
    (out / f"{stem}.json").write_text(json.dumps(data, indent=1, ensure_ascii=False))
    caps = make_captions(data["segments"], a.max_chars)
    with open(out / f"{stem}.srt", "w") as f:
        for n, (cs, ce, t) in enumerate(caps, 1):
            f.write(f"{n}\n{srt_time(cs)} --> {srt_time(ce)}\n{t}\n\n")
    slots = [{"id": s["id"], "start": s["start"], "end": s["end"], "text": s["text"]} for s in data["segments"]]
    (out / f"{stem}.slots.json").write_text(json.dumps(slots, indent=1, ensure_ascii=False))
    low = [w for s in data["segments"] for w in s["words"] if w["p"] < 0.5]
    print(f"{len(data['segments'])} segments, {len(caps)} captions, language {info.language}")
    if low:
        print("check these words (low confidence): " + ", ".join(f"{w['w']}@{w['start']}s" for w in low[:15]))


if __name__ == "__main__":
    main()
