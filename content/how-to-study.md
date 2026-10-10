# How to study

## Order
Do the levels in order. Inside a level, you can do the courses in any order, unless a course lists a prerequisite.

| Level | Courses | Focus |
|---|---|---|
| L1 | C01–C03 | How the models work, screen language, LLMs and agents |
| L2 | C04–C07 | Image, video, audio, and 3D/world generation |
| L3 | C08–C10 | AI-native editing and finishing |
| L4 | C11–C15 | Pipelines, orchestration, infrastructure, fine-tuning, scale |
| L5 | C16–C18 | Law and provenance, frontier research, capstone |

## Each module
1. **Outcomes.** Read them first. They tell you what you must be able to do.
2. **Listen.** A short spoken summary (synthetic voice). The transcript is below the player.
3. **Learn.** The concept text. It uses no product names.
4. **Diagram.** The structure of the idea in one picture.
5. **Watch.** Selected videos and pages, with a note on what to look at.
6. **Worked example.** Real prompts, settings, and decisions, step by step.
7. **Lab.** Do it. Each lab gives a deliverable and a result checklist.
8. **Quiz.** Each answer shows an explanation.
9. **Model answer.** Compare it with your result after the lab.
10. **Go deeper.** Primary sources: papers, model cards, official docs.

## Your production repository
Make one Git repository for the whole program, for example `ai-video-lab/`. Put every lab result in it:

```
ai-video-lab/
  C01/  C02/  ...  C18/
  prompts/          # prompt log: every prompt, model, seed, settings, cost
  rights/           # rights log: sources, licenses, consent records
  evals/            # your model comparison sets and results
  pipelines/        # code, ComfyUI workflows, agent configs
```

Rule: every generated asset has a line in the prompt log. Every asset that you did not make has a line in the rights log. You use these logs in C16 and in the capstone.

## Time
About {{HOURS}} hours in total ({{MODULES}} modules). At 15 hours a week, this is about {{MONTHS_15}} months. At 40 hours a week, it is about {{MONTHS_40}} months. The site adds up these numbers from the module pages.

## When a tool changes
Tools in labs change often. If a lab tool is not available:
1. Read the "Tool landscape" page for the current alternative.
2. Use the same concept and the same result checklist with the alternative.
3. Write the change in your prompt log.
