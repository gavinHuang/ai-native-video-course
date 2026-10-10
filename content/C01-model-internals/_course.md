---
code: C01
title: Generative Model Internals
level: 1
hours: 60
prereq: none (entry knowledge only)
outcomes:
  - Explain training and inference, and how parameters, loss, and data make a model.
  - Explain tokens, embeddings, and attention in a transformer.
  - Explain latent space, VAEs, diffusion, and flow matching.
  - Explain how a diffusion transformer makes video and audio together.
  - Control a generation with conditioning, guidance, seeds, and steps.
  - Choose a quantized, distilled, or LoRA-adapted model for a given GPU and job.
  - Design a small eval set and compare models with it.
---
## About this course

You will use generative models in every other course. This course shows you what happens inside them. You do not need to train a large model. You need a correct mental model, so that you can predict what a model can do, why it fails, and which setting to change.

The labs use Python notebooks. They run on a laptop or in Google Colab. Some labs call hosted APIs.

**Starter tools for this course** (in the [starter kit](starter.zip); tested on 2026-10-04):

| Tool | Use |
|---|---|
| `tools/model_trial.py` | Usable rate with intervals and cost per usable second per shot type, for your eval set (M07) |
| `tools/promptlog.py` | The prompt log for every generation (M03, M05) |
