---
title: Music generation and licenses
hours: 12
outcomes:
  - Write a music brief with genre, tempo, key, mood, instruments, structure with times, and length.
  - Edit generated music to the cut on bar lines, and land a picture hit on a strong beat.
  - Read the license terms of every track, save a copy, and record them in the rights log.
  - Choose between generated, library, and commissioned music for a job, with reasons.
keywords: [music generation, stems, license tier, tempo]
summary: >
  Music models make full songs or instrumentals from a prompt. Give genre, tempo, key, mood, instruments, structure
  with times, and length. Generate instrumentals for most video work, and get stems if you can, so you can edit and
  mix. Cut music on bar lines and land picture hits on strong beats; a bar grid from the tempo shows where. The
  license depends on the service and the plan, and it changes; save a copy of the terms with every download. For
  brand campaigns, library or commissioned music is often the safer choice.
diagram:
  type: compare
  title: Choose the music source
  left:
    title: "Generated"
    items: ["Fits timing and mood exactly", "Fast and cheap variants", "License depends on plan and date", "Risk: similarity to existing songs"]
  right:
    title: "Library or commissioned"
    items: ["Clear, proven licenses", "Known composers and quality", "Less exact fit (edit needed)", "Commissioned: highest cost, full control"]
watch:
  - title: "Best AI music models Sept 2026 — prices and rights (TeamDay)"
    url: https://www.teamday.ai/blog/best-ai-music-models-2026
    note: "Read the license column for each plan."
  - title: "Suno vs ElevenLabs Music 2026 — v6 vs v2.5, licensing"
    url: https://undetectr.com/blog/suno-vs-elevenlabs-music
    note: "Note the download caps and the streaming rights by plan."
quiz:
  - q: "At 112 BPM in 4/4, how long is one bar?"
    options: ["1.12 s", "4 × 60 / 112 = 2.14 s", "0.54 s", "4 s"]
    answer: 1
    explain: "One beat = 60 / BPM = 0.536 s. A 4/4 bar has 4 beats: 2.14 s."
  - q: "A beat detector reports 112.3 BPM and a first beat at 0.82 s. The real downbeat is at 0.27 s. What happened?"
    options: ["The detector is broken", "It found the tempo correctly but locked onto beat 2, not the downbeat; check the downbeat by ear and set the offset", "The file is too short", "The tempo is wrong"]
    answer: 1
    explain: "Detectors find beats well and downbeats less well. They can also choose half or double tempo. Always check by ear."
  - q: "A picture hit (a door slam) is at 6.00 s; the nearest strong beat is at 6.70 s. What do you do?"
    options: ["Nothing", "Move the music (slip it 0.70 s earlier, or cut a bar) or move the picture event, so the hit lands on the beat within about 40 ms", "Speed up the video", "Add a sound effect only"]
    answer: 1
    explain: "A hit that is more than about 40 ms off the beat feels wrong. Slip the music, edit it on a bar line, or trim the picture."
  - q: "Why ask for 'instrumental, no vocals' for most video music?"
    options: ["Vocals are illegal", "Vocals compete with dialogue and voice-over, and lyrics add meaning that you did not plan", "It is cheaper", "Models cannot sing"]
    answer: 1
    explain: "Under speech, music must leave space. Vocals fill the same frequency range as the voice."
  - q: "What do you save with every downloaded generated track?"
    options: ["Only the audio", "The audio, the prompt, the track ID, the plan, the date, and a PDF copy of the terms on that date; a line in the rights log", "The invoice only", "Nothing"]
    answer: 1
    explain: "Terms change. You must be able to show which terms applied when you made and used the track."
  - q: "Your prompt says 'in the style of [famous band]'. What is the problem?"
    options: ["None", "It asks for a copy of a protected style and voice; many services block it, and outputs that sound too close to a known song are a legal risk. Describe the musical features instead", "It is too short", "The band name is misspelled"]
    answer: 1
    explain: "Describe tempo, instruments, harmony, and mood. Do not name artists. Check outputs for similarity to known songs."
  - q: "A 30 s cue ends at 31.3 s, on a bar line. The picture ends at 30.0 s. What is a clean fix?"
    options: ["Fade out over 0.5 s", "Cut one bar earlier and use the ending phrase (or generate an ending variant), so the music resolves at 30 s", "Speed up the cue 4 %", "Stop the music hard"]
    answer: 1
    explain: "Music needs a real ending. Edit on bars so the last phrase lands at the end, or make an ending variant."
deeper:
  - title: "Copet et al. (2023) — MusicGen: Simple and Controllable Music Generation"
    url: https://arxiv.org/abs/2306.05284
  - title: "ElevenLabs — Music docs"
    url: https://elevenlabs.io/docs/capabilities/music
  - title: "librosa — beat tracking documentation"
    url: https://librosa.org/doc/0.11.0/generated/librosa.beat.beat_track.html
---
## Learn

### The music brief
A music model follows a brief like a composer does. Write it with:
- **Genre and character.** Describe the musical features: "indie electronic, plucked synth, warm bass". Do not name artists. Many services block artist names, and an output that sounds too close to a known song is a legal risk.
- **Tempo** in BPM, for example 96 BPM. Tempo sets the bar length, so it sets where you can cut.
- **Key and mood:** "D minor, tense, then hopeful".
- **Instruments:** "felt piano, soft synth pad, light percussion, no vocals".
- **Structure with times:** "0–8 s intro; 8–24 s build; hit at 24 s; 24–30 s resolve".
- **Length** in seconds, and the type of ending: "clean ending on a held chord".

For most video work, ask for instrumentals. Vocals compete with dialogue, because they use the same frequency range, and lyrics add meaning that you did not plan.

### Music time
To edit music you need its grid:
- one beat = 60 / BPM seconds; at 112 BPM, 0.536 s;
- one bar of 4/4 = 4 beats; at 112 BPM, 2.14 s; at 120 BPM, exactly 2.00 s;
- the **downbeat** is beat 1 of a bar. Phrases usually last 4 or 8 bars.

A music edit sounds right when you cut on a bar line, ideally at the start of a phrase. A picture hit (a door, a cut, a title) feels right when it lands on a strong beat, within about 40 ms. `starter/tools/bars.py` makes the grid from the tempo and the first downbeat. It shows the nearest beat and bar for each picture event, and where to end the cue.

Beat detectors (in `bars.py --detect`) find the tempo well. They often choose the wrong downbeat, and sometimes half or double the tempo. Check by ear: tap along, and listen for beat 1.

### Editing to the cut
1. Place the cue so that the main hit lands on its picture event. Slip the music in time if needed.
2. Cut out bars (or whole phrases) to shorten. Cut on bar lines, with a short crossfade (10–30 ms).
3. For the end, use the music's own ending. Generate an "ending" variant if the cue has none.
4. Use stems if you have them: lower the drums under dialogue; remove the lead instrument under voice-over.

### Licenses
The license of a generated track depends on the service, the plan, and the date. Typical differences between plans: commercial use or not, streaming platforms or not, download limits, and credit requirements. Terms change often. For every track that you use:
- save the audio, the prompt, the track ID, the plan, and the date;
- save a PDF copy of the terms on that date;
- add a line to the rights log (`promptlog.py rights`).

### Choose a source
- **Generated:** best fit to timing and mood, fast variants, low cost. The license depends on the plan and can change. There is a small risk of similarity to existing music.
- **Library (stock):** clear, proven licenses and known quality. It fits less exactly, so it needs more editing.
- **Commissioned:** a composer writes for the picture. The highest cost and full control. Common for brand campaigns.
Many brand clients still require library or commissioned music. Social content and prototypes often use generated music.

## Tool walkthrough

### Services (as of 2026-10; check the current terms)
- **Suno v6** (2026-09-09): trained on licensed music (deals with WMG, BMG, Believe); downloads capped by plan.
- **ElevenLabs Music v2.5** (2026-09-11): licensed data (Merlin, Kobalt, Believe; UMG deal); the Starter plan is "commercial, no streaming"; higher plans are broader.

### Make the grid and check hits

```bash
python starter/tools/bars.py --bpm 112 --sig 4/4 --offset 0.27 --length 30           # bar lines
python starter/tools/bars.py --bpm 112 --offset 0.27 --snap 6.0,20.1                 # picture events
python starter/tools/bars.py --bpm 112 --offset 0.27 --cut-to 30                     # where to end
pip install librosa
python starter/tools/bars.py --detect cue.wav --snap 6.0,20.1                        # estimate BPM and first beat
```

### Log the track

```bash
python starter/tools/promptlog.py rights --id MUS-AD-CUE2 --source "music service, plan X, track 8f2c…" \
  --license "plan X terms 2026-10-04 (rights/terms/plan_x_2026-10-04.pdf)" --use "online ad, no broadcast" \
  --file music/cue2.wav
```

## Worked example

**Detection test** (2026-10-04, librosa). A 30 s test track with clicks at exactly 112 BPM; the first downbeat is at 0.270 s:

```
detected: 112.3 BPM, first beat at 0.824 s
```

The tempo is correct to 0.3 %. The first beat is wrong: 0.824 s is beat 2 (0.270 + 0.536 = 0.806 s). If you used the detected offset, every "bar line" would be one beat late. We set the offset by ear to 0.27 s. Then:

```
python bars.py --bpm 112 --offset 0.27 --snap 6.0,20.1
   event nearest beat  off ms nearest bar  off ms
   6.000        6.163    +163       6.699    +699  <- move the cut or the music
  20.100       20.091      -9      19.556    -544
```

The second event is 9 ms from a beat: it already feels right. The first is 163 ms early. A change before the first event moves both events, so it would break the second hit. Fix with two picture changes:
1. Extend the shot before the first event by 4 frames (167 ms at 24 fps). Event 1 moves to 6.167 s: 4 ms from the beat. Event 2 moves to 20.267 s.
2. Trim 4 frames from a shot between the two events. Event 2 moves back to 20.100 s: 9 ms from its beat.
Check again with `--snap` after every change.

**30 s ad cue:**
Prompt: "Instrumental, 112 BPM, upbeat indie electronic, plucked synth, claps, warm bass; 0–6 s sparse intro; 6–20 s build; 20 s drop on a big clap; 20–30 s full groove; clean ending at 30 s; no vocals." Three takes; take 2 chosen; stems downloaded; drums −6 dB under the voice-over. The cue ended at 31.3 s, so we cut one bar inside the groove (on a bar line, with a 20 ms crossfade). The rights-log line has the plan, the terms PDF, and the track ID.

## Lab

**Deliverable:** `C06/M03/` with 3 cues fitted to picture, `bars.py` reports, rights-log lines with terms copies, and a comparison.

1. Write briefs for 3 cues of your project: tension, light, and ending.
2. Generate each with 2 services (or 2 plans), 2–3 takes each.
3. Find the tempo and the downbeat of each chosen cue (`bars.py --detect`, then check by ear).
4. Edit each cue to your animatic or sequence: cut on bar lines, land one picture hit within 40 ms, end on the music's ending.
5. Record the license details for each track, with a PDF of the terms.
6. Compare one generated cue with one library cue for the same scene: fit, quality, license, cost, time.

**Result checklist**
- [ ] 3 cues fitted to picture; one hit within 40 ms (show the `--snap` output).
- [ ] Rights-log lines with terms PDFs.
- [ ] Generated-versus-library comparison.

## Model answer

**Fitting report (shape of a strong answer):**

| Cue | BPM (detected / checked) | Downbeat | Picture hit | Off after edit | Edits |
|---|---|---|---|---|---|
| Tension (S01–S06) | 84.1 / 84 | 0.42 s (detector chose beat 3) | Photo reveal at 3.00 s | +8 ms | slipped −0.31 s |
| Light (S07–S12) | 56 / 112 (detector halved it) | 0.10 s | Locker opens at 14.20 s | −12 ms | 2 bars cut at 18.4 s |
| Ending (S13–S14) | 70 / 70 | 0.00 s | Rain starts at 52.80 s | +21 ms | ending variant generated |

"The detector halved the tempo of the light cue (56 instead of 112). I found it by ear: the claps were on every 'beat'."

**Comparison:**

| | Generated | Library |
|---|---|---|
| Fit to the cut | Exact structure from the brief | Needed 3 edits |
| Time to final | 40 min (6 takes + edit) | 70 min (search + edit) |
| Cost | Plan fee | US$49 single-use license |
| License | Plan terms, no broadcast | Broadcast allowed |
| Choice for this film | Generated (online only) | Would use for a TV version |
