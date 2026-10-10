---
code: C05
title: "Video Generation: Directing the Model"
level: 2
hours: 90
prereq: C01, C02, C04
outcomes:
  - Choose the right generation mode for each shot (T2V, I2V, R2V, V2V, edit).
  - Write video prompts that control camera, motion, and timing.
  - Use first/last frames, camera control, and motion references for exact shots.
  - Keep characters, products, and places consistent across multi-shot sequences.
  - Use native audio and dialogue generation, and know its limits.
  - Edit existing video with AI editing models.
  - Plan coverage and budgets with cost per usable second.
---
## About this course

This is the core craft of the program. You learn to direct a video model like a crew: a clear plan, exact instructions, references, and a review of every take.

Current tools (as of 2026-10): Kling 3.0 / 3.0 Omni, Seedance 2.5, Veo 3.1 + Flow, Gemini Omni Flash, Runway Gen-4.5 + Aleph, Luma Ray3; open: Wan 2.7, LTX-2.5, HunyuanVideo 1.5. Note: the Sora 2 API was removed on 2026-09-24.

**Starter tools for this course** (in `tools/` of the [starter kit](starter.zip)):

| Tool | Use |
|---|---|
| `takes.py` | Take log, selects with in/out points, caps, and cost per usable second (M01, M06) |
| `join_check.py` | Measures loops and chained joins: jump ratio and color shift (M02, M03) |
| `identity_score.py` + `drift_plot.py` | Identity per shot and the drift trend of a sequence (M03) |
| `stems.py` | Splits native audio into dialogue and background stems (M04) |
| `clip_diff.py` | Measures an edited clip against its source, frame by frame (M05) |

Open-model workflows for image-to-video, first/last frame, and control video are in `comfyui/` (C11 explains them).
