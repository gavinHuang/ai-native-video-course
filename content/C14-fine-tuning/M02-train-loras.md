---
title: Train image and video LoRAs
hours: 16
outcomes:
  - Explain the main LoRA settings - rank, learning rate, steps, resolution, batch, precision - and what each changes.
  - Train an image LoRA and a video LoRA on open models, locally or on rented GPUs, with checkpoints.
  - Render fixed eval prompts at every checkpoint, and read the fidelity-flexibility curve.
  - Choose a checkpoint by a rule with measurements, and log every experiment with its cost.
keywords: [LoRA rank, learning rate, checkpoint, overfitting, sample grid]
summary: >
  Training a LoRA adjusts a small set of extra weights until the base model makes your subject on the trigger word.
  Rank sets how much the LoRA can store, the learning rate how fast it changes, and the steps how long it trains.
  Save checkpoints often, and render the same eval prompts with the same seeds at each one. Identity rises with the
  steps; then flexibility falls and the subject starts to appear without the trigger. Choose the checkpoint where
  identity is strong, new prompts still work, and nothing leaks. Log the data version, settings, checkpoints, scores,
  and cost of every run.
diagram:
  type: flow
  title: A training run
  nodes: ["Dataset v3 (checked)", "Config: rank, LR, steps, buckets", "Train; checkpoint every 250–500 steps", "Render eval prompts per checkpoint (fixed seeds)", "Score: fidelity, leakage, flexibility", "Choose by rule; log run + cost"]
  highlight: [3, 4]
watch:
  - title: "fal — Wan 2.2 LoRA trainer (hosted training playground)"
    url: https://fal.ai/models/fal-ai/wan-22-trainer/t2v-a14b/playground
    note: "See which parameters a hosted trainer exposes."
  - title: "musubi-tuner — Wan / HunyuanVideo / FLUX.2 training docs"
    url: https://github.com/kohya-ss/musubi-tuner
    note: "Read the Wan training document; note the FP8 and block-swap options."
quiz:
  - q: "Identity is weak at step 1,200, strong and flexible at 1,800, and at 2,400 the raincoat appears in every image, also in prompts for scrubs. Which checkpoint, and why?"
    options: ["2,400: strongest identity", "1,800: identity is strong and new prompts still work; at 2,400 the LoRA overfits (it copies training details)", "1,200: less risk", "Average them"]
    answer: 1
    explain: "This is the classic curve: identity rises, then flexibility falls. Choose before the fall."
  - q: "Without the trigger word, half of the eval images show your character. What does it mean?"
    options: ["The LoRA is excellent", "Leakage: the LoRA changed the model too much; it affects prompts it should not; use an earlier checkpoint, a lower strength, or a lower learning rate", "The prompt is wrong", "The seed is wrong"]
    answer: 1
    explain: "No-trigger prompts in the eval set measure leakage. A useful LoRA leaves other prompts alone."
  - q: "What does a higher LoRA rank do?"
    options: ["Trains faster", "Gives the adapter more capacity (more parameters): it can store more detail, and it can also overfit more easily and makes larger files", "Lowers the learning rate", "Changes the base model"]
    answer: 1
    explain: "Start at 16–32 for a character. Raise it only if fine details do not hold."
  - q: "Why render the same prompts with the same seeds at every checkpoint?"
    options: ["It is required", "Then the only difference between images is the checkpoint, so you can compare them fairly", "To save time", "For the dataset card"]
    answer: 1
    explain: "Fixed seeds turn the checkpoint series into an experiment."
  - q: "You train on a spot instance, and it stops at step 2,100 of 3,000. What makes this harmless?"
    options: ["Nothing", "Checkpoints every 250–500 steps on a persistent volume, and a trainer that resumes from the last checkpoint", "A bigger GPU", "A lower rank"]
    answer: 1
    explain: "Design training to resume (C13·M03)."
  - q: "Your identity score is high at every checkpoint, but images for 'in a café' still show the locker room. What does the score miss?"
    options: ["Nothing", "Flexibility: an identity score measures the face, not whether the rest of the prompt was followed; score prompt adherence on 'out' prompts with a person or a calibrated LLM judge", "The seed", "Leakage"]
    answer: 1
    explain: "Measure fidelity, leakage, and flexibility. One number is not enough."
  - q: "What must the experiment log of a run contain?"
    options: ["The final file only", "Dataset version, base model and hash, all settings, checkpoints, eval scores per checkpoint, the choice and its reason, time, and cost", "The GPU temperature", "Nothing"]
    answer: 1
    explain: "Without a log, you cannot repeat a good run or explain a bad one."
deeper:
  - title: "Hugging Face Diffusers — LoRA training guide"
    url: https://huggingface.co/docs/diffusers/training/lora
  - title: "Weights & Biases — experiment tracking docs"
    url: https://docs.wandb.ai/
  - title: "Hu et al. (2021) — LoRA: Low-Rank Adaptation (the method)"
    url: https://arxiv.org/abs/2106.09685
---
## Learn

### What training does
Training shows the model your images with their captions, many times. At each step, the trainer measures how far the model's prediction is from the training image (the loss) and adjusts only the LoRA weights a little to reduce it (C01·M01). The base model stays frozen. After enough steps, the trigger word makes the subject.

### The main settings
| Setting | What it changes | Starting point: image LoRA (character) | Video LoRA |
|---|---|---|---|
| Rank | Capacity of the adapter; file size | 16–32 | 16–64 |
| Learning rate | Size of each update | 1e-4 (AdamW) | 1e-4 to 2e-4 |
| Steps | Training length | 1,500–3,000 | 2,000–5,000 |
| Resolution | Detail learned; VRAM; time | about 1024 px, with buckets | 480–720p, short clips |
| Batch size | Images per step | 1–4 | 1 |
| Precision | VRAM and speed | BF16, or an FP8 base model | FP8 base model, block swap if needed |

These are starting points from practice, not rules. Change one setting at a time and compare checkpoints.

### Overfitting and the checkpoint curve
As training goes on:
1. **Identity rises:** the face, the hair, and the marks hold better.
2. **Then flexibility falls:** the LoRA starts to copy training details (the same coat, the same room, the same expression), even when the prompt asks for something else.
3. **Leakage grows:** the subject appears in prompts without the trigger, and other people start to look like it.
So save a checkpoint every 250–500 steps, and choose one from the middle of the curve.

### The eval set
Fix 6–12 prompts and their seeds before training:
- **in:** like the training data (identity check);
- **out:** new clothes, new places, new styles (flexibility check);
- **no trigger:** the same kind of scene without the trigger (leakage check).
Render all of them at every checkpoint. Score:
- **fidelity:** the identity score on trigger prompts (face embeddings, C11·M03; for products, an image-similarity score);
- **leakage:** the identity score on no-trigger prompts (should be low);
- **flexibility:** prompt adherence on "out" prompts, scored 1–5 by you or by a calibrated LLM judge (C12·M04). Identity scores cannot see it.

### Where to train
- **Local:** a 24–96 GB GPU. Image LoRAs fit on 24 GB with FP8 base models; video LoRAs often need block swapping (moving parts of the model in and out of VRAM).
- **Rented GPU:** a container with the trainer, the dataset and the output on persistent volumes, checkpoints on the volume. Spot capacity works if the trainer resumes from checkpoints (C13·M03).
- **Hosted trainers:** upload the dataset, set a few parameters, receive the LoRA. Least control, no operations.
Typical times (practitioner reports): an image LoRA in under 1 hour on one high-end GPU; a video LoRA in several hours.

### The experiment log
For every run: the dataset version (and its check report), the base model and its hash, every setting, the checkpoints, the eval scores per checkpoint, the choice and its reason, the time, and the cost. A folder with a JSON file per run is enough; an experiment tracker adds charts.

## Tool walkthrough

### Trainers (as of 2026-10)
- **musubi-tuner (kohya-ss):** Wan, HunyuanVideo, FLUX.2; FP8 base models; block swap for video.
- **AI Toolkit (ostris):** FLUX-family image LoRAs and more.
- **Diffusers training scripts:** a reference implementation.
- **Hosted trainers** (for example fal's Wan 2.2 trainer).
Read the trainer's current documentation for the config format and the recommended values for your base model. They change with each model release.

### Render and score checkpoints

```
eval/
  prompts.json        [{"id": "in01", "kind": "in"}, {"id": "out01", "kind": "out"}, {"id": "nt01", "kind": "no_trigger"}]
  ckpt-1200/in01.png  ckpt-1200/out01.png  ...
  ckpt-1800/...
  flex.csv            checkpoint,prompt,score    (1–5 for "out" prompts)
```

Render the images with your LoRA loaded in the starter workflows (C11: add a LoRA loader after the model loader), or with the trainer's sample feature. Then:

```bash
python starter/tools/lora_eval.py eval/ --ref refs/CHAR-MARA/01_front.png --ref refs/CHAR-MARA/02_34.png --grid eval/grid.png
```

The grid has one row per checkpoint and one column per prompt.

## Worked example

**Evaluator test** (2026-10-04, synthetic checkpoints from public-domain portraits; reference: a photo of person A):

| Checkpoint | Fidelity | Leakage | Flex (from flex.csv) | Pass |
|---|---|---|---|---|
| ckpt-0500 (identity mostly missing) | 0.135 | 0.135 | 4.5 | no |
| ckpt-1000 (identity on trigger prompts only) | 0.676 | 0.135 | 4.0 | yes |
| ckpt-1500 (person A in every image, also without the trigger) | 0.676 | 0.676 | 2.5 | no |

"choose ckpt-1000 (highest flexibility among passing checkpoints)". The overfit checkpoint has the same fidelity as the right one; only the leakage and flexibility columns separate them.

**Mara image LoRA:** rank 32, learning rate 1e-4, 2,400 steps, 1024 buckets, 32 images; a rented 48 GB GPU, 38 minutes, about US$2. Checkpoints: 1,200 weak identity; 1,800 strong and flexible; 2,400 strong, but the raincoat in every image → choose 1,800.
**Mara video LoRA** on Wan from the still images: rank 32, 3,000 steps, 3.5 h on an 80 GB GPU, about US$10–15. Identity holds in I2V and T2V with the trigger.

## Lab

**Deliverable:** `training/<subject>/runs/` with configs, logs, eval renders, grids, the evaluator output, chosen checkpoints, and costs.

1. Write the eval set before training: 4 in, 4 out, 4 no-trigger prompts with fixed seeds.
2. Train one image LoRA on your checked dataset (M01), with checkpoints every 300 steps.
3. Train one video LoRA (or use a hosted trainer if you have no GPU).
4. Render the eval set at every checkpoint. Score flexibility for the "out" prompts in `flex.csv`.
5. Run `lora_eval.py`. Choose a checkpoint by its rule; write if you agree with it, and why.
6. Log both runs: data version, settings, checkpoints, scores, choice, time, cost.

**Result checklist**
- [ ] Two trained LoRAs with checkpoints.
- [ ] Eval renders and a grid per run.
- [ ] Evaluator table and the chosen checkpoint with a reason.
- [ ] Experiment logs with costs.

## Model answer

**Run log (shape of a strong answer):**

```json
{"run": "mara-img-r32-lr1e4-v3", "dataset": "mara v3 (32 images, check: 0 problems)",
 "base": "flux-2-klein-base-4b.safetensors sha256 9c5fed22…", "rank": 32, "lr": 1e-4, "steps": 3000, "save_every": 300,
 "gpu": "rented 48 GB", "minutes": 44, "cost_usd": 2.35,
 "eval": {"ckpt-1500": {"fidelity": 0.52, "leakage": 0.14, "flex": 4.3},
          "ckpt-2100": {"fidelity": 0.61, "leakage": 0.17, "flex": 4.0},
          "ckpt-2700": {"fidelity": 0.64, "leakage": 0.41, "flex": 2.9}},
 "choice": "ckpt-2100", "reason": "passes fidelity >= 0.5 and leakage <= 0.3; best balance; 2700 leaks (Leo looks like Mara)"}
```

The log is short, but it answers every later question: which data, which base model, which settings, what it cost, and why this checkpoint.

The second run (the video LoRA) has the same fields. Its log also records the block-swap setting that made it fit in 48 GB, and one failed start: "step 0: out of memory at 720p with batch 2 → 480p, batch 1".

"The evaluator chose ckpt-1500 (highest flex). I chose ckpt-2100: its fidelity on the 'out' prompts was 0.58 against 0.44, and the profile shots in C11·M03 failed most often. I changed the rule for this character: fidelity on 'out' prompts ≥ 0.5." The disagreement is useful: it shows which number the project depends on, and the rule now says so.
