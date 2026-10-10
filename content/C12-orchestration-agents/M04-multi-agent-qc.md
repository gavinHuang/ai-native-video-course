---
title: Multi-agent production and automated quality gates
hours: 20
outcomes:
  - Design a multi-agent studio - writer, director, generator, editor, reviewer - with clear input and output contracts.
  - Write the orchestrator as code (a state machine), and use LLM agents inside its steps.
  - Place human gates where creative, legal, and cost decisions happen.
  - Add automated gates at every stage that return PASS, FIX, or REJECT with reasons.
  - Measure the system - cost per finished minute, human minutes per finished minute, rejection rate per gate, lead time.
keywords: [orchestrator, quality gate, human gate, LLM judge, pipeline metrics]
summary: >
  A multi-agent studio splits production into roles with contracts: the writer makes a tagged script, the director
  a shot list and prompts, the generator clips, the editor timelines, and the reviewer scores. The orchestrator is
  usually code: a state machine that moves each item through the stages, calls agents and tools, and stops at
  gates. Human gates sit at story, legal, cost, and final approval. Automated gates check every item and return
  PASS, FIX, or REJECT with reasons, so the system can fix or regenerate without a person. Measure the system, not
  only the film.
diagram:
  type: flow
  title: Item states with gates
  nodes: ["Brief → script (writer)", "Human gate: story + legal", "Shot list + prompts (director); schema gate", "Clips (generator); shot gate: tech + identity", "Timeline + versions (editor); delivery gate", "Human gate: final approval → publish"]
  highlight: [1, 5]
watch:
  - title: "Anthropic — How we built our multi-agent research system"
    url: https://www.anthropic.com/engineering/multi-agent-research-system
    note: "Read the lessons on orchestration, delegation, and evaluation."
  - title: "X — Claude Code can run your creative team (thread/article)"
    url: https://x.com/PrajwalTomar_/article/2077346824759984581
    note: "Read critically: which steps still need a human?"
quiz:
  - q: "Why is the orchestrator usually code, not an LLM?"
    options: ["LLMs cannot plan", "A production pipeline needs predictable states, retries, budgets, and audit; code gives that, and calls LLM agents inside the steps where judgment or language is needed", "Code is cheaper to write", "MCP requires it"]
    answer: 1
    explain: "Use LLM orchestration for open-ended tasks. Use code for a repeatable production line."
  - q: "Where do human gates belong?"
    options: ["After every step", "Where creative, legal, and cost decisions happen: the script (story; real people, brands, music), spend above a limit, the final cut, and publication", "Nowhere", "Only at the end"]
    answer: 1
    explain: "Too many gates and nothing moves; too few and the system publishes mistakes."
  - q: "A shot gate returns FIX for a frozen 1.5 s tail. What does the orchestrator do?"
    options: ["Reject the shot", "Run the fix (trim the frozen part), check the gate again, and continue if it passes", "Ask a person", "Ignore it"]
    answer: 1
    explain: "FIX means a cheap, known fix exists. REJECT means regenerate. Only repeated failures go to a person."
  - q: "A gate scores identity 0.145 against the character references. What is the verdict and the next step?"
    options: ["FIX: color correct", "REJECT: the face is a different person; regenerate with stronger references (or route to a person after N tries)", "PASS", "Lower the threshold"]
    answer: 1
    explain: "Identity is not fixable in post. Regenerate."
  - q: "Why must every fix loop have a limit?"
    options: ["To save electricity", "A loop of generate → reject → generate can spend the budget on a shot that the method cannot make; after N tries the item goes to a person", "Agents get tired", "MCP limits calls"]
    answer: 1
    explain: "Limits protect money and surface real problems (C03·M03, C05·M06)."
  - q: "An LLM 'reviewer' scores clips 1–10 for quality. How do you make its score useful?"
    options: ["Trust it", "Give it a rubric with concrete checks, calibrate it against your own judgments on 20+ items, and use it next to measurable gates (tech, identity, loudness), not instead of them", "Use a bigger model", "Only use it at the end"]
    answer: 1
    explain: "An LLM judge is a classifier. Calibrate it like one (C03·M03)."
  - q: "Which system metric shows that automation is working?"
    options: ["Number of agents", "Human minutes per finished minute, together with cost per finished minute and the rejection rate per gate", "Lines of code", "GPU temperature"]
    answer: 1
    explain: "The goal is quality output with less human time and a known cost."
deeper:
  - title: "Anthropic — Building effective agents (orchestrator-workers)"
    url: https://www.anthropic.com/engineering/building-effective-agents
  - title: "Chinese industry — AI short-drama tools: one-click vs full pipeline (The Paper)"
    url: https://m.thepaper.cn/newsDetail_forward_33643563
  - title: "Zheng et al. — Judging LLM-as-a-Judge (MT-Bench and Chatbot Arena)"
    url: https://arxiv.org/abs/2306.05685
---
## Learn

### Roles and contracts
A multi-agent studio splits the work into roles. Each role has a contract: its input, its output (with a schema), and its tools.

| Role | Input | Output | Tools |
|---|---|---|---|
| Writer | brief, bible | treatment, tagged script | LLM |
| Director | script, references, look bible | shot list (JSON), prompts, routing | LLM, prompt adapters |
| Generator | approved shots | clips, prompt-log lines, sidecars | queue (M01), node-graph server (C11) |
| Editor | selects, script | timeline, versions | media functions (M02), NLE tools (C08) |
| Reviewer | any output + rubric | scores, defects, verdict | gates, vision LLM, QC scripts |

Contracts make agents replaceable. If the director agent changes model, the shot list must still pass the same schema.

### The orchestrator
The orchestrator moves each item (a script, a shot, a cut) through states: `drafted → approved → generating → generated → passed → edited → delivered`. Write it as code: a state machine with a database (the queue of M01 is one). It calls agents and tools in each step, applies the gates, retries within limits, and stops at human gates. Code gives predictable states, retries, budgets, and an audit trail. Use an LLM as the orchestrator only for open-ended tasks where the steps are unknown.

### Human gates
Place a person where decisions need judgment or responsibility:
- **Story and legal:** the treatment and the script. Real people, brands, music, claims (C16).
- **Cost:** spend above a limit (the approval step of M03).
- **Final cut:** rhythm, emotion, the story as a whole.
- **Publication:** the last check before the public sees it, including disclosure (C16·M03).
Keep human gates few and fast: a clear summary, the evidence, and a yes/no. A person who must open ten files to decide will skip the check.

### Automated gates
Every stage has a gate that returns one of three verdicts, with reasons:
- **PASS:** move on.
- **FIX:** a known, cheap fix exists (trim a frozen tail, conform the frame rate, normalize loudness). The orchestrator applies it and checks again.
- **REJECT:** regenerate (wrong identity, too short, unusable). After N rejects, the item goes to a person.

Gates per stage:
- **Script and shot list:** schema validation; durations add up; every tagged character has references.
- **Shot:** frame rate, length, black and frozen frames, identity against the references (C11·M03), logo and text checks.
- **Timeline:** no gaps, no flash frames, durations match the plan.
- **Delivery:** the full spec: format, color tags, loudness, true peak, captions (C09·M04, C10·M02); provenance signing present (C16·M03).

### LLM judges
A vision-capable LLM can score clips against a rubric ("Is the photo in her left hand? Is the room the locker room?"). Treat it as a classifier: give concrete questions, calibrate it on 20 or more items that you judged yourself, and use it next to the measurable gates, not instead of them.

### Metrics of the system
- **Cost per finished minute** (generation, compute, licenses).
- **Human minutes per finished minute**, split by gate.
- **Rejection rate per gate** (which stage wastes the most?).
- **Lead time** from brief to delivery.
Reported numbers from Chinese AI short-drama producers: about 2 hours of human time and about ¥200 per finished minute with end-to-end tools. These are claims; measure your own.

## Tool walkthrough

### The starter gate runner

```bash
cd starter/pipeline
python qc_gate.py --stage shot --item takes/S07_t04.mp4 --refs refs/CHAR-MARA/01_front.png refs/CHAR-MARA/02_34.png --json gate.json
python qc_gate.py --stage delivery --item out/film_web.mp4 --spec web_1080p
```

Exit codes: 0 = PASS, 1 = FIX, 2 = REJECT, so a shell or a workflow engine can branch on them. Edit `GATES` in the file for your project (allowed frame rates, identity threshold, black and freeze limits).

### An orchestrator step (sketch)

```python
for shot in db.items(state="generated"):
    verdict = run_gate("shot", shot.file, refs=shot.refs)       # qc_gate.py
    if verdict == "PASS":
        db.move(shot, "passed")
    elif verdict == "FIX" and shot.fix_tries < 2:
        apply_fixes(shot); shot.fix_tries += 1                  # trim, conform; then gate again
    elif shot.regen_tries < 3:
        genqueue.submit(f"{shot.id}.p{shot.prompt_v}.g{shot.gen + 1}", shot.backend, shot.inputs, cap=shot.cap)
        db.move(shot, "generating")
    else:
        db.move(shot, "needs_person")                           # with the gate reasons
```

## Worked example

**Gate test** (2026-10-04, `qc_gate.py --stage shot` with one reference photo):

| Clip | Verdict | Reasons |
|---|---|---|
| A 4 s, 24 fps shot of the right person | PASS | — |
| The same shot with a 1.5 s frozen tail | FIX | frozen picture at 2.96 s for 1.54 s |
| The same shot at 16 fps | FIX | frame rate 16.0 |
| A shot of a different person | REJECT | identity 0.145 |

The first version of the gate showed "no score" for every clip: it wrote the identity JSON to `/dev/stdout` inside a captured subprocess, which failed silently. The fix was to write to a temporary file. A gate that cannot measure must not pass: it returned REJECT, and the problem was visible at once.

**"Weekly series" system** for a product channel: 5 videos × 45 s per week.
- Writer: 5 scripts from a topic list → human gate (15 min).
- Director: shots and prompts → schema gate.
- Generator: 60 shots → shot gates: 18 % rejected (11 shots), regenerated once; 2 to a person.
- Editor: cuts and 3 versions each → delivery gates: 4 FIX (loudness), all fixed automatically.
- Human final gate: 20 min for 5 videos.
Week 1: US$38 generation, 2.5 h human time for 3.75 finished minutes: about 40 human minutes per finished minute.

## Lab

**Deliverable:** `pipelines/studio/` with an orchestrator, gates for every stage, a run of a real mini-project, and a metrics report.

1. Define the contracts (input, output schema, tools) for 5 roles.
2. Write the orchestrator as a state machine (a database table of items and states). Use the queue (M01) for generation and the gates (`qc_gate.py`, extended) for checks.
3. Put human gates at the script, at spend above your limit, and at the final cut. Make each gate a short summary with a yes/no.
4. Add one LLM-judge check with a rubric of 5 concrete questions. Calibrate it on 20 clips that you judged yourself; write its agreement rate.
5. Run a mini-project end to end: 3 videos of 30–45 s from 3 briefs.
6. Write the metrics report: cost per finished minute, human minutes per finished minute (by gate), rejection rate per gate, lead time.

**Result checklist**
- [ ] Contracts and the state machine in code.
- [ ] Gates with PASS/FIX/REJECT and limits on loops.
- [ ] LLM judge with a calibration result.
- [ ] 3 delivered videos and the metrics report.

## Model answer

**Metrics report (shape of a strong answer):**

| Metric | Value |
|---|---|
| Finished minutes | 2.1 (3 videos) |
| Generation and compute cost | US$22.40 → US$10.67 per finished minute |
| Human time | 84 min → 40 min per finished minute |
| Human time by gate | script 25 min, cost approvals 4 min, final cut 40 min, "needs person" items 15 min |
| Rejection rate | shot gate 21 % (identity 14 %, frozen tails 7 % → FIX), delivery gate 0 % REJECT, 2 FIX (loudness) |
| Lead time | brief → delivery: 1 day 3 h |

"LLM judge calibration: agreed with my judgment on 17 of 20 clips (85 %). The 3 disagreements were all 'photo in the wrong hand', which the judge missed. I keep it as a filter for the room and the wardrobe, and the hand check stays with the person at the final cut."

"The shot gate saved most time: 9 identity rejects were regenerated without me. The most expensive part was still the final cut (40 of 84 minutes), which is where it should be."
