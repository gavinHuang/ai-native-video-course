---
title: Diffusion transformers for video and audio
hours: 9
outcomes:
  - Describe the main blocks of a current video model (text encoder, video VAE, DiT, decoders).
  - Explain how a model generates audio and video together.
  - Explain what a mixture-of-experts (MoE) model is and why video models use it.
  - Read a video model card and find the information that matters for production.
keywords: [DiT, text encoder, MoE, joint audio-video, model card]
summary: >
  A current video model has four main parts. A text encoder turns the prompt into embeddings. A video VAE compresses
  the frames. A diffusion transformer, or DiT, removes noise from the space-time tokens. Decoders turn latents back
  into video and sound. Joint audio-video models put audio tokens and video tokens in one transformer, so speech and
  lips match. Mixture-of-experts models have several expert networks and use only some of them for each step. This
  gives more capacity for the same compute.
diagram:
  type: stack
  title: Anatomy of a 2026 video model
  nodes: ["Prompt + references: text, images, video, audio, 3D", "Encoders: LLM text encoder, image encoder, video VAE, audio codec", "Diffusion transformer (DiT): space-time + audio tokens, many layers", "Mixture of experts: e.g. high-noise expert vs low-noise expert", "Decoders: video VAE decoder + audio decoder", "Output: video with synchronized sound"]
  highlight: [2]
watch:
  - title: "Yannic Kilcher — Scalable Diffusion Models with Transformers (DiT) explained"
    url: https://www.youtube.com/watch?v=aSLDXdc2hkk
    note: "Watch 0:00–25:00. Why transformers replaced U-Nets in diffusion."
  - title: "OpenAI — Video generation models as world simulators (2024 technical report)"
    url: https://openai.com/index/video-generation-models-as-world-simulators/
    note: "Read the sections on space-time patches. The model is gone, but the ideas are standard now."
quiz:
  - q: "Which component turns the prompt into embeddings?"
    options: ["VAE", "Text encoder (often an LLM)", "Sampler", "Audio codec"]
    answer: 1
    explain: "Modern video models use a large language model as text encoder (for example Gemma 4 12B in LTX-2.5). A better encoder = better prompt understanding."
  - q: "Why do joint audio-video models give better lip sync than adding audio later?"
    options: ["They use a higher frame rate", "Audio and video tokens attend to each other during generation", "They have no VAE", "They use more steps"]
    answer: 1
    explain: "In one transformer, the mouth tokens and the speech tokens exchange information at every step."
  - q: "In an MoE video model with a high-noise expert and a low-noise expert, what does the low-noise expert mostly do?"
    options: ["Choose the composition", "Refine detail in late steps", "Encode the prompt", "Decode audio"]
    answer: 1
    explain: "Early (high-noise) steps decide layout and motion. Late (low-noise) steps add detail. Splitting experts by noise level gives each a specialized job."
  - q: "Which model-card item matters most to decide if a model can be used for a paid client project?"
    options: ["Number of layers", "License", "Name of the authors", "Training framework"]
    answer: 1
    explain: "License decides commercial use. Apache 2.0 allows it; 'research only' does not."
  - q: "A model card says '720p, 5 s native'. You ask for 1080p, 20 s in one generation. What do you expect?"
    options: ["Better quality", "Lower quality or failures (repetition, drift, broken motion): position encoding and training covered other sizes; generate at native size, then upscale and extend", "The same result", "A smaller file"]
    answer: 1
    explain: "Work at the trained resolution and duration, then use upscaling (C09) and extension (C05)."
  - q: "You give a model 3 reference images of a character as extra tokens. What is the main benefit, and the main cost?"
    options: ["No benefit", "Identity follows the references without training; each reference adds tokens and cost, and conflicting references confuse the model", "It removes the prompt", "It makes the model smaller"]
    answer: 1
    explain: "In-context references are the first tool for consistency (C04). Train an adapter only when they are not enough (C14)."
deeper:
  - title: "Peebles & Xie (2022) — Scalable Diffusion Models with Transformers (DiT)"
    url: https://arxiv.org/abs/2212.09748
  - title: "Wan Team (2025) — Wan: Open and Advanced Large-Scale Video Generative Models"
    url: https://arxiv.org/abs/2503.20314
  - title: "Kong et al. (2024) — HunyuanVideo technical report"
    url: https://arxiv.org/abs/2412.03603
  - title: "Meta (2024) — Movie Gen: A Cast of Media Foundation Models"
    url: https://arxiv.org/abs/2410.13720
---
## Learn

### Four main parts
1. **Encoders.** The **text encoder** turns the prompt into embeddings. Current models use a large language model for this, so they understand long, detailed prompts. Image and video references go through image encoders or the VAE. Audio references go through an audio codec.
2. **Video VAE.** It compresses frames into a latent (M03).
3. **Diffusion transformer (DiT).** This is the large part: 5 to 30 billion parameters. It removes noise from the space-time tokens. Each layer has self-attention (video ↔ video), conditioning on the text (cross-attention or joint attention), and a feed-forward network.
4. **Decoders.** The VAE decoder makes frames. In joint models, an audio decoder makes the waveform.

### Joint audio-video generation
Since 2025, top models generate sound with the picture, both hosted and open models (examples in the Tool walkthrough). The method: audio tokens and video tokens are in the same transformer, or in two streams that attend to each other ("dual-stream"). The effects:
- Lip movement and speech match.
- Footsteps, impacts, and doors match the action.
- Room acoustics match the space.

The limits: the voice can change between clips, the music is generic, and the mix is not controllable. In C06 and C10 you will often replace or layer the generated audio.

### Mixture of experts (MoE)
A **mixture-of-experts** model has several "expert" sub-networks. A router chooses which experts run for each token or each step. Only a part of the parameters run each time, so the model has more capacity for the same compute. Some open video models use MoE. One common split: a high-noise expert for layout and motion, and a low-noise expert for detail. All experts must be in memory (or offloaded), so MoE does not reduce VRAM need.

### Positions in space and time
Attention itself does not know where a token is. The model adds position information for three axes: frame (time), row, and column. Most current models use a rotary method (RoPE) for this. It explains two practical facts. A model works best at the resolutions, aspect ratios, and durations that it was trained on. Quality falls when you go far beyond them (for example 4× the trained duration). Read the native values in the model card.

### References as tokens
Many models take reference images or clips (a character, a product, a style) as extra tokens in the same sequence. The video tokens attend to them like to the prompt. This is "in-context" conditioning: no training is needed, and identity follows the reference closely. Limits: each reference adds tokens (cost), and many references can conflict. C04 uses this for consistency; C14 trains an adapter when references are not enough.

### How to read a model card
Check these items first:

| Item | Why it matters |
|---|---|
| License | Commercial use, or research only? |
| Modes | T2V, I2V, V2V, reference, editing, audio? |
| Native resolution, fps, max duration | Output that does not need upscaling or extension |
| Parameter count, precision variants | VRAM need (M01) |
| Distilled variant, recommended steps | Speed |
| Text encoder | Prompt understanding, extra VRAM |
| Known limits | Text in frame, hands, fast motion, faces |
| Training data statement | Legal risk (C16) |

## Tool walkthrough

### Model families by architecture (as of 2026-10)
| Feature | Examples |
|---|---|
| Joint audio-video generation | Veo 3.1, Kling 3.0, Seedance 2.x, LTX-2.5 (open weights) |
| Mixture of experts (high-noise and low-noise experts) | Wan 2.2, Wan 2.7 |
| LLM text encoder | LTX-2.5 (Gemma 4 12B), Wan (umT5), HunyuanVideo 1.5 |
| Many references as tokens | Seedance 2.5 (up to 50 references), Kling 3.0, Wan 2.7 reference-to-video |

Check each claim against the model card on the day you use it; versions change monthly.

## Worked example

**Task:** Read the LTX-2.5 announcement and fill the model-card table (facts as of 2026-08).

| Item | LTX-2.5 |
|---|---|
| Release | 2026-08-11, open weights on Hugging Face, day-one ComfyUI, also an API |
| Architecture | 22B asymmetric dual-stream DiT; video and audio generated together |
| Text encoder | Gemma 4 12B with a learned projection |
| Modes | T2V, I2V, V2V, text-to-audio, audio-to-video; native multishot; auto duration |
| Output | Up to 4K HDR |
| Speed variants | Full "dev" + distilled few-step; INT8 and NVFP4 quantizations |
| VRAM | Reported about 32 GB with FP8 |
| License | LTX-2.x Community License: a paid license for companies with annual revenue of US$10 million or more (C16·M01) |

Decision for a 32 GB GPU: use the distilled FP8 or NVFP4 build. Generate at 720p. Upscale selected shots. Use audio-to-video for music-driven shots.

## Lab

**Deliverable:** `C01/M04/model-cards.md`.

1. Choose 3 video models: one hosted (for example Kling 3.0 or Veo 3.1), and two open (for example Wan 2.7 and LTX-2.5 or HunyuanVideo 1.5).
2. Fill the model-card table for each one. Use only the vendor page, the Hugging Face card, or the technical report.
3. Mark each fact with its source URL and date.
4. Write a 5-line recommendation: which model for (a) a commercial ad, (b) a private local pipeline, (c) a dialogue scene with lip sync.

**Result checklist**
- [ ] 3 complete tables with sources.
- [ ] License is clearly stated for each.
- [ ] The recommendation uses the model-card facts, not opinions from social media.

## Model answer

- **(a) Commercial ad:** a hosted top model (Kling 3.0, Veo 3.1, or Seedance 2.5). Reasons: best quality, native audio, vendor terms allow commercial use on paid plans. Risk: vendor change (compare Sora 2 API shutdown on 2026-09-24).
- **(b) Private local pipeline:** Wan 2.7 (Apache 2.0, local weights, no data leaves the company) or LTX-2.5 (LTX-2.x Community License: free below US$10 million annual revenue). Reason: control and privacy. Check the license of every file in the workflow, not only the model (the VAE and the text encoder can differ).
- **(c) Dialogue with lip sync:** a joint audio-video model (Kling 3.0 with voice lock, Veo 3.1, or LTX-2.5). Alternative: generate silent video, then use a dedicated lip-sync model (C06).

Every recommendation names its source and date, and states the main risk, so that a reader can re-check it when the facts change.
