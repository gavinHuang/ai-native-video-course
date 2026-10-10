---
title: Lip sync, avatars, and dubbing
hours: 12
outcomes:
  - Lip-sync generated or real faces to new dialogue, and know when lip sync fails.
  - Make a talking-avatar video from a script, with consent and a clear disclosure.
  - Run a dubbing pipeline - transcribe, adapt, voice, fit, lip sync, review - with files at each step.
  - Check dubbing quality with measurements (fit, transcript errors) and a human review.
keywords: [lip sync, avatar, dubbing, localization]
summary: >
  Lip-sync models change the mouth movement of a face to match new audio. Avatar tools make a talking person from a
  script. Dubbing tools translate speech, keep the speaker's voice, and re-sync the lips. A dubbing pipeline has
  clear steps: transcribe with word timestamps, adapt the translation to the time slots, voice it, check the fit,
  lip-sync the speaker shots, and review. Measure what you can: transcript errors, line fit, and lip sync on
  frontal shots. A fluent human must review meaning and tone.
diagram:
  type: flow
  title: Dubbing pipeline
  nodes: ["Separate the voice stem", "Transcribe: words + timestamps", "Adapt translation to slot lengths", "Voice: cloned (consent) or chosen TTS", "Fit check + lip sync speaker shots", "Mix over M&E; fluent review"]
  highlight: [2, 4]
watch:
  - title: "HeyGen — Best AI dubbing tools 2026 (vendor comparison, read critically)"
    url: https://www.heygen.com/blog/best-ai-dubbing-tools
    note: "Note the test criteria. Compare them with the QC checklist of this module."
  - title: "Wav2Lip — research code of an early lip-sync model"
    url: https://github.com/Rudrabha/Wav2Lip
    note: "Look at the examples. Modern tools are much better, but the idea is the same."
quiz:
  - q: "Which shots of a dubbed video need lip sync?"
    options: ["All shots", "Shots where the speaker's mouth is visible and readable: frontal and three-quarter close shots; B-roll, wide shots, and backs of heads need none", "Only the first shot", "None; viewers do not look at lips"]
    answer: 1
    explain: "Lip sync costs time and can add artifacts. Apply it where the mouth is readable."
  - q: "Your transcript of a noisy clip has many wrong words. What do you do first?"
    options: ["Use a smaller model", "Split the voice from music and effects (a stem), and transcribe the voice stem with a larger model and a prompt that lists names and terms", "Translate anyway", "Speed up the audio"]
    answer: 1
    explain: "In the module test, at 0 dB signal-to-noise ratio the small model had 0 % word errors and the base model 25 %. Clean input and a larger model reduce errors."
  - q: "A translated line is 58 % longer than its slot. What is the correct fix?"
    options: ["Speed it up 58 %", "Adapt the translation: keep the meaning in fewer words, using a character limit from the slot length and the speaking rate", "Move the cut", "Drop the line"]
    answer: 1
    explain: "Dubbing translation is adaptation, not word-for-word translation. Give the translator (human or LLM) a character limit per line."
  - q: "How do you compute a character limit for a dub line?"
    options: ["Same as the original", "Slot length × the measured speaking rate of the target voice in characters per second, minus a small margin", "Always 42", "Ask the voice model"]
    answer: 1
    explain: "Example: a 2.8 s slot at 14 characters per second gives about 39 characters, so aim for 35."
  - q: "Why do you dub over the voice stem only and keep the M&E (music and effects) track?"
    options: ["It is faster", "The new voice replaces only the speech; music, effects, and ambience stay the same in every language", "Platforms require it", "It saves storage"]
    answer: 1
    explain: "An M&E track is the standard delivery for dubbing (C10·M02). Without it, the dub would need a new mix of everything."
  - q: "A back-translation by a second LLM says the Spanish dub is correct. Is the review done?"
    options: ["Yes", "No: back-translation finds missing meaning, but it misses tone, register, and unnatural phrasing; a fluent human must review", "Yes, if two LLMs agree", "Only for Japanese"]
    answer: 1
    explain: "Machine checks are a filter. A fluent person decides whether it sounds natural and right for the audience."
  - q: "You make a talking avatar of a real employee for a training video. What must you have?"
    options: ["Nothing", "The person's documented consent for this use, and a clear AI disclosure in the video and its description", "Only the vendor account", "A watermark only"]
    answer: 1
    explain: "Likeness and voice need consent (C16·M02). Viewers must know that the person is synthetic (C16·M03)."
deeper:
  - title: "Prajwal et al. (2020) — A Lip Sync Expert Is All You Need (Wav2Lip)"
    url: https://arxiv.org/abs/2008.10010
  - title: "faster-whisper — Whisper transcription with CTranslate2 (GitHub)"
    url: https://github.com/SYSTRAN/faster-whisper
  - title: "Radford et al. — Robust Speech Recognition via Large-Scale Weak Supervision (Whisper)"
    url: https://arxiv.org/abs/2212.04356
---
## Learn

### Lip sync
A lip-sync model takes a video and an audio track and changes the mouth region so that it matches the audio. It works best when:
- the face is frontal or three-quarter, and large enough in the frame;
- the light is good, and nothing covers the mouth (hands, a microphone, a cup);
- the head does not turn fast.
It fails at profiles, at fast head turns, and with teeth or tongue detail at high resolution. Joint audio-video models (C05·M04) and audio-to-video models (C11·M03) already make synced lips. Use separate lip sync for new lines in existing shots, and for dubbing.

Apply lip sync only where the mouth is readable. Wide shots, B-roll, and the backs of heads need none. Each lip-synced shot is a chance for an artifact, so check every one at full size.

### Avatars
An avatar tool makes a talking person from a script and a voice: a presenter for training, explainers, or localized product videos. Two rules:
1. **Consent** for any real person whose face or voice the avatar uses (C16·M02).
2. **Disclosure:** the video and its description say that the presenter is AI-generated (C16·M03).

### The dubbing pipeline
Build dubbing as a pipeline with a file at each step. Then you can check and repeat each step:
1. **Separate the voice** from music and effects (stems, C05·M04). You get a voice stem and an M&E stem.
2. **Transcribe** the voice stem with word timestamps. Separate speakers. Fix names and terms.
3. **Adapt the translation.** Keep the meaning and fit the time. Each line has a slot (start and end) from the transcript. Give the translator a character limit for each line: slot length × the speaking rate of the target voice, minus a margin. Keep a glossary of names and product terms.
4. **Voice** the lines: a cloned voice of the speaker (with consent), or a chosen TTS voice. Use duration control if the model has it.
5. **Check the fit** of each line against its slot (M01). Re-take or re-adapt lines that do not fit.
6. **Lip-sync** the speaker shots.
7. **Mix** the new voice over the M&E stem (C10).
8. **Review:** a fluent person checks meaning, tone, and naturalness. You check the fit, the lips, the voice, and the mix.

### Transcription quality
Transcription models are very good on clean speech, and they fail in noise. Larger models are more robust. Two rules help most:
- Transcribe the separated voice stem, not the full mix.
- Give the model the names and terms in a prompt ("Mara, Leo, locker room").
Read every transcript. Names, numbers, and product terms are the most common errors. Words with low confidence are where to look first.

### Why translation is adaptation
Most languages need more syllables than English for the same meaning. Spanish, German, and French lines are often 15–30 % longer. A word-for-word translation does not fit the slots. Ask for an adapted translation with a character limit per line. An LLM can do this well if you give it the limits, the context of the scene, and the glossary. A fluent human must still review it.

### Measurable QC
| Check | Method | Pass |
|---|---|---|
| Transcript | Read it; correct names and terms | No errors in names, numbers, terms |
| Fit | `fit_check.py` per line | ≤ 10 % longer, ≤ 25 % shorter |
| Meaning | Fluent reviewer (back-translation as a first filter) | No meaning errors |
| Tone | Fluent reviewer | Natural for the audience |
| Lips | Watch every lip-synced shot at full size | No visible mismatch on frontal shots |
| Voice | Listen across the video | Same voice for each speaker |
| Mix | Dub over M&E; loudness check (C10·M02) | M&E unchanged; loudness on target |

## Tool walkthrough

### Transcribe with word timestamps

```bash
pip install faster-whisper
python starter/tools/stems.py demo.mp4 --out stems/
python starter/tools/transcribe.py stems/demo_dialogue.wav --model small --lang en \
  --prompt "Mara, Leo, locker room" --out tr/
# -> tr/demo_dialogue.json (segments, words), tr/demo_dialogue.srt, tr/demo_dialogue.slots.json
```

The `slots.json` file has one entry per line with its start and end. Add a `text_target` field with the translated line, then check the target voice with `fit_check.py`.

### Adaptation prompt for an LLM

```text
Translate each line into Spanish (Spain) for a dub. Keep the meaning and the tone (a tired nurse, quiet,
night). Each line has a character limit; never go over it. Use the glossary: "locker" = "taquilla".
Return JSON: [{"id": "L01", "text_target": "...", "chars": N}].
Lines: [{"id": "L01", "text": "Every photo showed tomorrow.", "max_chars": 21}, ...]
```

### Tools (as of 2026-10)
- **Hosted dubbing and avatars:** ElevenLabs (dubbing, Avatars), HeyGen (Avatar IV, lip-synced dubbing in 175+ languages), Synthesia.
- **Open:** Whisper models (faster-whisper) for transcripts; IndexTTS-2 for duration-controlled voice; lip sync with LTX-2.3 audio-to-video (starter workflow `07`) or community lip-sync models in ComfyUI.

## Worked example

**Transcription test** (2026-10-04, faster-whisper, CPU, int8). A synthetic voice line of 18 words, with speech-shaped noise added at 4 signal-to-noise ratios. Word error rate (WER):

| Signal-to-noise ratio | tiny | base | small |
|---|---|---|---|
| +10 dB | 0 % | 0 % | 0 % |
| 0 dB | 15 % | 25 % | 0 % |
| −5 dB | 100 % | 115 % | 30 % |
| −10 dB | 100 % | 100 % | 100 % |

On clean speech all sizes were perfect (0 %, also with a music bed under the voice). In noise, the small model was much more robust. Above 100 % means the model wrote more wrong words than the line had. Real dialogue has accents, overlaps, and room sound, so test on your own material.

**Product demo, 90 s, English → Spanish, German, Japanese:**
1. Stems; transcript of the voice stem with word timestamps (small model). Two terms corrected by hand.
2. Slot limits from the timing: 14 characters per second for the target voices, minus 10 %.
3. LLM adaptation with the limits and the glossary. 3 of 24 Japanese lines over the limit → re-adapted.
4. Voice: the presenter's cloned voice (consent on file), duration-controlled.
5. `fit_check.py`: Spanish 24 of 24, German 22 of 24 (two re-takes), Japanese 24 of 24.
6. Lip sync on 6 speaker shots; the B-roll needs none.
7. Fluent review: German line 7 too formal ("Sie" → "du" for this brand); the product term in line 12 wrong → glossary fixed.

## Lab

**Deliverable:** `C06/M02/` with a 60 s video in 2 extra languages, the files of each pipeline step, and a QC report.

1. Record or generate a 60 s talking video (you, or a person who consents).
2. Separate the voice. Transcribe it with `transcribe.py`. Correct the transcript.
3. Compute character limits per line. Adapt the translation to 2 languages, with a glossary.
4. Voice the lines. Check each language with `fit_check.py` until all lines fit.
5. Lip-sync the speaker shots. Mix the new voice over the M&E stem.
6. Get a fluent review (a person; use back-translation only as a first filter).
7. Fill in the QC table for both languages.

**Result checklist**
- [ ] Every step has a file: stems, transcript JSON, adapted lines JSON, voice files, fit reports, final videos.
- [ ] All lines fit in both languages.
- [ ] QC table with the problems found and fixed.
- [ ] Consent and disclosure recorded.

## Model answer

**QC report (shape of a strong answer):**

| Check | Spanish | German |
|---|---|---|
| Transcript | 2 corrections (product name, "24 hours" heard as "20 hours") | same transcript |
| Fit (`fit_check.py`) | 21 of 24 first pass → 24 of 24 after 3 re-adaptations | 19 of 24 → 24 of 24 (3 re-adaptations, 2 re-takes) |
| Meaning (fluent reviewer) | 1 error: "taquilla" vs "casillero" (regional word; we chose Spain) | 0 errors |
| Tone | natural | line 7 too formal → changed |
| Lips (6 shots) | 5 good; 1 profile shot with a visible mismatch → recut to a reaction | 6 good |
| Mix | over M&E; −14 LUFS | same |

"Back-translation found 0 problems in German. The fluent reviewer found the formality problem and one unnatural phrase. Machine checks are a filter, not a review."

The folder has a file for each step, so a client change (a new product name) reruns only the steps from the transcript on.
