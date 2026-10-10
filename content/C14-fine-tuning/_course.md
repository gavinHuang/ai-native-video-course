---
code: C14
title: Fine-Tuning and Self-Hosting
level: 4
hours: 50
prereq: C01, C11, C13
outcomes:
  - Build legal, clean, well-captioned datasets for characters, products, and styles.
  - Train image LoRAs and video LoRAs on open models.
  - Evaluate LoRAs for fidelity, flexibility, overfit, and leakage.
  - Quantize and serve your adapted models.
---
## About this course

A LoRA teaches an open model your character, product, or style. It is the strongest tool for consistency, and it keeps client data in your own infrastructure. Tools: musubi-tuner (kohya-ss), AI Toolkit (ostris), Diffusers, fal LoRA trainers; open models such as FLUX.2, Wan 2.x, HunyuanVideo, LTX.

**Starter tools for this course** (in `tools/` of the [starter kit](starter.zip)):

| Tool | Use |
|---|---|
| `dataset_check.py` | Dataset QC before training: captions, trigger, size, blur, near duplicates, bound features, rights (M01) |
| `lora_eval.py` | Fidelity, leakage, and flexibility per checkpoint; a choice rule; a checkpoint × prompt grid (M02, M03) |
| `identity_score.py` | Face-embedding identity score (from C05·M03 and C11·M03) |
| `../solutions/C11-M03/character_shot.py` | The pipeline test with and without the LoRA (M03) |

**C11 connection:** C11·M03 builds the character pipeline with references only. In M03 of this course you run its weakest shots again with your LoRA and measure the gain.
