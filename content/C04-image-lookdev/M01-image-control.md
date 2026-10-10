---
title: Prompt and reference control for images
hours: 10
outcomes:
  - Write image prompts with the shot grammar from C02, in a fixed order that you can automate.
  - Use reference images for identity, objects, style, and composition, and say in the prompt what each reference is for.
  - Compare 3 image models on your own eval set with a scoring sheet, and route jobs to models from the results.
  - Log every kept image with model, prompt, seed, settings, references, and cost.
keywords: [reference image, style reference, aspect ratio, prompt log]
summary: >
  Image models accept text and reference images. Text controls subject, action, camera, light, and style. Reference
  images control identity, objects, style, and composition more exactly than words. Write prompts in a fixed order,
  so code can build them and you can compare them. Say what each reference is for. Models have different strengths,
  so test them on your own cases with a scoring sheet and route each job to the best model. Log every image that you
  keep, with everything that you need to make it again.
diagram:
  type: compare
  title: Text vs reference control
  left:
    title: "Text controls well"
    items: ["Shot size, angle, lens", "Action and setting", "Light and mood words", "General style"]
  right:
    title: "References control well"
    items: ["Exact face and body", "Exact product shape and logo", "Exact palette and texture", "Exact composition (sketch / layout)"]
watch:
  - title: "Google — Gemini image generation guide (prompting and multi-image references)"
    url: https://ai.google.dev/gemini-api/docs/image-generation
    note: "Read the prompt strategies and the multi-image examples. 20 minutes."
  - title: "OpenAI — image generation guide"
    url: https://platform.openai.com/docs/guides/image-generation
    note: "Read the sections on editing with reference images and on quality settings."
  - title: "Black Forest Labs — FLUX.2 announcement and docs"
    url: https://bfl.ai/
    note: "Look at the multi-reference examples and the model variants (pro, dev, klein)."
quiz:
  - q: "A client must see their real product's logo exactly. What is the correct control, and what is the second step?"
    options: ["Describe the logo in detail in the prompt", "Use the product photo as a reference image, then compare every output with the original at 100 % zoom", "Raise the guidance value", "Use a style reference of the brand colors"]
    answer: 1
    explain: "Words cannot describe a logo exactly. A reference can, but models still change small details, so a check is part of the method."
  - q: "You give three reference images without explanation. The output copies the color palette of the location image onto the character's clothes. What is the fix?"
    options: ["Use fewer steps", "Say in the prompt what each image is for: 'Image 1: the woman. Image 2: the room only. Image 3: color mood only.'", "Use one reference only", "Use a bigger model"]
    answer: 1
    explain: "Without roles, the model mixes features from all references. Name each reference and its job."
  - q: "Model A wins your text-only test. Model B wins with references. Your project has a fixed cast in 40 shots. Which do you use for key frames?"
    options: ["Model A, because it won first", "Model B, because the project needs identity from references in every shot", "Both at random", "Neither; use text-to-video"]
    answer: 1
    explain: "Choose by the job. A fixed cast means reference control is the main requirement."
  - q: "Your eval set has 6 prompts, all bright day exteriors. Model C scores best. What is wrong with the conclusion?"
    options: ["Nothing", "The set does not cover your real cases (night, interiors, faces, hands, text), so the score does not predict your project", "6 is too many prompts", "Day scenes are harder"]
    answer: 1
    explain: "An eval set must look like the work. Include your hardest cases: night, mixed light, close-ups, hands, and text."
  - q: "Which fields must a prompt-log line have so that you can make the image again?"
    options: ["File name only", "Model and version, full prompt, seed, settings, reference IDs, date, and cost", "Only the prompt", "The client name"]
    answer: 1
    explain: "Without the exact model version, seed, settings, and references, you cannot reproduce or vary the image. C16 also needs the log to show where each image came from."
  - q: "You need a 9:16 vertical key frame. When do you set the aspect ratio?"
    options: ["Crop a 16:9 image later", "At generation time, so the model composes for the vertical frame", "After upscaling", "It does not matter"]
    answer: 1
    explain: "A model composes for the frame that it gets. A crop of a 16:9 frame often cuts the head or leaves the subject too small."
  - q: "A hosted model gives the best results, but the client contract forbids sending their unreleased product photos to third parties. What do you do?"
    options: ["Use the hosted model and do not tell the client", "Use an open-weight model on your own infrastructure for those shots, and test it on the same eval set", "Use only text prompts", "Refuse the job"]
    answer: 1
    explain: "Data rules are requirements. An open-weight model that runs on your own GPU keeps the data inside. Measure its quality before you promise it."
deeper:
  - title: "Midjourney — docs on style and character references"
    url: https://docs.midjourney.com/
  - title: "LMArena — text-to-image leaderboard (check the date of each ranking)"
    url: https://lmarena.ai/leaderboard
  - title: "Artificial Analysis — text-to-image arena and model pages"
    url: https://artificialanalysis.ai/text-to-image
---
## Learn

### Why start with images
In AI-native video, most shots start as a still image. A still costs a few cents and a few seconds. A video take costs 10–100 times more. The still fixes the things that are expensive to fix later: who is in the frame, where they stand, the lens, the light, and the look. When the still is right, the video model only adds motion (C05).

So the image stage is not decoration. It is the design stage of each shot.

### The prompt order
Write every image prompt in the same order. Then code can build prompts from your shot list (C03·M02), and you can see what changed between two versions.

1. **Shot:** size, angle, lens look. "Medium close-up, eye level, 85 mm look, shallow depth of field."
2. **Subject:** who or what, with the fixed descriptor from the character sheet (M03).
3. **Action:** one clear action or state. "She reads a small printed photo."
4. **Place and time:** "Hospital locker room, night."
5. **Light:** direction, quality, color. "Cold fluorescent top light, warm practical lamp from frame left."
6. **Look:** the look suffix from the look bible (M04).
7. **Format:** aspect ratio and size, as a setting if the model has one.

Keep each part short and concrete. A model follows "85 mm look, background soft" better than "beautiful cinematic depth".

### Text inside the image
Current models can render short text well. Put the exact text in quotes and say where it goes: `a sign on the door that reads "STAFF ONLY"`. Check every letter. Long text and small text still fail often. For logos and legal text, use the real file in a later edit or in compositing (C09·M03). Do not trust generation for those.

### Aspect ratio
Set the aspect ratio when you generate: 16:9, 9:16, 4:5, or 2.39:1. A model composes for the frame that it gets. A vertical crop of a horizontal frame usually puts the subject too small or cuts the head. If you need several ratios, generate the main one, then extend the frame for the others (M02).

### Reference control
A reference image gives the model exact visual information that words cannot hold:
- **Identity:** face, hair, body, clothes. Use 2–3 views from the character sheet.
- **Objects:** product shape, logo, packaging, materials.
- **Place:** room layout, windows, props.
- **Style:** palette, texture, rendering. Use a style reference only for style.
- **Composition:** a sketch, a 3D block-out, or a photo with the layout you want.

Most current models accept several references in one request. They do not know the role of each image unless you say it. Write the roles into the prompt: "Image 1 is the character. Image 2 is the room; keep its layout. Image 3 is for color mood only; do not copy objects from it." Without roles, models mix features across images. A common failure is the palette of the place image on the character's clothes.

### How references reach the model
There are two common methods inside the models:
1. **Encoded references.** The image is encoded (often by the same VAE that makes the output) and attached to the conditioning. The model attends to it at every step. This copies detail well. You will see this method node by node in C11·M02.
2. **Image embeddings.** A vision encoder turns the image into a short vector of features. An adapter feeds these features to the model. This copies style and general identity, and fine detail less well.
You do not need to know which method a hosted model uses. You need to test how exactly it copies the detail that matters for your shot.

### Choose models by test
Model rankings change every month. Your project has its own needs. So build a small eval set and test (C01·M07):
1. **Cases:** 6–10 shots from your own shot list. Include the hard cases: night, mixed light, close-ups, hands, text, and your product.
2. **Variants:** text only, and text plus references.
3. **Scores:** 1–5 for prompt adherence, identity, light, look, and artifacts. Score blind if you can: hide the model name.
4. **Cost and time:** per image and per kept image.
5. **Route:** choose a model per job. One model can be best for hero key frames, another for edits, and an open model for private client work.

### The prompt log
Every image that you keep gets one log line. The line must let you make the image again, change it, and prove where it came from (C16). Use `starter/tools/promptlog.py`. It appends JSON lines to `prompts/log.jsonl`, adds a SHA-256 hash of the file, and checks the log for missing fields, typos, changed files, and references without a rights record.

## Tool walkthrough

This walkthrough shows one hosted path and one open path (as of 2026-10). Use the landscape page for current alternatives.

### Hosted: an image API from Python
The official Gemini image guide (2026-10) shows this shape for text plus one reference image:

```python
from google import genai
import base64

client = genai.Client()  # reads the API key from the environment
ref = base64.b64encode(open("refs/CHAR-MARA/01_front.png", "rb").read()).decode()
interaction = client.interactions.create(
    model="gemini-3-pro-image",
    input=[
        {"type": "text", "text": PROMPT},
        {"type": "image", "data": ref, "mime_type": "image/png"},
    ],
    response_format={"type": "image", "aspect_ratio": "9:16", "image_size": "2K"},
)
open("out/S07_a.png", "wb").write(base64.b64decode(interaction.output_image.data))
```

Check the guide before you use this code. Vendors change SDKs and model IDs often. The model IDs listed on 2026-10-04 were `gemini-3-pro-image`, `gemini-3.1-flash-image`, `gemini-3.1-flash-lite-image`, and `gemini-2.5-flash-image`.

Then log the image:

```bash
python starter/tools/promptlog.py add --id S07_a --model gemini-3-pro-image \
  --prompt-file prompts/S07.txt --refs CHAR-MARA-01,LOC-LOCKER-02 --cost 0.13 \
  --file out/S07_a.png --status kept
```

### Open: the starter ComfyUI workflows
If you have a GPU (or rent one), use the C11 starter workflows now. You do not need to understand the graphs yet.
- `01_t2i_flux2_klein_4b.json`: text only, 4 steps.
- `02_ref_edit_flux2_klein_4b.json`: two references (character and place) plus a prompt.
Run them from the editor, or with `starter/solutions/C11-M04/comfy_run.py` and the map files. The open path keeps client images on your own machine.

### The scoring sheet
Use one CSV row per image: `shot,model,variant,seed,adherence,identity,light,look,artifacts,cost_usd,kept`. A spreadsheet pivot by model and variant gives the routing table.

## Worked example

**Key frame for shot S07** (from the C02·M06 shot list): "MCU, eye level, 85 mm look. Mara reads a printed photo. Locker room, night. Cold fluorescent top light and a warm practical lamp. 9:16."

| Try | Input | Result | Decision |
|---|---|---|---|
| 1 | Text only, model A | Good light. The face does not match the character sheet. | Reject |
| 2 | Text + 2 character views, model A | Face correct. The photo in her hand is blank. | Keep as fallback |
| 3 | Text + 2 character views + room, model B, roles named | Face and room correct. Light too warm. | Edit (M02) |
| 4 | Instruction edit of try 3: "make the top light colder, keep everything else" | All correct. | Keep: `KF-S07-v3` |

Cost: 4 calls at about US$0.04–0.13 each. The log line for `KF-S07-v3` has `parent: S07_try3`, so the edit history is clear.

**Routing from a 6-shot test** (example of the shape):

| Job | Model | Why |
|---|---|---|
| Hero key frames with cast | B | Identity 4.5 / 5 with references |
| Small fixes and edits | B | Keeps unchanged areas best (M02) |
| Client product shots (private data) | Open model on own GPU | Data stays inside; identity 4 / 5 |
| Fast exploration | Open model, 4-step | US$0 per image on own GPU, 3 s each |

## Lab

**Deliverable:** `C04/M01/` with a scoring sheet, a routing table, and 6 kept key frames with log lines.

1. Choose 6 shots from your C02·M06 shot list. Include at least one night shot, one close-up, and one shot with text in the frame.
2. Write each prompt in the 7-part order. Save each prompt as a text file.
3. Generate each shot with 3 models: first text only, then with references with named roles. Use at least one hosted model and one open model.
4. Score every image in the CSV. Hide the model names while you score, if you can.
5. Keep the best frame for each shot. Log each kept frame with `promptlog.py`. Run `promptlog.py check` until it passes.
6. Write the routing table: job → model → reason, with numbers from your sheet.

**Result checklist**
- [ ] 36 or more images, all scored in the CSV.
- [ ] 6 kept key frames, each with a complete log line; `promptlog.py check` passes.
- [ ] Routing table with numbers.
- [ ] One paragraph: what references fixed, and what they did not fix.

## Model answer

A strong submission has a sheet with 36–48 rows and a summary like this:

| Variant | Mean identity | Mean adherence | Mean cost per kept image |
|---|---|---|---|
| Text only, all models | 2.1 | 3.8 | US$0.31 |
| With named references, all models | 4.2 | 3.9 | US$0.12 |

The text explains the numbers: "References doubled identity on every model. Prompt adherence did not change, because references do not carry action or camera. The cost per kept image fell by 60 %, because fewer takes failed."

The routing table names a model for each job and gives the score that justifies it. It also names a risk: "Model B changed the scar position in 2 of 12 images. Check the scar in every review."

The log passes `promptlog.py check`. Every kept image has its references by ID, and every reference that you did not make has a rights line.

The paragraph on limits says what references did not fix: hands, small text, and the photo inside the photo. These need edits (M02) or compositing (C09·M03).
