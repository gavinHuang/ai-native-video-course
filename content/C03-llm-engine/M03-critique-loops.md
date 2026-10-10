---
title: Critique loops and LLM as judge
hours: 7
outcomes:
  - Build a generate-critique-revise loop with explicit criteria.
  - Use a vision-capable model to review images and video frames.
  - Calibrate an LLM judge against human scores.
  - Know where LLM judges fail and when a human must decide.
keywords: [critique loop, LLM as judge, rubric, calibration]
summary: >
  An LLM can review work as well as make it. Give it a rubric with clear criteria and a scale. In a critique loop,
  one call makes a draft, a second call scores it against the rubric and lists problems, and a third call revises.
  Vision-capable models can also review frames from generated video. A judge must be calibrated: compare its scores
  with human scores on the same items. LLM judges are good at checklists and consistency. They are weak at taste,
  humor, and subtle visual defects. Humans make the final creative decision.
diagram:
  type: cycle
  title: Generate - critique - revise
  nodes: ["Draft (LLM or generator)", "Critique against rubric", "Revise with critique", "Stop rule: score ≥ target or 3 rounds"]
  center: "human approves"
watch:
  - title: "Hamel Husain — Creating an LLM-as-a-judge that drives business results"
    url: https://hamel.dev/blog/posts/llm-judge/
    note: "Read all. The method for calibration with human labels."
  - title: "Anthropic — Building effective agents (evaluator-optimizer pattern)"
    url: https://www.anthropic.com/engineering/building-effective-agents
    note: "Read the 'Evaluator-optimizer' section."
quiz:
  - q: "What must a judge prompt include?"
    options: ["Only 'rate this 1–10'", "Explicit criteria, a defined scale, and examples of each level", "The model name", "Nothing"]
    answer: 1
    explain: "Vague judges give random-looking scores. A rubric makes scores consistent."
  - q: "How do you calibrate an LLM judge?"
    options: ["Ask it if it is correct", "Compare its scores with human scores on 30+ items; fix the rubric where they disagree", "Use a bigger model", "Lower the temperature to 0 only"]
    answer: 1
    explain: "Agreement with humans is the measure."
  - q: "Where is an LLM judge weakest?"
    options: ["Checking that all required fields exist", "Counting shots", "Subtle taste, humor, and small visual artifacts", "Checking duration"]
    answer: 2
    explain: "Use judges for objective checks; keep humans for taste."
  - q: "Why a stop rule in the loop?"
    options: ["To save tokens and avoid endless rewrites that drift away from the brief", "It is required by the API", "To make output longer", "To use a different model"]
    answer: 0
    explain: "Unlimited loops cost money and often make the work worse."
  - q: "A judge agrees with you on 95 % of 'logo visible' items, but 90 % of items pass. Kappa is 0.00. What does this mean?"
    options: ["The judge is excellent", "The judge always says 'pass'; its agreement comes from the base rate, not from looking; do not use it for this criterion", "Kappa is broken", "Use a 1–5 scale"]
    answer: 1
    explain: "In the module example, the judge answered 'pass' for all 40 items."
  - q: "In pairwise comparisons, the judge prefers whichever option comes first. What do you do?"
    options: ["Accept it", "Run each pair in both orders and keep only results that agree; count the rest as ties", "Always put your favorite first", "Use a longer rubric"]
    answer: 1
    explain: "Position bias is common. Swapping the order measures and removes it."
deeper:
  - title: "Zheng et al. (2023) — Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena"
    url: https://arxiv.org/abs/2306.05685
  - title: "Madaan et al. (2023) — Self-Refine: Iterative Refinement with Self-Feedback"
    url: https://arxiv.org/abs/2303.17651
---
## Learn

### The loop
1. **Draft:** an LLM writes a script, or a model generates a shot.
2. **Critique:** a judge call scores the draft against a rubric and lists concrete problems.
3. **Revise:** a call fixes the listed problems only.
4. **Stop rule:** stop when the score is at or above the target, or after 3 rounds.

Use a different prompt (and sometimes a different model) for the judge. A model often likes its own style.

The revise step gets the draft and the list of problems, and the instruction to change nothing else. Without this instruction, each revision rewrites good parts too, and the loop drifts away from the approved treatment. Log every round: the draft, the scores, and the fixes. The log shows where the loop helps and where it only costs tokens.

### The rubric
Each criterion has a name, a question, and a scale with examples:
- **Hook (1–5):** "Does frame 1 create a visual question?" 1 = logo or context; 5 = strong visual question, no text needed.
- **Brand rules (pass/fail):** "Is the logo correct and visible for ≥ 1 s? No forbidden imagery?"
- **Timing (pass/fail):** total duration in the target range.

Ask for JSON output: score per criterion, evidence, and one fix per problem.

### Vision review
Current multimodal LLMs can see images and video frames. Practical method for video:
1. Extract frames with ffmpeg: `ffmpeg -i shot.mp4 -vf fps=2 frames/%03d.jpg`.
2. Send a grid of frames plus the shot specification.
3. Ask: "Does the output match each element of the spec? List defects with frame numbers."

They find: wrong shot size, wrong wardrobe color, a missing object, text errors, obvious deformation. They miss: subtle flicker, small morphing, timing feel. A grid of still frames cannot show motion quality; for motion, use a human review or measured checks such as frame differences (C05).

### Calibration
1. Score 30–50 items yourself (or two humans).
2. Run the judge on the same items.
3. Measure agreement per criterion.
4. Where agreement is low, rewrite the criterion and add examples. Repeat.
5. Use the judge only for criteria with high agreement.

### Agreement beyond chance
Raw agreement can mislead. If 90 % of items pass, a "judge" that always answers "pass" agrees with you 90 % of the time and has learned nothing. **Cohen's kappa** corrects for this: it measures agreement beyond what chance and the base rates would give. 0 means no better than chance; 1 means perfect. A common reading: 0.8 and above, good; 0.6–0.8, usable as a first filter; below 0.6, do not trust it alone. For 1–5 scales, also report "within ±1" agreement, because a 4 against a 5 is a smaller error than a 1 against a 5.

### Common judge biases
- **Position bias:** in pairwise comparisons, judges prefer the first (or the second) option. Run both orders and keep only consistent results.
- **Length bias:** longer answers get higher scores. Put length limits in the rubric.
- **Self-preference:** a model prefers text in its own style. Use another model or prompt for the judge.
- **Leniency:** many judges give high scores by default. Ask for evidence first, then the score, and include examples of low scores in the rubric.

### Responsibility
The judge is a filter. It saves your time on obvious problems. Final creative and legal decisions stay with a human.

## Tool walkthrough

### Measure agreement
```bash
python starter/tools/judge_agreement.py starter/examples/judge_scores.csv --within 1
```
The CSV has one row per item and criterion: `item,criterion,human,judge`. The tool prints raw agreement, Cohen's kappa (checked against statsmodels), and a verdict per criterion.

### Frames for vision review
```bash
ffmpeg -i shot.mp4 -vf "fps=2,scale=480:-1,tile=4x3" -frames:v 1 grid.jpg   # 12 frames in one image
```
One grid image is cheaper than 12 separate images and keeps the order visible.

## Worked example

**Script critique for the water-bottle ad (C03·M02).**

Judge output (JSON, shortened):
```json
{"hook": {"score": 2, "evidence": "Opens on a sunrise skyline", "fix": "Open on ice cubes rattling in the bottle at hour 24"},
 "brand": {"pass": true},
 "timing": {"pass": false, "evidence": "Sum of shots = 34 s", "fix": "Cut shot 5 (city wide) to 2 s and merge 6+7"},
 "clarity": {"score": 4}}
```
Revise call → new script. Round 2: hook 4, timing pass. Stop. Human review: approves, but changes one line of voice-over for tone.

## Lab

**Deliverable:** `pipelines/critic/` + a calibration report.

1. Write a rubric (5 criteria) for your shot lists or scripts.
2. Implement the loop: draft → critique (JSON) → revise, with a stop rule.
3. Implement a frame-review tool for generated clips: extract frames, send grid + spec, return defects.
4. Score 30 items yourself. Run the judge. Calculate agreement per criterion.
5. Improve the weakest criterion once. Measure again.

**Result checklist**
- [ ] Loop runs with a stop rule and logs each round.
- [ ] Frame review returns defects with frame numbers.
- [ ] Agreement table before and after the rubric fix.

## Model answer

**Agreement report** (the example sheet `starter/examples/judge_scores.csv`: 40 simulated items with known judge behavior):

| Criterion | Raw agreement | Kappa | Verdict |
|---|---|---|---|
| timing (pass/fail) | 95 % | 0.87 | use the judge |
| logo visible (pass/fail) | 95 % | 0.00 | do not use: the judge said "pass" for every item |
| hook (1–5) | 52 % (92 % within ±1) | 0.40 | keep it human, or rewrite with examples |

The logo row is the important lesson: 95 % agreement looked good, but the judge never found a single fail. After the rubric fix ("first list every frame where the logo is visible, with frame numbers; then decide"), measure again on new items. The final setup: the judge for criteria with kappa ≥ 0.8 and as a first filter; humans for taste and for every criterion that the judge cannot yet do.
