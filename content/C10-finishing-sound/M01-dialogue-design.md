---
title: Dialogue edit and sound design
hours: 14
outcomes:
  - Set up a standard session layout with dialogue, music, and effects tracks routed to buses that become stems.
  - Edit dialogue - clicks, breaths, joins, level matching - and fill dropouts with room tone.
  - Build four layers of sound design - ambience, Foley, hard effects, and design.
  - Make shots from different generations sound like one space, with one ambience and one reverb.
  - Use a DAW for the first time - import, edit, fade, route, automate, bounce.
keywords: [dialogue edit, room tone, Foley, sound design, bus]
summary: >
  Sound finishing starts with order: one session layout, with dialogue (DX), music (MX), and effects (FX) on their
  own tracks and buses, because the buses become the stems. The dialogue edit removes distractions, smooths joins,
  matches levels, and fills every dropout with room tone. Sound design adds four layers: ambience for the space,
  Foley for human actions, hard effects, and design sounds for emotion. Generated shots each bring their own room
  sound; one ambience bed and one reverb make them one place.
diagram:
  type: stack
  title: Standard session layout
  nodes: ["DX: dialogue tracks (one per character) + room tone", "FX: ambience, Foley, hard effects, design", "MX: music cues", "Buses: DX bus, FX bus, MX bus → the stems", "Mix bus → loudness check (M02)"]
  highlight: [3]
watch:
  - title: "Blackmagic — DaVinci Resolve training (Fairlight audio chapters)"
    url: https://www.blackmagicdesign.com/products/davinciresolve/training
    note: "Do the Fairlight chapter on dialogue editing."
  - title: "SoundWorks Collection — interviews with film sound designers"
    url: https://soundworkscollection.com/
    note: "Watch one sound-design interview. Note how sounds are layered."
quiz:
  - q: "Three TTS lines are joined with digital silence between them. On headphones the room 'disappears' at each gap. What is the fix?"
    options: ["Raise the volume", "Fill each gap with room tone (the quiet sound of the place), with short crossfades", "Add music", "Cut the gaps out"]
    answer: 1
    explain: "Every place has a sound. Digital silence sounds like a hole. In the module test, 3 gaps (2.55 s) were filled and none were left."
  - q: "The tool cannot find room tone in a TTS file: the quietest non-silent second is speech at −15 dBFS. Why?"
    options: ["The tool is broken", "TTS output has no room sound at all, only speech and digital silence; room tone must come from a recording of the place, a native-audio clip, or a generated bed", "The file is too short", "The voice is too loud"]
    answer: 1
    explain: "Synthetic voices are 'dry'. You add the room in the mix."
  - q: "Why route all dialogue tracks to one DX bus, all effects to an FX bus, and music to an MX bus?"
    options: ["It looks tidy", "The buses become the stems (DX, MX, FX), which deliveries, dubs, and cut-downs need; bus processing also treats each group the same", "DAWs require it", "It saves CPU"]
    answer: 1
    explain: "Plan the stems at the start of the session, not at the end."
  - q: "What is Foley?"
    options: ["Background music", "Sounds of human actions performed and recorded (or generated) to picture: steps, cloth, hands, props", "Room reverb", "Dialogue replacement"]
    answer: 1
    explain: "Foley makes hands and bodies feel real. Generated clips often lack it or have weak versions of it."
  - q: "Six generated shots each have their own reverb and background noise. The scene sounds like six places. What do you do?"
    options: ["Raise the music", "Separate or reduce the native room sound, put one continuous ambience bed under the whole scene, and send all dialogue to one scene reverb", "Use more effects", "Add compression"]
    answer: 1
    explain: "One ambience and one reverb make one place. Crossfade the ambience across cuts."
  - q: "You removed all breaths from a dialogue track. It sounds wrong. Why?"
    options: ["Breaths are required by law", "People breathe; a voice with no breaths sounds machine-made and the rhythm feels rushed; remove only loud or distracting breaths", "The fades are wrong", "The level is wrong"]
    answer: 1
    explain: "Edit for distraction, not for perfection."
  - q: "A generated line sounds brighter and closer than the recorded lines around it. What do you match?"
    options: ["Only the level", "Level, EQ (tone), and space (reverb and room tone), so that the line sits in the same place as the others", "Only the pitch", "Nothing"]
    answer: 1
    explain: "Lines match when level, tone, and space match."
deeper:
  - title: "Wikipedia — Foley (filmmaking)"
    url: https://en.wikipedia.org/wiki/Foley_(filmmaking)
  - title: "Holman — Sound for Film and Television (book)"
    url: https://www.routledge.com/Sound-for-Film-and-Television/Holman/p/book/9781138468801
  - title: "FFmpeg filters — audio filters (afade, acrossfade, sidechaincompress)"
    url: https://ffmpeg.org/ffmpeg-filters.html#Audio-Filters
---
## Learn

### Why sound finishing
Viewers forgive a weak image sooner than weak sound. In AI-native work, the sound comes from many sources: native audio of several generations, TTS or cloned voices, generated music and effects, and some recordings. Each has its own level, tone, and room. Sound finishing makes them one soundtrack.

### The session layout
Use the same layout in every project:
- **DX:** one track per character, plus a room-tone track.
- **FX:** tracks for ambience, Foley, hard effects, and design sounds.
- **MX:** music cues.
- **Buses:** route all DX tracks to a DX bus, all FX tracks to an FX bus, all MX tracks to an MX bus. A bus is a submix: one fader and one set of processing for a group.
- **Mix bus:** the three buses meet here.
The DX, FX, and MX buses become the stems of the delivery (M02). Plan them from the start.

### The dialogue edit
Goals: clear words, no distractions, and joins that nobody hears.
- **Clicks and mouth noise:** remove them (a short cut or a de-click tool).
- **Breaths:** remove loud or distracting breaths; keep the others. A voice with no breaths sounds machine-made.
- **Joins:** short crossfades (5–20 ms) at every cut, so there are no clicks.
- **Levels:** match the level of lines and takes, so the voice does not jump.
- **Tone and space:** a generated line next to a recorded line often sounds brighter or closer. Match the EQ and the space.
- **Noise:** clean only as much as needed (C06·M04).

### Room tone
Every place has a sound: air, a fridge, distant traffic. This is **room tone**. When you cut dialogue, the room tone stops and starts with the cuts, and digital silence between lines sounds like a hole. Fill every gap with room tone, with short crossfades.

Generated and synthetic sources make this more important:
- TTS and cloned voices have no room tone at all, only speech and digital silence.
- Native audio of each generated shot has its own, different room tone.
Get room tone from a recording of a real, similar place (30 s), from the quietest part of a native-audio clip of the scene, or from a generated ambience (C06·M04).

### Four layers of sound design
1. **Ambience:** the space and the time (night city, a hospital air system, rain on the window). It runs under the whole scene.
2. **Foley:** human actions to picture: steps, cloth, hands, props. Generated clips often lack Foley or have weak Foley.
3. **Hard effects:** distinct events: doors, lockers, cars, impacts.
4. **Design:** sounds for emotion and transitions: whooshes, risers, low hits, tonal beds.
Generate the missing layers (C06·M04), and keep their IDs in the sound library.

### One space
Generated shots each carry their own reverb and background. Make them one place:
1. Separate the dialogue from the native audio (stems, C05·M04), and reduce the native reverb if needed.
2. Put one continuous ambience bed under the whole scene, across the cuts. Crossfade it slowly at scene changes.
3. Send all dialogue of the scene to one reverb that fits the place (for example a small room, 0.6 s).
4. Use J and L cuts for the ambience at scene changes (C02·M04): let the next place's sound start a little before its picture.

## Tool walkthrough

### Your first session in a DAW (DaVinci Resolve Fairlight, free)
1. On the Fairlight page, import the picture (the edited timeline is already there if you edited in Resolve).
2. **Tracks:** add tracks (right-click the track headers → Add Track): DX_MARA, DX_LEO, DX_ROOM, FX_AMB, FX_FOLEY, FX_HARD, FX_DESIGN, MX.
3. **Buses:** in the Fairlight menu, open the bus setup (Bus Format in older versions); create DX, FX, and MX submix buses. Route each track to its bus in the mixer.
4. **Edit:** cut clips with the blade (razor) tool; add fades by dragging the fade handles at the clip corners; crossfade by overlapping clips.
5. **Automation:** turn on automation (the automation toolbar), choose "Volume", and draw level changes on the track.
6. **Bounce:** Deliver page → Audio Only, or render stems with "Render each track / bus".
Other DAWs (Pro Tools, Reaper, Logic) use the same ideas.

### Fill dropouts with room tone (scripted)

```bash
python starter/tools/roomtone.py dx_mara.wav --tone room_tone.wav --out dx_mara_filled.wav
```

The tool finds stretches below −70 dBFS longer than 50 ms, fills them with looped room tone, and crossfades the joins. With `--auto-tone` it takes tone from the quietest non-silent part of the file, and it refuses if that part is speech (as in TTS files).

### Generated Foley and effects
Use the five prompt parts of C06·M04 (source, action, material, space, distance). Place each effect on its frame: the sound starts on the frame of the contact.

## Worked example

**Room tone test** (2026-10-04). Three TTS lines joined with digital silence (0.8 s, 1.1 s, 0.6 s gaps). Room tone: 5 s of pink noise at −62.5 dBFS (a stand-in for a quiet room).

```
roomtone.py dx_raw.wav --tone tone.wav   → {"gaps_found": 3, "gap_seconds": 2.55, "tone_level_dbfs": -62.5, "gaps_after": 0}
roomtone.py dx_raw.wav --auto-tone       → no room tone found: the quietest non-silent second is -15.0 dBFS (speech)
```

The second result is the lesson: a TTS file contains no room. The room must come from somewhere else.

**Café scene, 6 generated shots with native audio:**
1. Separate the voice from each clip; light de-reverb on 2 clips that sounded like a hall.
2. One café ambience bed for the whole scene (a generated 90 s loop, checked with `loop_audio.py`).
3. Foley: cups and saucers generated and placed on the hand actions.
4. One small room reverb (0.6 s) on both voices.
5. Room tone from the quietest 2 s of shot 3, under all dialogue joins.
Result: the 6 clips sound like one café.

## Lab

**Deliverable:** `C10/M01/` with a sound-designed scene (45–60 s), the session file, and a short sound report.

1. Set up the standard layout with DX, FX, and MX buses.
2. Edit the dialogue: clicks, distracting breaths, joins, levels. Fill every gap with room tone (`roomtone.py` or by hand).
3. Build the 4 layers of sound design. Place Foley and hard effects on their frames.
4. Unify the space: one ambience bed across the cuts and one dialogue reverb.
5. Automate levels where needed (ambience under dialogue).
6. Bounce a rough mix and the three bus stems (the final mix is in M02).
7. Write the sound report: sources, what you generated, what you fixed.

**Result checklist**
- [ ] Standard track layout with three buses.
- [ ] No clicks, no dropouts, smooth joins (listen on headphones).
- [ ] Four layers present; effects on their frames.
- [ ] The scene sounds like one space.

## Model answer

A strong session is labeled and colored by group (DX blue, FX green, MX purple), and every track goes to its bus.

**Sound report (shape of a strong answer):**

| Element | Source | Treatment |
|---|---|---|
| Mara dialogue | Native audio of S03, S07; TTS in S09 (fixed voice) | Stems; S09 TTS EQ'd darker (−3 dB at 6 kHz) and sent to the room reverb to match S07 |
| Room tone | Quietest 2.4 s of S07 native audio | Filled 11 gaps |
| Ambience | Generated "hospital night, air system, distant monitor" 90 s loop | Loop checked: SEAMLESS |
| Foley | Generated cloth and locker sounds; 2 recorded (photo paper) | Placed on contact frames |
| Hard effects | Generated locker door | Layered with native click for timing |
| Design | Low rumble on the turn (S11) | Automated in over 2 s |

"The TTS line in S09 was the most obvious problem: it was dry and bright next to the native lines. EQ, the room reverb, and room tone under it made it sit in the same room."
