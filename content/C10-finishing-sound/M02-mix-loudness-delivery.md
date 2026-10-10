---
title: Mix, loudness, and audio deliverables
hours: 26
outcomes:
  - Mix with clear priorities - dialogue first - using EQ, compression, ducking, and panning, and check on several playback systems.
  - Measure loudness (integrated LUFS, loudness range, true peak) and normalize to a target in two passes.
  - Tune ducking with measurements - how much the music falls under speech and in pauses.
  - Deliver a full mix, stems, and an M&E track, and prove with a null test that the stems add up to the mix.
  - Add loudness and stem checks to automated QC.
keywords: [LUFS, true peak, stem, M&E, null test, ducking]
summary: >
  A mix has one priority: the words are clear at all times; effects support the action, and music supports the
  emotion under the speech. Loudness is measured in LUFS over the whole program, plus the true peak. Platforms and
  broadcasters set targets, for example about −14 LUFS for streaming platforms and −23 LUFS for European broadcast,
  both with a true-peak maximum of about −1 dBTP. Normalize in two passes so one gain keeps the dynamics. Deliver the
  mix with stems and an M&E, and prove with a null test that the stems add up to the mix.
diagram:
  type: layers2d
  title: Loudness targets (examples; the spec decides)
  rows: ["Web / streaming", "EU broadcast (EBU R128)", "US broadcast (ATSC A/85)"]
  cols: ["Integrated loudness", "True peak max"]
  cells:
    - ["about −14 LUFS (platforms normalize)", "−1 dBTP"]
    - ["−23 LUFS ± 0.5 LU", "−1 dBTP"]
    - ["−24 LKFS ± 2", "−2 dBTP"]
watch:
  - title: "EBU R 128 — loudness recommendation (official page)"
    url: https://tech.ebu.ch/publications/r128
    note: "Read the summary page."
  - title: "Netflix — sound mix specifications (Partner Help Center)"
    url: https://partnerhelp.netflixstudios.com/
    note: "Search for 'sound mix specifications'; note the dialogue-gated measurement."
quiz:
  - q: "What is the first priority of a mix?"
    options: ["Loud music", "Dialogue is clear at all times, on every playback system", "Bass", "Wide stereo"]
    answer: 1
    explain: "If viewers cannot understand the words, nothing else works. Effects and music fit around the dialogue."
  - q: "Integrated loudness is −16.6 LUFS; the target is −14. Why is a two-pass normalization better than a limiter that pushes it up?"
    options: ["It is faster", "Pass 1 measures the program; pass 2 applies one gain (+2.6 dB here), which keeps the dynamics; a limiter changes the dynamics", "It is required by law", "It changes the pitch"]
    answer: 1
    explain: "In the module test, two-pass linear normalization moved −16.6 to −13.9 LUFS with the loudness range unchanged (1.8 LU)."
  - q: "Ducking lowers the music by 18 dB under speech. The mix feels like the music switches off. What do you change?"
    options: ["Raise the music", "Use a higher threshold or a lower ratio, so the music falls about 6–10 dB under speech and almost nothing in pauses; measure again", "Remove the music", "Use a longer release only"]
    answer: 1
    explain: "In the module test, threshold 0.02 / ratio 8 gave −18 dB; threshold 0.05 / ratio 3 gave −8.6 dB under speech and −0.3 dB in pauses."
  - q: "What is an M&E track?"
    options: ["A master and an export", "Music and effects without dialogue, complete, so that a dub can add a new language", "A metadata file", "A mono export"]
    answer: 1
    explain: "Effects that were only in the dialogue recording (steps, a door) must be added to the effects, or the dub loses them."
  - q: "The stems do not null with the mix: residual −0.7 dB; after aligning by 240 samples it is still −5.9 dB. What is the cause?"
    options: ["The stems are fine", "Processing on the mix bus (here a look-ahead limiter) that is not on the stems; print the stems through the same processing, or deliver the mix without it", "Wrong sample rate", "The stems are too quiet"]
    answer: 1
    explain: "An offset alone would null after alignment. A residual after alignment means the mix has processing that the stems do not."
  - q: "The null test reports an offset of 240 samples and −219 dB after alignment. What happened?"
    options: ["A processing problem", "A latency of 5 ms at 48 kHz on the mix path without delay compensation; the sounds are the same but shifted", "A missing stem", "Clipping"]
    answer: 1
    explain: "A look-ahead limiter or a plugin added latency. Turn on delay compensation, or shift the mix."
  - q: "Why check the mix on headphones, laptop speakers, and a phone?"
    options: ["For fun", "Viewers use all of them; small speakers lose bass and show whether the dialogue is still clear", "Specs require it", "To measure LUFS"]
    answer: 1
    explain: "A mix that works on a phone speaker works almost everywhere."
deeper:
  - title: "ITU-R BS.1770 — loudness measurement algorithm"
    url: https://www.itu.int/rec/R-REC-BS.1770
  - title: "FFmpeg loudnorm filter (two-pass normalization)"
    url: https://ffmpeg.org/ffmpeg-filters.html#loudnorm
  - title: "ATSC A/85 — techniques for establishing and maintaining audio loudness"
    url: https://www.atsc.org/atsc-documents/a85-techniques-for-establishing-and-maintaining-audio-loudness-for-digital-television/
---
## Learn

### Mix priorities
1. **Dialogue** is clear at all times.
2. **Effects** support the action.
3. **Music** supports the emotion, under the speech.
Work at a fixed, calibrated listening level, so your sense of loudness stays the same. Check the mix on headphones, laptop speakers, and a phone. A phone speaker has almost no bass and shows whether the words are still clear.

### Techniques
- **EQ:** remove low rumble from dialogue (a high-pass filter at about 80 Hz). Make space for speech in the music (a small cut around 1–4 kHz under speech).
- **Compression:** evens out the dialogue level, so quiet words are heard and loud words do not jump out.
- **Ducking (sidechain compression):** the music falls when someone speaks. A compressor on the music listens to the dialogue (the sidechain) and lowers the music by a few dB. A good target is 6–10 dB under speech and almost no change in pauses. Too much ducking sounds like the music switches off.
- **Automation:** draw level changes by hand where a rule does not work.
- **Panning:** dialogue in the center; ambience wide; effects where their source is on screen.

### Loudness
Loudness is perceived level. It is measured in **LUFS** (loudness units relative to full scale) with a standard method (ITU-R BS.1770) that weights frequencies like the ear and ignores silence.
- **Integrated loudness:** over the whole program. This is the number that specs set.
- **Loudness range (LRA):** how much the loudness changes in the program. Large values mean quiet parts are very quiet.
- **True peak (dBTP):** the highest level of the reconstructed signal, including peaks between samples. Specs set a maximum (often −1 dBTP), because encoders and converters can clip above it.

Targets depend on the delivery (the diagram shows examples). Streaming platforms normalize to about −14 LUFS: a louder mix is turned down, a quieter one may be turned up. Broadcasters set strict values (−23 LUFS ± 0.5 LU in EBU R128). The client's spec decides.

### Normalize in two passes
1. **Measure** the program: integrated loudness, LRA, true peak.
2. **Apply one gain** (linear mode) that moves the integrated loudness to the target. The dynamics stay the same.
3. **Measure** again.
If one gain would push the true peak over the limit, the normalizer must change the dynamics (dynamic mode). Better: put a true-peak limiter at the end of the mix bus, so the peaks are under control, and normalize again.

### Deliverables
- **Full mix:** stereo, and 5.1 or Atmos if the spec asks for it.
- **Stems:** DX, MX, FX (and AMB or Foley if asked). Each full length, from the same start point.
- **M&E:** music and effects with no dialogue, complete. If an effect was only in a dialogue recording (steps, a door in the native audio), re-create it on the effects, or the dubbed version loses it.
- **Captions:** SRT or VTT (C08·M04).

### Null test
Stems must add up to the mix. Sum the stems, subtract the mix, and measure what is left (the residual):
- below about −60 dB relative to the mix: the stems null;
- otherwise something differs. Two typical causes:
  - **latency:** the mix is shifted by a few milliseconds (a look-ahead limiter or a plugin without delay compensation). After alignment, the residual disappears;
  - **mix-bus processing** that is not on the stems (a limiter, a compressor, an EQ on the mix bus). After alignment, a residual remains. Print the stems through the same processing, or deliver the mix without it.

### Automate the checks
Add loudness and true peak to the delivery spec (`spec_check.py`, C09·M04), and run the null test on every stem delivery. Fail the delivery if a check fails.

## Tool walkthrough

### Measure

```bash
ffmpeg -i mix.wav -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|LRA:|Peak:"
```

### Normalize in two passes

```bash
python starter/tools/normalize.py mix.wav --target -14 --tp -1 --out mix_web.wav
python starter/tools/normalize.py mix.wav --target -23 --tp -1 --out mix_broadcast.wav
```

### Ducking with ffmpeg (or a sidechain compressor in your DAW)

```bash
ffmpeg -i music.wav -i dialogue.wav -filter_complex \
  "[0][1]sidechaincompress=threshold=0.05:ratio=3:attack=20:release=300:makeup=1[m]" -map "[m]" music_ducked.wav
```

In a DAW: put a compressor on the MX bus, set its sidechain input to the DX bus, and adjust the threshold and ratio while you watch the gain reduction meter.

### Null test

```bash
python starter/tools/null_test.py --mix mix.wav --stems DX.wav MX.wav FX.wav
```

## Worked example

**Normalization test** (2026-10-04, a 5.8 s mix of TTS dialogue, a music bed, and effects):

| | Integrated | LRA | True peak | Mode |
|---|---|---|---|---|
| Before | −16.6 LUFS | 1.8 LU | −5.2 dBTP | — |
| Target −14 | −13.9 LUFS | 1.8 LU | −2.5 dBTP | linear |
| Target −23 | −22.9 LUFS | 1.8 LU | −11.5 dBTP | linear |

Both results are within 0.1 LU of the target, and the loudness range did not change: one gain, no change to the dynamics.

**Ducking test** (the music bed under the same dialogue; the change in music level, measured in 50 ms blocks):

| Sidechain settings | Under speech | In pauses |
|---|---|---|
| threshold 0.02, ratio 8 | −18.1 dB | −2.0 dB |
| threshold 0.05, ratio 4 | −9.7 dB | −0.4 dB |
| threshold 0.05, ratio 3 | −8.6 dB | −0.3 dB |
| threshold 0.1, ratio 2.5 | −4.2 dB | 0.0 dB |

The first setting is too strong: the music almost switches off and does not fully recover in short pauses. Threshold 0.05 with ratio 3 is in the target range.

**Null tests** (stems DX, MX, FX and mixes made from them):

| Mix | Residual | After alignment | Diagnosis |
|---|---|---|---|
| Plain sum of the stems | −219.4 dB | — | PASS |
| Sum delayed by 5 ms | +0.7 dB | −219.5 dB (offset 240 samples) | latency |
| Sum through a look-ahead limiter | −0.7 dB | −5.9 dB | mix-bus processing |

## Lab

**Deliverable:** `C10/M02/` with the final mix in two loudness versions, the stems, an M&E, captions, a loudness report, a ducking table, a null-test report, and QC results.

1. Mix your scene from M01 (or your best piece). Check it on headphones, laptop speakers, and a phone. Write what you changed after each check.
2. Tune the ducking of the music under dialogue. Measure the music level under speech and in pauses for 3 settings. Choose one.
3. Make a web version at −14 LUFS ± 1, true peak ≤ −1 dBTP, and a broadcast version at −23 LUFS ± 0.5. Use two-pass normalization.
4. Bounce the DX, MX, and FX stems and an M&E. Check the dialogue stem for effects that must move to the M&E.
5. Run the null test. Fix any residual (latency or mix-bus processing) until it passes.
6. Make captions (SRT) and check them.
7. Add loudness to your delivery spec and run `spec_check.py` on the final video.

**Result checklist**
- [ ] Two loudness versions within tolerance (reports saved).
- [ ] Ducking table with 3 settings and the choice.
- [ ] Stems null with the mix (report saved); M&E complete.
- [ ] QC passes on the final video.

## Model answer

**Report (shape of a strong answer):**

"Playback checks: on the phone, the music hid Mara's whisper in S07 → music −2 dB in that scene and a 2 dB cut at 2.5 kHz in the MX bus under speech. On the laptop, the low rumble in S11 disappeared, which is fine: it is a design layer."

| Check | Web | Broadcast |
|---|---|---|
| Integrated | −14.1 LUFS | −23.0 LUFS |
| True peak | −1.6 dBTP | −9.8 dBTP |
| LRA | 6.2 LU | 6.2 LU |
| Normalization | linear | linear |

"Ducking: threshold 0.05 / ratio 3 → −8.4 dB under speech, −0.5 dB in pauses."

"Null test, first run: residual −0.8 dB, offset 240 samples, −6.1 dB after alignment. Cause: the limiter on the mix bus. Fix: limiter removed from the mix bus; a true-peak limiter on each stem bus instead. Second run: −74 dB, PASS."

"M&E: 2 effects were only in the native dialogue (the locker click in S03, steps in S09). Re-created on FX from the sound library. The M&E plays the whole scene with no gaps."

"QC: `spec_check.py` on the web video: PASS 19/19."
