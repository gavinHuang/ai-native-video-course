---
title: Sound effects, ambience, separation, and cleanup
hours: 12
outcomes:
  - Generate sound effects and ambience from text and from video, with prompts that name source, action, material, space, and distance.
  - Make seamless ambience loops, and measure the loop point.
  - Clean noisy dialogue at the least strength that works, and compare classic denoising with AI voice isolation by measurement and by ear.
  - Build a sound library with IDs, metadata, and licenses that pipelines can search.
keywords: [sound effects, ambience, stem separation, noise reduction]
summary: >
  Sound-effect models make effects and ambience from text, and some make them from the video itself, in sync. Name
  the source, the action, the material, the space, and the distance. Ambience beds must loop without a step or a
  click. Stem-separation and voice-isolation models split a mix into voice and the rest; they now clean noisy
  dialogue much better than classic spectral noise reduction. Use the least strength that works, compare with the
  original, and keep some room sound. Store every sound with an ID, metadata, and its license.
diagram:
  type: flow
  title: From noisy clip to clean, layered sound
  nodes: ["Native or recorded audio", "Separate: voice stem + background", "Clean the voice (least strength)", "Generate effects + ambience loops", "Library: ID, tags, license", "To the mix (C10)"]
  highlight: [2]
watch:
  - title: "ElevenLabs — sound effects docs"
    url: https://elevenlabs.io/docs/capabilities/sound-effects
    note: "Read the prompt tips for effects."
  - title: "Demucs — GitHub (music source separation)"
    url: https://github.com/facebookresearch/demucs
    note: "Read the usage section; you run it in the lab."
quiz:
  - q: "Which prompt gives the most useful door sound?"
    options: ["'Door sound'", "'Heavy wooden door slams in a large stone hall, close to the microphone, long echo'", "'Loud cinematic door'", "'Door, high quality'"]
    answer: 1
    explain: "Source, action, material, space, and distance decide how a sound sounds. 'Cinematic' and 'high quality' carry no information."
  - q: "An ambience loop has a soft 'step' in level every 90 s. What is the cause and the fix?"
    options: ["The speakers", "The end and the start of the file have different levels; crossfade the end into the start (equal power), then check the loop point", "The sample rate", "Too much reverb"]
    answer: 1
    explain: "A loop point joins the end to the start. Any difference in level or texture is heard every cycle. In the module test, the step fell from 5.4 dB to 3.0 dB after a 2 s crossfade."
  - q: "You set a classic noise reducer to remove 40 dB of noise, but the output is unchanged. What is a likely cause?"
    options: ["The file is mono", "The noise floor setting is far below the real noise level, so the tool finds no noise; measure the noise in a pause and set the floor to it", "The reducer needs more CPU", "40 dB is too little"]
    answer: 1
    explain: "In the module test, a floor of −40 dB gave no change on noise at −21 dBFS. With the floor at −21 dB, the reducer worked."
  - q: "Classic denoising at 24 dB and at 40 dB gave the same measured result. Which do you use?"
    options: ["40 dB, it is stronger", "24 dB or less: more strength gave no gain, and stronger settings add 'watery' artifacts", "Neither", "Both in series"]
    answer: 1
    explain: "Use the least strength that works. Extra strength adds artifacts without benefit."
  - q: "On the same noisy line, classic denoising reached 9.1 dB SI-SDR and an AI voice-isolation model reached 14.9 dB. What else must you check before you use the AI result?"
    options: ["Nothing", "Listen: AI isolation can remove breaths and room sound and make the voice sound 'pasted on'; mix back a little room tone", "The file size", "The tempo"]
    answer: 1
    explain: "Numbers say how close to the clean voice. Ears say whether it sounds natural in the scene."
  - q: "Why keep a little room sound under cleaned dialogue?"
    options: ["It is required", "A voice with no room sound sounds unnatural and makes cuts between shots audible; room tone glues the edit", "To hide the music", "For loudness"]
    answer: 1
    explain: "Every place has a sound. Dialogue edits need a continuous room tone under them (C10·M01)."
  - q: "What does each sound-library entry need?"
    options: ["Only the file", "An ID, tags (source, action, material, space, distance), the origin (prompt and model, or the recordist), the license, and a rights-log line", "The duration only", "A cover image"]
    answer: 1
    explain: "Pipelines search by tags. C16 needs the origin and the license."
deeper:
  - title: "Défossez et al. — Hybrid Transformers for Music Source Separation (Demucs v4)"
    url: https://arxiv.org/abs/2211.08553
  - title: "Freesound — CC-licensed sound library (check the license of each sound)"
    url: https://freesound.org/
  - title: "FFmpeg filters — afftdn (FFT denoiser) documentation"
    url: https://ffmpeg.org/ffmpeg-filters.html#afftdn
---
## Learn

### What effects and ambience do
**Sound effects** are the sounds of actions: a door, steps, paper, a cup. **Ambience** is the sound of a place: rain, traffic, a hospital air system, a café. Ambience runs under a whole scene and tells the viewer where they are. Effects make actions feel real and land the edit (C10·M01).

### Prompt effects like a sound designer
A sound depends on five things. Name all five:
1. **Source:** a heavy wooden door; a metal locker door.
2. **Action:** slams; creaks open slowly; clicks shut.
3. **Material:** wood, metal, glass, gravel, linoleum.
4. **Space:** a small tiled bathroom; a large stone hall; outdoors.
5. **Distance:** close to the microphone; across the room; far away.
"Cinematic", "epic", and "high quality" carry no information. Generate 3–4 takes. The material and the distance usually need 2–3 prompt changes.

Some models make sound from the video itself (video-to-audio). They place effects on events in the clip: steps when the feet touch the floor. Check the sync at the frame level. Step through the clip one frame at a time at each impact. The sound should start on the frame where the contact happens, or one frame later. A sound that starts before the contact is easy to notice, even when it is only one or two frames early.

### Ambience beds
Generate ambience long: 60–120 s. Say what must not be in it: "no voices, no music". Viewers notice when a bed repeats in a short loop.

A bed that plays under a long scene must loop. A loop point joins the end of the file to the start. If the level or the texture differs, the listener hears a step or a click every cycle. Fix: crossfade the last seconds into the first seconds with equal-power curves (one fades out, the other fades in, so the loudness stays even). Then check the loop point. `starter/tools/loop_audio.py` does both.

### Separation
Source-separation models split a mix into parts: voice and the rest (two stems), or voice, drums, bass, and other (four stems). Uses:
- take the voice out of a native-audio clip (C05·M04);
- remove music from a clip that you must re-score;
- reuse the ambience of a clip.

### Cleanup: classic and AI
Noisy dialogue has two kinds of tools:
- **Classic spectral noise reduction** estimates the noise spectrum and subtracts it. It needs a correct noise estimate. It works on steady noise (hum, hiss, air conditioning). Too much strength makes the voice "watery".
- **AI voice isolation and separation** models learned what voices sound like. They remove changing noise too (traffic, babble, music). They can remove breaths and room sound, and make a voice sound pasted onto the scene.

Rules for both:
1. Measure the noise first, in a pause: its level and its type.
2. Use the least strength that works. Try 3 strengths and listen.
3. A/B every result with the original, on headphones and on a small speaker.
4. Keep a little room sound. Mix room tone back under a fully isolated voice.

### The sound library
Store every sound you keep:

```
sfx/
  DOOR-LOCKER-SLAM-01.wav
  DOOR-LOCKER-SLAM-01.json   {"tags": ["door", "metal", "slam", "small room", "close"],
                              "origin": "generated: model X, prompt '...'", "license": "...", "date": "2026-10-04"}
```

Tags follow the five prompt parts, so you can search "metal, close, small room". Add a rights-log line for every sound that you did not make yourself (C16).

## Tool walkthrough

### Effects tools (as of 2026-10)
- **Hosted:** ElevenLabs sound effects (text to effect); some video models add synced effects natively (C05·M04).
- **Open separation:** Demucs (MIT) through `starter/tools/stems.py`.
- **Cleanup:** iZotope RX, Adobe Podcast, DaVinci Resolve Voice Isolation (hosted or desktop); ffmpeg `afftdn` for classic denoising in scripts.

### Make and check a loop

```bash
python starter/tools/loop_audio.py rain_90s.wav --out rain_loop.wav --xfade 2.0
python starter/tools/loop_audio.py rain_loop.wav --check
```

### Classic denoise in a script
Measure the noise level in a pause first (for example with `ffmpeg -i in.wav -af astats -f null -` on a cut of the pause). Then set the noise floor (`nf`) to that level:

```bash
ffmpeg -i noisy.wav -af "afftdn=nr=12:nf=-21" clean_nr12.wav
```

### AI isolation

```bash
python starter/tools/stems.py noisy_line.wav --out iso/     # iso/noisy_line_dialogue.wav
```

## Worked example

**Loop test** (2026-10-04). A 20 s ambience bed (pink noise with a slow level change and a low hum):

| File | Level step at the loop point | Ratio to normal steps | Click | Result |
|---|---|---|---|---|
| Raw file, end → start | 5.35 dB | 3.66 | no | AUDIBLE JOIN |
| After a 2 s equal-power crossfade | 2.96 dB | 2.07 | no | SEAMLESS |

**Cleanup test** (2026-10-04). A synthetic voice line with steady broadband noise at 5 dB signal-to-noise ratio. SI-SDR against the clean voice (higher is better), and the noise level in the pause before the line:

| Method | SI-SDR | Noise in the pause |
|---|---|---|
| Noisy input | 4.2 dB | −20.9 dBFS |
| Classic denoise, noise floor set wrong (−40 dB) | 4.3 dB | −21.0 dBFS (no effect) |
| Classic denoise, floor −21 dB, 6 dB reduction | 7.3 dB | −24.6 dBFS |
| Same, 12 dB reduction | 8.5 dB | −26.2 dBFS |
| Same, 24 dB reduction | 9.1 dB | −27.1 dBFS |
| Same, 40 dB reduction | 9.1 dB | −27.2 dBFS |
| AI separation (Demucs, voice stem) | 14.9 dB | −54.7 dBFS |

Three lessons:
1. A wrong noise estimate makes a classic reducer do nothing. Measure the noise first.
2. Above 24 dB of reduction there was no gain. More strength only adds artifacts.
3. The AI model was much better here: 5.8 dB more than the best classic setting, and an almost silent pause. Listen anyway: the pause is now unnaturally silent, so add room tone in the mix.

## Lab

**Deliverable:** `C06/M04/` with before/after audio, a cleanup table, 2 loops with reports, and 10 library entries.

1. Take 2 native-audio clips (or recordings with noise). Separate the stems.
2. Clean one noisy voice with a classic reducer at 3 strengths (measure the noise floor first) and with AI isolation. Measure each result (SI-SDR if you have a clean reference; otherwise the noise in a pause) and listen. Choose one, and explain why.
3. Generate 6 effects and 2 ambience beds for your scene. Use the five prompt parts. Write how many takes each needed.
4. Make both beds loop with `loop_audio.py`. Save the check reports.
5. Add 10 entries to your sound library with JSON metadata and rights-log lines.

**Result checklist**
- [ ] Cleanup table with measurements and a listening note for each version.
- [ ] 6 effects and 2 loops, with loop reports that pass.
- [ ] 10 library entries with tags, origin, and license.

## Model answer

**Cleanup choice (shape of a strong answer):** "Noise in the pause: −32 dBFS, mostly air conditioning (steady). Classic denoise at 6 / 12 / 18 dB: the 12 dB version removes the hum and keeps the voice natural; 18 dB starts to sound watery on 's' sounds. AI isolation: the cleanest, but her breaths are gone and the voice sounds dry against the room. Choice: classic 12 dB for this steady noise. For the café scene (babble and music), AI isolation plus room tone at −42 dBFS."

**Effects log:**

| Sound | Takes | What changed between takes |
|---|---|---|
| Locker door click | 3 | "metal locker" + "small tiled room" fixed the material and the space |
| Photo paper rustle | 2 | "close to the microphone" |
| Rain on a window, inside | 4 | "heard from inside, through glass" removed the outdoor splash |

The two loop reports show SEAMLESS. The library entries use the same tag vocabulary, so `grep -l '"metal"' sfx/*.json` finds every metal sound.
