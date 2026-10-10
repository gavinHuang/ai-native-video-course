---
title: Upscale, interpolation, repair, delivery, and QC
hours: 15
outcomes:
  - Upscale generated video and check faces, text, textures, and stability over time.
  - Conform frame rates by interpolation, and measure the motion cadence and the frame count of the result.
  - Repair typical generated-video artifacts - flicker, warping at the end of a clip, soft frames, black and frozen frames.
  - Encode deliverables to platform and client specifications with correct tags.
  - Run automated QC on every deliverable, and fix every failure before delivery.
keywords: [upscaling, frame interpolation, deliverables, QC, cadence]
summary: >
  Generated clips often need more resolution, another frame rate, and repairs. Video upscalers add detail and can
  invent it; check faces, text, and stability. A frame-rate conform by repeated frames makes judder; blending makes
  ghosts; motion interpolation makes even motion with edge artifacts, and can change the frame count. Measure the
  cadence and the length after every conform. Encode each delivery to its spec with correct color tags, and run an
  automated QC on every file: format, color tags, loudness, black and frozen frames.
diagram:
  type: flow
  title: From finished timeline to delivered files
  nodes: ["Upscale (only shots that need it)", "Conform frame rate; measure cadence", "Repair artifacts", "Encode per spec; tag color", "Automated QC (spec_check)", "Fix failures → deliver + log"]
  highlight: [4]
watch:
  - title: "Topaz Labs — video upscaling and frame interpolation (docs)"
    url: https://docs.topazlabs.com/
    note: "Read the model descriptions for upscaling and interpolation."
  - title: "FFmpeg — H.264 encoding guide (trac wiki)"
    url: https://trac.ffmpeg.org/wiki/Encode/H.264
    note: "Read the CRF and preset sections."
quiz:
  - q: "A 16 fps generated clip is conformed to 24 fps by repeating frames. What do viewers see, and what does a cadence check show?"
    options: ["Nothing", "Judder: every second frame is repeated in a 3-frame pattern; the check shows about a third of the frame steps with no change", "Ghost images", "A color shift"]
    answer: 1
    explain: "In the module test: 33.7 % repeated frames and an uneven step size (spread 0.76, against 0.07 for native 24 fps)."
  - q: "Frame blending gives 0 % repeated frames. Why is it still a weak conform for motion?"
    options: ["It is slow", "It mixes neighbor frames: moving objects show double edges (ghosting), even though the cadence numbers look good", "It changes the color", "It is not allowed"]
    answer: 1
    explain: "Numbers and eyes check different things. Look at moving edges in playback."
  - q: "After motion interpolation, the clip has 94 frames instead of 96. Why does it matter?"
    options: ["It does not", "The clip is shorter than the edit expects; sync with audio and cut points shift, so check the frame count and pad or trim to the exact length", "It improves quality", "It saves storage"]
    answer: 1
    explain: "Conform tools can drop or add frames at the start or end. Check the length against the timeline."
  - q: "A generative upscaler makes a face look like plastic. What do you change?"
    options: ["Use it on all shots", "Lower its strength, upscale only the shots that need it, or use a non-generative upscaler for faces of real people", "Raise the strength", "Add grain only"]
    answer: 1
    explain: "Generative upscalers draw new detail. On faces, too much looks artificial."
  - q: "QC reports a 1.5 s frozen picture at the end of a clip. What is the typical cause in AI-native work?"
    options: ["The QC is wrong", "A generated clip or a failed render that holds its last frame; trim it or replace it", "Wrong loudness", "Wrong tags"]
    answer: 1
    explain: "Generated clips sometimes end with frozen or black frames. QC finds them before the client does."
  - q: "Your QC passes 17 of 19 checks on a delivery. What do you do?"
    options: ["Deliver it; 17 is good", "Fix the 2 failures and run QC again; deliver only files that pass, or document an approved exception from the client", "Change the spec", "Deliver and fix later"]
    answer: 1
    explain: "A spec is a contract. Every failure is fixed or approved in writing."
  - q: "Why upscale before the final grade (or test both orders)?"
    options: ["It is required", "The upscaler can change contrast, sharpness, and noise; grading after it lets you correct those changes, and the grade is not re-sharpened in strange ways", "Upscalers need graded input", "It is faster"]
    answer: 1
    explain: "Finish in an order where each step can correct the step before. Test on one shot."
deeper:
  - title: "Huang et al. — RIFE: Real-Time Intermediate Flow Estimation for Video Frame Interpolation"
    url: https://arxiv.org/abs/2011.06294
  - title: "FFmpeg filters — ebur128, blackdetect, freezedetect, minterpolate"
    url: https://ffmpeg.org/ffmpeg-filters.html
  - title: "EBU R 128 — loudness normalization and permitted maximum level (EBU tech page)"
    url: https://tech.ebu.ch/publications/r128
---
## Learn

### Upscaling
Video models often output 720p or 1080p. Deliveries ask for 1080p or 4K. Two kinds of upscalers:
- **Non-generative** (for example lanczos scaling, classic super-resolution): sharper enlargement, no new content. Safe for text and faces of real people. Looks softer.
- **Generative / AI video upscalers:** add detail with a trained model. Look sharper. They can invent detail: plastic skin, wrong letters, repeated textures, and detail that changes from frame to frame (shimmer).

Rules:
1. Upscale only the shots that need it.
2. Check faces, text, repeated textures (brick, leaves), and stability in playback.
3. Lower the strength when faces look artificial.
4. Upscale before the final grade, or test both orders on one shot: the upscaler can change contrast and noise.

### Frame-rate conform
Generated clips arrive at 16, 24, 25, or 30 fps. The timeline has one rate (C08·M01). Three ways to convert, for example 16 → 24 fps:
- **Repeat frames:** some frames are shown twice. The motion stutters (judder).
- **Blend frames:** new frames mix their neighbors. The motion is smoother, but moving edges show double images (ghosting).
- **Motion interpolation:** new frames are computed from the estimated motion between frames. The motion is even. Artifacts appear at edges, at occlusions (a hand that passes in front of a face), and in fast motion.

Measure after every conform:
- **Cadence:** the size of the change between neighbor frames. Even motion has similar steps. Repeated frames show as steps near zero. `starter/tools/cadence.py` reports the share of repeated frames and the spread of the steps.
- **Frame count and duration:** some tools drop or add frames at the start or end. Compare with the timeline.
- **By eye:** moving edges for ghosts and warps.

For cinema-style work, keep 24 fps and conform other rates to it. Do not interpolate 24 fps material to 60 fps for a "smooth" look unless the client asks for it.

### Repairs for generated video
| Artifact | Repair |
|---|---|
| Flicker in texture or light | Deflicker or temporal denoise; check that it does not smear motion |
| Warping at the end of a clip | Trim to the clean part; use coverage (C05·M06) |
| Soft frames in the middle | Light sharpening, or replace from neighbor frames |
| One bad object for a few frames | Cleanup (M03) |
| Black or frozen frames at the end | Trim; QC finds them |

### Encoding deliverables
A delivery spec says the container, codec, size, frame rate, pixel format, color tags, bitrate limits, audio format, and loudness. Examples:
- **Web master:** MP4, H.264, 1920 × 1080 (or 3840 × 2160 with H.265), the project frame rate, `yuv420p`, Rec.709 tags, AAC 48 kHz stereo, about −14 LUFS integrated, true peak ≤ −1 dBTP.
- **Vertical social:** 1080 × 1920, the same codecs, the platform's duration limit.
- **Archive:** ProRes 422 HQ master and WAV stems (C10·M02).
The client's spec always overrides these examples.

Encoding facts for H.264: CRF sets quality (lower = better; 16–20 is high quality for masters, 20–23 for web), and the preset sets speed against compression efficiency. Tag the color with the `setparams` filter, so that all four tags are written (M01).

### Automated QC
Run the same checks on every file, every time:
- format: container, codec, size, frame rate, pixel format, duration;
- color tags: primaries, transfer, matrix, range;
- audio: codec, sample rate, channels, integrated loudness, true peak;
- picture faults: black frames and frozen pictures.
`starter/tools/spec_check.py` reads a spec JSON and runs all of these with ffprobe and ffmpeg. It prints PASS or FAIL with the fix for each failure. Deliver only files that pass, or document an exception that the client approved.

## Tool walkthrough

### Conform and measure

```bash
ffmpeg -i gen16.mp4 -vf "minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" -c:v prores_ks -profile:v 3 gen24.mov
python starter/tools/cadence.py gen24.mov
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 gen24.mov
```

Dedicated interpolation tools (RIFE-type models, Topaz, Resolve Optical Flow / Speed Warp) usually give fewer artifacts than ffmpeg's `minterpolate`. Use the same measurements for all of them.

### Encode and check

```bash
ffmpeg -i master.mov -vf "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv" \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 320k -ar 48000 web_1080p.mp4
python starter/tools/spec_check.py web_1080p.mp4 --spec starter/specs/web_1080p.json --json qc_web.json
```

The starter specs (`web_1080p.json`, `reels_9x16.json`, `broadcast_ebu_r128.json`) are examples. Copy one and change it to the client's spec.

## Worked example

**Conform test** (2026-10-04). A 24 fps clip with even motion (a portrait moving at 200 px/s) was reduced to 16 fps (as a stand-in for a 16 fps model output), then conformed back to 24 fps in 3 ways:

| Clip | Repeated frames | Step spread (lower = more even) | Frames |
|---|---|---|---|
| Original 24 fps | 0 % | 0.07 | 96 |
| 16 fps source | 0 % | 0.22 (uneven: made by dropping frames) | 64 |
| 16 → 24, repeat frames | 33.7 % | 0.76 | 96 |
| 16 → 24, blend frames | 0 % | 0.22 | 96 |
| 16 → 24, motion interpolation (`minterpolate`, mci) | 0 % | 0.19 | **94** |

Repeating frames gave the clear judder pattern. Blending looked even in the numbers but showed ghosts by eye. Motion interpolation gave the most even motion, and it lost 2 frames: the clip became 83 ms shorter. Pad or trim it to the timeline length before you replace the shot.

**QC test** with `spec_check.py` and the web spec:
- An untagged export with a mix at −16.2 LUFS: FAIL on 4 color tags and loudness ("adjust the mix by +2.2 LU").
- The same export tagged with `setparams` and normalized: PASS, 19 of 19 checks.
- A file with 1 s of black at 4 s and a frozen 2 s tail: FAIL on black frames (4.00–5.04 s) and frozen picture (4.00 s for 1.04 s; 5.21 s for 2.04 s).

## Lab

**Deliverable:** `C09/M04/` with the conformed and repaired shots, cadence reports, the deliverables, the QC reports, and a delivery log.

1. Take 3 clips at a frame rate other than your timeline's. Conform each in 2 ways. Run `cadence.py` and check the frame count. Choose a method per clip, with a reason.
2. Upscale 2 hero shots. Compare a generative and a non-generative method on faces and text at 200 % zoom.
3. Repair 2 artifacts (flicker, a warp at the end, a soft frame).
4. Write the spec JSON for 3 deliverables (a web master, a vertical social version, and one spec of your choice).
5. Encode the 3 deliverables from your C09 timeline. Run `spec_check.py` on each. Fix every failure and run it again.
6. Write the delivery log: file, spec, QC result, fixes, date.

**Result checklist**
- [ ] Cadence reports and frame counts for 3 conformed clips; a method chosen for each.
- [ ] Upscale comparison with notes.
- [ ] 3 deliverables that pass QC (reports saved).
- [ ] Delivery log.

## Model answer

**Conform decisions (shape of a strong answer):**

| Clip | Source fps | Method | Repeated frames | Spread | Frames vs expected | Decision |
|---|---|---|---|---|---|---|
| S03 | 16 | Motion interpolation | 0 % | 0.18 | −2 → padded 2 frames | ✓ |
| S03 | 16 | Repeat | 33 % | 0.74 | ok | ✗ judder |
| S09 | 30 | Speed change to 80 % | 0 % | 0.09 | ok | ✓ (slow motion fits the beat) |
| S11 | 25 | Motion interpolation | 0 % | 0.12 | ok | ✗ hand warps across the face at 1.2 s → 4 % speed change instead |

**Delivery log (extract):**

| File | Spec | First QC | Fix | Final QC |
|---|---|---|---|---|
| camera_web_1080p.mp4 | web_1080p | FAIL: transfer and primaries unknown | setparams | PASS 19/19 |
| camera_reels.mp4 | reels_9x16 | FAIL: −12.8 LUFS, true peak −0.4 dBTP | remix (C10·M02) | PASS |
| camera_prores_master.mov | client archive | PASS | — | PASS |

"QC caught 3 problems that I could not see or hear on my laptop: missing color tags, loudness on the vertical mix, and a 6-frame black tail on S14."
