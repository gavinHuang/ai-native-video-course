# Next steps and specializations

After the capstone, choose one path. Each path gives the next skills, the primary sources to follow, and a first project.

## 1. AI Director
- **Next skills:** directing actors for performance capture; advanced story structure; longer-form continuity (10+ min); music video and ad formats.
- **Follow:** festival AI-film tracks; Curious Refuge case studies; vendor showcase channels (Runway, Kling, Google Flow).
- **First project:** a 5-minute narrative with 3 recurring characters and one location built as a 3D world.

## 2. Creative Technologist / Pipeline Engineer
- **Next skills:** custom ComfyUI nodes in Python; your own MCP servers; queue systems; evaluation harnesses.
- **Follow:** ComfyUI blog and GitHub; Model Context Protocol specification; Banodoco community; posts from ComfyUI and practitioners on X.
- **First project:** an open-source MCP server that controls one creative tool, with tests.

## 3. Generative Media Infrastructure Engineer
- **Next skills:** Kubernetes GPU scheduling; model serving (TensorRT, torch.compile, xDiT, sequence parallel); cost observability; multi-region storage.
- **Follow:** NVIDIA developer blog; vLLM and SGLang (multimodal serving); cloud vendor GPU docs.
- **First project:** serve an open video model behind an autoscaling endpoint with a cost dashboard (cost per output second).

## 4. Model Fine-Tuning Specialist
- **Next skills:** dataset curation at scale; captioning models; video LoRA and full fine-tune; distillation; evaluation design.
- **Follow:** musubi-tuner and AI Toolkit repos; Hugging Face Diffusers docs; arXiv cs.CV (video generation).
- **First project:** a brand-safe product LoRA for one open video model, with an eval report.

## 5. AI Finishing Artist (color, VFX, sound)
- **Next skills:** ACES deep dive; Nuke compositing; Houdini basics; Dolby Atmos mixing.
- **Follow:** Blackmagic training and certification; Foundry learning; Mixing Light; Netflix Partner Help Center (delivery specs).
- **First project:** a finishing pass that combines generated and real shots without visible difference.

## 6. Localization and Scale Producer
- **Next skills:** dubbing quality control; cultural adaptation; variant testing; platform APIs.
- **Follow:** platform creator docs; dubbing vendor research blogs.
- **First project:** one video, 10 languages, lip-synced, with a QC report and cost per language.

## 7. Research Engineer: video generation
- **Next skills:** PyTorch; diffusion and flow-matching math; distributed training; reading and reproducing papers.
- **Follow:** arXiv (cs.CV, cs.LG); open model technical reports (Wan, LTX, HunyuanVideo); CVPR, ICCV, NeurIPS, ICLR.
- **First project:** reproduce one ablation from an open video model paper at small scale.

## How to keep up (for every path)
1. Once a week: read release notes of the 5 tools you use most.
2. Once a month: run your fixed eval set (C17) on any new model.
3. Once a quarter: update your own tool landscape page.
4. Follow both English and Chinese sources. Many video models and pipelines come from Chinese labs first.
