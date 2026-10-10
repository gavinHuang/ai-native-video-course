# Tool landscape, October 2026

This page lists the current tools by category. It changes every quarter. The concept text in the modules does not depend on it. Facts marked **(V)** are checked on a primary or trade source. Other facts are reported by several sources but are not checked.

## Video generation: hosted

| Model | Vendor | Strong points (as of 2026-10) |
|---|---|---|
| Kling 3.0 / 3.0 Omni | Kuaishou | #1 in the blind-vote text-to-video arena (V). Up to 6 shots per generation, each 3–15 s, with shot size and camera move for each shot. Native audio with a voice locked from a reference. |
| Seedance 2.5 | ByteDance | 30 s in one take, native 4K, native audio, up to 50 references (images, audio, 3D white models, style), 10-bit color, region editing (V). In CapCut and Jimeng (即梦). |
| Veo 3.1 + Flow | Google | Cinematic realism, 4K, native 48 kHz audio, "Ingredients" (reference images), scene extension, Scene Builder. |
| Gemini Omni Flash | Google | Any-to-any model. Edit video by conversation. SynthID watermark on every clip. API about US$0.10/s. |
| Runway Gen-4.5 + Aleph 2.0 | Runway | Aleph edits existing video: remove objects, relight, add elements, restyle. Also inside Adobe Firefly. |
| Luma Ray3 / Ray3 Modify | Luma | Native 16-bit HDR. Video-to-video on actor footage. |
| Sora 2 | OpenAI | **API removed 2026-09-24 (V).** Use this as a case study for vendor risk. |

## Video generation: open weights (local or rented GPU)

| Model | Key facts |
|---|---|
| Wan 2.7 (Alibaba) | Apache 2.0. 27B MoE. T2V, I2V, reference-to-video with voice clone, instruction editing. 1080p, 15 s, first/last frame. |
| Wan 2.2 / 2.6 | Smaller variants run from about 8 GB VRAM (5B GGUF). Wide LoRA support. |
| LTX-2.5 (Lightricks) | 22B audio+video DiT, multishot, 4K HDR, distilled few-step variant, INT8 and NVFP4 builds, day-one ComfyUI (V). About 32 GB VRAM with FP8. |
| HunyuanVideo 1.5 (Tencent) | 80 GB full; about 24 GB INT8; lower with FP8 + tiling. |

## Image generation
GPT Image 2 (top of the image arenas, Sept 2026), Nano Banana Pro / Nano Banana 2 (Google, strong editing, 4K), FLUX.2 (open weights; FLUX.2 Klein is the small variant), Midjourney V8.x (style), Kling Image 3.0, Seedream (ByteDance).

## Audio
- **Voice, dubbing, avatars:** ElevenLabs (TTS, voice clone, dubbing, Avatars), HeyGen (Avatar IV, lip-synced dubbing in 175+ languages), Synthesia.
- **Music:** Suno v6 (2026-09-09, licensed training data), ElevenLabs Music v2.5 (2026-09-11, licensed). Licenses differ by plan.
- **Open TTS:** IndexTTS-2 / 2.5 (duration control for dubbing), CosyVoice 3 (0.5B, about 4 GB VRAM, Apache 2.0), Qwen3-TTS. Fish Audio S2 weights are for research only.

## LLMs and agents
Frontier families: Claude (Anthropic), GPT (OpenAI), Gemini (Google). Open weights: Qwen, DeepSeek. Agent coding tools: Claude Code, Codex. Rankings change monthly. Use LMArena and Artificial Analysis, then test on your own task (C03).

## Editing and finishing
- **DaVinci Resolve 21.1:** native MCP server in Resolve Studio (Sept 2026) (V). Assistants can organize timelines, rename, grade, apply LUTs, add markers, render, and check delivery specs.
- **Adobe Premiere 26.5:** Firefly AI Assistant (agent) for bins, renames, markers, first cut, storyboard to video. Generate Video, Sound Effects, Soundscape, and Music. An MCP server is reported.
- **Bridges:** Jumper (MCP for Premiere, Resolve, Final Cut, Avid), EditAssist.
- **Others:** Final Cut Pro, Avid Media Composer, Descript (transcript editing), CapCut (social, Seedance inside).
- **Finishing:** After Effects, Nuke, Fusion, Blender, Topaz (upscale and interpolation), iZotope RX, Pro Tools, Fairlight.

## Pipelines
- **ComfyUI:** the standard node graph for open models. **Comfy MCP** (public beta) connects Claude, Codex, and Cursor to ComfyUI workflows. Local community MCP servers also exist.
- **Model APIs:** fal.ai, Replicate (many models, one API), and vendor APIs.
- **Higgsfield:** multi-model studio, with an MCP server.
- **Training:** musubi-tuner (kohya-ss), AI Toolkit (ostris), fal LoRA trainers.

## Infrastructure
- **Local GPU:** RTX 5090 (32 GB), RTX PRO 6000 Blackwell (96 GB). Apple Mac Studio M5 Max (up to 128 GB) and M5 Ultra (up to 512 GB unified memory) are very good for editing and LLMs, and slower for most video diffusion. DGX Spark and Strix Halo give 128 GB unified memory in a small box.
- **Cloud GPU (mid-2026 list prices):** RunPod H100 about US$2.89/h; Modal H100 about US$3.95/h base; fal H100 about US$4.50/h (raw GPU), and per output about US$0.05 per video second; Replicate H100 about US$5.49/h.

## Law and provenance
- **EU AI Act Article 50:** transparency duties apply from 2026-08-02. Deepfakes need a clear label at first exposure. The Code of Practice asks for more than one marking layer: C2PA signed metadata + invisible watermark.
- Platform rules (YouTube, TikTok, Meta) add their own AI labels.
- Google SynthID is on Google model output. C2PA Content Credentials can be added with `c2patool`.

## Chinese ecosystem (useful to follow)
Kling (可灵), Jimeng / Seedance (即梦), Wan / Tongyi Wanxiang (通义万相), Hunyuan (混元), Vidu. There is a large "AI short drama" (AI短剧 / AI漫剧) industry with an industrial pipeline: engineered script → storyboard → image assets → video → edit. Many tutorials are on Bilibili and Zhihu.
