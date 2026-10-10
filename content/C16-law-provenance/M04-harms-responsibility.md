---
title: Harms, misuse, bias, and professional responsibility
hours: 10
outcomes:
  - Recognize deepfake harms, misinformation risks, and harassment uses, and run a risk review on a request.
  - Detect and reduce bias in generated people, voices, and stories with explicit casting and pattern reviews.
  - Estimate the energy footprint of a production's own compute, and report what vendors do not disclose.
  - Apply a written studio policy to refuse or change harmful work.
keywords: [deepfake, misinformation, bias review, energy footprint, studio policy]
summary: >
  Synthetic video can harm people: deepfakes damage reputations and enable fraud and abuse; realistic fake events
  mislead even when labeled, because labels are lost when clips are re-posted; content can target individuals.
  Models also repeat stereotypes in who appears in which roles. A professional studio decides casting on purpose,
  reviews patterns, measures its footprint, and has a written policy that says what it never makes and how it
  refuses or changes a request. A short risk review before production catches most problems.
diagram:
  type: flow
  title: Risk review of a request
  nodes: ["Real people? (consent)", "Could it be taken as real? (misinformation)", "Who could be harmed? (targets, groups)", "Bias: who is shown how?", "Decision: make / change the design / refuse", "Record the decision"]
  highlight: [1, 4]
watch:
  - title: "Partnership on AI — Responsible Practices for Synthetic Media"
    url: https://syntheticmedia.partnershiponai.org/
    note: "Read the practices for creators."
  - title: "WITNESS — synthetic media and deepfakes (resources)"
    url: https://lab.witness.org/projects/synthetic-media-and-deep-fakes/
    note: "See how human-rights groups think about synthetic media."
quiz:
  - q: "A client wants 'a viral video of a flood in our city' to raise donations. What is the main risk, and a good response?"
    options: ["None; it is for charity", "It can be taken as real news and spread without its label; change the design: a clearly illustrated style, a visible label, real data on screen, and the donation link", "Make it more realistic", "Refuse all charity work"]
    answer: 1
    explain: "Realistic fake events mislead even with a label, because clips are cut and re-posted. Change the design so the content cannot pass as real."
  - q: "Why is a visible label not enough for a realistic fake event?"
    options: ["Labels are illegal", "Re-posts, screenshots, and cuts often remove the label; the content then circulates as if real", "Labels are too small", "Platforms remove labels"]
    answer: 1
    explain: "Design for the worst re-post: a style that does not look like news footage."
  - q: "In 100 generated 'doctor' shots, 90 are men. What is the professional response?"
    options: ["Accept the model's choice", "Write the casting explicitly in the bible and the prompts, and review the pattern across outputs; models over-represent some groups in some roles", "Use fewer doctors", "Blame the model"]
    answer: 1
    explain: "Defaults are not neutral. Research documents stereotype amplification in text-to-image models."
  - q: "How do you estimate the energy of your own generation work?"
    options: ["You cannot", "GPU hours × measured power × an overhead factor (the rest of the machine and cooling), then × the grid's emission factor for CO2e", "Count the files", "Use the model size only"]
    answer: 1
    explain: "In the module example, 1,200 takes of 60 GPU seconds on a 700 W GPU: about 20 kWh; 400 takes: about 6.5 kWh."
  - q: "A hosted video API does not disclose energy per output. What do you report?"
    options: ["Invent a number", "'Not disclosed by the vendor', with the number of output seconds, so that the gap is visible", "Zero", "The price"]
    answer: 1
    explain: "Do not invent precision. Report what you know and what you do not."
  - q: "Which change lowers a production's footprint the most?"
    options: ["A smaller font", "Fewer and cheaper takes: explore at low size and few steps, generate finals only for chosen takes", "Shorter titles", "Lower audio bitrate"]
    answer: 1
    explain: "The number of generations dominates. The same workflow cuts cost and energy."
  - q: "A team member thinks a job breaks the studio policy. What does a good policy say?"
    options: ["Finish the job first", "Anyone can stop the job; a named person decides quickly; the decision and the reason are recorded; a changed design or a written refusal follows", "Ask the client to decide", "Nothing"]
    answer: 1
    explain: "A policy without a stop-and-decide process is a poster, not a policy."
deeper:
  - title: "Bianchi et al. (2023) — Easily Accessible Text-to-Image Generation Amplifies Demographic Stereotypes"
    url: https://arxiv.org/abs/2211.03759
  - title: "Luccioni et al. (2024) — Power Hungry Processing: Watts Driving the Cost of AI Deployment?"
    url: https://arxiv.org/abs/2311.16863
  - title: "The Green Grid — PUE: a comprehensive examination of the metric"
    url: https://www.thegreengrid.org/en/resources/library-and-tools/20-PUE%3A-A-Comprehensive-Examination-of-the-Metric
---
## Learn

### Harms
- **Deepfakes of real people:** reputational damage; fraud (a fake call from a CEO, a fake endorsement); non-consensual intimate content, which is a crime in many places.
- **Misinformation:** realistic fake events (disasters, crimes, statements). Even labeled content can be cut and re-posted without its label, and then it circulates as if real.
- **Harassment:** content that targets a person or a group.
- **Erosion of trust:** when anything can be faked, real evidence is doubted too. Provenance (M03) helps real content prove itself.

### The risk review
Before production, answer five questions for every request:
1. **Real people?** Is any real person shown or heard? Is there consent for this use (M02)?
2. **Could it be taken as real?** Would a viewer who sees a re-posted clip without its label believe it happened?
3. **Who could be harmed?** A person, a group, the audience (by deception)?
4. **Bias:** who is shown in which roles, and how?
5. **Decision:** make it, change the design, or refuse. Record the decision and the reason.
Changing the design is often possible: a clearly illustrated or stylized look, a visible label in the picture, real data on screen, no real names.

### Bias
Generative models learn from data that over-represents some groups in some roles and under-represents others. Research has shown that text-to-image models amplify demographic stereotypes (for example in occupations). Voices and accents can be stereotyped too. Professional practice:
- **Decide casting explicitly** in the bible and the prompts: age, gender, skin tone, body type, accent. Do not leave it to model defaults.
- **Review patterns** across many outputs: in the last 50 generated people, who appears in which roles? who is missing?
- **Review stories**, not only faces: who is the expert, who is the victim, who speaks.

### Footprint
Video generation uses far more compute than text. Estimate the energy of your own compute:
- energy (kWh) = GPU hours × average GPU power (kW) × overhead (the rest of the machine and cooling; data centers report a PUE of about 1.1–1.6);
- emissions (kg CO2e) = energy × the grid's emission factor (it varies widely by country, region, and hour).
Hosted APIs rarely disclose energy per output: report "not disclosed" with the output seconds, instead of inventing a value. The biggest lever is the number of takes: explore cheaply, and generate finals only for chosen takes (C05·M06).

### Fraud and impersonation
Voice clones and face swaps are used in fraud: a fake call from a manager asking for a payment, a fake video of a celebrity selling an investment. Do not build tools or content that make this easier: no unverified voice cloning, no realistic impersonation of real people. If you publish a voice model or an avatar service, verify consent and keep logs.

### A studio policy
Write one page and sign it as a team. It says what you never make, what needs consent or a license, and your rules for disclosure, bias review, data handling, and footprint. It also says how anyone can stop a job, how you refuse or change a request, and how you handle misuse of your content. Review it every year. The starter kit has a template (`templates/studio_policy.md`).

## Tool walkthrough

### Estimate the footprint

```bash
python starter/tools/footprint.py --takes 1200 --takes-gpu-s 60 --gpu-w 700 --grid 0.35 --finished-min 20 --api-output-s 1500
```

Measure the GPU power during a run with `nvidia-smi --query-gpu=power.draw --format=csv -lms 1000`. Take the grid factor from your grid operator or your cloud region's published data. GPU seconds per take come from your take log or the queue (C05, C12).

### The policy and the review
Copy `starter/templates/studio_policy.md`. Add the risk review (the five questions) to the brief template of C03·M02, so that every project answers it before the treatment.

## Worked example

**Footprint** (`footprint.py`, a 700 W GPU, overhead 1.4, grid 0.35 kg CO2e/kWh, 20 finished minutes):

| Practice | Takes | GPU hours | Energy | CO2e | Per finished minute |
|---|---|---|---|---|---|
| Generate every take at final quality | 1,200 | 20.0 | 19.6 kWh | 6.9 kg | 0.98 kWh |
| Explore cheaply, finals for chosen takes (about a third of the GPU time) | 400 equivalent | 6.7 | 6.5 kWh | 2.3 kg | 0.33 kWh |

1,500 s of hosted API output: "energy not disclosed by the vendor".

**The flood request.** Risk review: no real people; could be taken as real news: yes; harm: deception of the public, panic. Decision: change the design to a clearly illustrated style, a visible label "illustration of a possible flood", real flood-risk data on screen, and the donation link. The client agreed. Recorded in the project file.

**Bias review.** In a 40-shot hospital series, the first draft had 11 of 12 doctors as men in their 40s and all nurses as young women. The bible now specifies the cast of every recurring role; a review of the next 50 people showed a balanced mix that matched the story's setting.

## Lab

**Deliverable:** `C16/M04/` with your studio policy, 3 risk reviews, a bias review, and a footprint report.

1. Adapt the studio policy template to your studio. Have one other person read it and challenge one rule.
2. Write risk reviews (the five questions and the decision) for 3 requests: one from your project, and two difficult invented ones (one that you change, one that you refuse).
3. Review the last 50 generated people of your project: roles, age, gender, skin tone, accent. Write what you change in the bible.
4. Estimate the footprint of your project with `footprint.py` from your logs. Show the effect of your explore-then-finish workflow.

**Result checklist**
- [ ] Studio policy, read and challenged by one other person.
- [ ] 3 risk reviews, including a changed design and a refusal.
- [ ] Bias review with bible changes.
- [ ] Footprint report with the measured inputs.

## Model answer

**A refusal (shape of a strong answer):** "Request: a 'leaked' video of a rival company's factory with safety violations, to post anonymously. Risk review: realistic fake event about a real company; intended to be taken as real; harm to the company and its workers; deception of the public. Decision: refused under policy section 1 ('realistic fake events presented as real'). Offered instead: an explainer about safety standards with real, cited data and clearly labeled illustrations. Recorded on 2026-10-04 by the producer."

**Footprint report:** "Our project: 14.2 GPU hours (queue log) at an average of 520 W (nvidia-smi samples), overhead 1.4, grid 0.30 → 10.3 kWh, 3.1 kg CO2e, 0.52 kWh per finished minute. Hosted API output: 2,140 s, energy not disclosed. Exploring at 640 × 352 with 4-step LoRAs cut our own GPU time by about 60 % against generating every take at final settings."
