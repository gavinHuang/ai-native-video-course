---
code: C06
title: "Audio Generation: Voice, Music, Sound"
level: 2
hours: 50
prereq: C01
outcomes:
  - Design and direct synthetic voices, and clone voices only with consent.
  - Make lip-synced dialogue, avatars, and dubbed versions of a video.
  - Generate music and know the license of every track.
  - Generate sound effects and ambience, and separate and clean audio.
---
## About this course

Sound is half of the experience. AI now makes voices, music, and effects at production quality. This course teaches you to use these tools well and legally. C10 then teaches you to mix the result.

Current tools (as of 2026-10): ElevenLabs (TTS, cloning, dubbing, music v2.5, avatars), HeyGen, Synthesia, Suno v6; open: IndexTTS-2, CosyVoice 3, Qwen3-TTS; Demucs for stems.

**Starter tools for this course** (in the [starter kit](starter.zip)):

| Tool | Use |
|---|---|
| `tools/fit_check.py` | Speech length of each line against its time slot (M01, M02) |
| `tools/transcribe.py` | Transcript with word timestamps, captions (SRT), and dub slots (M02) |
| `tools/stems.py` | Voice and background stems (M02, M04) |
| `tools/bars.py` | Bar and beat grid, picture-hit check, beat detection (M03) |
| `tools/loop_audio.py` | Seamless ambience loops and a loop-point check (M04) |
| `templates/voice_consent.md` | Consent record for a voice clone or likeness (M01, M02) |

Python packages: `pip install faster-whisper demucs librosa` (all open source; CPU works).
