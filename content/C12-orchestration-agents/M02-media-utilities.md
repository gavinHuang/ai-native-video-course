---
title: ffmpeg, Whisper, and media utilities as pipeline stages
hours: 10
outcomes:
  - Use ffmpeg in code for probe, transcode, trim, concat, audio, and analysis, and know which features depend on the build.
  - Use Whisper-family models for transcripts with word timestamps as a pipeline stage.
  - Write media functions that never overwrite inputs, return structured results, and raise clear errors.
  - Test media functions with generated media in CI, without real footage.
  - Store media with a metadata sidecar that connects to the prompt log and the rights log.
keywords: [ffmpeg, ffprobe, sidecar metadata, frame-accurate trim, test media]
summary: >
  ffmpeg and ffprobe are the workhorses of every media pipeline: they read, convert, cut, join, and measure almost
  any file. Use them from code through small functions with one job each, which never overwrite inputs, return
  structured results, and raise errors with the ffmpeg message. Some filters depend on how ffmpeg was built, so test
  for them. Generated test media (test patterns and tones) let you test every function in CI. Transcription is a
  stage like any other. Every asset gets a metadata sidecar that links it to its prompt, its rights, and its tech data.
diagram:
  type: flow
  title: Selects to assembly as stages
  nodes: ["probe() every input", "trim() each select (frame accurate)", "concat() with conform", "transcribe() → captions", "loudness() + spec QC", "sidecar JSON for every output"]
  highlight: [1]
watch:
  - title: "FFmpeg — documentation"
    url: https://ffmpeg.org/documentation.html
    note: "Read the main ffmpeg tool page and the pages of the filters you use."
  - title: "WhisperX — GitHub"
    url: https://github.com/m-bain/whisperX
    note: "Read about word-level timestamps and diarization."
quiz:
  - q: "Why is `-ss` after `-i` (with re-encoding) used for a frame-accurate trim?"
    options: ["It is faster", "ffmpeg then decodes and cuts at the exact frame; a stream copy can only cut at keyframes, so the start can be off by up to a GOP", "It changes the codec", "It is required for audio"]
    answer: 1
    explain: "Stream copy is fast but cuts at keyframes. For edits, decode and re-encode (to an intermediate). The starter trim test checks that 1.5 s gives exactly 36 frames at 24 fps."
  - q: "Your script uses the `subtitles` filter. It works on your laptop and fails in CI with 'No such filter'. Why?"
    options: ["CI is broken", "Filters depend on the ffmpeg build (libass for subtitles, freetype for drawtext); test for the filters you need, or use a method that every build has (for example images and overlay)", "The SRT is wrong", "CI has no fonts"]
    answer: 1
    explain: "This course's test machine (ffmpeg 9.0.2) had neither drawtext nor subtitles. The starter caption tool draws text with Pillow and uses overlay."
  - q: "Two clips have different sizes, frame rates, and one has no audio. Why does `-f concat -c copy` fail or give a broken file?"
    options: ["It never works", "The concat demuxer with stream copy needs identical codecs and parameters; use the concat filter and conform each clip (scale, fps, audio) first", "It needs more memory", "The files are too short"]
    answer: 1
    explain: "The starter concat() conforms each input, adds silence for clips without audio, and then joins them."
  - q: "What must a media function return?"
    options: ["Nothing; it prints", "A structured result (paths, duration, size, warnings) that the next stage and the logs can use; on failure, an exception with the ffmpeg message", "Only True", "The ffmpeg command"]
    answer: 1
    explain: "Structured results make stages composable and testable."
  - q: "How do you test media functions without real footage?"
    options: ["You cannot", "Generate test media with ffmpeg sources (testsrc2 for video, sine for audio) at known sizes, rates, and lengths, and assert the results", "Use a phone video", "Only in production"]
    answer: 1
    explain: "Generated test media make tests fast, repeatable, and free of rights questions."
  - q: "What goes into the sidecar JSON of a generated clip?"
    options: ["Only the file name", "The prompt-log ID, model, seed, cost, the rights status, and the tech data (fps, size, duration, color tags)", "The client's email", "Nothing"]
    answer: 1
    explain: "The sidecar connects the file to its history (C04 prompt log), its rights (C16), and search."
  - q: "Why should a function refuse to overwrite an existing output by default?"
    options: ["It is slower", "A wrong path in a batch job can destroy approved work; an explicit overwrite=True makes the intent clear", "ffmpeg requires it", "To save disk"]
    answer: 1
    explain: "Safe defaults matter most in automated pipelines and agent tools (M03)."
deeper:
  - title: "Radford et al. (2022) — Robust Speech Recognition via Large-Scale Weak Supervision (Whisper)"
    url: https://arxiv.org/abs/2212.04356
  - title: "FFmpeg trac wiki — encoding guides"
    url: https://trac.ffmpeg.org/wiki
  - title: "FFmpeg — formats documentation (the concat demuxer)"
    url: https://ffmpeg.org/ffmpeg-formats.html#concat
---
## Learn

### ffmpeg and ffprobe
**ffprobe** reads facts about a file: container, streams, codecs, size, frame rate, duration, color tags, audio format. **ffmpeg** reads inputs, applies filters, and writes outputs. Almost every pipeline stage in this program uses them. Learn four ideas:
1. **Inputs, filters, outputs.** Options before `-i` apply to the input; options after it apply to the output.
2. **Filter graphs.** `-vf` and `-af` for one stream; `-filter_complex` for several inputs and outputs, with labels like `[0:v]` and `[v]`.
3. **Stream copy versus re-encode.** `-c copy` copies the compressed data: very fast, no quality loss, but it can only cut at keyframes and cannot change anything. Re-encoding decodes and encodes: exact and flexible, and slower.
4. **The build.** Some filters exist only if ffmpeg was built with a library: `drawtext` needs freetype, `subtitles` needs libass, some codecs need their libraries. Test for the filters you need (`ffmpeg -filters`) and have a fallback.

### Common stages
- **Probe** every input before you use it: fps, size, duration, audio, color tags.
- **Intermediate:** convert generated clips once to a 10-bit intermediate for finishing (C09·M01).
- **Proxy:** a small file with the same frame rate and length, for editing (C08·M01).
- **Trim:** frame accurate. Decode and re-encode to an intermediate; put `-ss` and `-to` after `-i`.
- **Concat:** the concat demuxer with stream copy works only for identical files. For real material (different sizes, rates, or audio), use the concat filter, and conform each clip first.
- **Audio:** extract, resample to 48 kHz, measure loudness (C10·M02).
- **Review images:** a contact sheet of frames for reviewers and for agents that can see images (M04).

### Function design
- **One job per function:** `trim(src, t_in, t_out, dst)`, `make_proxy(src, dst)`.
- **Never overwrite an input.** Refuse to overwrite an existing output unless the caller says `overwrite=True`.
- **Structured results:** return a dict with paths, durations, sizes, and warnings.
- **Clear errors:** raise an exception that contains the ffmpeg error message.
- **Tests with generated media:** `testsrc2` (a moving test pattern) and `sine` (a tone) at known sizes, rates, and lengths. Assert frame counts and durations.

### Encoding settings for each stage
Choose the encoding by the job of the file, not by habit:
- **Intermediates and selects** (for finishing): an intra-frame, 10-bit codec such as ProRes 422 HQ, with 24-bit PCM audio. Every frame is a keyframe, so cuts are exact and decoding is fast. Files are large: Apple's target data rate for ProRes 422 HQ at 1080p and 24 fps is about 176 Mbit/s (about 1.3 GB per minute) for natural images; the real rate depends on the content (a synthetic test pattern encoded at 63 Mbit/s in our test).
- **Proxies** (for editing): H.264 at a small size and a fast preset. Same frame rate and length as the source.
- **Deliveries** (for viewers): H.264 or H.265 at the spec's size, with CRF or a bitrate from the spec, `yuv420p`, color tags set, AAC audio (C09·M04).
- **Archive:** the master in the intermediate codec, plus the stems as WAV (C10·M02).
Each re-encode with a lossy codec loses a little quality. Re-encode from the intermediate, never from a delivery file.

### Transcription as a stage
A transcript with word timestamps feeds captions (C08·M04), paper edits (C08·M02), dubbing (C06·M02), and search. Run it on the dialogue stem (C05·M04) with names and terms in the prompt. Store the transcript JSON next to the media.

### The asset sidecar
Every generated or processed file gets a sidecar JSON file with the same name:

```
assets/gen/S07/S07.p2.g4.mp4
assets/gen/S07/S07.p2.g4.json
  {"prompt_log_id": "S07.p2.g4", "model": "...", "seed": 1234, "cost_usd": 0.60,
   "rights": {"status": "own", "refs": ["CHAR-MARA", "LOC-LOCKER"]},
   "tech": {"fps": 24, "width": 1280, "height": 704, "duration": 6.04, "color": {...}}}
```

The sidecar connects the file to the prompt log (C04·M01), the rights log (C16), the take log (C05), and search. Write it in the same stage that writes the file.

## Tool walkthrough

### The starter media library

```python
import sys; sys.path.insert(0, "starter/pipeline")
import mediakit as mk
info = mk.probe("takes/S07_t04.mp4")
mk.trim("takes/S07_t04.mp4", 0.4, 4.1, "selects/S07_t04.mov")
mk.concat(["selects/S06.mov", "selects/S07_t04.mov"], "assembly.mov", fps=24)
print(mk.loudness("assembly.mov"))
mk.contact_sheet("assembly.mov", "review/assembly_sheet.png")
```

Run its tests: `pytest -q starter/pipeline/test_mediakit.py`.

### Check the build of ffmpeg

```bash
ffmpeg -version | head -1
ffmpeg -hide_banner -filters | grep -E " (drawtext|subtitles|lut3d|ebur128|minterpolate) "
```

### Transcribe as a stage
`starter/tools/transcribe.py` (C06·M02) writes the transcript JSON, an SRT, and dub slots. Call it on the dialogue stem.

## Worked example

**Media library tests** (2026-10-04, `pytest -q test_mediakit.py`, 6 passed in 1.0 s):

| Test | Generated input | Assertion |
|---|---|---|
| probe | 640 × 360, 24 fps, 2 s, with a tone | size, rate, duration, audio codec |
| frame-accurate trim | 4 s clip; trim 1.0–2.5 s | exactly 36 frames, 10-bit 4:2:2 |
| no overwrite | a proxy made twice | the second call raises "exists" |
| concat with mixed inputs | 640 × 360 at 24 fps with audio + 1280 × 720 at 30 fps without audio | one 640 × 360 24 fps file of 2 s with audio |
| loudness and errors | a 3 s tone; a clip without audio | a value between −30 and 0 LUFS; "no audio" error |
| contact sheet | a 3 s clip | a PNG file |

**The build lesson:** the test machine's ffmpeg 9.0.2 had no `drawtext` and no `subtitles` filter. Two starter tools (the animatic labels and the captions) first used them and failed. Both now draw text with Pillow and use `overlay`, which every build has. The same version also removed `-vsync` (use `-fps_mode`) and `-filter_complex_script` (use `-/filter_complex`). Pin and record the ffmpeg version in your pipeline README.

**Selects to assembly as a script:**
1. For each select: `trim()` with 2-frame handles → `selects/S07_t04.mov`.
2. `concat()` all selects with conform → `assembly.mov`.
3. Transcribe the dialogue stem → SRT; correct terms with the glossary.
4. `loudness()` and `spec_check.py` → report.
5. A sidecar JSON for every output.

## Lab

**Deliverable:** `pipelines/mediakit/` with your media functions (or the starter library extended), tests, and a `make_assembly.py` script.

1. Run the starter library and its tests. Read the code.
2. Add 3 functions that your project needs, for example `add_handles()`, `burn_logo()`, `make_vertical()`. Each with a test on generated media.
3. Write `make_assembly.py`: selects CSV → trimmed clips → assembly → transcript → loudness → QC report → sidecars.
4. Run it on your C05 selects.
5. Run the tests in CI (for example a GitHub Actions job with ffmpeg installed). Record the ffmpeg version.

**Result checklist**
- [ ] 3 new functions, each with a test.
- [ ] `make_assembly.py` runs end to end on real selects.
- [ ] Every output has a sidecar JSON.
- [ ] Tests pass in CI; the ffmpeg version is recorded.

## Model answer

A strong `make_assembly.py` is short, because the functions do the work:

```python
for row in csv.DictReader(open("selects.csv")):
    out = mk.trim(row["file"], max(0, float(row["in"]) - 2/24), float(row["out"]) + 2/24, f"selects/{row['take']}.mov")
    write_sidecar(out["path"], prompt_log_id=row["take"], tech=out)
asm = mk.concat(sorted(glob("selects/*.mov"), key=shot_order), "assembly.mov", fps=24)
L = mk.loudness("assembly.mov")
report = {"assembly": asm, "loudness": L, "qc": run_spec_check("assembly.mov", "web_1080p")}
```

Its README states: "ffmpeg 9.0.2; filters used: scale, pad, fps, concat, ebur128, overlay (all in the default build)." The script never writes outside `selects/`, `assembly.mov`, and `reports/`, and it stops with a clear message if a select file is missing, instead of making a shorter assembly without telling anybody.

The three new functions each have a test with generated media: `add_handles()` (asserts 2 extra frames at each end, and no handles beyond the media), `burn_logo()` (asserts that the logo area changed and the rest did not, with `clip_diff.py`), and `make_vertical()` (asserts 1080 × 1920 and the same frame count). The CI log shows 9 tests passing in 2.4 s. The QC report of the first real run found 2 selects at 16 fps (from the `probe()` data that the script checks), which were conformed before the assembly.
