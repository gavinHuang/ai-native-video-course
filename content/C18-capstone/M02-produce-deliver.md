---
title: Produce, deliver, document, and assess
hours: 70
outcomes:
  - Run the full production through your pipeline.
  - Deliver all files to specification with QC reports and provenance.
  - Write a technical write-up with evaluation data and costs.
  - Assess the result with the rubric and plan improvements.
keywords: [deliverables, technical write-up, rubric, showreel]
summary: >
  Produce the film and the series with your pipeline. Keep the logs. Deliver masters, platform files, stems,
  captions, and signed provenance. Write a technical report: model choices with test data, pipeline diagram, costs,
  usable rates, human time, problems, and fixes. Assess yourself with the rubric. Finish with a showreel and a public
  portfolio page.
diagram:
  type: layers2d
  title: Capstone rubric (each 1–4)
  rows: ["Story + direction", "Visual quality + consistency", "Sound", "Pipeline + automation", "Infrastructure + cost", "Rights + disclosure", "Write-up + evidence"]
  cols: ["4 = professional", "2 = needs work"]
  cells:
    - ["Clear hook, strong structure, intent in every shot", "Unclear story, random shots"]
    - ["No visible drift; graded as one film", "Drift, mismatched looks"]
    - ["Clean dialogue, mixed to spec, licensed music", "Noisy, levels wrong"]
    - ["Reproducible, gated, agent-assisted", "Manual, undocumented"]
    - ["Justified choices; within budget; metrics", "No cost data"]
    - ["Complete logs; C2PA; labels", "Missing records"]
    - ["Data-based decisions; honest limits", "Opinions only"]
watch:
  - title: "Vimeo — Staff Picks (search and study 3 short films)"
    url: https://vimeo.com/channels/staffpicks
    note: "Study the pacing and the credits of strong short films."
  - title: "Content Credentials — verify tool"
    url: https://contentcredentials.org/verify
    note: "Check your signed deliverables."
quiz:
  - q: "Which files together prove how the film was made?"
    options: ["The thumbnail", "The signed deliverables (C2PA), the prompt log, the rights log, and the consent records", "The MP3", "The title card"]
    answer: 1
    explain: "The provenance package (C16). The signature proves the file; the logs prove the origin of every asset."
  - q: "Halfway through production, you have spent 60 % of the budget with 40 % of the shots done. What do you do?"
    options: ["Continue and hope", "Record a decision: find the route with the low usable rate, then change it, shorten or merge shots, or move shots to a cheaper route; update the plan version and the risk register", "Stop the project", "Raise the cap silently"]
    answer: 1
    explain: "Change the plan by recorded decisions. The weekly review exists to catch this early."
  - q: "capstone_check.py says 'content credentials Valid (test certificate)' and fails. Why?"
    options: ["The file is fake", "The signature is valid, but the c2patool sample certificate is not trusted; a real delivery needs a certificate from a trusted issuer (use --allow-test-cert only for practice)", "The tool is wrong", "The video is too short"]
    answer: 1
    explain: "The same rule as the delivery gate in C16·M03."
  - q: "What makes a technical write-up strong?"
    options: ["Length", "Decisions backed by your own data (usable rates, costs, human time, test reports), with the problems, the fixes, and honest limits", "Screenshots only", "A list of model names"]
    answer: 1
    explain: "Evidence over claims. A reader must be able to check every number in your logs."
  - q: "Your self-score is 4 on every row; a peer gives 2 on Sound. What do you do?"
    options: ["Ignore the peer", "Find the evidence: re-run the loudness checks, listen with the peer at the timecodes they name, then fix it or explain why the score stands", "Average the scores", "Remove the Sound row"]
    answer: 1
    explain: "A score needs evidence (timecodes, reports). Disagreement shows where to look."
  - q: "Rubric 'Pipeline + automation: 4' requires:"
    options: ["Any tools", "A pipeline in a tagged repository that reproduces a shot with one command, with gates and agent-assisted stages", "One big prompt", "A manual export"]
    answer: 1
    explain: "The C11–C13 standard. The README must reproduce one shot."
  - q: "What goes on the showreel?"
    options: ["Everything", "The best 30–90 s, the strongest first, with a disclosure in the credits and a link to the write-up", "Only the credits", "Raw generations"]
    answer: 1
    explain: "Quality over quantity. Viewers decide in the first 10 seconds."
deeper:
  - title: "Netflix Partner Help Center — delivery specifications (a reference standard)"
    url: https://partnerhelp.netflixstudios.com/
  - title: "GitHub Pages — publish your portfolio"
    url: https://pages.github.com/
---
## Learn

### Production
Follow the plan (M01). Use the pipeline; do not bypass it for "just one quick shot", because that shot then has no log. Work in this order:
1. **Adapters and references first:** train and test the character LoRAs; lock the bible.
2. **Key frames and the animatic:** check story and timing before you generate motion.
3. **Generation in the background:** the queue runs routes with caps while you review.
4. **Selects and the edit:** score takes, build the timeline from selects, lock the picture.
5. **Sound:** dialogue clean-up, music, effects, mix to the spec; stems and M&E.
6. **Finishing:** grade as one film, conform, captions, localization or variants.
7. **Delivery:** encode, QC, sign last, verify.

### The weekly review
Every week, in 30 minutes: spend against budget per route; usable rate per route; shots done against plan; the risk register (re-score, close, add); and decisions. Write each decision with a date and a reason, and change the plan version. Silent changes make the write-up impossible.

### Deliverables
- The film master (ProRes 422 HQ or better) and the platform versions.
- The series (and variants or languages as the brief requires).
- Stems (dialogue, music, effects) and an M&E mix.
- Captions per language (SRT or VTT).
- QC reports: spec checks pass for every file.
- Signed provenance (C2PA, signed last) with the prompt log, the rights log, and the consent records.
- The pipeline repository, tagged, with a README that reproduces one shot.

### The technical write-up (8–12 pages)
1. Brief and approach.
2. Pipeline: the diagram and its components.
3. Model choices with test data.
4. Costs: planned against actual; cost per usable second; cost per finished minute.
5. Human time per stage.
6. Problems and fixes.
7. Rights and disclosure.
8. What you would change.
Every number must come from a log or a report that is in the repository.

### Assessment
Score each rubric row from 1 to 4, with evidence: timecodes, reports, log lines. Ask one peer to score blind to your scores. Where the scores differ by 2 or more, look at the evidence together. Write 3 improvements, each with the change you would make in the plan or the pipeline.

### Common problems in the last week
- **A late model change:** a route changes behavior or price near the end. Do not re-generate approved shots; finish with what you have, and record it.
- **Credentials lost:** a file was re-encoded after signing. Sign again, as the last step.
- **Loudness off by one platform:** each platform file needs its own measurement; do not copy the master's numbers.
- **Missing captions for a variant:** captions are made per cut, not per project.
Plan the last week for checks and fixes only, not for new shots.

### Credits and disclosure
List the human roles (writing, direction, editing, sound) and the kinds of AI tools used, with a clear disclosure line (C16·M03). Credit consenting people and licensed music as their licenses require.

### Showreel and portfolio
Cut 30–90 s of your best work, the strongest first. Put the disclosure in the credits. Publish a portfolio page with the film, the showreel, the write-up, and the repository link.

## Tool walkthrough

### Check the package

```bash
cp starter/templates/capstone/delivery.json starter/templates/capstone/rubric_scores.json capstone/
python starter/tools/capstone_check.py capstone/delivery.json            # a real delivery: studio certificate
python starter/tools/capstone_check.py capstone/delivery.json --allow-test-cert   # practice only
```

The tool checks the plan parts, runs `spec_check.py` on every file against its spec, verifies the C2PA credentials (set `C2PATOOL` if c2patool is not on PATH), counts caption cues and log lines, checks the write-up sections and the number of measured values, and checks the rubric scores. It proves completeness, not quality.

### The other gates
`pipeline/qc_gate.py` (C12·M04) for every shot, `tools/rights_audit.py` (C16·M01) before delivery, and `tools/provenance.py gate` (C16·M03) per file.

## Worked example

**Capstone check on a practice package** (2026-10-04; a 6 s signed test film, the web spec, sample logs):

First run:
```
Visual quality + consistency
  ok   deliver/film_web.mp4: 19/19 spec checks
Sound
  FAIL captions deliver/film.de.srt: missing
  FAIL stem deliver/stems/FX.wav
Rights + disclosure
  FAIL deliver/film_web.mp4: content credentials Valid (test certificate), source ['trainedAlgorithmicMedia']
Write-up + evidence
  FAIL write-up: 25 words; missing sections: ['change']
  FAIL write-up: 3 measured values (want 10 or more)
  FAIL rubric scores (self): 1/7 rows
  FAIL rubric scores (peer): 0/7 rows
  FAIL improvements: 1 (want 3)
13/21 checks pass -> NOT READY
```

After adding the German captions, the effects stem, the missing write-up section with measured values, and both rubric scores: 20/21 (only the test certificate fails); with `--allow-test-cert`: 21/21, READY. A real delivery signs with the studio certificate.

**Brief B results (example):** film 4:10; series 5 × 45 s; budget US$148 against a cap of US$165; usable rate 41 % overall (dialogue 52 %, wides 33 %); human time 58 h; cost per finished minute about US$19 (US$148 ÷ 7.9 finished minutes: 250 s of film and 225 s of series). Self-score 4, 3, 4, 4, 4, 4, 3; peer score 4, 3, 3, 4, 4, 4, 3 (Sound: room tone changes at 2:12 and 3:05; fixed). Improvements: a better LoRA for Leo's wardrobe; sound design earlier; more reaction coverage.

## Lab

**Deliverable:** `capstone/` with all deliverables, the write-up, the rubric scores, the showreel, and the portfolio page.

1. Produce through the pipeline, with weekly reviews and recorded decisions.
2. Deliver all files; run the QC gates and the rights audit.
3. Sign every delivery file last, with a trusted certificate if you have one; verify.
4. Write the technical write-up.
5. Self-assess and peer-assess with evidence; write 3 improvements.
6. Run `capstone_check.py` until it reports READY.
7. Publish the showreel and the portfolio page.

**Result checklist**
- [ ] All deliverables pass QC.
- [ ] Provenance verified for every delivery file.
- [ ] Write-up complete, with numbers from the logs.
- [ ] Self and peer scores with evidence, and 3 improvements.
- [ ] `capstone_check.py`: READY.
- [ ] Showreel and portfolio online.

## Model answer

**Write-up extract: costs (shape of a strong answer):**

| Route | Planned generated s | Actual | Planned cost | Actual | Usable rate (plan / actual) |
|---|---|---|---|---|---|
| Dialogue | 465 | 512 | US$46 | US$51 | 52 % / 47 % |
| Inserts | 403 | 380 | US$4 | US$4 | 45 % / 48 % |
| Wides | 550 | 690 | US$49 | US$62 | 33 % / 26 % |

"Wides went over the plan: night exteriors had a 26 % usable rate. Decision on 2026-11-03 (plan v1.2): 4 wides were replaced by 2 inserts and 1 3D-layout shot. Video total US$117 against US$100 planned; project total US$148, within the cap of US$165. Human time 58 h: selects 14 h, edit 12 h, mix 11 h, finishing 9 h, other 12 h. Next time I would test the night-exterior route on 30 clips before planning (C17·M02)."

A professional capstone looks like one piece (no visible model switching), sounds clean, and is fully documented. The write-up reads like an engineering report: decisions, real numbers, and honest limits.
