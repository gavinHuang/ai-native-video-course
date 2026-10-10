# Readiness: what must exist before content production

Date: 2026-10-04 (v2 — content only; logistics removed)
Related: `PLAN.md` v4

Every item below is a content asset. Each one is necessary because the modules depend on it.

| # | Item | Why the content needs it | Output |
|---|---|---|---|
| R1 | **Competency map** | All 18 courses must connect without gaps or repetition. Each outcome has one home module and a prerequisite. | `docs/competency-map.md` |
| R2 | **Course outlines (18)** | Defines modules, outcomes, labs, and sources before writing. | `courses/Cxx-*/outline.md` |
| R3 | **Writing rules** | STE rules + the list of technical names that STE allows (for example "VRAM", "LoRA", "sampler", "timeline"). Keeps 100+ modules consistent. | `docs/writing-rules.md` |
| R4 | **Glossary** | One definition per term, linked from every module. | `glossary/` |
| R5 | **Verified landscape** | Every model, tool, price, and law fact checked on a primary source. Wrong facts destroy trust with IT professionals. | `research/ai-landscape-2026-10.md` (verified) |
| R6 | **Primary-source library** | Papers, model cards, technical reports, official docs for each course ("Go deeper" sections). | `research/sources/` |
| R7 | **Reference workflows** | Tested ComfyUI graphs, API scripts, agent and MCP configs, ffmpeg recipes. Labs and worked examples are built on them. | `lab-kit/` (repo) |
| R8 | **Generated example library** | Real outputs (good and bad) with prompts, settings, and cost. Needed for "visual examples" and "worked example" in every generation module. | `assets/generated/` + `CREDITS.md` |
| R9 | **Eval set** | A fixed set of prompts and briefs to compare models. Used in C01, C05, C17, and to refresh the landscape each quarter. | `lab-kit/evals/` |
| R10 | **Diagram set** | Core architecture and pipeline diagrams reused across courses (diffusion process, DiT, latent space, ComfyUI graph, agent + MCP loop, local vs cloud architecture). | `assets/diagrams/` |
| R11 | **Module template** | The fixed 11-part page, quiz format, lab format. | `templates/` |

## Dependency between items

```
R1 → R2 → (R3, R4) → R11 → modules
R5 → R6
R5 → R7 → R8, R9
R10 can start after R2
```

## What Claude needs to produce R7–R9

Real generated outputs need generation access: an aggregator API key (fal.ai or Replicate) covers most image and video models, plus an ElevenLabs key for audio. Without keys, R7–R9 use vendor sample outputs and links, and the worked examples are weaker.
