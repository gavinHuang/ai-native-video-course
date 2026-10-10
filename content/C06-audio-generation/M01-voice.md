---
title: Synthetic voice - design, direction, cloning
hours: 14
outcomes:
  - Choose a TTS model by quality, languages, latency, license, and duration control, with a small listening test.
  - Direct a synthetic voice with context, tags, punctuation, and reference audio, and assemble clean takes.
  - Fit lines to time slots, and measure the fit.
  - Clone a voice only with documented consent, and store the consent record.
  - Make a consistent 2-minute voice-over and store the voice settings in the character bible.
keywords: [TTS, voice clone, consent, duration control, voice design]
summary: >
  Text-to-speech models now sound human. Choose a model by quality, languages, speed, license, and control, and test
  it on your own lines. Direct the voice like an actor: give context, emotion, pace, and pauses, with text tags or a
  reference recording. Many projects need each line to fit a time slot, so measure the speech length against the
  slot. A cloned voice needs documented consent from the person. Store one voice ID and its settings per character,
  and use them in every line.
diagram:
  type: flow
  title: From script line to clean voice track
  nodes: ["Line + context + slot length", "Voice: library, designed, or cloned (consent)", "Generate 2–3 takes with direction", "Fit check: speech length vs slot", "Pick and assemble in the DAW", "Store voice ID + settings in the bible"]
  highlight: [3]
watch:
  - title: "ElevenLabs — Text to Speech docs (models, voice settings, tags)"
    url: https://elevenlabs.io/docs/capabilities/text-to-speech
    note: "Read the voice settings and the expressive tags section."
  - title: "IndexTTS-2 (open source) — GitHub"
    url: https://github.com/index-tts/index-tts
    note: "Look at the duration control and emotion control examples."
quiz:
  - q: "A line must fit a 2.8 s slot in the picture. The take is 3.4 s of speech. What are your options, in order?"
    options: ["Speed it up 25 %", "Generate a new take with a faster pace or duration control; if still long, shorten the text; speed up by at most about 10 %", "Move the picture", "Accept it"]
    answer: 1
    explain: "Speech sped up more than about 10 % sounds unnatural. Direct the pace first, then edit the words. Duration control in some models targets a length directly."
  - q: "Which input helps a TTS model most to deliver a whispered, tired line?"
    options: ["Capital letters", "Context and delivery: who speaks, why, how ('a tired nurse, whispering at night'), plus a [whispers] tag if the model supports tags", "More exclamation marks", "A longer line"]
    answer: 1
    explain: "Models use the context and tags as acting notes. Punctuation also shapes pauses and pitch."
  - q: "A client asks you to clone the voice of their CEO from a conference video. The CEO is not in the email thread. What do you do?"
    options: ["Clone it; the video is public", "Ask for a signed consent record from the CEO with scope, time, and revocation, and use the vendor's verification step", "Use a voice that sounds similar", "Clone it for a test only"]
    answer: 1
    explain: "A voice clone needs the person's consent. A public video is not consent. Many vendors also require voice verification (C16·M02)."
  - q: "Why store a voice ID and the exact settings per character?"
    options: ["For billing", "The same ID and settings give the same voice in every line and episode; small setting changes can change the character", "It is required by law", "To save storage"]
    answer: 1
    explain: "Voice consistency is like visual consistency: a fixed reference, used every time."
  - q: "Your Spanish dub lines are 35–160 % longer than the English slots. What does this tell you?"
    options: ["The TTS is broken", "Spanish text is usually longer than English; the translation must be adapted to the slot length, not translated word for word", "Use a faster voice for all lines", "Slots are wrong"]
    answer: 1
    explain: "Text expands in translation. Give the translator a character limit per line from the slot length and the speaking rate (C06·M02)."
  - q: "When does an open TTS model win over a hosted one?"
    options: ["Never", "When the text or voice is private, when you need many hours at low cost, or when you need to run it inside your own infrastructure, and its quality passes your listening test", "Always", "Only for music"]
    answer: 1
    explain: "Hosted models often lead on emotional range. Open models are close on clean narration and win on privacy and cost."
  - q: "How do you compare two TTS models fairly?"
    options: ["Listen to the vendor demos", "Generate the same 10 lines of your script with both, mix the order, rate blind for naturalness, pronunciation, and emotion, and count errors", "Compare prices", "Ask a forum"]
    answer: 1
    explain: "Vendor demos are chosen examples. Your lines, rated blind, predict your project."
deeper:
  - title: "IndexTTS 2.5 technical report"
    url: https://arxiv.org/abs/2601.03888
  - title: "CosyVoice (FunAudioLLM) — GitHub"
    url: https://github.com/FunAudioLLM/CosyVoice
  - title: "ITU-R BS.1534 (MUSHRA) — a standard method for blind listening tests"
    url: https://www.itu.int/rec/R-REC-BS.1534
---
## Learn

### How modern TTS works
A current text-to-speech model takes text (and often a voice reference or a voice ID) and produces audio. Many current models work like language models: they turn the text into tokens, predict audio tokens (a compressed code of sound), and decode the tokens into a waveform. Others use diffusion or flow matching on audio features. For you, two consequences matter:
1. The model can take acting directions as text, because text is its input.
2. Each generation is a new take. The same line gives a slightly different delivery each time, like an actor.

### Choose a model
Choose by your requirements, then test:

| Requirement | What to check |
|---|---|
| Quality and emotion | Blind listening test on your own lines |
| Languages and accents | Native listeners for each language |
| Duration control | Can it target a length? (dubbing, C06·M02) |
| Latency | Streaming output for live or interactive use |
| Privacy | Can it run on your own machine? Where does the text go? |
| License | Commercial use of outputs; voice cloning terms; open-model license |

A fair test: generate the same 10 lines of your own script with each model. Mix the order. Rate each take blind for naturalness, pronunciation, and emotion (1–5). Count errors: wrong words, wrong stress, artifacts.

### Direct the voice
Direct a synthetic voice like an actor:
- **Context:** who speaks, to whom, why, and where. "A tired nurse, whispering at night in an empty locker room."
- **Tags:** many models accept delivery tags such as `[whispers]`, `[laughs]`, `[pause]`. Use them sparingly.
- **Punctuation:** a comma is a short pause, a full stop a longer one. An ellipsis (…) makes hesitation. A question mark raises the pitch at the end.
- **Reference read:** some models copy the delivery of a reference recording (a "read" by you or by a voice actor).
- **Takes:** generate 2–3 takes of each line. Pick the best. Join takes in an audio editor (DAW) at breaths or pauses.

### Fit lines to time
In video, a line often has a slot: the time between two cuts, or the time that a mouth moves on screen. Measure the fit. Speech length is the audio length without the silence at the start and the end. Compare it with the slot:
- More than about 10 % longer: generate a faster take, use duration control, or shorten the text.
- More than about 25 % shorter: add a word, or slow the pace.
- Speed changes in post: up to about 10 % sound natural. More sounds wrong.
`starter/tools/fit_check.py` measures every line of a script against its slot and reports the speaking rate in characters per second. You use the same tool for dubbing (M02) and localization (C15·M02).

### Library, designed, and cloned voices
- **Library voice:** a vendor voice. You may use it under the vendor's terms.
- **Designed voice:** made from a text description ("warm, low, 40s, slight rasp"). No real person behind it.
- **Cloned voice:** copied from a real person's recording (from about 10 s to several minutes of audio). It needs that person's documented consent. Store who consented, the scope, the time, the revocation terms, and the signature. Many vendors also require a verification step in which the person reads a text. The starter kit has a template (`templates/voice_consent.md`); a lawyer must check it for client work (C16·M02).

### Consistency across a project
Store one voice ID and its exact settings per character in the character bible (C04·M03): the model, the voice ID, the settings (for example stability and style values), and one reference line. Use them for every line. If the model version changes, test the voice again before you continue a series.

## Tool walkthrough

### Hosted and open voices (as of 2026-10)
- **Hosted:** ElevenLabs (TTS, voice design, cloning with verification, dubbing). Other hosted TTS services are in the landscape page.
- **Open:** IndexTTS-2 and 2.5 (duration control and emotion control), CosyVoice 3 (0.5B, about 4 GB VRAM, Apache 2.0), Qwen3-TTS (check its license). Fish Audio S2 weights are for research only.

### Measure the fit of a voice-over

```bash
# slots.json: one line per entry with start, end (from the edit), and text
python starter/tools/fit_check.py slots.json --audio-dir vo/
```

Name each audio file by the line ID (`vo/L01.wav`). The tool ignores silence at the start and the end.

### A quick local voice for tests
For timing tests before you pay for TTS, any system voice works. On macOS: `say -v Samantha -o vo/L01.aiff "Every photo showed tomorrow."` Do not use test voices in deliveries.

## Worked example

**Fit test** (2026-10-04, system voices, slots set from an English read):

| Line | Slot | English speech | Fit | Spanish speech | Fit |
|---|---|---|---|---|---|
| L01 "Every photo showed tomorrow." | 1.49 s | 1.56 s | +5 % ✓ | 2.35 s | +58 % ✗ |
| L02 "Except mine." | 0.85 s | 0.89 s | +5 % ✓ | 1.15 s | +35 % ✗ |
| L03 "I took this photo an hour ago…" | 2.81 s | 2.96 s | +5 % ✓ | 7.32 s | +160 % ✗ |

The Spanish L03 was a long, literal translation with extra words. The tool reports "cut about 31 characters". The fix is not a faster voice. It is a shorter translation that keeps the meaning: this is the job of M02.

**Mara's voice-over, 2 minutes:**
1. Voice design: "woman, early 30s, calm, slightly husky, tired, warm". Three candidates; candidate 2 chosen in a blind test (naturalness 4.4 / 5).
2. Line: "Every photo showed tomorrow… [pause] except mine." Take 3 chosen.
3. Settings stored in `refs/CHAR-MARA/sheet.json`: model, voice ID, stability 0.45, style 0.3, one reference line.
4. All 24 lines pass `fit_check.py` after 3 re-takes with a faster pace.

## Lab

**Deliverable:** `C06/M01/` with voice tests, a 2-minute voice-over, a fit report, and a consent record.

1. Design 3 candidate voices for one character. Rate them blind on 5 lines. Choose one with reasons.
2. Write `slots.json` for a 2-minute voice-over from your animatic (C04·M04): one entry per line with the slot from the picture.
3. Generate the voice-over with direction. Run `fit_check.py`. Re-take lines that do not fit. Assemble one clean track at 48 kHz.
4. Generate the same 30 s with one open TTS model, locally or on a rented GPU. Compare blind with the hosted take.
5. Fill in the consent template for your own voice. Clone your own voice. Compare it with the designed voice.
6. Store the voice ID and settings in your character bible. Log every kept take in the prompt log.

**Result checklist**
- [ ] 2-minute voice-over WAV at 48 kHz; all lines pass `fit_check.py`.
- [ ] Blind rating sheet for 3 candidate voices and for hosted versus open.
- [ ] A filled consent record for your own voice clone.
- [ ] Voice ID and settings in the character bible.

## Model answer

**Blind rating sheet (shape of a strong answer):**

| Voice | Naturalness | Pronunciation errors (5 lines) | Fits the character | Notes |
|---|---|---|---|---|
| A (designed, hosted) | 4.4 | 0 | 5 | Warm, slightly husky |
| B (library, hosted) | 4.1 | 0 | 3 | Too bright for a night-shift nurse |
| C (open model, local) | 3.8 | 1 ("locker" stress) | 4 | Clean; less range in the whisper |

"Chosen: A. The open model C is close on calm narration and loses on whispers. I will use C for internal drafts and A for delivery."

**Fit report:** "24 lines. First pass: 19 fit, 4 too long, 1 too short. Fixes: 3 faster takes, 1 text edit ('I took this photo an hour ago' → 'I took this an hour ago'; approved by the writer), 1 slower take. Final: 24 of 24 fit; mean speaking rate 14.2 characters per second."

The consent record names the scope ("my voice, this course project, online video, until 2027-06-30"), the revocation terms, and the vendor where the clone is stored. The rights log has a line that points to it.
