---
code: C10
title: "AI Finishing: Sound"
level: 3
hours: 40
prereq: C06
outcomes:
  - Edit and clean dialogue, and build sound design from generated and recorded elements.
  - Mix to platform loudness targets with correct peak levels.
  - Deliver stems, M&E mixes, and captions to specification.
---
## About this course

A good mix makes generated video feel real. This course takes your dialogue, effects, ambience, and music from C06 and finishes them. Tools: Fairlight (in Resolve), Pro Tools, Reaper, Audition; iZotope RX; ffmpeg ebur128 for checks.

**Starter tools for this course** (in the [starter kit](starter.zip)):

| Tool | Use |
|---|---|
| `tools/roomtone.py` | Fills dropouts in dialogue with room tone; refuses TTS "tone" that is really speech (M01) |
| `tools/stems.py`, `tools/loop_audio.py` | Voice/background separation and seamless ambience loops (from C06) |
| `tools/normalize.py` | Two-pass loudness normalization to a target, with a before/after report (M02) |
| `tools/null_test.py` | Proves that stems add up to the mix; tells latency from mix-bus processing (M02) |
| `tools/spec_check.py` | Loudness and true peak in the delivery QC (M02) |
