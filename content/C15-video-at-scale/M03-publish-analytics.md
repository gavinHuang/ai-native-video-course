---
title: Publishing, platform specs, and the analytics loop
hours: 14
outcomes:
  - Publish videos with correct specs, metadata, thumbnails, captions, and AI disclosure.
  - Use platform APIs for upload and scheduling, and store the platform ID with the asset.
  - Read click-through rate, retention curves, and engagement, and map drops and bumps to shots.
  - Feed analytics back into the hook library, the treatment template, pacing rules, and the routing table.
keywords: [retention curve, click-through rate, platform API, AI disclosure, analytics loop]
summary: >
  Publishing is the last gate: the file must meet the platform's spec, carry clear metadata, a tested thumbnail,
  captions, and the AI disclosure that the platform and the law require. Platform APIs upload and schedule, and the
  platform's video ID goes into the asset record. After release, click-through rate shows how well the thumbnail and
  title promise; the retention curve shows where viewers leave or rewatch. Map those moments to shot IDs, compare
  like with like, and turn each finding into a rule for the next production.
diagram:
  type: cycle
  title: The analytics loop
  nodes: ["Publish: spec, metadata, captions, disclosure", "Measure: CTR, retention, engagement", "Map drops and bumps to shots", "Rules: hooks, pacing, routing", "Next production"]
  center: "One series"
watch:
  - title: "YouTube Help — audience retention in YouTube Analytics"
    url: https://support.google.com/youtube/answer/9314415
    note: "Learn to read the retention curve and key moments."
  - title: "YouTube Help — disclosing altered or synthetic content"
    url: https://support.google.com/youtube/answer/14328491
    note: "Read when disclosure is required."
quiz:
  - q: "The retention curve loses 18 points between second 2 and second 4, against a typical 0.6 points per second. What is the likely problem?"
    options: ["The thumbnail", "The hook: the opening does not keep the promise of the title and thumbnail, or it starts too slowly", "The music license", "The captions"]
    answer: 1
    explain: "A steep early drop is the most common finding. Test a result-first hook (C02·M05) in the next video."
  - q: "A bump in the curve at 0:41 means what?"
    options: ["A bug", "Viewers rewatch or skip back to that moment: it is strong or unclear; check which", "More new viewers", "A loudness peak"]
    answer: 1
    explain: "Bumps mark the moments that viewers care about. Look at the shot before you decide."
  - q: "Video A has 5.1 % CTR, video B 3.2 %. A is a short, B a 10-minute explainer. What can you conclude?"
    options: ["A's thumbnail is better", "Little: compare like with like (same series, format, length, audience, time); different formats have different normal rates", "B is bad", "Make only shorts"]
    answer: 1
    explain: "Benchmarks come from comparable videos, and small samples mislead (C15·M01)."
  - q: "Where does the platform's video ID go after upload?"
    options: ["Nowhere", "Into the asset record with your asset ID, so analytics can be joined with the prompt log, the shot list, and the costs", "Into the title", "Into the file name"]
    answer: 1
    explain: "The join between the platform data and your production data is what makes the loop work."
  - q: "Your video shows a realistic person who does not exist, saying things in a news-like style. What must you do on a platform that has a synthetic-content setting?"
    options: ["Nothing", "Turn on the platform's altered or synthetic content disclosure, add a visible label if the law or the platform requires it, and keep C2PA credentials in the file where supported", "Only add a hashtag", "Blur the face"]
    answer: 1
    explain: "Realistic synthetic people and events need disclosure (C16·M03)."
  - q: "Which thumbnail rule is supported by most platform guidance and testing?"
    options: ["Many small words", "One clear face or object, high contrast, few words, and a promise that the first seconds keep", "A full frame of text", "A random frame"]
    answer: 1
    explain: "Generate options (C04) and test them with the platform's thumbnail testing where it exists."
  - q: "After 8 videos you find: 'result-first hooks keep 20 % more viewers at 30 s'. What do you do with it?"
    options: ["Remember it", "Write it as a rule in the hook library and the treatment template, with the data, so writers and agents use it in the next scripts", "Post it", "Nothing"]
    answer: 1
    explain: "A finding that is not written into a template is lost."
deeper:
  - title: "YouTube Data API — videos.insert"
    url: https://developers.google.com/youtube/v3/docs/videos/insert
  - title: "TikTok for Developers — Content Posting API"
    url: https://developers.tiktok.com/doc/content-posting-api-get-started
  - title: "YouTube Analytics API — reports"
    url: https://developers.google.com/youtube/analytics
---
## Learn

### Publish correctly
Publishing is the last gate of the pipeline (C12·M04). Check:
- **Spec** per platform: aspect ratio, maximum length, resolution, frame rate, audio (`spec_check.py`, C09·M04).
- **Metadata:** a title with a clear promise, a description with context, chapters, credits, and tags.
- **Thumbnail:** one clear face or object, high contrast, few words. The first seconds of the video must keep its promise.
- **Captions:** an uploaded caption file (SRT or VTT) in each language (C08·M04, C15·M02).
- **AI disclosure:** the platform's altered or synthetic content setting where required, a visible label where the law or the platform requires it, and C2PA content credentials in the file where supported (C16·M03).

### Platform APIs
Most platforms offer APIs to upload, set metadata, schedule, and read analytics. Use them for series and variants:
- store your credentials in a secret manager (C13·M05);
- after upload, store the platform's video ID with your asset ID;
- read analytics on a schedule into the same database.
The join of platform data with production data (the shot list, the prompt log, the costs) is what makes the loop useful.

### Read the data
- **Click-through rate (CTR):** the share of people who saw the thumbnail and clicked. It measures the thumbnail and the title.
- **Retention curve:** the share of viewers still watching at each second. A steep drop marks a weak moment; a bump marks a rewatched moment.
- **Average view duration** and the share at fixed points (3 s, 30 s, the end).
- **Engagement:** comments, shares, saves.
Compare like with like: the same series, format, length, audience, and time of year. Small samples mislead (C15·M01).

### Map moments to shots
A drop at 0:22 is only useful when you know what is at 0:22. With the shot list and its durations, every second maps to a shot ID. Typical findings:
- a steep drop in the first 3–5 s: the hook does not keep the promise, or it starts too slowly;
- a drop at a cut: a confusing cut or a broken continuity (C02·M04);
- a drop before the end card: the payoff came too early, or the end is too long;
- a bump: a strong or unclear moment; watch it to decide.

### Watch for false lessons
Analytics can mislead:
- **Small samples:** three videos are not a pattern (C15·M01).
- **Different traffic:** a video shown on the home feed and one found by search have different viewers.
- **Seasonal effects:** a holiday week changes all numbers.
- **Several changes at once:** a new hook and a new thumbnail in the same video cannot be separated.
Write each finding with its sample size and the conditions, and test it again before it becomes a fixed rule.

### Close the loop
Once a month, review the series: three findings, each with its data. Write each one into the tools that make the next video:
- the **hook library** (hook types with their measured hold rates);
- the **treatment template** and pacing rules (C03·M02);
- the **routing table** (which model for which shot type, C05·M06);
- the **thumbnail rules**.
Agents (C12) that write scripts and shot lists read these files, so the findings reach production automatically.

## Tool walkthrough

### Find the drops and map them to shots

```bash
python starter/pipeline/retention.py retention.csv --shots shots.json
```

Export the retention curve from the platform's analytics as `time_s,pct`. `shots.json` is your shot list with durations.

### Upload with an API (YouTube example)
The YouTube Data API `videos.insert` method uploads a video with its metadata; the response contains the video ID. Store it:

```json
{"asset_id": "camera_ep03_v2", "platform": "youtube", "platform_id": "<video id>", "published": "2026-10-04T18:00:00Z",
 "variant": "hook=result", "cost_usd": 41.20}
```

Other platforms (TikTok Content Posting API, Meta Graph API) have their own upload flows and limits; read their current documentation and review rules before you automate posting.

## Worked example

**Retention test** (2026-10-04, a 60 s curve with three planted moments, mapped to a 5-shot list):

```
start 100 %, end 46 % at 60 s; typical drop 0.60 points/s
  held at 3 s: 90 %
  held at 30 s: 61 %
steep drops: 3 s -9.0 (15x typical) S01 | 4 s -9.0 (15x typical) S01 | 22 s -5.0 (8.3x typical) S03
bumps (rewatching): 41 s +2.5 S05
```

The tool found all three moments and named their shots: a weak hook in S01, a problem in S03 at 22 s, and a rewatched moment early in S05.

**Series of 8 explainers:** average CTR 3.1 %; a steep drop at 0:04 in 6 of 8. Change: start with the result image (hook type "result first", C02·M05) and cut the intro. The next 4 videos: the first steep drop moved to 0:20; average view duration +35 %. The hook library now has: "result-first: 3-second hold 61 % (n = 4) against 47 % for question hooks (n = 8)".

## Lab

**Deliverable:** `C15/M03/` with publishing checklists, the asset records with platform IDs, analytics exports, a retention analysis per video, and a monthly review.

1. Publish (or prepare for publishing, if you cannot publish publicly) 3 videos of your project with spec checks, metadata, thumbnails, captions, and disclosure.
2. Upload with an API (or record each manual step that the API would replace). Store the platform IDs with the asset records.
3. After at least 7 days, export CTR and retention for each video.
4. Run `retention.py` with each video's shot list. Write what is at each steep drop and each bump.
5. Write the monthly review: 3 findings with data, and the change in each tool (hook library, template, routing, thumbnail rules).

**Result checklist**
- [ ] 3 publishing checklists, all passed (including disclosure).
- [ ] Asset records with platform IDs.
- [ ] Retention analysis per video, mapped to shots.
- [ ] Monthly review with 3 rule changes.

## Model answer

**Monthly review (shape of a strong answer):**

| Finding | Data | Rule change |
|---|---|---|
| Question hooks lose viewers at 0:03–0:05 | steep drops 12–15× typical in 3 of 3 question-hook videos | Hook library: result-first is the default; question hooks only with the answer on screen by 2 s |
| Viewers rewatch the "photo comes true" reveal | bumps of +2–3 points at the reveal in 3 of 3 | Treatment template: the reveal moves 5 s earlier; a 1 s hold after it |
| The end card loses 8 points before the CTA | drop at end card start | End card 4 s → 2 s; CTA in the last shot instead |

"CTR (3.4 %, 2.9 %, 3.8 %) varied with the thumbnail; the one with a single face at high contrast was highest. The sample is too small to call it a rule (C15·M01); the next 6 videos test it with the platform's thumbnail test."
