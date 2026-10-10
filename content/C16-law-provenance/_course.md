---
code: C16
title: Law, Provenance, and Trust
level: 5
hours: 40
prereq: none (recommended after L3)
outcomes:
  - Explain the copyright questions around AI training and AI outputs, and manage the risk.
  - Read and record licenses for models, outputs, music, stock, and fonts.
  - Get and store consent for likeness and voice.
  - Apply disclosure rules (EU AI Act Article 50, platform policies).
  - Add C2PA content credentials and watermarks in the pipeline.
  - Recognize harms - deepfakes, misinformation, bias - and refuse harmful work.
---
## About this course

This course is not legal advice. Laws differ by country and change fast. It gives you a working method: know the questions, keep records, follow platform rules, and ask a lawyer when the stakes are high. As of 2026-10, EU AI Act Article 50 transparency duties apply from 2026-08-02 (fines for breaches up to €15 million or 3 % of worldwide turnover, Article 99(4)).

**Starter tools for this course** (in the [starter kit](starter.zip); tested on 2026-10-04):

| Tool | Use |
|---|---|
| `tools/rights_audit.py` | Rights audit before delivery: missing rights lines, risky licenses, expired consents and adapters (M01, M02) |
| `templates/voice_consent.md` | Consent record for voice and likeness (M02) |
| `tools/provenance.py` | Sign with C2PA (c2patool), verify, and gate delivery on credentials and disclosure (M03) |
| `tools/footprint.py` | Energy and CO2e of your own GPU work (M04) |
| `templates/studio_policy.md` | A one-page studio policy (M04) |
