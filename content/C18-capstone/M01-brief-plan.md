---
title: Brief, plan, and pipeline design
hours: 30
outcomes:
  - Choose a brief and write a complete production plan.
  - Design the pipeline - tools, models, routing, gates, infrastructure.
  - Build the budget, schedule, and risk register.
  - Get the plan approved at a self-review gate.
keywords: [production plan, risk register, pipeline diagram]
summary: >
  Choose one of three briefs: a brand film, a narrative short, or an explainer series. Write a production plan: the
  treatment, look bible, cast and reference library, shot list, routing table, pipeline diagram, infrastructure
  choice, budget, schedule, rights plan, and disclosure plan. List the main risks and how you will reduce them.
  Review the plan against the rubric before you start production.
diagram:
  type: flow
  title: Capstone plan contents
  nodes: ["Brief + treatment", "Look bible + references + LoRA plan", "Shot list + routing + budget", "Pipeline diagram + infrastructure", "Rights, consent, disclosure plan", "Risk register + schedule → self-review gate"]
  highlight: [5]
watch:
  - title: "StudioBinder — How to write a production schedule"
    url: https://www.studiobinder.com/blog/production-schedule/
    note: "Adapt the idea to an AI production schedule."
  - title: "Curious Refuge — AI film case studies (free start page)"
    url: https://curiousrefuge.com/start-here
    note: "Look at how AI short films are presented and credited."
quiz:
  - q: "What must the routing table in your plan be based on?"
    options: ["Opinions and launch videos", "Your own eval results and cost per usable second per shot type (C01·M07, C17·M02)", "The most expensive model", "Random choice"]
    answer: 1
    explain: "A route without your own numbers is a guess. Re-test any route that is older than 3 months."
  - q: "You need 186 s of usable dialogue. The route has a 52 % usable rate, and you generate 30 % extra length for handles. How many seconds must you generate?"
    options: ["186", "About 465 (186 × 1.3 ÷ 0.52)", "97", "1,000"]
    answer: 1
    explain: "Budget from the usable rate, not from the finished length. This is the most common budget error."
  - q: "What is a risk register?"
    options: ["A list of risks, each with likelihood, impact, an early sign, a mitigation before and a response after, an owner, and a status", "A cash register", "A list of models", "A shot list"]
    answer: 0
    explain: "Review it every week. A risk without an early sign is noticed too late."
  - q: "Which risks are most typical in AI productions?"
    options: ["Weather and permits", "Identity drift, vendor or API changes, rights gaps, and budget overrun from low usable rates", "Actor illness", "Lost tapes"]
    answer: 1
    explain: "Each has a known mitigation from the program: LoRAs and gates, backend abstraction, the rights log, and caps."
  - q: "Why a self-review gate before production?"
    options: ["Bureaucracy", "A change in the plan costs minutes; the same change after generation costs takes, money, and days", "Platforms require it", "To delay"]
    answer: 1
    explain: "The same logic as approval gates (C03·M02): fix early, where it is cheap."
  - q: "Your plan schedules 70 production hours, and generation alone needs 30 hours of queue time. What do you plan?"
    options: ["Wait for the queue", "Run generation in the background (queue and agents) while you edit, score, and mix other scenes; plan the order by dependencies", "Generate everything on the last day", "Buy a second computer"]
    answer: 1
    explain: "Human time and machine time are separate resources. The schedule must show both."
  - q: "Which test proves that the plan is complete?"
    options: ["It is long", "Another student could run the production from it without asking you questions", "It has many diagrams", "It uses the newest models"]
    answer: 1
    explain: "Use this test at the self-review gate."
deeper:
  - title: "PMI — Don't leave home without it: project risk registers"
    url: https://www.pmi.org/learning/library/project-risk-registers-anticipate-opportunities-4273
  - title: "Atlassian — risk register template and guide"
    url: https://www.atlassian.com/work-management/project-management/risk-register
---
## Learn

### Choose a brief
- **A. Brand film (2–3 min) and a series:** a launch film for a fictional product, and 5 × 30 s social variants in 2 languages.
- **B. Narrative short (3–5 min) and a series:** a short film with 2 recurring characters, and 5 × 45 s episodes of a spin-off.
- **C. Explainer (3–5 min) and a series:** a technical explainer with an avatar host, and 5 × 60 s chapter cut-downs in 3 languages.

You can write your own brief at the same level. Every brief must have at least 2 consistent characters (or 1 character and 1 product), and dialogue, native or replaced. It needs music with a clear license, and at least one controlled camera shot (a 3D layout or first and last frames). It also needs localization or variants, and full provenance. Use fictional brands and people, or people who consent in writing (C16·M02).

### The plan (one folder, seven parts)
1. **Treatment and script** (C02, C03).
2. **Look bible, reference library, and adapter plan** (C04, C14): which LoRAs, from which data, with which consent.
3. **Shot list** as JSON (C03·M04), with a shot type per shot.
4. **Routing table and budget** (C05·M06, C17·M02): a route per shot type, its usable rate and price from your own tests, and caps.
5. **Pipeline diagram** (C11–C13): stages, agents, gates, tools, the infrastructure, and what runs without you.
6. **Rights and disclosure plan** (C16): the rights log, consents, labels, and signing.
7. **Schedule and risk register.**

### Budget from usable seconds
For each route: generated seconds = used seconds × handle factor ÷ usable rate. The handle factor (about 1.2–1.3) covers the extra length that you generate and trim. Then cost = generated seconds × price per second. Add images, adapter training, voice, music plans, and storage. Add a reserve of 20–30 %, and set caps in the queue at the budget, not above it.

### The pipeline diagram
Draw every stage as a box with its input, its output, its tool, and its gate. Mark which stages run without you (queue, agents, renders) and which need your decision (selects, approvals, the mix). Mark the fallback for every hosted service, and the place where each log is written. The diagram is also the table of contents of your repository: each box points to a folder or a script.

### Schedule: human time and machine time
About 70 hours of your time are planned for production (M02). Machine time (generation, training, rendering) runs at the same time, in the background. Order the work by dependencies: adapters before character shots; locked picture before the final mix; final encode before signing. Put review gates in the schedule.

### The risk register
For each risk: likelihood and impact (1–3), an early sign, a mitigation before it happens, a response if it happens, an owner, and a status. Review it weekly. The typical AI-production risks are identity drift, vendor or API changes, rights gaps, budget overrun from low usable rates, and GPU shortage.

### The self-review gate
Before you generate a final shot, review the plan against the rubric (M02). Ask: could another student run the production from this folder without asking me? Are all routes and prices from my own tests? Does every person and asset have a rights line? Fix the weak parts, then freeze the plan as version 1 with a Git tag. Change it later only by recorded decisions.

## Tool walkthrough

### Templates

```bash
cp -r starter/templates/capstone capstone/templates      # delivery.json, rubric_scores.json, risk_register.md
```

### Budget from your own numbers
Use `starter/tools/cost_model.py` (C13·M04) for self-hosted routes and your one-day test reports (`model_trial.py`, C17·M02) for usable rates. Set the caps in `pipeline/genqueue.py` (C12·M02) to the budget per route.

### Freeze the plan

```bash
git add capstone/plan && git commit -m "Capstone plan v1" && git tag capstone-plan-v1
```

## Worked example

**Brief B: "Night Shift"** (4 min film, and 5 × 45 s spin-off episodes). Used seconds: 240 + 225 = 465 s. Handle factor 1.3. Prices are planning values from the student's own tests (use yours).

| Route (shot type) | Share | Used s | Usable rate | Generated s | Price per s | Cost |
|---|---|---|---|---|---|---|
| Dialogue: hosted joint audio-video model | 40 % | 186 | 52 % | 465 | US$0.10 | US$46 |
| Inserts: open model on a serverless GPU (US$2/h, 100 s per 5 s clip) | 30 % | 140 | 45 % | 403 | US$0.011 | US$4 |
| Wides: hosted model with 3D layout references | 30 % | 140 | 33 % | 550 | US$0.09 | US$49 |
| Video total | | 465 | | 1,418 | | US$100 |

Other costs: 2 character LoRAs (about US$6 of GPU time), about 300 key frames (US$12), the music plan (US$10), storage (US$3). Total about US$131; with a 25 % reserve, the cap is US$165.

**Risk register (top 3 of 8):** R1 identity drift on Leo (L3 × I3; early sign: identity score below 0.5; mitigation: LoRA v4 and the identity gate); R2 the wides route is removed by the vendor (L2 × I3; mitigation: a second route tested on 10 cases); R3 the dialogue usable rate falls below 40 % (L2 × I2; early sign: spend over 50 % with less than 40 % of shots done; response: shorter lines, more coverage from the inserts route).

**Pipeline:** preproduction CLI → genqueue with caps → character pipeline with the identity gate → studio MCP server → NLE timeline from selects → QC gates (spec check, loudness) → C2PA signing → capstone check.

## Lab

**Deliverable:** `capstone/plan/` with all 7 parts, a self-review note, and the tag `capstone-plan-v1`.

1. Choose a brief (or write one at the same level).
2. Write all 7 plan parts. Calculate the budget from used seconds, handle factor, and your own usable rates.
3. Write the risk register with at least 6 risks, each with an early sign (template: `templates/capstone/risk_register.md`).
4. Do the self-review: score the plan against each rubric row, and ask the "another student" question. Fix the weak parts.
5. Freeze the plan with a Git tag.

**Result checklist**
- [ ] 7 plan parts in one folder.
- [ ] Budget from usable rates, with a reserve and caps.
- [ ] Risk register with 6 or more risks and early signs.
- [ ] Self-review note and the Git tag.

## Model answer

**Self-review note (shape of a strong answer):** "Plan v1 reviewed on 2026-10-04. Story: the treatment has a clear turn at 2:40; the spin-off episodes each have one question and one answer. Routes: all 3 tested in the last month (reports in evals/runs/). Weak parts found and fixed: (1) the wides budget used the launch-page rate; replaced by our test rate of 33 %, which raised the cost from US$22 to US$49; (2) no consent line for the voice of the narrator (a friend): signed consent added, with an expiry; (3) the schedule had the final mix before the picture lock; reordered. Another student read the folder and asked one question (which LUT); the answer is now in the bible. Tagged capstone-plan-v1."

A strong plan is complete enough for someone else to run, uses budgets and routes from your own data, and has a risk register with real mitigations and early signs.
