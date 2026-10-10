---
title: Long-to-short and multi-format versions
hours: 15
outcomes:
  - Find the best standalone short moments in long content with transcripts, signals, and an LLM ranking.
  - Reframe 16:9 to 9:16 with face tracking, and find the shots where tracking fails.
  - Make cut-downs (60/30/15/6 s) from one master, each with its own hook and ending.
  - Burn captions in social and sentence styles inside platform safe zones, and deliver SRT and VTT files.
keywords: [reframe, cut-down, safe zone, captions, highlight detection]
summary: >
  One master edit becomes many versions: shorter cut-downs, other aspect ratios, and clips from long content. A
  highlight finder uses the transcript and signals to propose moments, and an LLM ranks them by standalone value.
  Reframing moves a vertical crop window with the main face; it fails on two-shots, fast moves, and text, so the
  report must list these. For AI shots, a vertical version made natively from the key frame is often better than a
  crop. Each cut-down needs its own hook and end. Captions must stay inside the safe zones of each platform.
diagram:
  type: flow
  title: One master, many versions
  nodes: ["Master edit (16:9, 60 s)", "Cut-down plan: 30 / 15 / 6 s", "Reframe 9:16: track + report", "Fix: native vertical or manual crop", "Captions inside safe zones", "Render + spec check (recipe)"]
  highlight: [2]
watch:
  - title: "CapCut — help center (long video to shorts, auto-reframe, auto-captions)"
    url: https://www.capcut.com/help
    note: "Look at the auto-reframe and long-to-shorts features."
  - title: "DaVinci Resolve — training (Smart Reframe in the editing guide)"
    url: https://www.blackmagicdesign.com/products/davinciresolve/training
    note: "Find Smart Reframe in the editing guide."
quiz:
  - q: "A 16:9 two-shot (two people talking, at the left and the right of the frame) is reframed to 9:16. What happens, and what is the fix?"
    options: ["It works", "Both faces do not fit in a vertical crop; the crop shows one person or cuts both. Fix: cut between two singles, or make a native vertical version from the key frame", "Make it black and white", "Use a wider lens"]
    answer: 1
    explain: "In the module test, the reframe report flagged the two-shot for its whole length. Two-shots need an editorial decision."
  - q: "Why is a native vertical version often better than a crop for AI shots?"
    options: ["It is cheaper", "You can generate the 9:16 frame from the same key frame and references, composed for vertical, instead of losing 68 % of the 16:9 picture", "Crops are not allowed", "Vertical video has no sound"]
    answer: 1
    explain: "A 9:16 crop of a 16:9 frame keeps only 32 % of its width. A native generation uses the full vertical frame (C04·M02)."
  - q: "How do you make the 15 s version of a 30 s ad?"
    options: ["Cut the last 15 s off", "Plan it: a hook, the core product action, and the payoff, with its own rhythm; each version stands alone", "Speed it up 2x", "Use only the first 15 s"]
    answer: 1
    explain: "A cut-down is a new edit with the same parts, not a truncation."
  - q: "A highlight finder proposes 20 clips from a 1-hour podcast. How does an LLM rank them usefully?"
    options: ["By length", "By standalone value: does it make sense without context, is there a hook in the first 2 s, does it end on a point? Plus measured signals such as laughter or energy", "Randomly", "By speaker name"]
    answer: 1
    explain: "A short clip must work for a viewer who has seen nothing else. Rank by that, and check the top picks yourself."
  - q: "Why does the reframe report give the maximum crop speed?"
    options: ["For the file size", "A crop that moves fast looks like a nervous camera operator; smoothing or a manual keyframe fixes it", "Platforms limit it", "For the frame rate"]
    answer: 1
    explain: "Smoothing trades lag for calm. Check the fast parts by eye."
  - q: "Your burned-in captions sit at 85 % of the frame height. On the phone they are behind the app's caption and buttons. What is the rule?"
    options: ["Make them smaller", "Keep captions inside the platform's safe zone (away from the top, the bottom UI area, and the right-side buttons); check with a preview of the zones", "Put them at the very bottom", "Use a different font"]
    answer: 1
    explain: "Each platform covers parts of the frame with its interface. Use its current safe-zone template."
  - q: "Social captions show 1–3 words. Why should a caption group end at a full stop or comma?"
    options: ["It is shorter", "A caption that runs across a sentence end ('in here. I') is harder to read and splits the meaning", "Platforms require it", "To save time"]
    answer: 1
    explain: "Group words by meaning: end a caption at punctuation, then start the next one."
deeper:
  - title: "YouTube — Shorts specifications (help)"
    url: https://support.google.com/youtube/answer/10059070
  - title: "TikTok — ads help center (creative best practices and safe zones)"
    url: https://ads.tiktok.com/help/
  - title: "W3C — WebVTT: the Web Video Text Tracks format"
    url: https://www.w3.org/TR/webvtt1/
---
## Learn

### One master, many versions
Most projects deliver more than one file: a 60 s master, 30, 15, and 6 s cut-downs, vertical and square versions, and short clips from long content. Plan the versions in the edit. Mark which shots belong to which version. Then most of the work can be automated, and the agent recipes of M03 can render and check every file.

### Highlights from long content
For podcasts, streams, webinars, and interviews:
1. **Transcribe** with word timestamps and speakers (C06·M02).
2. **Signals:** audio energy, laughter, speaker changes, and (optionally) a vision model that tags moments.
3. **Candidates:** sentences or exchanges of 15–60 s.
4. **Rank** with an LLM by standalone value: does the clip make sense without context? Is there a hook in the first 2 s? Does it end on a point, not in the middle of a thought?
5. **Validate** the quotes against the transcript (M02) and check the top picks yourself.

### Reframe
A vertical crop of a 16:9 frame keeps only 32 % of its width (9:16 of the height). Tracking moves the crop window with the main subject, usually the largest face. Smoothing makes the move calm, with some lag.

Reframing fails in typical places:
- **Two-shots:** two people at the left and the right of the frame do not fit in one vertical crop.
- **Fast moves:** the crop lags or moves nervously.
- **Text and logos:** the crop cuts them off.
- **Composition:** a shot composed for 16:9 often has the subject at a third of the frame, with the space on the other side for a reason (eyeline, C02·M01).

So the reframe step must report where it fails. Then the editor decides for each problem shot:
- cut between two singles instead of a two-shot;
- set manual crop keyframes;
- for AI shots: generate a native vertical version from the same key frame and references (C04·M02). This is often the best fix, because the frame is composed for vertical.

### Cut-downs
A cut-down is a new edit made from the same material. Each version needs its own hook in the first second or two, and its own ending. Do not cut the end off a long version. A typical plan:
- **30 s:** hook, 3 build shots, payoff.
- **15 s:** hook, the core action, payoff.
- **6 s:** one strong action and the logo or the end line.

### Captions
- **Transcribe** and correct names and terms (C06·M02).
- **Social style** (Reels, TikTok, Shorts): 1–3 words at a time, large, high contrast, near the center. End a caption group at a full stop or comma, so a group does not run across a sentence.
- **Sentence style** (YouTube, accessibility): 1–2 lines of up to about 42 characters. Deliver SRT or VTT files too, so the platform can show captions that viewers switch on.
- **Safe zones:** vertical platforms cover parts of the frame with their interface: the top, a bottom area with the caption and the buttons, and a column on the right. Keep captions and important picture content out of these areas. The zones differ by platform and change; use each platform's current template.

## Tool walkthrough

### Reframe with a report

```bash
pip install opencv-python numpy
python starter/tools/reframe.py master_16x9.mp4 --out master_9x16.mp4 --aspect 9:16 --smooth 0.85 --report reframe.json
```

The report lists `two_faces_cut_s` (time spans where several faces do not fit), `face_outside_s` (the main face partly outside the crop), and `max_speed_px_s`. Check each span by eye. Smart reframe features in NLEs do the same job with more options; check the same failure types.

### Captions inside safe zones

```bash
python starter/tools/captions.py master_9x16.mp4 --transcript tr/master.json --preview zones.png
python starter/tools/captions.py master_9x16.mp4 --transcript tr/master.json --out master_9x16_capt.mp4 --style words --n 3
python starter/tools/captions.py master_16x9.mp4 --transcript tr/master.json --out master_16x9_capt.mp4 --style sentence \
  --top 0.05 --bottom 0.08 --right 0.05
```

The preview shows the frame with the unsafe areas in red. The default margins (top 14 %, bottom 22 %, right 12 %) are example values. Set them from each platform's current template. The tool also writes `.srt` and `.vtt` files, and works with every ffmpeg build (it draws text with Pillow).

### Render all versions
Use the `multi-format-render` recipe (M03) with an agent, or a script that calls ffmpeg for each version and runs the spec checks (C09·M04, C10·M02).

## Worked example

**Reframe test** (2026-10-04, 1280 × 720 → 404 × 720 crop):

| Clip | Two faces cut | Main face outside | Max crop speed |
|---|---|---|---|
| One person moving left to right at 200 px/s | none | none | 216 px/s |
| Two people, static, at the left and the right | 0.00–1.96 s (the whole clip) | none | 0 px/s |

The first version of the tool started the crop at the center and jumped to the face (984 px/s in the first frame). Now it starts on the first face. The two-shot cannot be fixed by tracking: it needs an editorial decision.

**Caption test:** a 5 s line in 9:16 at 1080 × 1920. The first version of the word grouping made "in here. I" (across a sentence end). With groups that end at punctuation: "That's my locker." | "It is raining" | "in here." | "I took this" | "photo an hour" | "ago," | "and now it" | "is real." — 8 captions, all inside the safe zone.

**Master 60 s ad (16:9) → versions:**
- 30 s: hook + 3 build shots + payoff. 15 s: hook + product action + payoff. 6 s: product close-up + logo.
- 9:16 of each: 7 of 12 shots reframed well; 3 shots (two-shots and a wide with text) regenerated natively vertical from their key frames; 2 shots re-cropped by hand.
- Captions: word style for Reels and TikTok; sentence style and SRT for YouTube.
- The `multi-format-render` recipe rendered 8 files and checked them; 1 loudness fail fixed.

## Lab

**Deliverable:** `C08/M04/` with 8 versions from one master, the reframe reports, caption previews, and a review sheet.

1. Take your best 60 s piece (or edit one from your C05 material).
2. Plan the 30, 15, and 6 s versions on paper: shots, hook, end. Edit them.
3. Make 9:16 versions with `reframe.py` (or your NLE's reframe). Read the reports. Fix each problem shot: singles, manual keyframes, or native vertical generation.
4. Add captions in two styles. Make a safe-zone preview for each vertical platform that you deliver to.
5. Render all versions with a recipe or a script, and run the spec checks.
6. Fill in the review sheet: shot, problem, fix, result.

**Result checklist**
- [ ] 8 files rendered and spec-checked.
- [ ] Reframe reports, with every flagged span reviewed.
- [ ] Caption previews inside the safe zones; SRT and VTT for the horizontal version.
- [ ] Review sheet.

## Model answer

**Review sheet (shape of a strong answer):**

| Shot | Problem (report) | Fix | Result |
|---|---|---|---|
| S02 two-shot café | two_faces_cut 0–3.2 s | Cut to OTS singles S02a/S02b (already in coverage) | ✓ |
| S05 wide with the shop sign | sign cut off (seen by eye) | Native 9:16 from the key frame, sign in the upper third | ✓ |
| S08 fast turn | max speed 1,450 px/s | Smoothing 0.92 + one manual keyframe | ✓ |
| S11 product + text | text under the bottom UI zone | Moved the end line up in the graphic | ✓ |

"Cut-downs: the 15 s needed a new hook (the cold test at 0 s instead of the dawn ride). The 6 s works only with the product close-up and the logo; we cut the dialogue."

The summary names the main rule: "Reframing worked for singles. Every two-shot and every shot with text needed a decision. For the next project, I plan a vertical key frame for those shots in C04."
