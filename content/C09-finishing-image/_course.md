---
code: C09
title: "AI Finishing: Image"
level: 3
hours: 60
prereq: C05, C08
outcomes:
  - Manage color correctly - color spaces, transfer functions, ACES, HDR.
  - Grade with scopes and match generated and real shots.
  - Use AI masks, relighting, object removal, and compositing for clean results.
  - Upscale, interpolate, and repair generated video, and deliver to spec with QC.
---
## About this course

Generated shots come from different models, with different colors, sharpness, and frame rates. Finishing makes them one film. Tools: DaVinci Resolve (color standard; Magic Mask, Relight, Voice Isolation), After Effects, Nuke, Fusion, Topaz Video, Runway Aleph; ffmpeg for checks.

**Starter tools for this course** (in the [starter kit](starter.zip)):

| Tool | Use |
|---|---|
| `tools/scopes.py` | Waveform, vectorscope, histogram, and exposure numbers for a frame or a clip (M01, M02) |
| `tools/match_color.py` | Shot match to a hero shot as a 3D LUT (.cube), with ΔE before and after (M02) |
| `tools/patch_restore.py` | Tracks an area and composites exact source pixels back onto an AI-edited clip (M03) |
| `tools/clip_diff.py` | Measures an edit against its source, frame by frame (M03) |
| `tools/cadence.py` | Repeated frames and motion evenness after a frame-rate conform (M04) |
| `tools/spec_check.py` + `specs/` | Delivery QC: format, color tags, loudness, black and frozen frames (M04) |
