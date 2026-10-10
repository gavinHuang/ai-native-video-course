# AI Video Landscape — October 2026

Date of research: 2026-10-04
Status: snapshot. These tools change every month. Update this file every 3 months. Lessons must refer to this file and must not hard-code model names into concept text.

Confidence: many sources are vendor blogs or comparison sites. Before a fact goes into a lesson, check it on the vendor's official page. Items marked (V) are checked on a primary or trade source.

---

## 1. Generative video models

| Model | Vendor | Access | Strong points (reported) |
|---|---|---|---|
| Kling 3.0 / v3 | Kuaishou | Closed, app + API | #1 text-to-video in blind-vote arena (score 1934, 2026-10-02) (V). Lifelike humans, motion control. |
| Happy Horse 1.0 | Alibaba | Closed | #2 in the same arena (1816) (V). |
| Seedance 2.0 / 2.5 | ByteDance | Closed, API | #3 (2.0 Fast, 1747) (V). Multi-shot, up to 12 references, native audio, clips up to 15 s. |
| Veo 3.1 | Google | Flow app, Gemini, API | Cinematic realism, 4K, native audio (48 kHz), "Ingredients" (up to 3 reference images), scene extension to about 140 s. |
| Sora 2 | OpenAI | App + API | Clips to about 25 s, 1080p. |
| Runway Gen-4.5 + Aleph 2.0 | Runway | Runway app; also inside Adobe Firefly | Aleph = in-context video editing: remove objects, relight, add elements, restyle. |
| Ray3 / Ray3 Modify | Luma | App + API | Native 16-bit HDR. Video-to-video edit of actor footage. |
| Firefly Video + partner models | Adobe | Firefly, Premiere | One interface for Adobe and partner models (Runway, Google, others). |

**Open-weight models (run locally or on rented GPUs):**

| Model | VRAM need (reported) |
|---|---|
| Wan 2.2 (5B GGUF to 14B) / Wan 2.5–2.6 | 8 GB (small quantized) up to 80 GB |
| LTX-2.3 / LTX-2.5 (Lightricks) | 2.3: 24 GB; 2.5: 32 GB with FP8 (RTX 5090 class). Image + audio to video. |
| HunyuanVideo 1.5 (Tencent) | 80 GB full; 24 GB INT8; about 8 GB with FP8 + tiling |
| CogVideoX, Mochi 1, Open-Sora | 24 GB class with optimization |

## 2. Generative image models

- GPT Image 2 (OpenAI): #1 in Artificial Analysis and LMArena image arenas, Sept 2026 (reported).
- Nano Banana Pro / Nano Banana 2 (Google Gemini): strong image editing, native 4K.
- FLUX.2 (Black Forest Labs): best open-weight choice for self-hosting; FLUX.2 Klein used in ComfyUI character workflows.
- Midjourney V8.1: artistic style.

## 3. Audio models

- **Music:** Suno v6 (Sept 9, 2026), trained on licensed music (WMG, BMG, Believe deals). ElevenLabs Music v2.5 (Sept 11, 2026), 3 s to 5 min, licensed training data, UMG deal. License terms differ by plan; teach students to read them.
- **Voice and dubbing:** ElevenLabs (TTS, voice clone, dubbing, Avatars since June 2026), HeyGen (Avatar IV, dubbing with lip sync, 175+ languages), Synthesia (140+ languages, multi-speaker lip sync).

## 4. Language models (for scripts, research, agents)

Frontier families: Anthropic Claude (Opus 5.5, Sonnet 5.5, Fable 5), OpenAI GPT (GPT-6 series), Google Gemini (3.x), plus open-weight Qwen and DeepSeek. Rankings change often. Teach students to read leaderboards (LMArena, Artificial Analysis) and to test on their own tasks.

## 5. AI in editing software

- **DaVinci Resolve 21.1 (Sept 2026) (V):** built-in MCP server (Studio version). AI assistants (Claude Desktop, Claude Code, ChatGPT, others) can organize timelines, rename clips, apply grades and LUTs, add markers, render several formats, and check delivery specs.
- **Third-party agent bridges:** Jumper (local MCP; Premiere, Resolve, Final Cut, Avid), EditAssist (Resolve, Premiere, After Effects, Final Cut), Palmier Pro (AI-native Mac editor with MCP).
- **Adobe Premiere Pro:** Firefly Generative Extend, auto-edit, partner models.
- **CapCut:** auto-captions, background removal, auto-reframe, TTS, long-video-to-shorts.
- **Descript:** edit video by editing the transcript.

## 6. Generative workflows (current best practice)

- **Node pipelines:** ComfyUI is the standard for local and controllable work. Typical chain: character sheet → train a small LoRA on 10–15 crops → start frame (FLUX.2) → image-to-video (LTX-2.3 / Wan) → lip sync → edit.
- **Consistency methods:** reference images ("ingredients"), first/last-frame control, IP-Adapter, LoRA.
- **All-in-one apps:** Google Flow (Scene Builder, Ingredients, Extend), Firefly boards, Runway.
- **Agentic editing:** an LLM agent drives the NLE through MCP; a human reviews each step.

## 7. World models and 3D

- Genie 3 (Google DeepMind): interactive worlds from text, about 720p/24 fps, about 60 s coherence; public to AI Ultra users since Jan 2026.
- Marble (World Labs): generates 3D worlds as Gaussian splats (.ply/.spz) from text, image, panorama, or video. Used for previs and virtual locations.
- NVIDIA Cosmos: world models for simulation.
- Unreal Engine: virtual production and real-time rendering.

## 8. Infrastructure

**Local hardware (2026):**
- NVIDIA RTX 5090 (32 GB GDDR7): the main consumer GPU for local video models. RTX PRO 6000 Blackwell for bigger models.
- Apple Mac Studio M5 Max (up to 128 GB unified memory, from US$2,499) / M5 Ultra (up to 512 GB). Very good for editing; slower than NVIDIA for most video generation.
- NVIDIA DGX Spark, AMD Strix Halo: 128 GB unified memory, compact.
- Main idea to teach: VRAM size vs memory bandwidth vs software support (CUDA vs Metal/MLX).

**Cloud GPU (reported list prices, mid-2026):**

| Provider | Type | H100 per hour |
|---|---|---|
| RunPod | Rent pods / serverless | about $2.89 (A100 community from $0.69) |
| Modal | Serverless (Python) | about $3.95 base (more for region / non-preemptible) |
| fal.ai | Model APIs per output, also raw GPUs | $4.50 raw; video about $0.05/s, image about $0.03 |
| Replicate | Model APIs, per-second billing | about $5.49 |

Per-second API prices for video (reported): Wan about $0.07/s, Veo 3.1 about $0.09/s.

## 9. Law and trust

- **EU AI Act Article 50:** transparency duties enforceable from 2 Aug 2026 (check for any later delay or change). Deepfakes must have a clear label at first exposure. The Code of Practice says to use more than one marking layer: C2PA signed metadata + invisible watermark.
- TikTok, Meta, and YouTube have their own AI disclosure rules on top.
- Penalties up to €7.5M or 1.5% of global revenue.

## 10. Education programs seen

- Curious Refuge (AI filmmaking, advertising, screenwriting, VFX, documentary tracks; final project = short film made mainly with AI).
- Harvard Extension: Generative Media and Creative AI Graduate Certificate (4 courses).
- NYU Tisch + Runway: "Generative Filmmaking in the Age of Hypercinema".
- UW-Stout: AI-Assisted Film and Video Production (summer 2026).
- Falmouth Post Production & VFX BA: Avid, Pro Tools, Houdini, Maya, Nuke, Unreal, Resolve.
- UCLA Extension Post-Production Certificate: Avid, After Effects / Nuke, AI/ML VFX methods, Pro Tools.

## 11. Addendum — second research pass (EN + ZH + X), 2026-10-04

**Verified on primary or trade sources (V):**
- **OpenAI Sora 2 API removed 2026-09-24** (V, OpenAI deprecations page): Videos API, sora-2, sora-2-pro. Announced 2026-03-24. No replacement. Reports say the consumer Sora app closed 2026-04-26. → Teaching case: never build a pipeline on one vendor. Remove Sora from "current tools" lists.
- **Seedance 2.5** (ByteDance, announced 2026-06-23 at Volcano Engine FORCE; public about July 31) (V): 30 s single take, native 4K, native audio, up to 50 multimodal references (images, audio, 3D white models, style refs), 10-bit color, region-level editing, 3D white-box preview. In CapCut / Jimeng (即梦). No US timeline at announcement.
- **Kling 3.0** (Kuaishou, 2026-02-05) (V, People's Daily / Zhihu): "all-in-one" multimodal; up to 6 shots per generation, each 3–15 s, with shot size and camera move per shot; native audio with voice lock from a reference video; Chinese dialects. Also Kling Video 3.0 Omni, Kling Image 3.0.
- **Wan 2.7** (Alibaba, 2026-04-01..06): four models (T2V, I2V, reference-to-video with voice cloning, instruction editing), Apache 2.0, 27B MoE, 1080p, 15 s, first/last frame, 9-grid I2V, up to 5 reference videos, "Thinking Mode" planning. Wan 2.6 R2V in ComfyUI (V, blog.comfy.org).
- **LTX-2.5** (Lightricks, 2026-08-11) (V, comfyui-wiki): 22B asymmetric dual-stream DiT, joint audio+video, Gemma 4 12B text encoder, native multishot, auto duration, 4K HDR, T2V/I2V/V2V/T2A/A2V. Distilled few-step variant; INT8 and NVFP4 quantizations; day-one ComfyUI.
- **Gemini Omni Flash** (Google, I/O 2026-05-19): any-to-any; conversational video editing; SynthID on every clip; in Gemini app, Flow, YouTube Shorts / YouTube Create; API since 2026-06-30, about $0.10/s.
- **Adobe Premiere 26.5 (Sept 2026)**: Firefly AI Assistant (agent) in Premiere — bins, renames, markers, first cut, storyboard → video. Generate Video from reference frames, Generate Sound Effects, Soundscape (beta), Music (beta). Premiere publishes an MCP server (reported).
- **Comfy MCP** (public beta, ComfyUI official X account): connect Claude / Codex / Cursor to ComfyUI; run workflows in natural language; search models/nodes/templates. Also community local MCP servers for ComfyUI; Claude Code can drive headless ComfyUI through its JSON API.
- **Higgsfield MCP**: one URL connects Claude to the Higgsfield multi-model video studio (reported on X).

**Prompting knowledge from X posts (practitioners, 2026):**
- Kling 3 rewards short prompts; Seedance rewards very specific long prompts; reference images help both.
- Structured (JSON) prompts for Veo: sections for shot (composition, lens, frame rate, camera movement), subject, scene, lighting, palette, audio. Start small, iterate like code. Google formula: [Cinematography] + [Subject] + [Action] + [Context] + [Sound].
- Typical low-cost UGC ad stack reported: Claude (script) + GPT Image 2 (frames) + Seedance 2 (motion) → about US$2–4 per video.

**Chinese industry practice (Zhihu, CSDN, Tencent Cloud, The Paper, Bilibili):**
- "AI short drama" (AI短剧 / AI漫剧) industrial pipeline: script → storyboard → image assets → AI video → edit. Scripts are "engineered for machines": character tags + standard parameters; scene = space + light; shot = type + size + camera move predefined.
- Consistency: character reference sheets (front, side, expression library), fixed seeds, consistency controls; 360° panorama as scene anchor for long video (Seedance).
- Reported cost: about ¥200 per finished minute; one person about 2 hours per episode with end-to-end tools; about ¥1,000 per AI short drama vs about ¥500,000 for a traditional micro-drama (claims, not verified).

**Audio (open models):** IndexTTS-2 / 2.5 (duration control for dubbing), CosyVoice 3 (0.5B, about 4 GB VRAM, Apache 2.0), Qwen3-TTS, Fish Audio S2 (research-only weights). 

**LoRA training:** musubi-tuner (kohya-ss) supports HunyuanVideo, Wan 2.1/2.2, FLUX.2, Qwen-Image and others; 12 GB+ image, 24 GB+ video (FP8 + block swap helps). AI Toolkit (ostris) has Wan I2V training with RunPod/Modal recipes. fal hosts a Wan 2.2 LoRA trainer. Character LoRAs trained on stills generalize to motion.

Additional sources:
- https://developers.openai.com/api/docs/deprecations
- https://thenextweb.com/news/bytedance-seedance-2-5-ai-video-4k-30-seconds
- https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5
- http://finance.people.com.cn/n1/2026/0205/c1004-40660255.html
- https://zhuanlan.zhihu.com/p/2002832521004590013
- https://comfyui-wiki.com/en/news/2026-08-11-ltx-2-5-open-weights-release
- https://blog.comfy.org/p/wan26-reference-to-video
- https://docs.comfy.org/zh/tutorials/video/wan/wan2_2
- https://thenextweb.com/news/google-gemini-omni-flash-video-model-io-2026
- https://community.adobe.com/announcements-727/what-s-new-in-adobe-premiere-26-5-september-2026-1641187
- https://techcrunch.com/2026/06/18/adobe-adds-its-ai-assistant-to-premiere-illustrator-and-indesign/
- https://x.com/ComfyUI/status/2071625866912944151
- https://x.com/PurzBeats/status/2030461786982392113
- https://x.com/startupideaspod/status/2045330626203824444
- https://x.com/GoogleCloudTech/status/1994889105860145655
- https://x.com/nestymee/article/2071972061124383110
- https://cloud.tencent.com/developer/article/2647810
- https://m.thepaper.cn/newsDetail_forward_33643563
- https://www.bilibili.com/video/BV1C7QoBZEEk/
- https://github.com/kohya-ss/musubi-tuner
- https://arxiv.org/pdf/2601.03888 (IndexTTS 2.5)
- https://arxiv.org/pdf/2603.08823 (Fish Audio S2)

## Sources

- https://llm-stats.com/leaderboards/best-ai-for-video-creation
- https://www.atlascloud.ai/blog/tips/best-ai-video-generation-models-2026
- https://www.media.io/comparison/best-ai-video-generation-models.html
- https://www.spheron.network/blog/ai-video-generation-gpu-guide/
- https://willitrunai.com/blog/video-generation-gpu-guide-2026
- https://ltx.io/blog/open-source-video-generation-models-guide
- https://comfy.org/workflows/use-cases/ai-image-to-video/
- https://www.runflow.io/blog/comfyui-consistent-characters-flux
- https://ymcinema.com/2026/09/17/davinci-resolve-21-1-mcp-ai-assistants-control-edit/
- https://getjumper.io/ai-agents
- https://editassist.dev/integrations
- https://www.techno-pulse.com/2026/04/best-ai-video-editing-tools-in-2026.html
- https://llm-stats.com/leaderboards/best-ai-for-image-generation
- https://www.teamday.ai/blog/best-ai-image-models-2026
- https://www.redsharknews.com/adobe-runway-ai-video-firefly-gen-4-5
- https://helpx.adobe.com/firefly/web/firefly-video-editor/generate-videos/generate-videos-using-runway-video-models.html
- https://lumalabs.ai/news/runway-ai
- https://aividpipeline.com/blog/google-flow-veo-3-1-guide-2026
- https://www.teamday.ai/blog/best-ai-music-models-2026
- https://undetectr.com/blog/suno-vs-elevenlabs-music
- https://www.heygen.com/blog/best-ai-dubbing-tools
- https://benchlm.ai/frontier-ai-models
- https://tech-insider.org/genie-3-vs-marble-vs-nvidia-cosmos-world-models-2026/
- https://radiancefields.com/world-labs-formally-launches-marble-a-generative-world-model
- https://www.digitalapplied.com/blog/best-hardware-run-local-ai-models-2026-price-brackets-guide
- https://medium.com/@rosgluk/rtx-5090-vs-128gb-unified-memory-strix-halo-dgx-spark-and-mac-studio-m5-566c12d6e374
- https://www.apple.com/mac-studio/
- https://getdeploying.com/fal-ai-vs-runpod
- https://jarvislabs.ai/ai-faqs/best-cloud-gpu-providers-2026
- https://www.buildmvpfast.com/api-costs/gpu
- https://blog.pebblous.ai/blog/eu-ai-content-labeling-article-50-provenance/en/
- https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content
- https://www.socialscalehub.com/academy/ai-content-disclosure-rules-2026-tiktok-instagram-youtube
- https://curiousrefuge.com/advanced-ai-filmmaking
- https://extension.harvard.edu/academics/programs/generative-media-and-creative-ai-graduate-certificate/
- https://www.uwstout.edu/about-us/news-center/vanguard-artificial-intelligence-filmmaking-course-emerges-uw-stout
- https://www.falmouth.ac.uk/study/undergraduate/post-production-visual-effects
- https://www.uclaextension.edu/entertainment/film-tv/certificate/post-production
