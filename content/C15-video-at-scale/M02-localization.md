---
title: Localization pipeline at scale
hours: 12
outcomes:
  - Prepare a master for localization - M&E stem, clean transcript with slots, text layers, glossary, style guides.
  - Automate translation, voice, fit check, mix over M&E, loudness, captions, and on-screen text per language.
  - Route review by risk, and send lines that do not fit back to adaptation, not to a faster voice.
  - Report cost, turnaround, and error rates per language.
keywords: [localization, M&E, glossary, style guide, risk-based review]
summary: >
  Localization at scale is the dubbing pipeline of C06·M02 run for many languages at once. It starts with a master
  made for it: a complete M&E stem, a corrected transcript with time slots, text kept as separate layers, a glossary,
  and a style guide per language. Each language then runs the same automated steps: adapt the lines to their slots,
  voice them, check the fit, mix them over the M&E, normalize, add captions and on-screen text. Review effort follows
  risk: regulated claims get a full human review, social clips automated checks and a sample.
diagram:
  type: flow
  title: One master, many languages
  nodes: ["Master kit: M&E, transcript slots, text layers, glossary", "Adapt lines to slot limits (per language)", "Voice + fit check (re-adapt lines that do not fit)", "Mix over M&E; normalize; captions; on-screen text", "Review by risk level", "Report: cost, time, errors per language"]
  highlight: [0, 2]
watch:
  - title: "HeyGen vs ElevenLabs vs Rask vs Dubverse — dubbing compared (2026, vendor blog)"
    url: https://www.heygen.com/blog/heygen-vs-elevenlabs-vs-rask-ai-vs-dubverse
    note: "Note the criteria; plan your own QC tests."
  - title: "W3C — WebVTT captions format"
    url: https://www.w3.org/TR/webvtt1/
    note: "Reference for caption files."
quiz:
  - q: "Which master deliverable makes localization possible without a new mix of everything?"
    options: ["The final mix", "A complete M&E stem (music and effects, no dialogue), so each language adds only its voice", "The proxy", "The EDL"]
    answer: 1
    explain: "Effects that were only in the dialogue recording must be moved to the M&E before localization (C10·M02)."
  - q: "On-screen text was burned into the master. What does that cost in localization?"
    options: ["Nothing", "Each language needs the text removed and replaced by compositing; keeping text as separate layers in the master avoids it", "Only a new caption file", "A new voice"]
    answer: 1
    explain: "Plan for localization in the edit: text as graphics layers, with a list of text and timecodes."
  - q: "The Spanish version of L03 is 70 % longer than its slot. The pipeline speeds lines up by at most 10 %. What happens to L03?"
    options: ["It is sped up 70 %", "It is marked 'does not fit' and goes back to adaptation for a shorter translation", "It is cut off", "It is dropped"]
    answer: 1
    explain: "In the module test, L03 did not fit in Spanish (+70 %) or German (+31 %); both were listed for re-adaptation."
  - q: "Which content needs a full review by a fluent human?"
    options: ["Every social clip", "High-risk content: legal, medical, financial claims, safety instructions, and regulated markets", "Nothing", "Only the first language"]
    answer: 1
    explain: "Review effort should follow the cost of an error."
  - q: "What belongs in a style guide per language?"
    options: ["The font only", "Formality (for example du/Sie), units, date and number formats, how to treat brand names and English terms, and caption rules", "The music", "The voice ID only"]
    answer: 1
    explain: "A style guide turns many small decisions into rules that translators and LLMs can follow."
  - q: "Why measure the loudness of every language version?"
    options: ["It is the same", "Different voices and line lengths change the mix; each version must meet the delivery target on its own", "Only for broadcast", "For the captions"]
    answer: 1
    explain: "In the module test, both versions were normalized to −14.0 LUFS after the voice was mixed over the M&E."
  - q: "Which metric shows that the pipeline is getting better?"
    options: ["The number of languages", "Errors found in review per language and the re-work rate, next to cost and turnaround", "File size", "The number of agents"]
    answer: 1
    explain: "Track what review finds. Each recurring error becomes a glossary entry, a style-guide rule, or a gate."
deeper:
  - title: "W3C — Timed Text Markup Language (TTML)"
    url: https://www.w3.org/TR/ttml2/
  - title: "Netflix — timed text style guides (Partner Help Center)"
    url: https://partnerhelp.netflixstudios.com/
  - title: "Unicode CLDR — locale data (dates, numbers, units by language)"
    url: https://cldr.unicode.org/
---
## Learn

### Localization starts in the master
A video that was not made for localization is expensive to localize. Make the master kit at the end of every project:
- **M&E stem:** music and effects, complete, with no dialogue (C10·M02).
- **Transcript with slots:** the corrected dialogue with start and end times per line (C06·M02).
- **Text layers:** on-screen text as separate graphics, with a list of every text and its timecode.
- **Glossary:** names, product terms, and phrases that must not be translated or must be translated one way.
- **Style guide per language:** formality, units, date and number formats, brand names, caption rules.

### The steps per language
1. **Adapt** each line to its slot (C06·M02): a character limit from the slot length and the speaking rate of the target voice, the glossary, the style guide, and the scene context. An LLM can do it; a fluent person reviews it.
2. **Voice** each line: a cloned voice with consent, or a chosen voice per language.
3. **Check the fit:** up to about 10 % too long can be sped up; more must go back to step 1. A faster voice is the wrong fix.
4. **Mix** every line at its slot start over the M&E.
5. **Normalize** the mix to the delivery target (C10·M02).
6. **Lip sync** the speaker shots where the mouth is readable (C06·M02).
7. **Captions** in the language, timed to the slots, following the style guide.
8. **On-screen text:** replace the text layers; re-render.
9. **Gates:** spec, loudness, captions, and fit (C12·M04).

### Review by risk
| Risk | Examples | Review |
|---|---|---|
| High | legal, medical, financial claims; safety; regulated markets | fluent human, full review |
| Medium | brand ads, product explainers | fluent human spot check + automated checks |
| Low | social clips, internal content | automated checks + a back-translation sample |

### Lines that do not fit
A line that is too long for its slot has three fixes, in this order:
1. **Adapt** the line again with the limit and the reason ("+70 % against a 3.0 s slot; at most 42 characters"). Most lines fit after one round.
2. **Open the slot:** if the picture allows it, extend the shot or move the next line later in the edit (a small change in the master edit, applied to all languages).
3. **Split** the line across a cut, if the speaker is off screen.
A voice that is sped up by more than about 10 % sounds wrong in every language. Do not use it as a fix.

### On-screen text and right-to-left languages
Text layers must be checked in every language: longer words (German), different scripts (Japanese, Chinese), and right-to-left layout (Arabic, Hebrew), which can also change the direction of graphics and lower-thirds. Plan the text boxes with room for about 30 % longer text.

### Scale effects
At 10–20 languages, small errors repeat. Every error that review finds should become a rule: a glossary entry, a style-guide line, or a gate. Measure per language: cost, turnaround, errors found in review, and the re-work rate.

## Tool walkthrough

### The starter localization script

```bash
python starter/pipeline/localize.py --video master.mp4 --me me.wav --lines lines.json --langs es,de --out loc/
```

`lines.json` holds each line's slot and its adapted translations (from `transcribe.py` and your adaptation step). The default voice backend is the macOS system voices, for timing drafts only. For deliveries, use `--tts cmd --tts-cmd '...'` with your voice service. Per language the script writes the video, an SRT file, and `report.json` with the fit of every line and the loudness.

### Tools (as of 2026-10)
Hosted dubbing (ElevenLabs, HeyGen, Rask, and others) does the whole chain in one product. Use the same QC on their output: fit, terms, tone, lips, loudness.

## Worked example

**Localization test** (2026-10-04): an 8 s master, an M&E stem, and 3 lines with adapted translations in Spanish and German. System voices; the run took 4.6 s for both languages.

| Line | Slot | Spanish speech | Fit | German speech | Fit |
|---|---|---|---|---|---|
| L01 "Every photo showed tomorrow." | 1.8 s | 1.68 s | −7 % ✓ | 1.97 s | +10 % ✓ (sped up to fit) |
| L02 "Except mine." | 1.0 s | 0.86 s | −14 % ✓ | 0.84 s | −16 % ✓ |
| L03 "I took this photo an hour ago, and now it is real." | 3.0 s | 5.09 s | +70 % ✗ | 3.92 s | +31 % ✗ |

Both versions: 2 of 3 lines fit; the mix over the M&E normalized to −14.0 LUFS (true peak −1.8 dBTP in Spanish, −1.0 in German); an 8.0 s MP4 with H.264 and AAC; captions in each language. The Spanish L03 had been translated with extra words ("…completamente real, aquí mismo, en esta habitación"); the report sends it back to adaptation with its slot.

**Explainer (3 min) → 12 languages:** about 2 hours of compute, about US$15–25 per language in API costs (example rates); 4 high-risk languages (regulated markets) with a full human review; turnaround 2 days instead of 3 weeks.

## Lab

**Deliverable:** `C15/M02/` with the master kit, 3 language versions, reports per language, and a pipeline report.

1. Make the master kit for one finished piece: M&E (check it plays with no gaps), transcript slots, text layers and their list, glossary, style guides for 3 languages.
2. Adapt the lines for 3 languages with slot limits. Review them (a fluent person for at least one language).
3. Run the pipeline (the starter script or your own). Re-adapt every line that does not fit until all fit.
4. Replace the on-screen text in every language.
5. Assign a risk level and do the matching review. Record every error found.
6. Report per language: cost, time, errors, re-work.

**Result checklist**
- [ ] Master kit complete.
- [ ] 3 language versions; all lines fit; loudness on target.
- [ ] Review records by risk level.
- [ ] Pipeline report per language.

## Model answer

**Pipeline report (shape of a strong answer):**

| Language | Risk | Lines | First fit | After re-adaptation | Review errors | Cost | Time |
|---|---|---|---|---|---|---|---|
| es-ES | medium | 24 | 21 | 24 | 1 (regional word) | US$6.10 | 40 min |
| de-DE | medium | 24 | 19 | 24 | 2 (formality, a term) | US$6.40 | 55 min |
| ja-JP | high | 24 | 22 | 24 | 3 (honorifics, a claim, a unit) | US$7.20 + 2 h review | 1 day |

"Every error became a rule: 'taquilla' in the es-ES glossary; 'du' in the de-DE style guide; units in metric with the imperial value in brackets for ja-JP captions of the product sheet. The second video in the series had 1 review error in total."
