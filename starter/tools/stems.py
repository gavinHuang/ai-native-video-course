#!/usr/bin/env python3
"""Split the audio of a clip into dialogue and background stems (C05·M04, C06·M04, C10·M01).

  pip install demucs            # open-source source separation (MIT license); uses PyTorch, runs on CPU or GPU
  python stems.py clip.mp4 --out stems/            # -> stems/clip_dialogue.wav, stems/clip_background.wav
  python stems.py clip.mp4 --out stems/ --four     # -> vocals, drums, bass, other

Native audio from a video model comes as one mixed track. Separation gives you the parts, so you can keep
the sync effects and ambience and replace or fix the voice. Listen to the stems: separation leaves small
artifacts (a thin voice, music residue in pauses). Use a stem for a mix, not as a clean recording.
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip")
    ap.add_argument("--out", default="stems")
    ap.add_argument("--four", action="store_true", help="4 stems instead of dialogue + background")
    ap.add_argument("--model", default="htdemucs")
    ap.add_argument("--device", help="cpu, cuda, or mps (default: the best available)")
    a = ap.parse_args()
    clip = Path(a.clip)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="stems_"))
    wav = tmp / f"{clip.stem}.wav"
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-vn", "-ac", "2", "-ar", "44100",
                        "-c:a", "pcm_s24le", str(wav)], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"no audio track in {clip}? ffmpeg: {r.stderr.strip()[-300:]}")
    cmd = [sys.executable, "-m", "demucs", "-n", a.model, "-o", str(tmp / "sep"), "--int24"]
    if not a.four:
        cmd += ["--two-stems", "vocals"]
    if a.device:
        cmd += ["-d", a.device]
    r = subprocess.run(cmd + [str(wav)], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"demucs failed (is it installed? pip install demucs):\n{r.stderr[-800:]}")
    src = tmp / "sep" / a.model / clip.stem
    names = {"vocals": "dialogue", "no_vocals": "background"} if not a.four else {}
    for f in sorted(src.glob("*.wav")):
        dest = out / f"{clip.stem}_{names.get(f.stem, f.stem)}.wav"
        shutil.move(str(f), dest)
        print(dest)
    shutil.rmtree(tmp)


if __name__ == "__main__":
    main()
