---
code: C04
title: Image Generation and Look Development
level: 2
hours: 50
prereq: C01, C02
outcomes:
  - Control image models with prompts, references, and instruction edits.
  - Build character, product, and environment sheets for consistency.
  - Write a look bible that keeps a whole project visually consistent.
  - Make key frames and storyboards that feed video generation.
---
## About this course

In AI-native video, most shots start as an image. The image fixes identity, composition, and look before you pay for motion. This course teaches you to make those images on purpose, and to make them the same across a whole project.

Current tools (as of 2026-10): GPT Image 2, Nano Banana Pro / 2, FLUX.2 (open weights), Midjourney V8.x, Kling Image 3.0, Seedream. See the tool landscape page.

**Two paths in every lab.** Use one hosted image API and one open model. The open path uses workflows 01 and 02 of the [starter kit](starter.zip) (`comfyui/`). You can run them now on a rented GPU; C11 explains them node by node.

**Starter tools for this course** (in `tools/` of the starter kit):

| Tool | Use |
|---|---|
| `promptlog.py` | Prompt log and rights log for every asset (all labs from now on) |
| `frame_diff.py` | Measures what an edit changed outside the target area (M02) |
| `refs_check.py` | Checks the reference library: views, files, rights, consent (M03) |
| `animatic.py` | Builds an animatic MP4 from frames, durations, moves, and temp audio (M04) |

The M04 storyboard script is in `solutions/C04-M04/`. Write your own first.
