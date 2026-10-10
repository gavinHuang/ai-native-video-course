---
title: Brief to treatment to script to prompts
hours: 9
outcomes:
  - Build a staged pipeline from a client brief to generation-ready prompts.
  - Write a "machine-ready" script with standard tags for characters, scenes, and shots.
  - Keep human approval gates between stages.
  - Version every stage so that a change upstream updates downstream.
keywords: [production pipeline, approval gate, machine-ready script, shot list]
summary: >
  Do not ask an LLM for "a video" in one step. Use stages: brief, treatment, script, shot list, and prompts. Each
  stage has a schema, an LLM step, automatic checks, and a human approval. The script is machine-ready: each
  character, location, and shot has a standard tag and fixed descriptors, so generation tools can use it directly.
  This is how industrial AI short-drama teams work. Version every stage. When the client changes the treatment, you
  regenerate only the affected downstream parts.
diagram:
  type: flow
  title: Staged pre-production pipeline
  nodes: ["Brief (client)", "Treatment + approval", "Script (tagged) + approval", "Shot list (JSON) + checks", "Prompts per model (adapters)", "Generation queue"]
  highlight: [1, 2]
watch:
  - title: "Tencent Cloud Dev — AI comic-drama production pipeline (Chinese, deep article)"
    url: https://cloud.tencent.com/developer/article/2647810
    note: "Use a browser translator. Note the 5 industrial stages and the 'engineered script' format."
  - title: "Zhihu — Seedance 2.0 full creation guide (Chinese)"
    url: https://zhuanlan.zhihu.com/p/2028206240107374401
    note: "Note how each 15 s clip is planned as 3–5 shots with first-frame descriptions."
quiz:
  - q: "Why split pre-production into stages with approvals?"
    options: ["LLMs need breaks", "Errors are cheap to fix early; each stage can be checked and versioned", "It looks professional", "To use more tokens"]
    answer: 1
    explain: "A wrong idea found at the treatment stage costs nothing. Found after generation, it costs money and days."
  - q: "What makes a script 'machine-ready'?"
    options: ["It is in PDF", "Standard tags and fixed descriptors for characters, locations, and shots", "It has no dialogue", "It is short"]
    answer: 1
    explain: "Tools can parse it, and every prompt uses the same descriptors."
  - q: "The client changes scene 3 only. What do you regenerate?"
    options: ["Everything", "Scene 3's script, shots, prompts, and media only", "Only the thumbnail", "Nothing"]
    answer: 1
    explain: "Versioned stages with IDs let you rebuild only the affected parts."
  - q: "Who approves the treatment?"
    options: ["The LLM", "A human (you or the client)", "The video model", "Nobody"]
    answer: 1
    explain: "Humans own creative and legal decisions."
  - q: "The brief says 'make it feel premium'. What do you do before the treatment?"
    options: ["Start generating", "Turn it into checkable requirements with the client (for example palette, pace, music type, reference ads), or record the client's own examples", "Ignore it", "Ask the LLM to decide"]
    answer: 1
    explain: "Requirements that cannot be checked cause late, expensive changes."
  - q: "Which step should be code, not an LLM call?"
    options: ["Writing three treatment options", "Building the final prompt for each model from the shot JSON and an adapter", "Writing dialogue", "Reviewing story beats"]
    answer: 1
    explain: "If you can write a unit test for the output, use code."
deeper:
  - title: "Fountain — plain-text screenplay format"
    url: https://fountain.io/syntax
  - title: "Chinese industry overview — 2026 AI short-drama tools compared (The Paper)"
    url: https://m.thepaper.cn/newsDetail_forward_33643563
---
## Learn

### A brief that can be checked
A good brief makes every later step checkable. Turn each wish into a test:
- "Short" → "30 s ± 1 s".
- "Show the product" → "logo readable for at least 2 s; the product shape never changes".
- "Young audience" → "cyclists aged 20–35; the cast matches; music is current and licensed".
- "No negative images" → a written must-not list.
If a requirement cannot be checked, ask the client what they mean, before the treatment. An LLM step can do a first pass: "List every requirement in this brief and say how we can test it."

### Stages
1. **Brief:** the client's goal, audience, platform, length, must-haves, must-nots, budget, deadline.
2. **Treatment:** the idea in one page (C02·M05). Human approval.
3. **Script:** scenes, action, dialogue. Tagged. Human approval.
4. **Shot list:** JSON (C03·M01). Automatic checks.
5. **Prompts:** one prompt per shot per model, built by code from the shot data and a model adapter.
6. **Queue:** jobs for generation (C12).

Each stage has: an input, a schema, an LLM step, checks, and a version number. A stage reads only the approved output of the stage before it, never a draft.

### The machine-ready script
Industrial AI short-drama studios in China (2026) call this an "engineered script": a script that a pipeline can read. Each element has a tag and fixed parameters:
- **Characters:** `@MARA` → age, face, hair, wardrobe A/B, voice ID, reference image IDs.
- **Locations:** `#LOCKER_ROOM` → space layout, light base, time of day, reference IDs.
- **Shots:** `[S07 MCU 85mm push-in 6s]`.

Example line:
```
#LOCKER_ROOM night
[S07 MCU 85mm slow-push-in 6s]
@MARA (wardrobe A) reads a printed photo. She looks up, off-camera left.
SFX: paper rustle. AMB: distant monitor beeps.
```
Code can parse this into the JSON shot list. A human can still read it.

### Prompt builders
Do not write final prompts by hand. Write a function:
`build_prompt(shot, bible, adapter) → str or dict`
The adapter holds model-specific rules (C02·M06): word limits, order, JSON or plain, camera vocabulary. When a model changes, you change only the adapter. When the story changes, you change only the shot data. The two never mix, so a new model does not need a new script, and a new scene does not need new prompt rules.

### What the LLM does, and what code does
Use the LLM where judgment and language are needed: ideas, treatments, dialogue, the first shot list, and reviews. Use code where the result must be exact and repeatable: parsing tags, building prompts from data, durations, IDs, file names, and dependencies. A rule of thumb: if you can write a unit test for the output, use code. This makes the pipeline cheaper, faster, and easier to debug, and it keeps creative choices where a person can review them.

### Review changes as diffs
When a stage output changes, review the difference, not the whole document. Scripts and shot lists in Git give you line diffs; for JSON, a small script can list changed shots and fields ("S07: duration 6 → 4 s; action changed"). Approvers then see exactly what they approve.

### Versions and dependencies
Give every item an ID: `SC03`, `S07`, `S07.p2` (prompt v2), `S07.p2.g4` (generation 4). Store the stage outputs in Git. When `SC03` changes, a script lists all shots, prompts, and generations that depend on it.

### Human gates
LLMs propose; humans approve. The approver checks: story, brand, legal risk (people, logos, music), and taste. Record the approval (who, when, version). An approval without a version number is useless: later, nobody can say which script the client approved. Keep the gates few and early: treatment, script, and the first generated look frames are the three that save the most money.

## Worked example

**Brief:** "30 s vertical ad for a reusable water bottle. Audience: city cyclists, 20–35. Must show: bottle logo, the cold test (ice after 24 h). Must not: plastic waste images. Platform: Reels + TikTok."

1. Treatment (LLM, 3 options) → human picks option B: "24 hours in 30 seconds".
2. Script with tags: `@RIDER`, `@BOTTLE` (product: exact references, no shape change), `#CITY_DAWN`, `#CITY_NIGHT`.
3. Shot list: 9 shots, 30 s total; checks pass.
4. Prompts: shots with `@BOTTLE` use the reference-to-video model and product references; the 2 wide city shots use a cheaper model.
5. Client changes "night" to "rain at night". Script v2 changes 3 shots. The dependency script lists 3 shots + 3 prompts to rebuild. The other 6 stay.

## Lab

**Deliverable:** `pipelines/preprod/` — a CLI with 4 commands.

1. `preprod treatment brief.yml` → 3 treatment options (Markdown).
2. `preprod script treatment.md` → tagged script.
3. `preprod shots script.txt` → validated `shots.json` (reuse C03·M01).
4. `preprod prompts shots.json --model kling|veo|wan` → prompts via adapters.
5. Store all outputs with IDs and versions. Add an `approve` command that records approver and time in `approvals.json`.
6. Run it on one real or invented brief, end to end.

**Result checklist**
- [ ] 4 commands work end to end.
- [ ] Tags parse correctly; unit test for the parser.
- [ ] Two model adapters give different prompt shapes from the same shot.
- [ ] A changed scene rebuilds only its dependants.

## Model answer

A good implementation has: stage folders `01_treatment/ 02_script/ 03_shots/ 04_prompts/`; a regex or small grammar parser for tags with tests; adapters as YAML files (word limit, field order, format); and a `deps.py` that maps scene → shots → prompts. The run log shows 3 LLM calls for treatment, 1 for script, 1–2 for shots (with one repair), and zero for prompts (code builds them).

**Change test (shape):** "Scene 3 changed from 'night' to 'rain at night' (script v2). `deps.py SC03` listed S07, S08, S09 and their prompts; the prompt builder rebuilt 3 prompts in 0.2 s; the 6 other shots kept their approved generations. Approval recorded: client, 2026-10-04 14:10, script v2." Every artifact has an ID and a version, and the run log shows the cost of each LLM stage, so the team knows where the money goes.
