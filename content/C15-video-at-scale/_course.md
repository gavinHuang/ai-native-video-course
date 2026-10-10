---
code: C15
title: Video at Scale
level: 4
hours: 40
prereq: C12
outcomes:
  - Generate many video variants from templates and data.
  - Run a full localization pipeline at scale.
  - Publish through platform APIs with correct specs and metadata.
  - Close the loop - use analytics to improve the next generation.
---
## About this course

AI-native production is not only about one film. It makes 100 versions, 20 languages, and a weekly series possible. This course builds the systems for that, and connects them to what audiences actually watch.

**Starter code for this course** (in `pipeline/` of the [starter kit](starter.zip); tested on 2026-10-04):

| File | Use |
|---|---|
| `variants.py` | Template + data table → validated, cached variant renders with a manifest (M01) |
| `ab_report.py` | A/B result with p-value and confidence interval; sample-size planning (M01, M03) |
| `localize.py` | Voice, fit check, mix over M&E, loudness, and captions per language (M02) |
| `retention.py` | Steep drops and rewatch bumps in a retention curve, mapped to shot IDs (M03) |
