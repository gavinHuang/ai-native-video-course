---
title: ComfyUI graph model, install, and model management
hours: 12
outcomes:
  - Explain how ComfyUI runs a graph - typed nodes, links, execution order, and the output cache.
  - Read a current text-to-image graph node by node and say what each node does.
  - Install a pinned ComfyUI version locally or in a container on a rented GPU.
  - Download model files into the correct folders, check their hashes, and record their licenses in a lock file.
  - Run a workflow from the UI and export it in UI format and API format.
keywords: [ComfyUI, node graph, checkpoint, custom node, subgraph, API format, models.lock]
summary: >
  ComfyUI is a graph executor for generative models. Each node does one job, for example load a model, encode a
  prompt, make noise, sample, decode, or save. Links carry typed data between nodes. When you run the graph,
  ComfyUI runs only the nodes whose inputs changed and takes the other results from its cache. Model files live in
  fixed folders by type. Pin the ComfyUI version, record each model file with its hash and license, and keep every
  workflow in Git. Custom nodes run code on your machine, so install only the nodes that you trust.
diagram:
  type: flow
  title: The first graph (FLUX.2 klein 4B, distilled)
  nodes: ["Loaders: diffusion model, text encoder, VAE", "Text encode prompt → positive conditioning", "Empty latent (1024 × 1024)", "Noise + guider + sampler + sigmas", "Sampler: 4 steps → clean latent", "VAE decode → image → save"]
  highlight: [3]
watch:
  - title: "ComfyUI documentation — getting started and the interface"
    url: https://docs.comfy.org/
    note: "Read 'Installation', 'Interface', and 'Workflow templates'. 20 minutes."
  - title: "ComfyUI — GitHub repository README"
    url: https://github.com/comfyanonymous/ComfyUI
    note: "Read the sections on model folders, launch options, and the keyboard shortcuts."
  - title: "ComfyUI docs — FLUX.2 klein tutorial"
    url: https://docs.comfy.org/tutorials/flux/flux-2-klein
    note: "Compare the official notes with the graph that you take apart in the worked example."
quiz:
  - q: "You run a graph. Then you change only the seed and run it again. Which nodes run the second time?"
    options: ["All nodes, because the output is different", "The noise node and every node after it (sampler, decode, save)", "Only the save node", "Only the loaders, because the seed is in the model"]
    answer: 1
    explain: "ComfyUI caches each node output by its inputs. The loaders and the text encoder have the same inputs, so they come from the cache. The noise node and all nodes downstream of it run again."
  - q: "A teammate sends you a workflow JSON. The first key is 'nodes' and each node has 'pos' and 'widgets_values'. What is it, and can you POST it to /prompt?"
    options: ["API format; yes", "UI format; no, export it in API format first", "API format; only after you add a client_id", "A subgraph; yes, the server expands it"]
    answer: 1
    explain: "UI format stores the layout and widget lists for the editor. The server accepts only API format, which maps node IDs to class types and named inputs."
  - q: "Your klein graph uses 'flux-2-klein-4b.safetensors' (Apache-2.0). The VAE file comes from the FLUX.2-dev repository. What do you record before client work?"
    options: ["Nothing, the model family is Apache-2.0", "The license of each file, because the VAE repository has a non-commercial license", "Only the ComfyUI version", "Only the hash of the diffusion model"]
    answer: 1
    explain: "Licenses attach to files and repositories, not to model families. A graph is only as free as its most restricted file. Check the VAE license or use a VAE file with a license that permits your use."
  - q: "Text encoding takes 9 s on each run, but you never change the prompt. What does this tell you?"
    options: ["The cache works correctly", "Something upstream of the text encoder changes on each run, for example a loader with a random input, or the server restarts", "The text encoder is too large", "The prompt is too long"]
    answer: 1
    explain: "A node runs again only when one of its inputs changes. Find the changing input. A common cause is a server restart, which clears the cache, or a node that outputs a new value on every run."
  - q: "A custom node pack promises a 3× speed-up. It has 40 GitHub stars and no releases. What is the safe procedure for a production machine?"
    options: ["Install it with the manager and test it", "Read its code, pin a commit, test it in a separate container without secrets, then decide", "Install it, because nodes run in a sandbox", "Never use any custom nodes"]
    answer: 1
    explain: "Custom nodes are Python code with full access to the machine. Review the code, pin the version, and isolate the test. Many production pipelines use custom nodes, but they control them."
  - q: "Your models are on a shared NAS at /mnt/models, and you run 3 ComfyUI containers. How do you avoid 3 copies of 60 GB?"
    options: ["Copy the models into each image", "Mount the NAS path into each container, or use extra_model_paths.yaml to point ComfyUI to it", "Use smaller models", "Put the models in the output folder"]
    answer: 1
    explain: "ComfyUI reads model folders from its models directory or from extra paths in extra_model_paths.yaml. Keep models out of the image. Mount them read-only."
  - q: "The distilled klein graph uses CFG 1 and 'ConditioningZeroOut' for the negative input. Why?"
    options: ["It is a bug in the template", "Distilled models are trained to work without classifier-free guidance; CFG 1 means the negative prompt has no effect", "It makes the image darker", "It saves VRAM only"]
    answer: 1
    explain: "With CFG 1 the sampler uses only the positive prediction, so one model call per step is enough. This is part of why the distilled model is fast (C01·M06)."
deeper:
  - title: "ComfyUI — server configuration and command-line options (cli_args.py)"
    url: https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/cli_args.py
  - title: "ComfyUI — official workflow templates repository"
    url: https://github.com/Comfy-Org/workflow_templates
  - title: "ComfyUI-Manager (custom node manager)"
    url: https://github.com/Comfy-Org/ComfyUI-Manager
---
## Learn

### What ComfyUI is
ComfyUI is a graph executor for generative models. You build a directed graph of nodes. Each node is a Python class with typed inputs and typed outputs. The server sorts the graph and runs it on your GPU. The browser editor is only a client of that server.

You already know this pattern from build systems and data pipelines. A node is like a build target. A link is a dependency. The cache is like a build cache: a node runs again only when its inputs change.

### Nodes, links, and types
Each input and each output has a type. A link can connect only an output to an input of the same type. These are the main types:

| Type | What it carries | Example node that makes it |
|---|---|---|
| MODEL | The diffusion model weights, with any LoRA applied | Load Diffusion Model |
| CLIP | The text encoder (the name is historical) | Load CLIP |
| VAE | The encoder and decoder between pixels and latents | Load VAE |
| CONDITIONING | Encoded prompt, plus any references or control | CLIP Text Encode |
| LATENT | The latent tensor that the sampler denoises | Empty Latent Image |
| IMAGE | Decoded frames as a batch of pixels | VAE Decode, Load Image |
| NOISE, GUIDER, SAMPLER, SIGMAS | The four parts of a custom sampling setup | Random Noise, CFG Guider, KSampler Select, a scheduler |

Widgets are the values that you type on a node, for example a seed or a file name. Most widgets can also become inputs. Then another node can drive them, for example one "Width" node that feeds both the latent size and the scheduler.

### How a run works
1. You click Run, or a client sends the graph to `POST /prompt`.
2. The server checks the graph. It checks that each class exists, that each required input is set, that link types match, and that each file name exists.
3. The server finds the output nodes (Save Image, Save Video, Preview) and walks back to find the nodes that they need. Nodes that no output needs do not run.
4. For each node, the server compares the inputs with the cache. If the inputs did not change, it uses the cached output.
5. The other nodes run in dependency order. The server sends progress messages on a WebSocket.

The cache explains a lot of behavior. If you change only the seed, the loaders and the text encoder do not run again. If you change only the file name prefix of the save node, only the save node runs. If the server restarts, the cache is empty and the first run loads all models again.

### Two file formats
ComfyUI saves a workflow in two formats:
- **UI format** (`workflow.json`): node positions, groups, notes, subgraphs, and the widget values as lists. The editor needs this format. Commit it so that people can open the graph.
- **API format** (`workflow_api.json`): a flat map from node ID to `class_type` and named `inputs`. The server needs this format. Your code changes it and sends it (C11·M04).

A **subgraph** is a group of nodes that looks like one node in the editor. The official templates use subgraphs to hide detail. When you export in API format, the subgraph expands, and the inner nodes get IDs such as `77:65` (subgraph node 77, inner node 65).

### Model folders
ComfyUI finds models by type in fixed folders under `models/`:

```
models/
  diffusion_models/      # DiT and UNet weights (FLUX.2, Wan, LTX transformer)
  checkpoints/           # all-in-one files (model + text encoder + VAE), for example the LTX-2.3 checkpoint
  text_encoders/         # umt5, Qwen, Gemma encoders
  vae/
  loras/
  latent_upscale_models/ # for example the LTX x2 spatial upscalers
  controlnet/  clip_vision/  upscale_models/
```

To share one model store between several installs or containers, use `extra_model_paths.yaml` or mount the store at `models/`. Do not copy models into a container image. Images become large and slow to deploy.

### The lock file
A workflow is reproducible only if you can get the same model files again. Keep a `models.lock.json` file with one entry for each file:

```json
"wan2.2_ti2v_5B_fp16.safetensors": {
  "directory": "diffusion_models",
  "url": "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors",
  "bytes": 9999658824,
  "sha256": "456f901338bd...",
  "license": "apache-2.0",
  "checked": "2026-10-04"
}
```

The starter kit contains a complete lock file for all starter workflows (`starter/comfyui/models.lock.json`). `download_models.py` uses it and stops if a hash does not match.

Record the license of each file, not of the model family. Example from the starter kit: the first image model has a permissive license. But its official template loads a VAE file from a sibling repository that has a non-commercial license. The lock file shows this conflict at once. The worked example names the files.

### Install options
1. **Local, NVIDIA GPU (Windows or Linux):** the portable build, the desktop app, or a manual install with Python and a CUDA build of PyTorch.
2. **Container on a rented GPU:** best for reproducible work. Pin the ComfyUI commit in the Dockerfile. Mount models, input, and output as volumes.
3. **Hosted ComfyUI:** no setup, pay per use. Good for a first try. Check what you can export and which custom nodes are available.
4. **Apple silicon:** many image models run. Most video models run much faster on CUDA. Use a rented GPU for C11 video labs.

### Memory options
If a model does not fit in VRAM, ComfyUI can move parts of it to system RAM. This is slower but it works. Useful launch flags (as of ComfyUI 0.38, 2026-10):
- `--lowvram`: split the model and offload more.
- `--reserve-vram 2`: keep 2 GB free for other programs.
- `--cache-none`: use less RAM and VRAM, but run every node every time.
- `--use-sage-attention`: a faster attention kernel, if it is installed.
Also choose smaller weight files: FP8 or 4-bit variants (C01·M06).

### Custom nodes
A custom node is a Python package in `custom_nodes/`. It runs with the same rights as ComfyUI. It can read your files and your environment variables. Rules:
- Use core nodes when they can do the job. All starter workflows use core nodes only.
- Before you install a node pack, read its code and pin a commit.
- Test new node packs in a separate container without secrets.
- Record the commit of each node pack in your run log.

## Worked example

**Task:** take apart the first starter graph, `01_t2i_flux2_klein_4b.json`, node by node. This graph comes from the official FLUX.2 klein template. We kept the distilled branch (4 steps).

| Node (ID) | Class | Key settings | What it does |
|---|---|---|---|
| 77:70 | UNETLoader | `flux-2-klein-4b.safetensors` | Loads the 4B diffusion transformer (7.75 GB file) |
| 77:71 | CLIPLoader | `qwen_3_4b.safetensors`, type `flux2` | Loads the text encoder, a 4B language model (8.04 GB) |
| 77:72 | VAELoader | `flux2-vae.safetensors` | Loads the VAE (0.34 GB) |
| 76 | PrimitiveStringMultiline | the prompt text | Holds the prompt, so one value can feed several nodes |
| 77:74 | CLIPTextEncode | text from node 76 | Turns the prompt into positive conditioning |
| 77:76 | ConditioningZeroOut | | Makes an empty negative. With CFG 1 the negative has no effect |
| 77:68, 77:69 | PrimitiveInt | 1024, 1024 | Width and height. They feed the latent and the scheduler |
| 77:66 | EmptyFlux2LatentImage | 1024 × 1024, batch 1 | Makes the empty latent canvas |
| 77:73 | RandomNoise | seed | Makes the start noise from the seed |
| 77:62 | Flux2Scheduler | 4 steps | Makes the noise levels (sigmas) for 4 steps at this size |
| 77:61 | KSamplerSelect | `euler` | Chooses the solver |
| 77:63 | CFGGuider | CFG 1 | Combines model, positive, and negative into a guider |
| 77:64 | SamplerCustomAdvanced | | Runs the denoising loop |
| 77:65 | VAEDecode | | Turns the latent into pixels |
| 9 | SaveImage | prefix `C11/t2i_klein` | Writes a PNG with the workflow in its metadata |

Three points:
1. The classic `KSampler` node does noise, guidance, solver, and schedule in one node. Current templates split them into four nodes. This lets you change one part, for example use a different schedule, and keep the others.
2. The scheduler takes width and height. Flow-matching models shift the noise schedule with image size. One "Width" node feeds both places, so they cannot disagree.
3. The total download for this graph is 16.1 GB. The 4B text encoder is bigger than the diffusion model.

**Cache test.** We ran a small graph three times on a ComfyUI 0.38.0 server (2026-10-04). First run: all nodes ran. Second run, same inputs: no node ran; all came from the cache. Third run, only the save prefix changed: only the save node ran.

## Lab

**Deliverable:** `pipelines/comfy/` with `INSTALL.md`, `models.lock.json`, 3 workflows (UI and API format), and `runs.md`.

1. Install ComfyUI. Use a container on a rented GPU or a local NVIDIA GPU. Pin the version and write the commit in `INSTALL.md`.
2. Download the models for `01_t2i_flux2_klein_4b` and `03_i2v_wan22_5b` with `starter/comfyui/download_models.py`. Check that the hashes pass.
3. Run `starter/comfyui/validate_workflow.py` on both workflows against your server. Fix any problem that it reports.
4. Open the official templates for both workflows in the editor. Run them. Save the UI format and export the API format into Git.
5. Make one change of your own to the image graph, for example a second branch with a different seed and size. Save it as your third workflow.
6. Do the cache test: run, run again unchanged, change the seed, change only the save prefix. Write which nodes ran each time and the time of each run in `runs.md`.
7. Add a `license` field to each lock entry. Mark any file that you cannot use for commercial work.

**Result checklist**
- [ ] `INSTALL.md` has the ComfyUI commit, the GPU, the driver, and the PyTorch version.
- [ ] All hashes in the lock file pass.
- [ ] 3 workflows in Git, each in UI and API format, each validated.
- [ ] `runs.md` shows the cache test with times.
- [ ] Each lock entry has a license, and you marked the restricted files.

## Model answer

A strong submission looks like this.

```
pipelines/comfy/
  INSTALL.md            # ComfyUI 0.38.0 (f1072eb), RTX 5090 32 GB, driver 580.x, torch 2.14 + cu128
  Dockerfile            # pinned commit; models mounted read-only from /data/models
  models.lock.json      # 7 files, all hashes pass; flux2-vae marked "non-commercial: check"
  workflows/
    01_t2i_flux2_klein_4b.json          # UI format
    01_t2i_flux2_klein_4b_api.json
    03_i2v_wan22_5b.json
    03_i2v_wan22_5b_api.json
    01b_t2i_two_sizes.json              # own change: 1024 × 1024 and 1344 × 768 branches
    01b_t2i_two_sizes_api.json
  runs.md
```

`runs.md` (example shape; your times depend on your GPU):

| Run | Change | Nodes that ran | Time |
|---|---|---|---|
| 1 | none (cold start) | all 15 | 41 s (model load 35 s) |
| 2 | none | none | 0.1 s |
| 3 | seed | noise, guider, sampler, decode, save | 3.2 s |
| 4 | save prefix | save | 0.1 s |

Conclusion in the file: "Model load time is most of a cold run. Keep the server running between jobs. Change seeds freely: one image costs about 3 s here."

The reference Dockerfile is in `starter/solutions/C11-M01/`. It pins the same commit and does not contain models.
