---
title: Transcript-based and script-based assembly
hours: 15
outcomes:
  - Edit talking content by editing a transcript, and keep natural pauses.
  - Assemble a first cut automatically from the shot list and the selects.
  - Use an LLM for a paper edit of long material, and validate every quote against the transcript.
  - Judge the machine cut, and improve rhythm, hook, and coverage in the editor's pass.
keywords: [paper edit, assembly, transcript editing, rough cut]
summary: >
  In transcript editing, the words are the timeline: delete text and you delete media. In an AI production you also
  have the script, the shot list, and the selects, so a script can build the first assembly. For long interviews, an
  LLM can make a paper edit: it chooses and orders quotes for a story. LLMs also invent words and join sentences from
  different places, so every quote must be found exactly in the transcript before it becomes an edit. The machine
  cut is a start. The editor's pass makes the rhythm, the hook, and the emotion.
diagram:
  type: flow
  title: LLM paper edit with validation
  nodes: ["Transcripts with word timestamps", "LLM: story goal + length → quotes in order (JSON)", "Validate: exact quote in transcript?", "Rejects → ask again or choose by hand", "Valid quotes → selects → timeline", "Editor's pass"]
  highlight: [2]
watch:
  - title: "Descript — edit video by editing text (help center)"
    url: https://help.descript.com/
    note: "Look at text-based editing and filler-word removal."
  - title: "TechCrunch — Adobe adds its AI assistant to Premiere (first cut, storyboard to video)"
    url: https://techcrunch.com/2026/06/18/adobe-adds-its-ai-assistant-to-premiere-illustrator-and-indesign/
    note: "Note which tasks the assistant does and which remain with the editor."
quiz:
  - q: "In a transcript editor you delete all the 'um's and every pause. The result sounds wrong. Why?"
    options: ["The audio codec", "Speech needs breaths and pauses; cuts with no gap sound unnatural and fast", "Too many cuts for the NLE", "The transcript is wrong"]
    answer: 1
    explain: "Remove fillers that distract. Keep the breaths and pauses that carry rhythm and meaning."
  - q: "An LLM returns the quote 'It is raining, and now it is real.' The speaker said 'It is raining in here.' and, 3 seconds later, '…and now it is real.' What is this, and what does the validator do?"
    options: ["A good quote", "A merged quote: two sentences from different places joined into one; the validator rejects it because the words are not contiguous in the transcript", "A translation", "A typo"]
    answer: 1
    explain: "A merged quote changes what the person said. In documentary and brand work this is not acceptable, unless the cut is visible and the meaning is kept. Choose by hand."
  - q: "The LLM writes 'I took this picture an hour ago.' The speaker said 'photo'. Why must you reject it?"
    options: ["You must not; the meaning is the same", "The media contains 'photo', so there is no audio of 'picture'; the edit cannot be made from the footage", "Picture is a better word", "The LLM is always right"]
    answer: 1
    explain: "A paper edit must point to real words in the media. A paraphrase has no media."
  - q: "What must the LLM paper-edit prompt contain?"
    options: ["Only 'make a good video'", "The story goal, the target length, the audience, the transcripts with IDs, and the rule 'quote exactly; return JSON with file and quote'", "The video files", "The music"]
    answer: 1
    explain: "Give the goal, the constraints, and the output format. The validator then checks the most dangerous failure: invented words."
  - q: "How do you find the in and out times of a valid quote?"
    options: ["Ask the LLM", "From the word timestamps of the transcript: the start of the first word and the end of the last word, plus a small pad", "Guess", "From the file size"]
    answer: 1
    explain: "Word timestamps (from transcription, C06·M02) make paper edits exact."
  - q: "A machine assembly from the shot list is coherent but feels flat. What does the editor usually change?"
    options: ["Nothing", "Pauses and pacing, a stronger hook in the first seconds, reactions and inserts, J and L cuts, and B-roll timed to words", "Only the music", "The color"]
    answer: 1
    explain: "The machine follows the plan. The editor follows the feeling: rhythm and emphasis."
  - q: "Why put B-roll on words, not on fixed time intervals?"
    options: ["It is cheaper", "B-roll that appears on the word it illustrates ('the locker…') makes the meaning clear; word timestamps give the exact place", "Platforms require it", "It saves render time"]
    answer: 1
    explain: "Cut to the image when the word is said, or just before it."
deeper:
  - title: "WhisperX — word-level timestamps and speaker diarization"
    url: https://github.com/m-bain/whisperX
  - title: "Murch — In the Blink of an Eye (editing judgment)"
    url: https://en.wikipedia.org/wiki/In_the_Blink_of_an_Eye_(Murch_book)
  - title: "pyannote.audio — speaker diarization (who speaks when)"
    url: https://github.com/pyannote/pyannote-audio
---
## Learn

### Transcript editing
A transcript editor shows the words of the media, with each word linked to its time. When you delete text, the editor deletes that media. When you move a sentence, it moves the media. Many NLEs now have a transcript panel, and some tools are built around it.

Rules:
- Remove fillers ("um", "you know") when they distract. Do not remove all of them; people sound unnatural without them.
- Keep breaths and short pauses. A cut with no pause sounds rushed.
- Check every cut by ear. A cut in the middle of a word or a breath is audible.
- Look at the picture too: a text cut can make a jump cut in the face. Hide it with B-roll or a cutaway.

### Script-based assembly
In an AI production you already have:
- the script and the shot list with shot IDs and planned durations (C03·M02);
- the selects with in and out points (C05·M06);
- the native audio, or the replaced dialogue (C05·M04, C06).
So a script can build the first assembly in shot order with the planned durations (M01: `selects_to_otio.py`). The assembly shows the story at once, with gaps where shots are missing. Watch the assembly before you fix any shot. Many problems are story problems, not shot problems: a beat that is not needed, a missing reaction, or an order that hides the turn. Fixing those first saves work on shots that you would cut later.

### LLM paper edit
For long material (interviews, conversations, events), a paper edit is a list of quotes in story order. An LLM can make a first paper edit from transcripts in seconds:
1. **Transcribe** each file with word timestamps and speakers (C06·M02).
2. **Prompt** the LLM with: the story goal, the audience, the target length, the transcripts with file IDs, and strict rules: "quote exactly, never change a word, do not join sentences from different places, return JSON: file, quote, reason".
3. **Validate** each quote (below).
4. **Build** selects from the valid quotes, then the timeline.
5. **Fill** gaps by hand: choose a quote yourself, or ask the LLM again with the reject reasons.

### Validation is mandatory
LLMs make three typical errors in paper edits:
- **Invented words:** a quote that nobody said.
- **Merged quotes:** two sentences from different places joined into one. It changes what the person said.
- **Paraphrase:** "picture" instead of "photo". There is no media for the new word.

A validator accepts a quote only if its words are an exact, contiguous sequence in the named transcript (after you ignore case and punctuation). Then the times of the first and the last word give the in and out points. Rejected quotes go back to you with the reason. `starter/tools/papercut.py` does this and writes a selects file for the timeline script.

When a merged quote is right for the story, make it an edit that viewers can see (a cut to B-roll or a reaction between the two parts), and keep the meaning of what the person said.

### The editor's pass
Watch the assembly once without stopping. Note where you lose interest. Then:
- **Pacing:** tighten or open pauses; remove repeated ideas.
- **Hook:** move the strongest moment into the first seconds if the start is weak.
- **Coverage:** add reactions and inserts (C05·M06); they control rhythm.
- **J and L cuts** at dialogue cuts (M01).
- **B-roll on words:** cut to the image on the word that it illustrates. Use the word timestamps.
- **Music:** temp music and the energy curve (C06·M03).

## Tool walkthrough

### Paper-edit prompt (any LLM)

```text
You are the story editor. Goal: a 90 s brand story for city cyclists: problem → turning point → result.
Use only the transcripts below. Rules:
1. Quote exactly. Never change, add, or remove a word inside a quote.
2. Never join text from different places into one quote. Make two quotes instead.
3. Return JSON only: [{"id": "P01", "file": "<file id>", "quote": "<exact words>", "reason": "<story role>"}]
4. Total spoken length about 100 s (the editor will cut to 90 s).
Transcripts: {"interview_a": "<text>", "interview_b": "<text>"}
```

### Validate and build

```bash
python starter/tools/transcribe.py interview_a.mp4 --model small --out tr/        # C06·M02
python starter/tools/papercut.py edit.json --transcripts tr/ --out pc_selects.csv
python starter/tools/selects_to_otio.py pc_selects.csv --rate 24 --out papercut.otio --fcpxml
```

### In the NLE
Import the FCPXML. Put B-roll on V2 above the interview. Use the transcript panel of your NLE for the fine pass, if it has one.

## Worked example

**Validator test** (2026-10-04). A transcript (faster-whisper, word timestamps) of the line "That's my locker. It is raining in here. I took this photo an hour ago, and now it is real." A paper edit with 4 segments, written like typical LLM output:

| ID | Quote | Validator |
|---|---|---|
| P01 | "I took this photo an hour ago," | Valid: 2.19–4.03 s |
| P02 | "That's my locker. It is raining in here." | Valid: 0.00–2.13 s |
| P03 | "It is raining, and now it is real." | REJECT: not found as spoken (3 of 8 words match in a row) — a merged quote |
| P04 | "I took this picture an hour ago." | REJECT: not found as spoken (3 of 7 words match in a row) — a paraphrase |

The two valid segments became selects (with a 0.15 s pad) and a timeline. The timeline script also warned that the clip was 25 fps on a 24 fps timeline.

**Brand story: 3 interviews (45 min) → 90 s:**
1. Transcripts with speakers.
2. LLM paper edit: 11 segments, 104 s; story: problem → turning point → result.
3. Validation: 2 rejects. Segment 6 merged two sentences from minutes 4 and 31. Segment 9 changed "bike lane" to "cycle path". Both replaced by hand.
4. Timeline built; B-roll from tagged selects placed on keywords.
5. Editor's pass: cut to 90 s, added 3 reactions, moved the strongest quote to the opening.

## Lab

**Deliverable:** `pipelines/papercut/` with transcripts, the LLM prompt and output, the validator report, the machine cut, your final cut, and a change list.

1. Get 20–40 minutes of interview material: record conversations with consent, or use public-domain or CC-licensed interviews (record the license in the rights log).
2. Transcribe with word timestamps.
3. Write the paper-edit prompt. Run it. Save the JSON.
4. Validate with `papercut.py` (or your own validator). Fix or replace every reject. Build the timeline.
5. Do your editor's pass in the NLE.
6. Compare the machine cut and your cut. List 10 changes and the reason for each.

**Result checklist**
- [ ] Validator report with at least one reject that you found and fixed.
- [ ] Machine cut and final cut exported.
- [ ] 10 changes with reasons.
- [ ] Rights-log lines for the interview material.

## Model answer

**Validator summary (shape of a strong answer):** "The LLM returned 14 segments. 11 valid. 3 rejects: 1 merged quote (minutes 3 and 22), 1 paraphrase ('started' for 'began'), 1 quote from the wrong file. After a second prompt with the reject reasons, 2 of 3 were replaced by valid quotes; I chose the third by hand."

**Change list (extract):**

| # | Change | Reason |
|---|---|---|
| 1 | Moved P07 ("I almost quit") to the start | The machine cut started with context; the hook was at 40 s |
| 2 | Removed P03 | It repeats P02 |
| 3 | Added a 1.5 s reaction after P07 | The line needs a beat to land |
| 4 | J-cut into P09 (0.4 s) | The cut felt abrupt |
| 5 | B-roll of the bike lane on the word "lane" | Shows what she says |
| … | | |

"The machine cut was coherent, with even pacing and no reactions. Most of my changes were about rhythm and the hook. The validator caught 3 problems that I would not have heard in a fast review, because the merged quote sounded natural."
