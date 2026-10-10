#!/usr/bin/env python3
"""Localize a finished video into other languages: voice, fit, mix over M&E, loudness, captions (C15·M02).

  python localize.py --video master.mp4 --me me.wav --lines lines.json --langs es,de --out loc/ \
      [--tts say] [--target -14]

lines.json (from transcribe.py slots + adapted translations, C06·M02):
  [{"id": "L01", "start": 0.40, "end": 3.10, "text": "Every photo showed tomorrow.",
    "tr": {"es": "Cada foto mostraba el mañana.", "de": "Jedes Foto zeigte das Morgen."}}, ...]

TTS backends:
  say      macOS system voices (for tests and timing drafts only; label drafts as such)
  cmd      any command: --tts-cmd 'mytts --voice {voice} --lang {lang} --out {out} --text {text}'
           (use your cloned or chosen voice with consent, C06·M01)
Per language the script: makes each line, checks its fit to the slot (fit_check rules: <= +10 %, >= -25 %),
speeds up lines that are up to 10 % long, places every line at its slot start over the M&E, normalizes the
mix (two passes), muxes it with the picture, and writes captions (SRT). It writes a report per language.
Lines that do not fit are listed: they need a shorter translation, not a faster voice.
"""
import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from fit_check import speech_span  # noqa: E402

SAY_VOICES = {"en": "Samantha", "es": "Eddy (Spanish (Spain))", "de": "Anna", "fr": "Eddy (French (France))"}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"failed: {' '.join(map(str, cmd[:5]))} ...\n{r.stderr[-600:]}")
    return r


def tts(text, lang, out, a):
    raw = out.with_suffix(".raw.aiff" if a.tts == "say" else ".raw.wav")
    if a.tts == "say":
        run(["say", "-v", SAY_VOICES.get(lang, "Samantha"), "-o", str(raw), text])
    else:
        cmd = a.tts_cmd.format(voice=a.voice or "", lang=lang, out=shlex.quote(str(raw)), text=shlex.quote(text))
        run(shlex.split(cmd))
    run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-ar", "48000", "-ac", "1", str(out)])
    raw.unlink()


def srt_time(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", required=True)
    ap.add_argument("--me", required=True, help="music and effects stem (no dialogue), full length")
    ap.add_argument("--lines", required=True)
    ap.add_argument("--langs", required=True)
    ap.add_argument("--out", default="loc")
    ap.add_argument("--tts", choices=["say", "cmd"], default="say")
    ap.add_argument("--tts-cmd")
    ap.add_argument("--voice")
    ap.add_argument("--target", type=float, default=-14.0)
    a = ap.parse_args()
    lines = json.loads(Path(a.lines).read_text())
    out = Path(a.out)
    for lang in a.langs.split(","):
        d = out / lang
        d.mkdir(parents=True, exist_ok=True)
        report = {"lang": lang, "lines": [], "not_fitting": []}
        placed = []
        for ln in lines:
            text = ln["tr"].get(lang)
            if not text:
                report["not_fitting"].append({"id": ln["id"], "why": "no translation"})
                continue
            wav = d / f"{ln['id']}.wav"
            tts(text, lang, wav, a)
            s, e = speech_span(wav)
            speech, slot = e - s, ln["end"] - ln["start"]
            diff = 100 * (speech - slot) / slot
            tempo = 1.0
            if 0 < diff <= 10:
                tempo = speech / slot  # speed up by at most 10 %
            ok = diff <= 10 and diff >= -25
            trimmed = d / f"{ln['id']}_fit.wav"
            af = f"atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS" + (f",atempo={tempo:.4f}" if tempo != 1.0 else "")
            run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-af", af, str(trimmed)])
            report["lines"].append({"id": ln["id"], "slot_s": round(slot, 2), "speech_s": round(speech, 2), "diff_pct": round(diff),
                                    "tempo": round(tempo, 3), "fits": ok})
            if not ok:
                report["not_fitting"].append({"id": ln["id"], "why": f"{diff:+.0f} % against the slot", "text": text})
            placed.append((ln, trimmed, text))
        # mix: every line at its slot start over the M&E
        inputs, labels = ["-i", a.me], []
        for i, (ln, f, _) in enumerate(placed, 1):
            inputs += ["-i", str(f)]
            ms = int(round(ln["start"] * 1000))
            labels.append(f"[{i}]adelay={ms}|{ms},aformat=channel_layouts=stereo[d{i}]")
        mix_in = "".join(f"[d{i}]" for i in range(1, len(placed) + 1))
        fc = ";".join(labels + ["[0]aformat=channel_layouts=stereo[me]",
                                f"[me]{mix_in}amix=inputs={len(placed) + 1}:normalize=0:duration=first[m]"])
        mix = d / "mix.wav"
        run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[m]", "-ar", "48000", "-c:a", "pcm_s24le", str(mix)])
        norm = d / "mix_norm.wav"
        r = subprocess.run([sys.executable, str(HERE.parent / "tools" / "normalize.py"), str(mix), "--target", str(a.target),
                            "--tp", "-1", "--out", str(norm)], capture_output=True, text=True)
        rep = json.loads(r.stdout[: r.stdout.rindex("}") + 1])
        report["loudness"] = rep["after"]
        final = d / f"{Path(a.video).stem}_{lang}.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-i", str(norm), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
             "-c:a", "aac", "-b:a", "192k", "-shortest", str(final)])
        with open(d / f"{Path(a.video).stem}_{lang}.srt", "w") as f:
            for n, (ln, _, text) in enumerate(placed, 1):
                f.write(f"{n}\n{srt_time(ln['start'])} --> {srt_time(ln['end'])}\n{text}\n\n")
        report["video"] = str(final)
        (d / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
        fits = sum(1 for x in report["lines"] if x["fits"])
        print(f"{lang}: {fits}/{len(lines)} lines fit; loudness {rep['after']['I']} LUFS; {final}")
        for nf in report["not_fitting"]:
            print(f"   - {nf['id']}: {nf['why']}  -> shorten the translation")


if __name__ == "__main__":
    main()
