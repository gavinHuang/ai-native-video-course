---
title: Evaluate models - arenas, benchmarks, your own eval set
hours: 8
outcomes:
  - Explain how arenas rank models with blind human votes (Elo / TrueSkill).
  - List the limits of public leaderboards and benchmarks.
  - Design a small eval set for your own production needs.
  - Run a blind comparison and calculate cost per usable second.
keywords: [eval, arena, Elo, cost per usable second, prompt adherence]
summary: >
  Public arenas show two outputs for the same prompt and ask people which is better. Many votes give a ranking such
  as Elo or TrueSkill. This is useful, but it measures general taste on general prompts. Your work needs specific
  things: the same character, exact product shape, a camera move, or clean speech. So you also need your own small
  eval set: fixed prompts and references that match your real jobs. Score each model blind, and calculate the cost
  per usable second, not the cost per generated second.
diagram:
  type: cycle
  title: Your evaluation loop
  nodes: ["Fixed eval set (10–20 cases)", "Generate with each model", "Blind scoring by criteria", "Usable rate + cost per usable second", "Decision + log"]
  center: "repeat for each new model"
watch:
  - title: "LMArena — Text-to-Video leaderboard"
    url: https://lmarena.ai/leaderboard
    note: "Look at the video and image arenas. Note the number of votes and the confidence intervals."
  - title: "Artificial Analysis — Video arena"
    url: https://artificialanalysis.ai/text-to-video/arena
    note: "Compare its ranking with LMArena. Note the differences."
quiz:
  - q: "Two models differ by 10 Elo points with wide confidence intervals. Conclusion?"
    options: ["The first is clearly better", "They are about equal; test on your own cases", "The second is broken", "Use the cheaper one only"]
    answer: 1
    explain: "Small Elo differences inside the error range do not mean a real difference for your job."
  - q: "What is 'cost per usable second'?"
    options: ["Price per generated second", "Total generation cost ÷ seconds that pass quality review", "GPU price per hour", "Subscription price ÷ 30"]
    answer: 1
    explain: "If only 1 in 5 clips is usable, the real cost is 5× the list price per second."
  - q: "Why score blind?"
    options: ["It is faster", "To avoid bias toward a brand or a model you like", "It needs no criteria", "Arenas require it"]
    answer: 1
    explain: "When you know the model name, you see what you expect."
  - q: "Which case belongs in an eval set for a beverage-ad studio?"
    options: ["A random fantasy dragon", "The same can, rotating, with readable label text, under 3 light setups", "A chess game", "A long poem"]
    answer: 1
    explain: "Eval cases must match real jobs and their failure modes."
  - q: "Model A has 5 of 8 usable clips, model B has 2 of 8. What can you say?"
    options: ["A is clearly better", "Not yet shown: the 95 % intervals overlap widely and the Fisher test gives p ≈ 0.16; generate more clips before you decide a route", "B is better", "Both are useless"]
    answer: 1
    explain: "Small samples show large problems, not small differences. C17·M02 gives the clip counts for a decision."
  - q: "A judge model agrees with your scores on 'label text correct' in 93 % of 30 clips, and on 'good acting' in 61 %. How do you use it?"
    options: ["For both criteria", "For label text only; keep acting as a human score", "For neither", "Only for acting"]
    answer: 1
    explain: "Measure agreement per criterion before you trust a judge. Taste and performance need people."
deeper:
  - title: "Chiang et al. (2024) — Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference"
    url: https://arxiv.org/abs/2403.04132
  - title: "Huang et al. (2023) — VBench: Comprehensive Benchmark Suite for Video Generative Models"
    url: https://arxiv.org/abs/2311.17982
  - title: "llm-stats — Best AI for video creation (blind-vote leaderboard)"
    url: https://llm-stats.com/leaderboards/best-ai-for-video-creation
---
## Learn

### Arenas
An arena shows two anonymous outputs for the same prompt. A person votes for the better one. A rating system (**Elo**, Bradley–Terry, or TrueSkill) turns many votes into a ranking. The top of the ranking changes almost every month. The top few models are often inside each other's error range (see the Tool walkthrough for a dated example).

Arenas are good for a first short list. Their limits:
- General prompts, general voters. Your clients are not general.
- Short clips. They do not test 10-shot consistency.
- They do not include cost, speed, license, or API stability.
- Vendors can tune for arena-style prompts.

### Benchmarks
Automatic benchmarks (for example VBench) measure many dimensions: motion smoothness, subject consistency, aesthetic quality, and **prompt adherence**. They are reproducible, but metrics do not always match human taste.

### Your own eval set
Make 10–20 fixed cases that match your real work. Each case has:
- a prompt (and references, if your work uses them),
- the criteria that matter, with a 1–5 scale,
- a "usable" rule: for example "all criteria ≥ 4 and no critical defect".

Write the criteria before you see any output; criteria written after viewing tend to favor the clips you already like. Typical criteria: prompt adherence, identity consistency, motion quality, physics, text/logo accuracy, audio sync, artifacts.

### Blind scoring
1. Generate each case with each model (same number of tries, for example 2 seeds).
2. Rename files with random IDs. Keep the key in a separate file, and do not open it until all scores are written.
3. Score without the names.
4. Join scores with the key.

### How many clips
A usable rate from a few clips is very uncertain. With 8 clips, "5 usable" means a true rate somewhere between about 31 % and 86 % (a 95 % interval). Two models with 5 of 8 and 2 of 8 are not shown to be different (p ≈ 0.16 in a one-sided Fisher test). Use the small first set (2 seeds per case) to find large problems and to build the habit. To decide a route, use about 30–40 clips per model per shot type (C17·M02 shows the numbers).

### Judge models
A vision-language model can score some criteria automatically: "is the label text correct?", "does the clip show two people?". This saves time on many clips. Check it first: score 30 clips yourself, let the judge score the same clips, and measure how often you agree. Use the judge only for the criteria where agreement is high (for example over 85 %). Keep taste, story, and acting for human scores (C03·M03).

### Keep the set alive
Version the set (v1, v2, …). Add a case for every real production failure. Retire cases that every model passes. Keep old results, so that you can show progress over time.

### Cost per usable second
`cost per usable second = total generation cost / total seconds that pass the usable rule`

This number decides production budgets. A cheap model with a 10% usable rate can cost more than an expensive model with a 50% usable rate.

## Tool walkthrough

### Arena example (dated)
As of 2026-10-02, one blind-vote video arena (llm-stats, "best AI for video creation") ranked Kling v3 first (1934), then Happy Horse 1.0 (1816), then Seedance 2.0 Fast (1747). Use such lists to choose which models to test, then test them on your own set.

### Scoring and analysis
Use the blind-rename script in the lab, a spreadsheet or CSV for scores, and `starter/tools/model_trial.py` (C17·M02) to compute usable rates with intervals and cost per usable second per shot type.

## Worked example

**Eval set "Coffee brand", 4 cases × 3 models × 2 seeds, 5 s clips.**

| Model | List price/s | Clips | Usable | Usable seconds | Cost | Cost per usable s |
|---|---|---|---|---|---|---|
| A (hosted, premium) | US$0.10 | 8 | 5 | 25 | US$4.00 | US$0.16 |
| B (hosted, fast) | US$0.05 | 8 | 2 | 10 | US$2.00 | US$0.20 |
| C (open, rented GPU) | about US$0.02 | 8 | 3 | 15 | US$0.80 | US$0.05 |

With 8 clips per model, these rates are rough (5 of 8 → 31–86 %); they show the method and the large differences, not a final ranking.

Decision: model C for background and B-roll (cheapest per usable second, private). Model A for hero shots with the product, where its higher usable rate matters most. Re-run the eval when a new model appears.

## Lab

**Deliverable:** `evals/v1/` in your repository: cases, outputs, scores, and a report. You will reuse this set in C05, C17, and the capstone.

1. Choose a domain you care about (for example a product, a story world, or explainer videos).
2. Write 10 cases. At least 3 must test consistency between two shots.
3. Define criteria and the usable rule.
4. Run 3 models (at least one open model, if possible).
5. Score blind. Calculate usable rate and cost per usable second.
6. Write a decision of 5–8 lines.

Starter script for blind renaming:
```python
import random, shutil, json, pathlib
src = pathlib.Path("raw"); dst = pathlib.Path("blind"); dst.mkdir(exist_ok=True)
key = {}
for f in src.glob("*.mp4"):
    rid = f"{random.getrandbits(32):08x}.mp4"
    shutil.copy(f, dst / rid); key[rid] = f.name
json.dump(key, open("key.json", "w"), indent=2)
```

**Result checklist**
- [ ] 10 cases with criteria and a usable rule.
- [ ] Blind scores for 3 models.
- [ ] Cost per usable second for each model.
- [ ] A decision with reasons.

## Model answer

A strong report shows a table like the worked example. It also says *why* clips failed (for example "model B: logo text changed in 5 of 8 clips"; "model C: hand deformation in fast motion"). It ends with a routing rule: which model for which shot type. It records the date and the model versions, because the result will be old in 3 months. It states the sample size and the intervals, and it says which results are only rough (small samples) and which justify a routing decision now. It lists two new cases for v2, taken from the failures that the run showed, and the date of the next run. A reader can repeat the whole test from the folder.
