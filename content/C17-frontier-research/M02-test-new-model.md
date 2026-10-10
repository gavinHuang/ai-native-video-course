---
title: Test a new model in one day
hours: 14
outcomes:
  - Run your fixed eval set on a new model with automation.
  - Compare with your current routing choices using blind scores and cost per usable second.
  - Decide - adopt, watch, or ignore - with evidence.
  - Update the routing table and the tool landscape.
keywords: [eval harness, routing table, adoption decision]
summary: >
  When a new model appears, do not trust the launch video. Run your fixed eval set from C01 with an automated
  harness. Score blind, compare with the current models in your routing table, and calculate cost per usable second.
  Then decide: adopt it for some shot types, watch it, or ignore it. Update your routing table and your tool landscape
  page. With a good harness, this takes one day.
diagram:
  type: flow
  title: One-day model test
  nodes: ["Morning: add backend adapter (C12·M01)", "Run eval set (cases × seeds)", "Blind scoring (human + judge)", "Afternoon: usable rate, cost per usable s", "Decision: adopt / watch / ignore", "Update routing + landscape"]
  highlight: [4]
watch:
  - title: "llm-stats — Best AI for video creation (blind-vote leaderboard)"
    url: https://llm-stats.com/leaderboards/best-ai-for-video-creation
    note: "Use it to choose which new models to test."
  - title: "Artificial Analysis — text-to-video arena"
    url: https://artificialanalysis.ai/text-to-video/arena
    note: "Compare with your own results after the test."
quiz:
  - q: "What makes a one-day model test possible?"
    options: ["Luck", "Work done before: a fixed eval set, a backend abstraction that takes a new model in an hour, a blind scoring sheet, and a script for the analysis", "A bigger GPU", "Reading the launch blog"]
    answer: 1
    explain: "C01·M07 (eval set), C12·M01 (backends), C03·M03 (scoring), and model_trial.py."
  - q: "With 10 clips per model per shot type, the candidate scores 10/10 on product shots and the current model 7/10. Is the candidate better?"
    options: ["Yes, clearly", "Not shown: the one-sided Fisher test gives p = 0.105; with 10 clips, a real 50 % vs 80 % difference is detected only about 28 % of the time", "No, it is worse", "The test is wrong"]
    answer: 1
    explain: "Small samples give large random differences. The module simulation shows the detection rate per sample size."
  - q: "About how many clips per model per shot type do you need to detect a 50 % vs 80 % usable-rate difference most of the time?"
    options: ["5", "About 40 (84 % detection) to 60 (96 %); 30 gives about 73 %", "1,000", "10 is always enough"]
    answer: 1
    explain: "Measured by simulation with the course tool (2,000 runs per size). A 50 % vs 65 % difference needs well over 100."
  - q: "A new model is better on product shots (p = 0.03) at a similar cost per usable second, and worse on wides. Decision?"
    options: ["Replace the current model everywhere", "Route by shot type: adopt it for product shots, keep the current model for wides, and re-test dialogue with more clips", "Ignore it", "Wait a year"]
    answer: 1
    explain: "The routing table is per shot type. One average hides the differences."
  - q: "Why must scoring be blind?"
    options: ["It is faster", "If you know which model made a clip, your expectations (a famous new model, an expensive one) change your score", "Vendors require it", "To save storage"]
    answer: 1
    explain: "Rename the files to random IDs before scoring; keep the key separate."
  - q: "What does 'watch' mean as a decision?"
    options: ["Ignore forever", "Not adopted now; a written trigger for a re-test - a new version, a price change, an API change, or a date", "Use in production", "Delete"]
    answer: 1
    explain: "Keep a watch list with triggers. Without a trigger, 'watch' means 'forget'."
  - q: "Which cost number do you compare between models?"
    options: ["Price per second of output", "Cost per usable second: total cost of all clips divided by the seconds that passed the usable rule", "Price per month", "Cost per prompt"]
    answer: 1
    explain: "A cheap model with a low usable rate can cost more per usable second than an expensive one."
deeper:
  - title: "VBench — benchmark suite for video generation (GitHub)"
    url: https://github.com/Vchitect/VBench
  - title: "Hamel Husain — Your AI product needs evals"
    url: https://hamel.dev/blog/posts/evals/
  - title: "Wikipedia — Fisher's exact test"
    url: https://en.wikipedia.org/wiki/Fisher%27s_exact_test
---
## Learn

### Why a fixed procedure
A new video model appears almost every week, each with a launch page of perfect clips. You cannot test every model, and you must not trust launch pages. A fixed procedure answers one question: does this model lower our cost per usable second, or raise quality, for any shot type in our routing table?

### Preparation (done in earlier courses)
- **Eval set** (C01·M07): cases grouped by shot type (product, dialogue, wide, insert, and others), each with criteria and a usable rule.
- **Backend abstraction** (C12·M01): a new model is one new adapter class.
- **Blind scoring** (C03·M03): clips renamed to random IDs; a human scores taste and story; a judge model scores objective criteria where it is reliable.
- **Cost tracking:** the cost of every clip in the take log.

### The day
1. **Adapter (1–2 h):** add the model to your backend: an API call or a node-graph workflow.
2. **Run (2–3 h, in parallel):** every case of the shot types that matter, with enough clips (see below).
3. **Score (1–2 h):** blind, with the same usable rule as the current models.
4. **Analyze (1 h):** usable rate per shot type with an interval, a test against the current model, and cost per usable second.
5. **Decide (30 min):** adopt for named shot types; watch with a trigger; or ignore.
6. **Update:** the routing table, the tool-landscape page with the date, and a short team note.

### How many clips
A usable rate from 10 clips has a wide interval: 7 of 10 means "somewhere between about 40 % and 89 %". Random differences between two models are then large. Use a test for two rates (the one-sided Fisher exact test is good for small samples) and know its power: the chance to detect a real difference.

| Real difference | 10 clips | 20 | 30 | 40 | 60 | 100 |
|---|---|---|---|---|---|---|
| 50 % vs 80 % | 28 % | 55 % | 73 % | 84 % | 96 % | 100 % |
| 50 % vs 65 % | 8 % | 13 % | 23 % | 29 % | 46 % | 64 % |

(Detection rate at p < 0.05, from 2,000 simulated tests per cell with the course tool.) Rules that follow:
- Use about 30–40 clips per model per shot type that you want to decide on; test fewer shot types instead of fewer clips.
- A small difference (15 points) needs hundreds of clips: you will usually not detect it in one day, and it rarely changes the routing.
- "No clear difference" is a result, not a failure: decide on cost, speed, and features.

### Decide by shot type
Report each shot type separately. A model can be better for product shots and worse for wides. Compare cost per usable second: total cost divided by the seconds that passed the usable rule. Then:
- **Adopt** where it is better (or equal and cheaper);
- **Watch** with a trigger (a new version, a price change, a date);
- **Ignore** where it is worse.

### Keep the eval set healthy
Add cases from real production failures. Retire cases that every model passes. Version the set (v1, v2, …) and keep old results, so that you can show trends.

## Tool walkthrough

### Analyze the scores

The score sheet is a CSV with one row per clip: `model,case,shot_type,seed,usable,seconds,cost_usd`.

```bash
python starter/tools/model_trial.py scores.csv --incumbent current --candidate x2
```

For each shot type, the tool prints the usable count, the rate with a 95 % Wilson interval, the cost per usable second, the one-sided Fisher p-value that the candidate is better, and a suggested decision. The decision is a suggestion: you add speed, features, licenses, and taste.

Two example sheets are in `starter/examples/` (simulated scores with known true rates; see the worked example).

### Choose which models to test
Public blind-vote arenas (for example the llm-stats and Artificial Analysis video arenas) rank models on general prompts. Use them to pick candidates, not to decide: your shot types and your usable rule are different.

## Worked example

The scores are **simulated** with known true usable rates, so that you can see what the test finds and misses. True rates: current model 50 % product, 55 % dialogue, 40 % wide, at US$0.06/s; candidate "x2" 80 % product, 30 % dialogue, 45 % wide, at US$0.09/s. Clips are 5 s.

**Day with 10 clips per shot type** (`example_scores_10.csv`):

| Shot type | Current | x2 | p (x2 better) | Suggestion |
|---|---|---|---|---|
| product | 7/10 | 10/10 | 0.105 | watch: no clear difference |
| dialogue | 6/10 | 3/10 | 0.965 | watch: no clear difference |
| wide | 6/10 | 4/10 | 0.911 | watch: no clear difference |

The real 30-point gain on product shots is not shown with this sample.

**Day with 30 clips per shot type** (`example_scores_30.csv`):

| Shot type | Current | x2 | $/usable s (current / x2) | p (x2 better) | Suggestion |
|---|---|---|---|---|---|
| product | 15/30 | 23/30 | 0.120 / 0.117 | 0.030 | adopt |
| dialogue | 16/30 | 14/30 | 0.113 / 0.193 | 0.781 | watch |
| wide | 16/30 | 8/30 | 0.113 / 0.337 | 0.992 | ignore (worse) |

The product gain is detected, at about the same cost per usable second. The true dialogue difference (55 % vs 30 %) was missed in this sample: random results happen, which is why "watch" has a re-test trigger. The wide result shows a model that is clearly worse and more expensive for that shot type.

**Decision note:** "x2: adopt for product shots (routing updated, 2026-10-04); dialogue: watch, re-test with 40 clips when version 2.1 is released; wides: ignore. Landscape page updated."

## Lab

**Deliverable:** `evals/runs/<date>-<model>/` with the clips, the blind key, the score sheet, the `model_trial.py` report, and a decision note; and eval set v+1.

1. Choose a model released in the last 3 months that you have not tested, and 2–3 shot types where it could change your routing.
2. Add the adapter to your backend. Generate 30 clips per shot type with the new model, and the same number with your current model (or reuse recent clips from the same eval cases).
3. Rename all clips to random IDs; score them blind with your usable rule.
4. Run `model_trial.py`. Write the decision note with the numbers per shot type and a trigger for every "watch".
5. Update your routing table and landscape page. Add 2 new eval cases from failures that you saw.

**Result checklist**
- [ ] Run folder with the blind key kept separate.
- [ ] Report per shot type with intervals and p-values.
- [ ] Decision note with triggers.
- [ ] Routing table, landscape page, and eval set updated.

## Model answer

**Decision note (shape of a strong answer):**

"Model: a new open video model, version 1.0, tested 2026-10-02 with eval set v4 (3 shot types × 30 clips per model, blind).

| Shot type | Current | New | $/usable s | p | Decision |
|---|---|---|---|---|---|
| insert (hands, objects) | 14/30 | 24/30 | 0.21 / 0.09 | 0.006 | adopt (self-hosted, cheaper) |
| dialogue | 19/30 | 12/30 | 0.18 / 0.35 | 0.98 | ignore: lip sync drifts after 4 s |
| wide | 11/30 | 15/30 | 0.30 / 0.17 | 0.21 | watch: re-test when the 1.1 release adds the planned camera control |

Speed: 95 s per 5 s clip on our 48 GB GPU. License: Apache-2.0 for every file in the workflow (checked). Routing updated for inserts; the landscape page has the date and the license. Eval set v5 adds 2 dialogue cases with long lines, from the failures."

The note gives numbers per shot type, uses enough clips, names a trigger, checks the license, and changes the eval set.
