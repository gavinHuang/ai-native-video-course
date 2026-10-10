---
title: Coverage, selects, and budgets
hours: 20
outcomes:
  - Plan coverage for generated scenes so that the editor has choices - masters, singles, reactions, inserts, cutaways.
  - Run a generation session like a shoot, with takes, selects, in and out points, and a gap list.
  - Route shots to models by cost per usable second, from your own measured data.
  - Build a budget with caps per shot, track it during sessions, and change the approach when a shot hits its cap.
keywords: [coverage, selects, routing, budget, cost per usable second]
summary: >
  A real shoot films each moment from several angles, called coverage. An AI production must plan coverage on
  purpose, because a model makes only what you ask. Treat each generation as a take: review takes, mark selects
  with in and out points, and write notes, like a script supervisor. Route each shot type to the model with the best
  measured cost per usable second for it. Set a budget and a cap per shot, and track them during each session. When a
  shot hits its cap, change the approach instead of generating more takes. Stop when the edit has enough material.
diagram:
  type: flow
  title: A generation session
  nodes: ["Shot list + routing table + caps", "Generate takes (2–4 per shot)", "Review: select with in/out, note, reject", "Selects bin → editor", "Report: usable seconds, cost, caps", "Gap list → next session"]
  highlight: [2, 4]
watch:
  - title: "Wikipedia — Master shot and coverage"
    url: https://en.wikipedia.org/wiki/Master_shot
    note: "Read how a master shot and closer coverage work together."
  - title: "X — How a creator makes AI UGC ads for US$2–4 (Claude + GPT Image 2 + Seedance 2)"
    url: https://x.com/nestymee/article/2071972061124383110
    note: "A claim about cost. Note what is counted and what is not (time, failed takes)."
quiz:
  - q: "Why are reaction shots and inserts the most useful coverage in an AI production?"
    options: ["They look good", "They are short and cheap, and they let the editor fix rhythm, hide drift at joins, and cut around defects in other shots", "Platforms need them", "They have no faces"]
    answer: 1
    explain: "A 1.5 s reaction costs little and solves many problems in the edit. Plan them in every scene."
  - q: "A shot has used its US$3 cap with no usable take. What do you do?"
    options: ["Generate until it works", "Stop and change the approach: another mode (I2V from a fixed key frame), a simpler action, another model, or a different shot that tells the same beat", "Raise the cap", "Delete the shot"]
    answer: 1
    explain: "A cap is a signal that the method does not work for this shot. More takes of the same method rarely help."
  - q: "Hero dialogue: Model A US$0.10/s with 50 % usable; Model B US$0.25/s with 80 % usable. Which is cheaper per usable second?"
    options: ["A: 0.20 vs B: 0.31, so A", "B, because more takes are usable", "Equal", "Cannot tell"]
    answer: 0
    explain: "Cost per usable second = price / usable share. A: 0.10 / 0.5 = 0.20. B: 0.25 / 0.8 = 0.31. B may still be the right choice if the shot is hard and time matters; decide with both numbers."
  - q: "How do you set the budget for a shot?"
    options: ["A fixed US$1 per shot", "Target usable seconds × measured cost per usable second for that shot type × a safety factor (about 1.5)", "The total budget divided by the number of shots", "Whatever the model costs"]
    answer: 1
    explain: "The formula uses your measured data per shot type. The safety factor covers bad luck and notes from the client."
  - q: "After session 1, the editor says: 'I cannot cut from the wide to Mara's close-up; the eyeline is wrong, and I have no reaction from Leo.' What is this list called, and what happens to it?"
    options: ["A complaint", "The gap list: it becomes the shot list of session 2", "The budget", "The look bible"]
    answer: 1
    explain: "Sessions end with a gap list from the edit. The next session makes only what the edit needs."
  - q: "A creator claims US$2–4 per finished ad. What must you check before you use this number in a quote?"
    options: ["Nothing", "What is counted: failed takes, subscriptions, time, edits, music licenses; then measure your own cost per finished minute with your tracker", "The creator's follower count", "The video length only"]
    answer: 1
    explain: "Reported numbers are claims. Your quote must use your own measured numbers."
  - q: "When do you stop generating?"
    options: ["When the budget is empty", "When the edit has enough good material for every beat, with at least one alternative for key moments", "After 100 takes", "Never"]
    answer: 1
    explain: "The edit is the goal. Extra takes beyond what the edit needs are waste."
deeper:
  - title: "Wikipedia — Script supervisor (the role that logs takes and continuity)"
    url: https://en.wikipedia.org/wiki/Script_supervisor
  - title: "Murch — In the Blink of an Eye (on cutting and coverage)"
    url: https://en.wikipedia.org/wiki/In_the_Blink_of_an_Eye_(Murch_book)
---
## Learn

### Coverage
On a film set, each moment is filmed from several angles. This is **coverage**. The editor needs it: to choose the best performance, to control rhythm, and to cut around mistakes. A video model makes only what you ask. So in an AI production, coverage must be planned on purpose.

For each scene, plan:
- a **master** (wide) of the whole action;
- **singles** or over-the-shoulder shots for each speaker;
- **reactions:** listening faces, 1–2 s each;
- **inserts:** hands, objects, details;
- **cutaways:** the place, the weather, a detail of the room;
- an **alternative angle** for the key moment.

Reactions and inserts are the most useful coverage. They are short and cheap. They let the editor change the rhythm, hide a join between generations, and cut around a defect in another shot (a hand flicker at 4 s).

### Takes and selects
Run a session like a shoot. Each generation is a take, named by shot: `S07_t03`. Review the takes of a shot together, in a grid. For each take record:
- a decision: select, maybe, or reject;
- for a select, the usable part (in and out points);
- a note: "hand flicker after 4.1 s", "best eyeline", "face drift".
The selects bin goes to the editor with the trims. This is the job of the script supervisor on a set. In this program it is your job, and `takes.py` keeps the log.

### Routing
Different shot types have different best models. Make a routing table from your own data (the mode table of M01, your eval set from C01·M07):

| Shot type | Model class | Mode | Reason |
|---|---|---|---|
| Hero product | Premium hosted | I2V + product references | Highest usable rate for logos |
| Dialogue | Joint audio-video | R2V + voice reference | Lip sync |
| Wide B-roll | Open model on a rented GPU | T2V | Lowest cost per usable second |
| Inserts | Fast model | I2V | Short and simple |

Update the table after every project. Models change monthly.

### The budget
Set a budget per shot before the session:

```
shot budget = target usable seconds × cost per usable second (for this shot type) × 1.5
```

The safety factor (about 1.5) covers bad luck and client notes. Set the cap of the shot to this budget. Track actual spend per shot during the session.

When a shot reaches its cap, stop. More takes of the same method rarely help. Change the approach:
1. another mode (I2V from a fixed key frame instead of R2V);
2. a simpler action, or a shorter clip;
3. another model;
4. another shot that tells the same beat (a reaction instead of the action).

### Sessions and gap lists
A project has several sessions. Each session ends with a rough edit of the selects and a **gap list**: what the edit still needs. "No reaction of Leo at the key line." "The OTS on Mara has the wrong eyeline." The gap list is the shot list of the next session. This keeps generation focused on what the edit needs. Stop when every beat has good material, with one alternative for the key moments.

### Reported numbers
Creators report very low costs, for example US$2–4 per short ad made with an LLM, an image model, and a video model. Short-drama producers in China report about ¥200 per finished minute with end-to-end tools. These are claims. They often leave out failed takes, subscriptions, edits, music, and time. Use your own tracker for your quotes.

## Tool walkthrough

### A session with `takes.py`

```bash
# before the session: targets and caps from the formula
python starter/tools/takes.py budget S07 --target 4 --cap 3.00
python starter/tools/takes.py budget S07r --target 1.5 --cap 0.40     # a reaction

# during the session: one line per take
python starter/tools/takes.py add S07 --model kling-3.0 --mode i2v --dur 6 --cost 0.60 --file takes/S07_t01.mp4

# review
python starter/tools/takes.py review S07_t01 select --in 0.4 --out 4.1 --note "hand flicker after 4.1 s"

# after the session
python starter/tools/takes.py report      # cost per usable second per model; coverage and cap per shot
python starter/tools/takes.py selects > selects.csv    # for the editor
```

The report marks each shot as `covered`, `GAP <seconds>`, or `OVER CAP`. Copy the gaps into the gap list.

### Selects into the edit
`selects.csv` has the file, the in point, and the out point of each select. In C08·M02 you turn this list into a timeline automatically (OTIO). For now, import the files into your editor and set the in and out points by hand.

## Worked example

**Scene: café dialogue, 40 s, 9 planned shots + 6 coverage shots.**

Measured cost per usable second from the M01 mode table: dialogue (joint audio, R2V) US$0.20; reactions and inserts (fast model, I2V) US$0.13.

| Shot group | Target usable s | Cost per usable s | × 1.5 | Cap |
|---|---|---|---|---|
| 9 dialogue shots | 25 | 0.20 | | US$7.50 |
| 6 coverage shots | 20 | 0.13 | | US$3.90 |
| Total | | | | US$11.40 |

**Session 1:** 31 takes, US$8.20, 13 selects. The rough edit gives the gap list:
1. No reaction of Leo at the key line (S05).
2. The OTS on Mara (S06) has the wrong eyeline: she looks camera-left; she must look camera-right.
3. S08 reached its cap (US$1.50) with no select: Mara's hand morphs when she pushes the photo.

**Changes:** for S08, a new approach: an insert of the photo sliding (hands only, I2V) plus a reaction. For S06, a new key frame with the eyeline fixed (C04·M02), then I2V.

**Session 2:** 6 takes, US$1.60. All gaps closed. Total US$9.80, under the cap of US$11.40. The usable share by model is written back into the routing table.

## Lab

**Deliverable:** `C05/M06/` with the coverage plan, the routing table, the budget, the take log, the selects, two gap lists, a 60 s scene, and a report.

1. Plan coverage for a 60 s scene of your story: a master, singles, 3 reactions, 3 inserts, 2 cutaways.
2. Write the routing table from your M01 data and your eval set.
3. Set targets and caps for every shot with the formula.
4. Run session 1. Log every take. Review every take. Make a rough edit from the selects. Write the gap list.
5. Run session 2 from the gap list only. Respect the caps: when a shot reaches its cap, change the approach and write the change.
6. Edit the 60 s scene from selects only.
7. Report: planned versus actual cost per shot and in total; usable share per model; which caps were reached and what you changed. Update the routing table.

**Result checklist**
- [ ] Coverage plan with reactions, inserts, and cutaways.
- [ ] Take log with in and out points and notes for every take.
- [ ] Two gap lists.
- [ ] 60 s edit.
- [ ] Planned-versus-actual report and an updated routing table.

## Model answer

A strong report is short and uses numbers:

| | Planned | Actual |
|---|---|---|
| Total cost | US$14.20 (caps) | US$11.65 |
| Takes | — | 47 |
| Usable seconds in selects | 60 | 74 (14 s of alternatives) |
| Usable share, hosted dialogue model | 50 % (from M01) | 44 % |
| Usable share, fast model (reactions, inserts) | 30 % | 41 % |

"Two shots reached their caps. S08 (hand pushes the photo) failed 4 times on the hand; I replaced it with an insert and a reaction, which cost US$0.45 and cut better. S12 (wide with rain) failed on the rain physics; I switched to the open model with a control video from a 3D layout (C07·M03) on the second session."

"Reactions and inserts were 25 % of the takes and 9 % of the cost, and they are in 11 of the 22 cuts of the final edit. They solved every continuity problem at the joins."

The updated routing table moves reactions and inserts to the fast model for the next project, and keeps hero dialogue on the hosted model despite its lower usable share, because its lip sync was the best.
