#!/usr/bin/env python3
"""Burn captions into a video, in social style or sentence style, inside safe zones (C08·M04, C15).

  python captions.py clip_9x16.mp4 --transcript tr/clip.json --out clip_capt.mp4 --style words --n 3
  python captions.py clip_16x9.mp4 --transcript tr/clip.json --out clip_capt.mp4 --style sentence
  python captions.py clip_9x16.mp4 --transcript tr/clip.json --preview zones.png    # one frame with the zones drawn

--style words     : 1–3 words at a time, large, centered (Reels, TikTok, Shorts)
--style sentence  : 1–2 lines of up to 42 characters (YouTube, accessibility; also written as .srt and .vtt)
Safe zones: platform buttons and text cover parts of a vertical video. The defaults keep captions out of the
top 14 %, the bottom 22 %, and the right 12 % of the frame. These are example values: check the current
safe-zone template of each platform and set --top, --bottom, --right.
Works with every ffmpeg build (no drawtext or subtitles filter needed): text is drawn with Pillow.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "json", path], capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    return int(s["width"]), int(s["height"])


def font(size):
    from PIL import ImageFont
    for name in ("DejaVuSans-Bold.ttf", "Arial Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                 "/Library/Fonts/Arial Bold.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def chunks_words(words, n):
    """Groups of at most n words; a group also ends after a word with . ? ! or , (do not run across sentences)."""
    out, g = [], []
    for w in words:
        g.append(w)
        if len(g) == n or w["w"].endswith((".", "?", "!", ",")):
            out.append((g[0]["start"], g[-1]["end"], " ".join(x["w"] for x in g)))
            g = []
    if g:
        out.append((g[0]["start"], g[-1]["end"], " ".join(x["w"] for x in g)))
    # close small gaps so captions do not flicker off between words
    return [(s, (out[k + 1][0] if k + 1 < len(out) and out[k + 1][0] - e < 0.3 else e), t)
            for k, (s, e, t) in enumerate(out)]


def safe_box(W, H, top, bottom, right, left):
    return int(W * left), int(H * top), int(W * (1 - right)), int(H * (1 - bottom))


def render_png(text, W, H, box, style, path):
    from PIL import Image, ImageDraw
    x0, y0, x1, y1 = box
    size = int(H * (0.045 if style == "words" else 0.032))
    f = font(size)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if style == "words":
        text = text.upper()
    lines = text.split("\n")
    while True:
        boxes = [d.textbbox((0, 0), ln, font=f, stroke_width=max(2, size // 12)) for ln in lines]
        tw = max(b[2] - b[0] for b in boxes)
        if tw <= (x1 - x0) * 0.95 or size < 14:
            break
        size = int(size * 0.9)
        f = font(size)
    lh = int(size * 1.2)
    th = lh * len(lines)
    cx = (x0 + x1) // 2
    ty = y1 - th - int(H * 0.02) if style == "sentence" else (y0 + y1) // 2 + int((y1 - y0) * 0.25) - th // 2
    for i, ln in enumerate(lines):
        b = d.textbbox((0, 0), ln, font=f, stroke_width=max(2, size // 12))
        d.text((cx - (b[2] - b[0]) // 2, ty + i * lh), ln, font=f, fill=(255, 255, 255, 255),
               stroke_width=max(2, size // 12), stroke_fill=(0, 0, 0, 255))
    im.save(path)
    bbox = im.getbbox()
    return bbox


def srt_time(t, sep=","):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}{sep}{int(round((s - int(s)) * 1000)):03d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip")
    ap.add_argument("--transcript", required=True, help="JSON from transcribe.py (word timestamps)")
    ap.add_argument("--out")
    ap.add_argument("--style", choices=["words", "sentence"], default="words")
    ap.add_argument("--n", type=int, default=3, help="words per caption in --style words")
    ap.add_argument("--top", type=float, default=0.14)
    ap.add_argument("--bottom", type=float, default=0.22)
    ap.add_argument("--right", type=float, default=0.12)
    ap.add_argument("--left", type=float, default=0.06)
    ap.add_argument("--preview")
    a = ap.parse_args()
    from transcribe import make_captions
    W, H = probe(a.clip)
    tr = json.loads(Path(a.transcript).read_text())
    words = [w for s in tr["segments"] for w in s["words"]]
    caps = chunks_words(words, a.n) if a.style == "words" else make_captions(tr["segments"], 42)
    box = safe_box(W, H, a.top, a.bottom, a.right, a.left)
    tmp = Path(tempfile.mkdtemp(prefix="capt_"))
    pngs, problems = [], []
    for i, (s, e, t) in enumerate(caps):
        p = tmp / f"c{i:04d}.png"
        bb = render_png(t, W, H, box, a.style, p)
        if bb and (bb[0] < box[0] or bb[1] < box[1] or bb[2] > box[2] or bb[3] > box[3]):
            problems.append(f"caption {i + 1} '{t[:30]}' leaves the safe zone")
        pngs.append((s, e, p))
    if a.preview:
        from PIL import Image, ImageDraw
        frame = tmp / "f.png"
        mid = (caps[0][0] + caps[0][1]) / 2 if caps else 0
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(mid), "-i", a.clip, "-frames:v", "1", str(frame)], check=True)
        im = Image.open(frame).convert("RGBA")
        over = Image.new("RGBA", im.size, (255, 0, 0, 90))
        ImageDraw.Draw(over).rectangle(box, fill=(0, 0, 0, 0))
        im = Image.alpha_composite(im, over)
        if pngs:
            im = Image.alpha_composite(im, Image.open(pngs[0][2]))
        im.convert("RGB").save(a.preview)
        print(f"wrote {a.preview} (red = outside the safe zone)")
    if a.out:
        inputs, chain, last = [], [], "0:v"
        for i, (s, e, p) in enumerate(pngs):
            inputs += ["-i", str(p)]
            tag = f"v{i}"
            chain.append(f"[{last}][{i + 1}:v]overlay=0:0:enable='between(t,{s:.3f},{e:.3f})'[{tag}]")
            last = tag
        fc = ";".join(chain) if chain else "[0:v]null[v0]"
        last = last if chain else "v0"
        (tmp / "fc.txt").write_text(fc)
        # ffmpeg 7.1+ reads a filter graph from a file with "-/filter_complex"; older versions use -filter_complex_script.
        new = subprocess.run(["ffmpeg", "-hide_banner", "-h", "full"], capture_output=True, text=True).stdout
        fc_opt = ["-filter_complex_script", str(tmp / "fc.txt")] if "filter_complex_script" in new else ["-/filter_complex", str(tmp / "fc.txt")]
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.clip, *inputs, *fc_opt,
                            "-map", f"[{last}]", "-map", "0:a?", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                            "-c:a", "copy", a.out], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"ffmpeg failed: {r.stderr[-800:]}")
        stem = Path(a.out).with_suffix("")
        with open(f"{stem}.srt", "w") as f:
            for n, (s, e, t) in enumerate(caps, 1):
                f.write(f"{n}\n{srt_time(s)} --> {srt_time(e)}\n{t}\n\n")
        with open(f"{stem}.vtt", "w") as f:
            f.write("WEBVTT\n\n")
            for s, e, t in caps:
                f.write(f"{srt_time(s, '.')} --> {srt_time(e, '.')}\n{t}\n\n")
        print(f"wrote {a.out}, {stem}.srt, {stem}.vtt ({len(caps)} captions)")
    for p in problems:
        print("PROBLEM", p)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
