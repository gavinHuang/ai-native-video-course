# Program Plan: AI-Native Video Content Creation

Version: 4 (2026-10-04)
Status: BUILT (2026-10-04). 18 courses / 74 modules in `content/`, site in `site/`. See `docs/progress.md`.
Language: ASD-STE100 (Simplified Technical English).

Change log:
- v1: single course, logistics, marketing kit. Rejected.
- v2: self-paced, 16 craft modules, one editor. Too narrow.
- v3: degree-level program, but "traditional video + AI added". Had logistics questions.
- v4: **AI-native.** AI is the main production medium. Audience = adult IT professionals. No logistics. Each level states its requirements.

---

## 1. Audience

Adults with several years of IT work experience. We assume the student can already:
- Use a command line, Git, and a package manager.
- Read and change Python and JSON. Call a REST API.
- Use a cloud console (AWS, GCP, or Azure) and Docker.

We do **not** assume any video, film, or design experience.

Effect on content: no computer basics. Technical depth is high (architecture, APIs, self-hosting, automation). Film craft is taught as the language that a person needs to direct and judge AI output.

## 2. Program goal

The graduate can:
1. **Explain** how current generative models for text, image, video, audio, and 3D work, at architecture level.
2. **Direct** models to make professional video: story, shots, consistency, sound, edit, finish.
3. **Build** AI-native production pipelines: node graphs, model APIs, LLM agents, MCP tools, automation at scale.
4. **Run** the infrastructure: local GPU, cloud GPU, serverless inference, storage, cost, and observability.
5. **Fine-tune and self-host** open models (LoRA for characters and styles; deploy on rented GPUs).
6. **Ship** content that obeys law and provenance rules (copyright, consent, EU AI Act Art. 50, C2PA).
7. **Go further:** read papers and model cards, test new models in one day, and choose a specialization.

## 3. AI-native principles

1. **AI is the medium, not a feature.** Generation, editing, and delivery are AI-first. Camera capture is one input type among others (reference, plate, performance capture).
2. **The human is the director and the quality gate.** Students learn film language to give precise intent and to reject bad output.
3. **Agents do the repetitive work.** LLM agents operate tools (NLE, ComfyUI, APIs) through MCP and scripts. The student designs, reviews, and approves.
4. **Concepts last; tools change.** Concept text has no product names. Product names live in `research/ai-landscape-YYYY-MM.md`, updated every quarter. Labs name the current best tool and one alternative.
5. **Measure, do not guess.** Every model choice uses a small test: quality, consistency, speed, and cost per usable second.
6. **Rights by design.** Every project keeps a prompt log, a source/rights log, and a disclosure plan from day one.

## 4. Program structure

5 levels, 17 courses, 1 capstone. About 1,000 study hours (the site adds up the module hours; 1,010 h on 2026-10-04).

### Level 1 — Core models and screen language (about 160 h)

| Code | Course | Content |
|---|---|---|
| C01 | Generative Model Internals | Tokens, embeddings, transformers, attention. VAEs and latent space. Diffusion, flow matching, diffusion transformers (DiT). Joint audio-video generation. Conditioning: text, image, reference, control signals. Sampling, steps, guidance (CFG), seeds. Distillation and fast models. Quantization (FP16, FP8, INT8, GGUF). LoRA and adapters. Evaluation: arenas, Elo, human preference, benchmarks and their limits. Labs in Python notebooks. |
| C02 | Screen Language for AI Directors | Shot sizes, angles, lens language (focal length, depth of field), camera movement, composition. Light language (key, fill, contrast, color temperature, motivated light). Continuity and the 180° rule. Cutting theory (rhythm, J/L cuts, match cuts). Story structure for 15 s, 60 s, 3 min, and 10 min. How to write each element as a precise prompt and how to judge it. |
| C03 | LLMs as Creative and Production Engine | Context engineering, structured output (JSON schema), multi-step reasoning. From brief → treatment → script → shot list → prompts, all as structured data. Critique loops (LLM as reviewer). Model selection by test. Agents and tool use. MCP: concept, clients, servers. Agentic coding tools (Claude Code, Codex) used for media work. |

### Level 2 — Generation (about 220 h)

| Code | Course | Content |
|---|---|---|
| C04 | Image Generation and Look Development | Text-to-image, image editing by instruction, reference control, style systems. Character sheets, product sheets, environment sheets. Key frames and storyboards. Upscaling. Current tools: GPT Image, Nano Banana Pro, FLUX.2, Midjourney V8. |
| C05 | Video Generation: Directing the Model | Text-to-video, image-to-video, video-to-video. First/last frame, camera and motion control, multi-shot generation, references ("ingredients"), extension, native audio. Consistency of character, product, and location across shots. Shot coverage plans for AI. Cost per usable second. Current tools: Kling 3, Seedance 2.x, Veo 3.1 / Flow, Sora 2, Runway Gen-4.5 + Aleph, Luma Ray3; open: Wan, LTX-2.x, HunyuanVideo. |
| C06 | Audio Generation: Voice, Music, Sound | TTS and voice design, voice cloning with consent, performance direction for AI voice. Lip sync and avatars. AI dubbing and localization. Music generation and license tiers. Sound effects generation. AI cleanup and stem separation. Current tools: ElevenLabs, HeyGen, Synthesia, Suno v6, Eleven Music v2.5. |
| C07 | World Models, 3D, and Virtual Production | Gaussian splatting, NeRF basics. Generated 3D worlds (Marble), interactive world models (Genie 3). Virtual camera moves in generated worlds. Unreal Engine for real-time scenes and previs. Combining 3D layout with video models for exact camera control. |

### Level 3 — AI-native post-production (about 160 h)

| Code | Course | Content |
|---|---|---|
| C08 | Agentic Editing | Transcript-based editing. Auto-assembly from a script and shot list. LLM agents that operate the NLE via MCP (Resolve 21.1 native MCP; bridges for Premiere, Final Cut, Avid). Review and approve each agent action. Long-form to short-form. NLE landscape: Resolve, Premiere Pro, Final Cut Pro, Avid, Descript, CapCut. |
| C09 | AI Finishing: Image | Color management (Rec.709, Rec.2020, ACES), scopes, grading. AI relight, AI roto, object removal, generative extend and fill. Upscaling, frame interpolation, restoration, HDR. Compositing generated elements with plates. Tools: Resolve, After Effects, Nuke, Runway Aleph, Topaz. |
| C10 | AI Finishing: Sound | Dialogue clean-up, sound design with generated elements, music edit, mix, loudness targets (LUFS) per platform, stems and deliverables. Tools: Fairlight, Pro Tools, iZotope RX, AI stem tools. |

### Level 4 — Pipelines and infrastructure (about 260 h)

| Code | Course | Content |
|---|---|---|
| C11 | Node Pipelines (ComfyUI) | Graph model, model loaders, samplers, ControlNet, IP-Adapter, first/last-frame nodes. Character pipeline: sheet → LoRA → start frame → i2v → lip sync. Custom nodes. Running ComfyUI as an API (headless). Version control of workflows. |
| C12 | Orchestration and Agents | Model APIs (vendor APIs, fal, Replicate). Async jobs, queues, retries, webhooks. Build your own MCP server for a media tool. Multi-agent production: writer agent, director agent, generator, reviewer. Automated quality checks (vision-model review, ffprobe checks, loudness checks). ffmpeg and Whisper in the pipeline. |
| C13 | Infrastructure for Generative Video | **Local:** GPU architecture, VRAM vs memory bandwidth, CUDA vs Metal/MLX; NVIDIA RTX 5090 / RTX PRO 6000 vs Apple M5 Max/Ultra vs DGX Spark class. NVMe, NAS, 10/25 GbE. **Cloud:** GPU rental (RunPod, Lambda, hyperscalers), serverless GPU (Modal), per-output APIs (fal, Replicate). Containers for model serving, cold starts, autoscaling, spot/preemptible. Object storage, CDN, media asset management. Review tools (Frame.io, Blackmagic Cloud). **Operations:** cost per usable second, local vs cloud break-even, monitoring, secrets, data privacy. Infrastructure as code. |
| C14 | Fine-Tuning and Self-Hosting | Datasets for LoRA (characters, products, styles): collect, caption, clean, consent. Train image and video LoRAs. Evaluate overfit and leakage. Quantize and serve open models (Wan, LTX, HunyuanVideo, FLUX.2) on rented GPUs. Throughput tuning. |
| C15 | Video at Scale | Templates + data → many variants (personalized, localized, A/B). Long-to-short automation. Localization pipeline (transcribe → translate → dub → lip sync → caption). Platform specs, publishing APIs, analytics feedback loop into generation. |

### Level 5 — Trust and frontier (about 100 h)

| Code | Course | Content |
|---|---|---|
| C16 | Law, Provenance, and Trust | Copyright status of training and outputs. Model and output licenses. Likeness and voice rights, consent records. EU AI Act Article 50, platform AI-disclosure rules. C2PA signing in the pipeline (c2patool), invisible watermarks. Deepfake risk, misuse, bias, energy cost. |
| C17 | Frontier and Research Practice | How to read a paper, a model card, and a technical report. How to test a new model in one day (a fixed eval set). Current research lines: longer coherence, real-time and interactive video, world models, 3D-consistent video, audio-video joint models. Specialization paths (Section 7). |

### Capstone — C18 (about 100 h)

One complete AI-native production, from a real-style brief:
1. A 2–5 minute short film or ad, mainly generated.
2. A 5-video short-form series made by an automated pipeline.
3. The pipeline itself: repo, diagram, cost report, eval results, rights log, C2PA signing.
4. A technical write-up: model choices with test data.

## 5. Requirements by level (stated, not asked)

| Level | Compute | Accounts / software | Typical spend (estimate, Oct 2026) |
|---|---|---|---|
| L1 | Any modern laptop. | Python 3, Jupyter (local or Colab). One frontier LLM subscription or API key. | US$20–50 / month |
| L2 | Any modern laptop. Local generation is optional. | Credits on 2–3 hosted generators, or one aggregator API (fal / Replicate). ElevenLabs. | US$100–300 for the level (video: about US$0.05–0.10 per generated second; plan 5× more generated than used) |
| L3 | Laptop with 16 GB+ RAM for editing. | DaVinci Resolve (free); Resolve Studio for native MCP (one-time licence). An MCP-capable LLM client. | One-time licence + LLM subscription |
| L4 | NVIDIA GPU with 24 GB VRAM minimum, 32 GB recommended (RTX 5090 class) **or** rented cloud GPU (H100 about US$3–5/h). | Docker, ComfyUI, cloud account, object storage. | Cloud path: about US$150–400 GPU time for the level |
| L5 | Same as L4. | c2patool. | Low |

All prices are estimates from `research/ai-landscape-2026-10.md`. Check them every quarter.

## 6. Standard module structure

1. Outcomes (testable).
2. Concept text (STE, no product names).
3. Diagram (minimum 1, SVG).
4. Visual examples (good vs bad output, labeled AI).
5. Audio (narration or sound comparison).
6. Watch (curated video links with timestamps and reason).
7. Worked example: real prompts, real settings, real outputs, real cost.
8. Lab: current best tool + one alternative (open or hosted). Code or workflow files in the repo.
9. Self-check quiz with explanations.
10. Model answer.
11. Go deeper: papers, model cards, official docs.

## 7. Specialization paths after the program

1. AI Director (narrative, ads, music video).
2. Creative Technologist / Pipeline Engineer (ComfyUI, agents, MCP, automation).
3. Generative Media Infrastructure Engineer (serving, scaling, cost).
4. Model Fine-Tuning Specialist (LoRA, datasets, evaluation).
5. AI Finishing Artist (color, VFX, sound with AI).
6. Localization and Scale Producer (dubbing, variants, analytics).
7. Research Engineer, Video Generation (PyTorch, training, papers).

## 8. Sources

- `research/ai-landscape-2026-10.md`: models, tools, infrastructure, law (October 2026).
- `research/similar-courses.md`: craft and degree courses (structure and exercises).

## 9. Work steps

See `docs/readiness.md` for what must be ready before content production.
