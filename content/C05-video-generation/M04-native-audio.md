---
title: Native audio and dialogue in video models
hours: 12
outcomes:
  - Write an audio block in every video prompt - dialogue, effects, ambience, and music - with timing.
  - Keep a character's voice consistent with voice references, and know the limits.
  - Decide for each sound type whether to keep, replace, or layer native audio.
  - Split native audio into dialogue and background stems, and judge the quality of the split.
keywords: [native audio, dialogue, voice lock, ambience, audio-to-video]
summary: >
  Many current video models generate sound with the picture. Write dialogue in quotes with the speaker name, add
  sound effects and ambience, and say if there is music. Voice references keep a character's voice the same across
  shots. Native audio gives excellent sync for lips, footsteps, and impacts. Its weaknesses are voice drift between
  clips, generic music, and one mixed track. Professional work often keeps the native sync sounds and ambience, and
  replaces or layers dialogue and music in post. Source separation splits the mixed track into stems.
diagram:
  type: compare
  title: Keep or replace native audio
  left:
    title: "Keep native"
    items: ["Short social clips", "Sync effects: steps, impacts, doors", "Room tone and ambience", "Lip sync for one-off lines"]
  right:
    title: "Replace or layer in post"
    items: ["Recurring character voices (consistency)", "Music (license + control)", "Brand voice-over", "Anything that needs a clean stem"]
watch:
  - title: "Google DeepMind — Veo model page (native audio examples)"
    url: https://deepmind.google/models/veo/
    note: "Listen to the examples with dialogue and effects. Note what sounds generic."
  - title: "Demucs — open-source music and voice separation (README)"
    url: https://github.com/facebookresearch/demucs
    note: "Read the usage section and the note on two-stem separation."
quiz:
  - q: "How do you write a line of dialogue in a video prompt so that the right character says it?"
    options: ["Write it without quotes", "Speaker name, delivery, and the exact words in quotes: MARA (whisper, surprised): \"That's my locker.\"", "Put it in the negative prompt", "Write it in capitals"]
    answer: 1
    explain: "Name, delivery, and quotes make it clear who speaks, how, and exactly what."
  - q: "Mara speaks in 6 shots made in 6 generations, without a voice reference. What do you expect?"
    options: ["The same voice", "A different voice in some shots: the model invents a voice from the description each time", "No voice", "Only music"]
    answer: 1
    explain: "Without a reference, the voice is generated again each time. Use a voice reference, or replace dialogue with one fixed voice (C06)."
  - q: "Which part of native audio do you usually keep?"
    options: ["Music", "Sync effects and ambience: footsteps, doors, impacts, room tone", "Brand voice-over", "Nothing"]
    answer: 1
    explain: "Sync effects are hard to make by hand and native audio gets their timing right. Music and recurring voices need control and licenses."
  - q: "Why do most edited projects replace native music?"
    options: ["It is always bad", "Generated music per clip does not continue across cuts, you cannot control it in the edit, and its license may be unclear", "Platforms forbid it", "It is too loud"]
    answer: 1
    explain: "Music must flow across the cut and follow the edit. Use one music track for the scene (C06·M03, C10)."
  - q: "You split native audio into stems. The dialogue stem sounds a little thin, and there is faint music in the pauses. Is this a failure?"
    options: ["Yes, always", "No, these are normal separation artifacts; use the stem inside a mix, and use a clean replacement voice if the line must stand alone", "It means the model is wrong", "It means the file is corrupt"]
    answer: 1
    explain: "Separation estimates the sources. A stem is good for a mix. It is not a clean studio recording."
  - q: "In a separation test, the voice estimate improves from 16.4 dB to 25.7 dB SI-SDR. What does SI-SDR measure?"
    options: ["Loudness", "How close the estimated signal is to the true source, in dB; higher is better", "File size", "Frame rate"]
    answer: 1
    explain: "SI-SDR compares an estimate with the original source. You can measure it only when you have the original, for example in a test that you mix yourself."
  - q: "When is audio-to-video the right mode?"
    options: ["Never", "When the picture must follow an existing audio track: a recorded line (lip sync), a music video, motion on beats", "When you have no audio", "Only for silent films"]
    answer: 1
    explain: "With audio-to-video the audio is fixed and the picture follows it. This is how C11·M03 makes lip-synced dialogue with a fixed voice."
deeper:
  - title: "Défossez et al. — Hybrid Transformers for Music Source Separation (Demucs v4)"
    url: https://arxiv.org/abs/2211.08553
  - title: "Le Roux et al. — SDR, half-baked or well done? (SI-SDR)"
    url: https://arxiv.org/abs/1811.02508
  - title: "Kling 3.0 — release notes (voice from reference)"
    url: https://app.klingai.com/global/release-notes
---
## Learn

### Joint audio-video generation
Some video models generate the sound and the picture together, in one model. The model learns from videos with sound, so it learns that a door makes a sound when it closes, and that lips move with speech. This gives very good sync for effects and lip movement. It also means that the audio is one mixed track, made again in every generation.

### The audio block
Add an audio block to every prompt, even when you want silence. Name each layer:
- **Dialogue:** speaker, delivery, and the exact words in quotes. `MARA (quietly, surprised): "It's raining… in here?"`
- **Sound effects:** the actions that make sound. "Paper rustles; a locker door clicks shut."
- **Ambience:** the place. "Distant hospital monitor beeps, air-conditioning hum."
- **Music:** "no music" is the default for edited work. Or describe it.

Add timing for longer clips: "at 3 s she speaks". If you say nothing about audio, the model decides, and it often adds music.

### Voice consistency
Without a reference, the model invents a voice from your description in each generation. A series character then has several voices. Methods, from strongest to weakest:
1. **Replace the dialogue** with one fixed voice (a designed or cloned voice with consent, C06·M01). Then use lip sync or audio-to-video so the picture follows that voice (C11·M03).
2. **A voice reference** in the generation. Some models take a reference clip and keep its voice and tone.
3. **The same voice description** in every prompt. Expect drift.
For one-off lines, native dialogue is often fine and has the best lip sync.

### Audio-to-video
Some models take an audio track as input and make the picture follow it: lips follow a recorded line, motion follows music beats. This is the mode for a fixed voice (method 1 above) and for music videos.

### Keep, replace, or layer
Decide for each layer, not for the whole track:
- **Keep** sync effects and ambience. They are hard to place by hand, and native audio gets the timing right.
- **Replace** recurring voices (consistency), brand voice-over (approved script and voice), and music (it must continue across cuts, follow the edit, and have a clear license).
- **Layer** when native effects are thin: keep the native sound for timing, and add a stronger designed effect on top (C10·M01).

### Split the mixed track into stems
Native audio arrives as one track. Source separation estimates the parts. A two-stem model gives "vocals" (dialogue) and "no vocals" (everything else). A four-stem model splits music further.

How to judge a split:
- **By ear:** listen to each stem alone, on headphones. Typical artifacts: a thin or watery voice, music residue in pauses, and effects that leak into the dialogue stem (a cough, a laugh).
- **By measurement in a test:** mix a voice and a background yourself, separate the mix, and compare each estimate with its original. The common measure is SI-SDR (scale-invariant signal-to-distortion ratio) in dB. Higher is better. You can measure it only when you have the originals, so it is a test of the tool, not a check of each clip.

Use stems inside a mix. A separated dialogue stem is not a clean studio recording. When a line must stand alone (a trailer, a voice-over), replace it.

## Tool walkthrough

### Native audio in current models (as of 2026-10)
- **Kling 3.0:** native audio; voice and tone from a reference video, kept for new dialogue; supports Chinese dialects.
- **Veo 3.1:** native 48 kHz audio with dialogue and effects.
- **Seedance 2.5:** native audio; audio references.
- **LTX-2.5 (open):** joint audio and video; starter workflow `06_i2v_ltx25`. LTX-2.3 image + audio → video: starter workflow `07_lipsync_ia2v_ltx23`.

### Split stems

```bash
pip install demucs
python starter/tools/stems.py S07_t04.mp4 --out stems/
# -> stems/S07_t04_dialogue.wav, stems/S07_t04_background.wav
python starter/tools/stems.py S07_t04.mp4 --out stems/ --four   # vocals, drums, bass, other
```

The tool extracts the audio with ffmpeg and runs Demucs (MIT license). It runs on CPU. A GPU makes it faster.

### Extract audio only

```bash
ffmpeg -i clip.mp4 -vn -c:a pcm_s24le clip.wav
```

## Worked example

**Separation test** (2026-10-04, Demucs `htdemucs`, two stems, CPU). We mixed a synthetic voice line (5.9 s) with a synthetic music bed (three tones with tremolo and pink noise). Then we separated the mix and compared each stem with its original:

| Estimate | SI-SDR against the original |
|---|---|
| The mix, used as "dialogue" | 16.4 dB |
| Demucs dialogue stem | 25.7 dB (+9.3 dB) |
| The mix, used as "background" | −16.5 dB |
| Demucs background stem | 8.9 dB (+25.4 dB) |

The separation took about 3 s for 5.9 s of audio on a laptop CPU (12 s including model load). The background stem gains most, because in the mix it is much quieter than the voice. Real native audio is harder than this test: effects overlap the voice, and the room adds reverb. Listen to every stem.

**Shot S07 with native audio:**
- Audio block: `MARA (whisper, surprised): "That's my locker." | SFX: paper rustle at 1 s | AMB: hospital beeps, AC hum | music: none`.
- Take 1: good lip sync; the voice is too young compared with S03.
- Take 2, with a voice reference from S03: the voice matches; one beep is too loud.
- Post: split stems; lower the beep in the background stem; keep the paper sound; keep the dialogue.

## Lab

**Deliverable:** `C05/M04/` with 4 clips with native audio, their stems, a separation test, and a decision table.

1. Generate 2 dialogue shots of the same character, without and then with a voice reference. Compare the voices.
2. Generate 1 action shot with sync effects (steps, a door, an impact).
3. Generate 1 shot from an audio track (audio-to-video), if one of your models supports it. Otherwise prepare a recorded line for C11·M03.
4. Split stems for 2 clips with `stems.py`. Listen to each stem and write the artifacts that you hear.
5. Run a separation test: mix your own voice recording with a music bed, separate it, and compute SI-SDR against the originals (use the script in the model answer).
6. Fill in a decision table for each clip: keep, replace, or layer, for dialogue, effects, ambience, and music, with a reason.

**Result checklist**
- [ ] Voice comparison with and without a reference.
- [ ] Stems as WAV files, with listening notes.
- [ ] Separation test with SI-SDR numbers.
- [ ] Decision table with a reason for each cell.

## Model answer

**SI-SDR script used for the test:**

```python
import numpy as np, subprocess
def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", "44100", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32)
def si_sdr(est, ref):
    n = min(len(est), len(ref)); est, ref = est[:n], ref[:n]
    target = np.dot(est, ref) / np.dot(ref, ref) * ref
    return 10 * np.log10(np.sum(target ** 2) / np.sum((est - target) ** 2))
print(si_sdr(load("stems/mix_dialogue.wav"), load("my_voice.wav")))
```

**Decision table (shape of a strong answer):**

| Clip | Dialogue | Effects | Ambience | Music |
|---|---|---|---|---|
| S03 (Mara, first line) | Replace: fixed voice for the series; lip sync in C11·M03 | Keep: the locker click is exactly on the frame | Keep | Replace: one cue for the scene |
| S07 (Mara whisper) | Keep: one-off line; the native lip sync is better than any dub | Keep paper; lower one beep in the stem | Keep | None |
| S09 (running) | — | Layer: native steps for timing + a designed impact | Keep | Replace |
| Ad end card | Replace: approved brand voice-over | — | — | Licensed track |

The listening notes are specific: "S07 dialogue stem: slight 'underwater' sound on the 's' sounds; one beep leaks into the stem at 2.1 s. Usable under the room tone in the mix." The voice comparison states the result: "Without a reference, S03 and S07 sound like two different women. With the reference, the pitch and accent match."
