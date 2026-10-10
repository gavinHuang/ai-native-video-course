---
title: Templates and data-driven variants
hours: 14
outcomes:
  - Design a video template with fixed and variable parts, and text slots with length limits.
  - Generate variants from a data table, with validation of every row before any render or generation.
  - Cache by input hash, so a re-run renders only what changed.
  - Control quality at scale with automated gates on every file and human review of a sample.
  - Design A/B variant sets that change one variable, and read the result with a significance test.
keywords: [template, variant, input hash cache, A/B test, minimum detectable effect]
summary: >
  A template fixes the structure, timing, look, and legal parts of a video, and leaves named slots for what changes:
  the hook, the product shot, the text lines, the voice, the language, the offer. A data table fills the slots, one
  row per variant. Validate every row first (columns, text lengths, files), cache outputs by a hash of their inputs,
  and gate every file. A/B tests compare variants that differ in one column, with a sample size planned before the
  test; most small differences in short tests are noise.
diagram:
  type: flow
  title: From data table to tested variants
  nodes: ["Template: fixed parts + named slots", "Data table: one row per variant", "Validate rows: columns, text limits, files", "Generate / render (cached by input hash)", "Gates on 100 %; people review a sample", "A/B: one variable; planned sample size"]
  highlight: [2, 5]
watch:
  - title: "Meta — business help center (search 'dynamic creative')"
    url: https://www.facebook.com/business/help
    note: "Note how the platform tests creative variants."
  - title: "X — AI UGC ads workflow at US$2–4 each (practitioner article)"
    url: https://x.com/nestymee/article/2071972061124383110
    note: "Note which parts are templated."
quiz:
  - q: "Which parts of an ad belong in the fixed part of the template?"
    options: ["The hook", "Shot structure and timing, the look, the logo, legal text, the music bed, and the end card", "The offer", "The language"]
    answer: 1
    explain: "Fixed parts carry brand and legal consistency. Variable parts are the things you want to test or localize."
  - q: "A German offer line is 47 characters in a slot designed for 32. When should the pipeline find this?"
    options: ["After the render, in review", "Before any generation or render: the row validation checks every text against its slot limit", "Never; the text shrinks", "After publishing"]
    answer: 1
    explain: "Validation is free; a wasted render or a published cut-off line is not. In the module test, the row was rejected before rendering."
  - q: "Why cache outputs by a hash of all their inputs?"
    options: ["For security", "A re-run after one change renders only the rows whose inputs changed; nothing is paid or rendered twice", "To make files smaller", "Platforms require it"]
    answer: 1
    explain: "In the module test, the second run rendered 0 and took all 4 valid variants from the cache."
  - q: "Your variant set changes the product, the hook, and the offer at once. B wins. What did you learn?"
    options: ["The hook works", "Very little about causes: three things changed, so you do not know which one made the difference; test one variable per set", "Everything", "The product is better"]
    answer: 1
    explain: "A matrix of variants is fine for production. For a test, change one column."
  - q: "A has 3.00 % CTR and B 3.38 % on 4,000 impressions each. Is B better?"
    options: ["Yes, +13 %", "Not shown: p = 0.34; the 95 % interval includes 0. To detect +20 % at a 3 % base rate you need about 13,900 impressions per variant", "Yes, if it continues", "A is better"]
    answer: 1
    explain: "Small differences on small samples are mostly noise. Plan the sample before the test."
  - q: "What does a person review when 200 variants are rendered?"
    options: ["All 200", "Every file that a gate flagged, plus a random sample (for example 5 %); the gates check every file", "None", "Only the first 10"]
    answer: 1
    explain: "Gates on 100 %, people on a sample and the exceptions."
  - q: "Why not stop an A/B test on the day it first shows p < 0.05?"
    options: ["It is rude", "Checking repeatedly and stopping at the first good result raises the false-positive rate far above 5 %; run to the planned sample size", "Platforms forbid it", "It wastes money"]
    answer: 1
    explain: "Decide the metric, the minimum effect, and the sample size before the test."
deeper:
  - title: "Kohavi, Tang, Xu — Trustworthy Online Controlled Experiments (book)"
    url: https://experimentguide.com/
  - title: "Remotion — programmatic video in React (template rendering)"
    url: https://www.remotion.dev/docs/
  - title: "Evan Miller — How not to run an A/B test (on peeking)"
    url: https://www.evanmiller.org/how-not-to-run-an-ab-test.html
---
## Learn

### Why variants
AI-native production makes many versions cheap: one ad for 4 products, 3 hooks, and 6 languages is 72 videos. Without a system, 72 videos are 72 chances for a typo, a wrong logo, a cut-off line, or a missing disclosure. A template and a data table turn them into one design plus 72 rows of data.

### Template design
Split the video into:
- **fixed parts:** shot structure and timing, the look, the logo, legal text, the music bed, the end card;
- **variable slots:** the hook shot, the product shot, text lines, the voice line, the background, the language, the offer, the call to action.
Each text slot has a length limit from its layout (and from the safe zone, C08·M04). Each media slot has a naming rule, for example `shots/hook_{hook_type}_{product_id}.mp4`. Keep text as separate layers in the master; burned-in text cannot be localized (M02).

### The data table
One row per variant: `variant_id, product_id, audience, language, hook_type, offer_text, cta, voice_id, ...`. Validate every row before you spend anything:
- every column that the template uses exists;
- every text fits its slot limit (in its language);
- every media file exists (or is queued for generation);
- banned words and legal terms are checked against a list.

### The pipeline
For each row:
1. Generate the missing variable shots through the queue (C12·M01). Many rows share shots (the same product hook in 2 languages), so generate each unique shot once.
2. Make the voice lines (C06·M01) and check their fit.
3. Assemble the segments, burn the text, mix the voice over the music.
4. Run the gates: spec, loudness, identity, logo, captions (C12·M04).
5. Write a manifest line: variant ID, file, input hash, and the row.

**Cache by input hash.** Compute a hash of everything that goes into a file: the template, the row, and the input media. If a file with that hash exists, skip it. A re-run after a one-line change renders only the changed rows.

### Generate each unique shot once
Count the unique inputs before you generate. 24 variants of 4 products × 3 hooks × 2 languages need only 12 hook shots, because the language changes the voice and the text, not the picture. A pipeline that generates per row pays twice for half of them.

### Quality at scale
- **Automated gates on 100 %** of the files.
- **People review** every flagged file and a random sample (for example 5 %). Sampling finds the problems that no gate checks yet; add a gate for each new problem type.

### A/B tests
An A/B test compares two variants that differ in **one** column (the hook type, or the voice, or the offer). Before the test, decide:
1. the metric (CTR, 30-second retention, completion);
2. the minimum effect worth acting on (for example +20 % relative);
3. the sample size needed to detect it.
Then run to that size and read the result with a significance test. With p ≥ 0.05 the honest result is "no difference found". Do not stop the test the first time it looks good; repeated checks raise false positives far above 5 %.

Sample sizes are larger than intuition suggests. At a 3 % click-through rate, detecting a +20 % change needs about 13,900 impressions per variant.

## Tool walkthrough

### Render variants

```bash
python starter/pipeline/variants.py template.json variants.csv --out variants/ --dry-run   # validate only
python starter/pipeline/variants.py template.json variants.csv --out variants/
```

The template format is in the script's help. Text is drawn with Pillow inside the default safe zone; voice is mixed over the music bed; outputs are named `<variant_id>_<hash>.mp4` with a `manifest.json`. The script also reports which columns vary, and warns when a set changes more than one.

For large programs, code-based rendering frameworks (for example Remotion) or NLE templates with automation do the same job with more layout control.

### Plan and read a test

```bash
python starter/pipeline/ab_report.py --plan --rate 0.03 --min-effect 0.2
python starter/pipeline/ab_report.py --a 120,4000 --b 152,4000
```

## Worked example

**Variant test** (2026-10-04): 5 rows (2 products × 2 hook types, plus one with a long offer line), a 3-segment vertical template (hook 2 s, product with offer text 3 s, end card with CTA 2 s), voice over a music bed.

```
5 variants; columns that vary: product_id, hook_type, offer_text
note: for an A/B test, change one column per test set; this set is a matrix, not a clean A/B test
PROBLEM v04: offer_text is 47 characters (limit 32): 'Ice cold for 24 hours and longer than you think'
rendered 4, from cache 0, rejected 1
```

The 4 valid variants rendered in 2.9 s (1080 × 1920, 7 s, H.264 + AAC). A second run: `rendered 0, from cache 4`.

**Reading tests** (`ab_report.py`; the numbers match statsmodels' z-test):

| A | B | Relative | p | Result |
|---|---|---|---|---|
| 120/4,000 (3.00 %) | 152/4,000 (3.80 %) | +27 % | 0.048 | a real difference, just |
| 120/4,000 (3.00 %) | 135/4,000 (3.38 %) | +13 % | 0.340 | no difference found; 13,914 per variant needed for +20 % |

**Camera campaign:** 4 products × 3 hooks × 2 languages = 24 variants. 12 unique hook shots and 8 voice lines generated (about US$40). 24 files rendered in 20 minutes; gates flagged 2 (a German line too long; an end card under the UI zone). The A/B test changed only the hook type, with 15,000 impressions per variant planned.

## Lab

**Deliverable:** `C15/M01/` with a template, a data table of 12 or more rows, the rendered variants, a manifest, gate reports, a sample-review note, and a test plan.

1. Design a template for a 15–30 s piece of your project: fixed parts, slots, text limits, naming rules.
2. Write a data table with 12 or more rows (at least 2 products or topics, 2 hooks, 2 languages).
3. Validate with `--dry-run`. Fix every problem.
4. Generate the missing shots through your queue; render all variants; run the gates on all files.
5. Review every flagged file and a 10 % random sample. Write what the sample found that the gates did not.
6. Plan one A/B test: the single variable, the metric, the minimum effect, the sample size. If you can, run it and read it with `ab_report.py`.

**Result checklist**
- [ ] Template and data table; validation passes.
- [ ] Variants rendered with a manifest; a re-run uses the cache.
- [ ] Gate reports and the sample-review note.
- [ ] A test plan with a calculated sample size (and a result, if run).

## Model answer

**Sample review (shape of a strong answer):** "Gates passed 22 of 24 and flagged 2. The 10 % sample (3 files) found one problem that no gate checks: in v17 the offer text covers the product's logo. New gate: the text box must not overlap the logo box of the product shot (stored in the product sheet). Re-run: the gate flagged v17 and v18; I moved the text slot up for that product."

**Test plan:**

| Item | Value |
|---|---|
| Variable | hook_type (result-first vs question) — everything else the same |
| Metric | 3-second hold rate (viewers still watching at 3 s) |
| Base rate | 42 % (last month) |
| Minimum effect | +10 % relative |
| Sample size | about 2,200 views per variant (`ab_report.py --plan --rate 0.42 --min-effect 0.1`) |
| Stop rule | run until both variants have 2,200 views; no early stop |

"Result: 46.7 % vs 42.3 % on 2,300 views each (+10 % relative, at the minimum effect): p = 0.002. Result-first hooks become the default for this series."
