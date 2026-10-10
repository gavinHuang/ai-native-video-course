# Build progress log

Autonomous build on 2026-10-04 while the teacher was away. Goal: a complete self-paced course per PLAN.md v4.

## Result

- **Published course (private link):** https://claude.ai/artifact/DVwwZWcJVi2RT4E5QvVgR1. Share it from the page's Share menu so students can open it.
- **Offline copy:** open `site/index.html` in any browser. The `site/audio/` folder must stay next to it.
- **Size:** 18 courses, 74 modules, about 900 study hours, 319 glossary terms, 74 narration tracks (about 1 minute each), 74 generated diagrams, and 5 concept illustrations.

## Assumptions made without the teacher

1. Delivery is one single-page HTML site with audio files, plus a private artifact link.
2. Source is Markdown in `content/`. `tools/build.py` builds the site and runs structure and STE checks.
3. Narration uses macOS TTS (voice "Samantha") and is labeled as a synthetic voice. A transcript is on every page.
4. Diagrams are generated from a spec in each module (`diagram:` front matter). Illustrations come from `tools/make_figures.py`.
5. No generation API keys were available. Visual examples are therefore diagrams, illustrations, and links to vendor and official pages. Labs give exact prompts and settings, and students make the outputs.
6. Videos are curated links. Where a stable URL could not be verified, the link is a labeled YouTube search.
7. Research covered English and Chinese sources, plus posts on X. All notes are saved in English (`research/`).
8. Product names stay in labs and on the landscape page. Concept text names no tools.
9. Module counts differ slightly from PLAN.md v4. Some planned modules were merged to keep each module substantial (for example, C10 has 2 modules).

## Checks run

- Structure check: every module has all required sections, quiz answers in range, and glossary terms present. **0 problems.**
- STE check: 50 Learn-section sentences are longer than 25 words, out of about 1,560 (3%). These can be shortened later.
- Link check: 277 unique links (`docs/link-report.md`). Real 404s were replaced. The remaining "not OK" results are bot-blocking responses (403) from sites that work in a browser (Zhihu, Adobe, Medium, and others).
- Visual check: a headless Chrome screenshot at desktop and narrow widths. One Markdown list bug was found and fixed.

## Open items (recommended next)

1. Add real generated example media (images and short clips) for each generation module when API keys are available (fal.ai or Replicate, plus ElevenLabs).
2. Record screen demos for the tool-heavy labs (ComfyUI, Resolve MCP, Premiere agent).
3. Shorten the 50 long sentences. Run `.venv/bin/python tools/build.py --check`.
4. Refresh `content/landscape.md` and `research/ai-landscape-*.md` every quarter.
5. Have one test student do C01·M01 and C05·M01, and collect feedback.

## How to rebuild

```
.venv/bin/python tools/make_figures.py      # illustrations
.venv/bin/python tools/build.py --audio     # site + narration (macOS)
.venv/bin/python tools/check_links.py       # link report
```

## Review fixes, 2026-10-04 — completed

All 74 modules in 18 courses pass the build gates (`tools/build.py --check`: 0 problems): teaching text ≥ 600 words, quiz ≥ 6 scenario questions, model answer ≥ 120 words, no product names in Learn, all keywords in the glossary (376 terms). STE warning: 85 sentences over 25 words (of about 3,465), down from 103.

Rewritten in this session: C15 (M01–M03), C16 (M01–M04), C17 (M01–M03), C18 (M01–M02), and C01–C03 (quizzes, model answers, teaching text, product names moved to Tool walkthroughs).

New tested starter files: tools/model_trial.py (Fisher test checked against scipy), tools/arxiv_watch.py (live arXiv API), tools/judge_agreement.py (kappa checked against statsmodels), tools/capstone_check.py (run on a signed practice package: 13/21 → 21/21), solutions/C03-M01/shotlist.py (5 tests), solutions/C03-M05/media_mcp.py (real MCP client test), templates/studio_policy.md, templates/production_note.md, templates/capstone/, examples/. Test suites: 31 pass (pipeline + solutions).

Findings that changed lesson text: in MCP Python SDK 2.3, a tool exception reaches the model only as "Error executing tool" (lessons now say: return errors as results); 10 clips per shot type detect a 50 % vs 80 % usable-rate difference only 28 % of the time (simulation; table in C17·M02); a C18 cost-per-minute figure was wrong (US$37 → US$19) and is fixed.

Link check (tools/check_links.py now records page titles): 317 links; 4 Routledge ISBNs, a Peachpit link, a dead PDF host, a librosa path, and an unconfirmed PMI ID were fixed. Details in docs/link-report.md.

Not done: example generated media (needs API keys or a GPU). The C11 workflows pass ComfyUI server validation but were not run on a GPU.
