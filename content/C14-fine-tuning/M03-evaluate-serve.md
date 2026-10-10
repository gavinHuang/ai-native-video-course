---
title: Evaluate, quantize, and serve adapted models
hours: 22
outcomes:
  - Evaluate a LoRA for fidelity, flexibility, leakage, and compatibility with other LoRAs and with the production workflows.
  - Measure what the LoRA adds to the C11·M03 character pipeline, against references only.
  - Combine several LoRAs and choose their strengths with tests.
  - Serve LoRAs per request on a quantized base model, and keep a model registry with versions, hashes, evals, and rights.
keywords: [LoRA evaluation, leakage, LoRA strength, model registry, adapter serving]
summary: >
  A LoRA is ready for production when it passes an eval set - fidelity, flexibility, and leakage - and when it
  improves the real pipeline. Measure the gain: run the weakest shots of the character pipeline again with the LoRA
  and compare identity scores and rejection rates. Combine LoRAs with tested strengths; two characters in one frame
  need regions or separate passes. Serve LoRAs per request on a quantized base model, and cache them. A registry
  records every adapter with its hash, base model, eval results, rights, and allowed uses.
diagram:
  type: flow
  title: From trained LoRA to production
  nodes: ["Eval set: in / out / no-trigger", "Pipeline test: weak shots of C11·M03 again", "Strength + combination tests", "Register: hash, base, evals, rights, uses", "Serve: base FP8 + LoRA per request", "Monitor identity in production"]
  highlight: [1]
watch:
  - title: "Hugging Face — Diffusers: load and combine LoRAs (adapters)"
    url: https://huggingface.co/docs/diffusers/tutorials/using_peft_for_inference
    note: "Read how to load several adapters and set their weights."
  - title: "fal — LoRA inference for open video models (docs)"
    url: https://docs.fal.ai/
    note: "Look at how hosted APIs accept LoRA URLs per request."
quiz:
  - q: "The LoRA passes the eval set. How do you know it is worth using in production?"
    options: ["The eval is enough", "Run the real pipeline again on the shots that failed before (C11·M03) and compare identity scores, rejection rate, and cost per accepted shot with and without the LoRA", "Ask the client", "Train longer"]
    answer: 1
    explain: "The question is the gain in the real workflow, at the real angles and sizes."
  - q: "Mara's LoRA at 1.0 and Leo's at 1.0 in one two-shot: their faces mix. What are the options?"
    options: ["Raise both to 1.2", "Lower both a little (for example 0.8–0.9) and use regional prompts or masks so each LoRA acts on its region; or generate each character separately and composite", "Use one LoRA only", "Remove the references"]
    answer: 1
    explain: "Two identity LoRAs over the whole frame compete. Limit each to its region."
  - q: "Why test strengths of 0.6, 0.8, and 1.0?"
    options: ["Tradition", "Strength trades identity against flexibility and leakage; the best value depends on the LoRA and the workflow", "Higher is always better", "Only 1.0 works"]
    answer: 1
    explain: "Typical: identity LoRAs 0.8–1.0, style LoRAs 0.4–0.7. Measure for yours."
  - q: "A LoRA trained on one base model version is loaded on a newer version. What can happen?"
    options: ["Nothing", "It can lose identity or produce artifacts, because the weights it adapts changed; re-run the eval before using it, or retrain", "It always works better", "It changes the license"]
    answer: 1
    explain: "A LoRA belongs to a base model and version. Record both in the registry."
  - q: "How does a service apply different LoRAs per request without reloading the base model?"
    options: ["It cannot", "Keep the base model loaded (quantized), load LoRA files on demand, cache the recent ones, and apply them with a per-request strength", "Reload for every request", "Merge all LoRAs"]
    answer: 1
    explain: "LoRAs are small. The base model is large. Load the large part once."
  - q: "What must a registry entry contain?"
    options: ["Only the file name", "ID, file hash, base model and version, dataset card link, eval results, rights and consent, allowed uses (internal, client X only), and an expiry date if consent expires", "The trainer's name", "Nothing"]
    answer: 1
    explain: "The registry is the source of truth for what may be used where (C16)."
  - q: "The client's consent for a likeness LoRA expires on 2027-06-30. What does the pipeline do after that date?"
    options: ["Nothing", "The service refuses the LoRA (the registry expiry), and the file is deleted as the consent record requires", "It warns once", "It keeps working"]
    answer: 1
    explain: "Rights rules must be enforced in code, not only in a document."
deeper:
  - title: "PEFT library — docs"
    url: https://huggingface.co/docs/peft
  - title: "Hugging Face — model cards"
    url: https://huggingface.co/docs/hub/model-cards
  - title: "Mitchell et al. (2019) — Model Cards for Model Reporting"
    url: https://arxiv.org/abs/1810.03993
---
## Learn

### Two levels of evaluation
1. **The eval set** (M02): in, out, and no-trigger prompts at fixed seeds. It answers: does the LoRA hold identity, follow new prompts, and leave other prompts alone?
2. **The pipeline test:** the real workflow, at the real sizes, angles, and lighting. It answers: does the LoRA make production better?
Both are needed. A LoRA can pass the eval set and still fail at the angles that the story needs.

### The pipeline test
In C11·M03 you chose the 2 shots where identity was weakest with references only. Now:
1. Add a LoRA loader to the start-frame workflow (and, for a video LoRA, to the video workflow).
2. Run the same shots with the same seeds and settings, with and without the LoRA.
3. Compare: the median identity score, the minimum, the rejection rate over 5 tries, and the cost per accepted shot.
4. Decide: use the LoRA for this character, for these shot types, at this strength.

### Compatibility checks
- **Strength:** test 0.6, 0.8, and 1.0. Identity LoRAs usually work at 0.8–1.0, style LoRAs at 0.4–0.7.
- **Combinations:** a character LoRA with a style LoRA; two character LoRAs. Two identity LoRAs over the whole frame compete and mix faces. Use regional prompts or masks, or generate each character separately and composite them (C09·M03).
- **Base model version:** a LoRA adapts specific weights of one base model. On another version, re-run the eval, or retrain.

### Quantize and serve
- **The base model** in FP8 or 4-bit (C01·M06) to fit the GPU and load faster.
- **LoRAs** in BF16; they are small (tens to hundreds of MB).
- **The service** (C13·M04) keeps the base model loaded, loads LoRAs on demand, caches the recent ones, and applies them per request with a strength: `{"lora": "mara_v4", "strength": 0.9}`.
- **Hosted alternative:** some per-output APIs accept a LoRA URL per request.

### When a LoRA is not worth it
A LoRA costs data work, training, evaluation, and maintenance (a new base model means a new LoRA). Use references only when:
- the subject appears in few shots, or only from the front;
- references already pass the identity gate in most tries (C12·M04);
- the project is short and the base model may change soon.
Train a LoRA when the subject appears in many shots, at many angles, over a long series, or when references fail at the angles the story needs.

### Monitor in production
Keep the identity gate (C11·M03, C12·M04) on every shot, also with the LoRA. Watch the rejection rate per character per week. A rising rate means something changed: a new base model version, a new kind of shot, or a strength that is too low for a new workflow.

### The registry
A registry is the source of truth for adapters. Each entry:
- ID and version, the file hash;
- the base model and its version;
- a link to the dataset card (M01);
- the eval results and the pipeline-test results;
- rights and consent, with the consent record;
- allowed uses (internal only, client X only, this series only);
- an expiry date if the consent or license expires.
The service reads the registry and refuses an adapter that is expired or not allowed for the project.

## Tool walkthrough

### Add a LoRA to a starter workflow
In the ComfyUI editor, add a `LoraLoaderModelOnly` node between `UNETLoader` and the next node that takes the MODEL, set the LoRA file and the strength, and export the API format again (C11·M01). Add the strength to the map file, for example `"lora_strength": "<node id>.strength_model"`.

### Measure with and without

```bash
python starter/solutions/C11-M03/character_shot.py --shot shots/S09.json --char-ref refs/CHAR-MARA/01_front.png \
  --char-ref refs/CHAR-MARA/03_side.png --place-ref refs/LOC-LOCKER/wide.png --line audio/S09.wav --out ab/S09_refs/
# then the same with the LoRA workflow (copy of 02 with the LoRA loader) -> ab/S09_lora/
python starter/tools/lora_eval.py eval/ --ref refs/CHAR-MARA/01_front.png --ref refs/CHAR-MARA/02_34.png
```

### A registry entry

```yaml
- id: mara_v4
  file: loras/mara_v4.safetensors
  sha256: 3f1c…
  base: flux-2-klein-base-4b.safetensors (sha256 9c5fed22…)
  dataset_card: training/mara/CARD.md
  eval: {fidelity: 0.61, fidelity_out: 0.58, leakage: 0.17, flex: 4.0, checkpoint: ckpt-2100}
  pipeline_test: {shots: [S07, S09], identity_median: [0.50, 0.62], reject_rate: [0.6, 0.2]}
  rights: {status: own, note: "fictional character, generated references"}
  allowed_uses: ["The Camera (series)"]
  strength: {single: 0.9, two_shot: 0.8}
  expires: null
```

## Worked example

**Mara LoRA v3 → v4:**
- v3 eval: fidelity median 0.68 (threshold 0.6) ✓; flexibility 85 % of out prompts rated 4 or 5 ✓; leakage: 0 of 10 no-trigger prompts show Mara ✓; but 3 of 10 out prompts show the training locker room → retrain with more varied backgrounds (v4).
- v4 eval: same scores; the locker room in 0 of 10.
- Combined with Leo's LoRA: faces merge at 1.0 / 1.0 → regional prompts at 0.9 / 0.9 ✓.
- Registry updated; the service loads v4.

**Pipeline test on the weak shots of C11·M03** (S07 head turn, S09 profile; 5 tries each, the same seeds):

| Shot | References only: median / min / rejects | With LoRA v4 (0.9): median / min / rejects |
|---|---|---|
| S07 (MCU, head turn) | 0.58 / 0.41 / 2 of 5 | 0.63 / 0.55 / 0 of 5 |
| S09 (profile MS) | 0.50 / 0.31 / 3 of 5 | 0.62 / 0.49 / 1 of 5 |

(This table shows the shape of the result; your numbers come from your own runs.)

Decision: LoRA v4 at 0.9 for every Mara shot with a profile or a head turn; references only for frontal close-ups, where the gain was small.

## Lab

**Deliverable:** `training/eval/`, `ab/` (the pipeline test), `infra/lora-service/` (or a hosted LoRA API setup), and `registry.yaml`.

1. Run the full eval set on your LoRAs from M02 (`lora_eval.py`). Fix one problem that you find (retrain, more varied data, or a strength change) and evaluate again.
2. Run the pipeline test: your 2 weakest shots from C11·M03, 5 tries each, with and without the LoRA. Compare the median, the minimum, the rejects, and the cost per accepted shot.
3. Test 3 strengths, and one combination (with a style LoRA or a second character).
4. Serve the LoRA per request (your service from C13·M04, or a hosted API that accepts LoRAs). Make 10 production shots through it.
5. Write the registry entries for your LoRAs, including rights and allowed uses. Make the service refuse a LoRA that is not in the registry for the project.

**Result checklist**
- [ ] Eval report and one documented fix.
- [ ] Pipeline test with and without the LoRA, and a decision.
- [ ] Strength and combination results.
- [ ] 10 shots through the service; registry entries; the refusal works.

## Model answer

**Pipeline test summary (shape of a strong answer):** "With the LoRA at 0.9, rejects on the 2 weak shots fell from 5 of 10 to 1 of 10. The cost per accepted shot fell from US$0.92 to US$0.66, so the LoRA (US$2.35 to train, 3 hours of my time for data and eval) pays back after about 9 weak shots. The series has about 40 such shots."

| Strength | Fidelity (out prompts) | Leakage | Flex |
|---|---|---|---|
| 0.6 | 0.49 | 0.12 | 4.4 |
| 0.8 | 0.56 | 0.15 | 4.2 |
| 1.0 | 0.61 | 0.22 | 3.6 |

"0.9 for single shots; 0.8 with regional prompts for two-shots with Leo. The service read `registry.yaml` and refused `leo_v1` for the client project 'Camera Ad Q4', because its allowed uses list only the series."
