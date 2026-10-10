---
title: Read papers, model cards, and technical reports
hours: 12
outcomes:
  - Read a paper in three passes and extract what matters for production.
  - Read a model card and technical report for capability, limits, and license.
  - Separate claims from evidence - benchmarks, cherry-picked demos, ablations.
  - Follow research in English and Chinese sources.
keywords: [paper, technical report, ablation, cherry-picking]
summary: >
  Read a paper in three passes. First, the title, abstract, figures, and conclusion, to decide if it matters. Second,
  the method and results, to understand what is new. Third, the details, only if you will use or reproduce it.
  Model cards and technical reports tell you architecture, data, training, limits, and license. Separate claims from
  evidence: demos are chosen, benchmarks can be gamed, and ablations show what really matters. Many video models
  come from Chinese labs first, so also follow Chinese sources.
diagram:
  type: flow
  title: Three-pass reading
  nodes: ["Pass 1 (10 min): abstract, figures, conclusion → relevant?", "Pass 2 (1 h): method, results, limits", "Pass 3 (hours): details, code, reproduce", "Production note: what changes for us?"]
  highlight: [3]
watch:
  - title: "S. Keshav — How to Read a Paper (PDF)"
    url: https://web.stanford.edu/class/ee384m/Handouts/HowtoReadPaper.pdf
    note: "Read all (3 pages). The three-pass method."
  - title: "Yannic Kilcher — paper explanation videos"
    url: https://www.youtube.com/@YannicKilcher
    note: "Watch one video-generation paper explanation."
quiz:
  - q: "You have 40 new papers this week and 3 hours. How do you use the time?"
    options: ["Read 2 papers completely", "Pass 1 on all of them from a filtered list (about 3 minutes each), pass 2 on the 2 or 3 that touch your routing table, pass 3 on none unless you will use one", "Read only the abstracts of 5", "Wait for a video about them"]
    answer: 1
    explain: "Pass 1 is a filter. Most papers stop there, and that is correct."
  - q: "What is an ablation?"
    options: ["A dataset", "An experiment that removes or changes one component to measure its effect on the result", "A demo video", "A license"]
    answer: 1
    explain: "Ablations show which part of the method gives the gain. A paper without them claims more than it shows."
  - q: "A launch page shows 12 perfect clips. What do you write in the 'Shown' field of your note?"
    options: ["'Excellent quality'", "'12 selected clips; the number of tries and the prompts are not stated' - then you test it on your own eval set", "'Fake'", "Nothing"]
    answer: 1
    explain: "Demos are selected best cases. They show what is possible, not the usable rate."
  - q: "A paper reports a gain on a benchmark that the same authors introduced in the same paper. How do you rate the evidence?"
    options: ["High: it is a benchmark", "Medium at most: a new benchmark can match the method's strengths; look for results on established benchmarks, human ratings, and ablations", "Low: new benchmarks are always wrong", "It does not matter"]
    answer: 1
    explain: "A new benchmark can be useful (it measures a new problem) but it is not independent evidence yet."
  - q: "The model card says 'Apache-2.0', and the repository also has a VAE and a text encoder. What do you check?"
    options: ["Nothing more", "The license of each file that the workflow loads; they can differ (C16·M01)", "Only the README", "The number of stars"]
    answer: 1
    explain: "A workflow is only as free as its most restricted file."
  - q: "Why follow Chinese-language sources?"
    options: ["It is required", "Many video models, their release notes, and production methods appear there first or only there", "Prices are lower", "The papers are shorter"]
    answer: 1
    explain: "A large part of the video frontier comes from Chinese labs. Use a translator and write your notes in English."
  - q: "A researcher's post says a new method 'solves long-video consistency'. What do you do?"
    options: ["Update the routing table", "Find the paper, read the claim in its own words and the evidence for it (which benchmark, how long, compared to what), then rate it", "Ignore all posts", "Repost it"]
    answer: 1
    explain: "Posts compress claims. Go to the source before you write a note."
deeper:
  - title: "arXiv — cs.CV recent (computer vision)"
    url: https://arxiv.org/list/cs.CV/recent
  - title: "Hugging Face — Daily Papers"
    url: https://huggingface.co/papers
  - title: "arXiv API — user manual"
    url: https://info.arxiv.org/help/api/user-manual.html
---
## Learn

### Three passes
Read research like an engineer who must decide something, not like a reviewer.
1. **Pass 1 (3–10 minutes):** title, abstract, the main figure, the results table, the conclusion, and the limitations section. Answer one question: does this touch any shot type in my routing table, or any step in my pipeline? Most papers stop here.
2. **Pass 2 (about 1 hour):** the method (what is new, in one sentence?), the experiments (compared to what, on which data, with which metrics?), the ablations, and the limits. Fill a production note.
3. **Pass 3 (hours):** the math, the code, the hyperparameters. Only when you will use, reproduce, or build on the work.

### Model cards and technical reports
A model release usually comes with a model card or a technical report instead of a peer-reviewed paper. Extract:
- architecture: the size of the diffusion transformer, the text encoder, the VAE (C01);
- modes: text, image, video, and audio inputs; first and last frame; references; editing;
- limits: resolution, duration, frame rate, languages;
- speed variants: distilled few-step versions, quantized files, VRAM;
- evaluation: which benchmarks, which human ratings, against which models;
- the training-data statement and the safety measures;
- the license of each file.
Use the model-card table from C01·M04.

### Claims versus evidence
Write two fields in every note: **claimed** (the authors' words) and **shown** (what the evidence supports).
- **Demos** are selected. Ask how many tries, and which prompts.
- **Benchmarks:** which ones? Are they saturated (all models score near the top)? Did the authors introduce the benchmark themselves? Are the metrics the ones that matter for you (motion, identity, text, audio sync)?
- **Human ratings:** how many raters, how many prompts, blind or not, who chose the prompts?
- **Ablations:** which component gives the gain? If there are no ablations, the paper shows a system, not a cause.
- **Baselines:** are the compared models current, and were they run with good settings?
- **Code and weights:** released, promised, or not mentioned?
Rate the evidence high, medium, or low, with one reason.

### From a paper to a production decision
A paper rarely changes your work directly. It tells you what will appear in tools in 3–12 months. Methods that train a small adapter on an existing open model often reach node graphs within weeks; new base models take longer. Write the expected path in the note: "adapter on an open model, code released → test when a node appears".

### Sources and a filter
- **Preprint servers** and **paper aggregators** with daily lists: filter them by keywords; a script can do pass 0 for you.
- **Lab blogs and model cards** for releases.
- **Chinese-language sources:** lab blogs, deep-dive articles on question-and-answer sites, video tutorials, and tech press. Many video models and production methods appear there first. Use a translator; write notes in English.
- **Practitioners:** a few researchers and studio engineers who post tests with settings.
Keep the list short. Ten good sources read every week are better than a hundred read never.

## Tool walkthrough

### Pass 0 with a script

```bash
python starter/tools/arxiv_watch.py --query "video generation" --query "video diffusion" \
  --query "talking head" --days 7 --max 40 > notes/arxiv_$(date +%F).md
```

The script calls the public arXiv API (one run per day is enough; it waits 3 s between queries) and writes a Markdown checklist with the first sentence of each abstract. Tick the papers that pass pass 1.

### Sources by name (as of 2026-10)
- English: arXiv (cs.CV, cs.LG, cs.SD), Hugging Face Daily Papers and model cards, lab blogs (Google DeepMind, Meta, NVIDIA, Lightricks, Runway, Luma).
- Chinese: lab blogs of ByteDance Seed, Alibaba Tongyi (Wan), Tencent Hunyuan, Kuaishou (Kling); Zhihu deep-dive articles; Bilibili tutorials; 36Kr and The Paper.

### The note
Copy `starter/templates/production_note.md` for each item.

## Worked example

**Pass 0** (2026-10-04): `arxiv_watch.py --query "video generation" --days 7 --max 20` returned 20 papers from 2026-09-27 to 2026-10-01. Pass 1 (from the abstracts) kept 2 of them.

**Note 1 — "Generative Cinematographer: Composing Camera and Object Motion in 3D"** (arXiv 2610.02180, pass 1 only).
- New: lifts one image into an editable 3D scaffold; the artist sets a camera path and moves parts of the subject with 3D handles; guidance maps drive a pretrained video model.
- Claimed: "consistent camera-relative motion, improved geometric consistency under viewpoint changes".
- Shown (from the abstract): not yet known; pass 2 must check the baselines and the human ratings.
- Available how: a guidance branch and LoRA adapters trained on a pretrained Wan model → if code is released, a node-graph port is likely soon.
- Fits: our "controlled camera + subject move" shots, which we now make with 3D white-box layouts (C05·M05).
- Decision: pass 2 this week; watch for code.

**Note 2 — "MosaiChunk: Compositing Spatio-Temporal Memory for Autoregressive Video Generation"** (arXiv 2610.02153, pass 1 only).
- New: a learned router picks past key-value entries across space and time for a frozen autoregressive generator, so details come back when an object reappears.
- Evidence to check: the authors introduce their own benchmark (RememBench) → evidence quality at most medium until independent tests exist.
- Fits: long single takes with revisits (a camera that returns to a set). Not in our tools yet.
- Decision: watch; re-check in 3 months.

**Model card example — LTX-2.5** (2026-08): pass 1 → relevant (open weights, joint audio and video, multishot). Pass 2 → asymmetric dual-stream DiT, Gemma 4 text encoder, distilled variant, INT8 and NVFP4 files; evidence: release notes and demos, few independent evaluations yet; license: the LTX-2.x Community License. Decision: one-day test (M02).

## Lab

**Deliverable:** `C17/M01/` with a pass-0 list, 3 production notes (one from a Chinese-language source), and a source list.

1. Run `arxiv_watch.py` with keywords for your shot types. Do pass 1 on the list and tick what passes.
2. Choose 3 items: a paper, a model card or technical report, and a Chinese-language source.
3. Do pass 1 and pass 2 on each, and write a production note with "claimed", "shown", and an evidence rating.
4. Write your source list: at most 10 sources, with the day you read each.

**Result checklist**
- [ ] Pass-0 list with ticks.
- [ ] 3 notes with claimed, shown, evidence rating, and a decision.
- [ ] One source in Chinese, the note in English.
- [ ] A source list of 10 or fewer.

## Model answer

**A strong note (shape):**

- **Item:** a technical report for a new open video model, 2026-09, English.
- **Read:** pass 2, 50 minutes.
- **New:** a 4-step distilled variant with audio, at 720p.
- **Claimed:** "matches the full model's quality at 8× the speed".
- **Shown:** one table with an automatic benchmark (no human ratings for the distilled variant); 3 ablations on the number of steps; no audio evaluation. Evidence: medium for video, low for audio.
- **Available:** weights on Hugging Face; the license of the VAE differs from the model license (non-commercial) → flagged.
- **Fits:** exploration takes for wides and inserts.
- **Test plan:** our eval set v3, 4 shot types × 30 clips each (M02 explains why 30).
- **Decision:** test on Friday.

The note is short and skeptical, separates claims from evidence, flags the license, and ends with a test plan and a date.
