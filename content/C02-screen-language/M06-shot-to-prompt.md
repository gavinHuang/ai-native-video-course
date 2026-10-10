---
title: Write the shot as a prompt
hours: 9
outcomes:
  - Use a fixed prompt grammar that covers every element of a shot.
  - Write structured (JSON) prompts for complex shots.
  - Adapt prompt length and style to the behavior of each model.
  - Review a generated shot against its specification and decide keep / fix / regenerate.
keywords: [prompt grammar, structured prompt, shot specification, review]
summary: >
  A shot prompt is a specification. Use the same order every time: shot and camera, subject, action, setting, light
  and color, sound, and style. For complex shots, use a structured prompt in JSON, so each element has its own
  field and you can change one field at a time. Models differ: some prefer short prompts, some prefer long and
  specific ones. Test this with your eval set. Review each output against the specification, and decide to keep,
  fix in post, or regenerate.
diagram:
  type: flow
  title: Prompt grammar for one shot
  nodes: ["Cinematography: size, angle, lens, move", "Subject: who / what, with fixed descriptors", "Action: one clear action with timing", "Context: place, time, weather", "Light + color", "Sound: dialogue, effects, ambience", "Style + format: look, ratio, duration"]
  highlight: [0]
watch:
  - title: "Google Cloud — Veo prompt guide"
    url: https://cloud.google.com/vertex-ai/generative-ai/docs/video/video-gen-prompt-guide
    note: "Read the prompt elements and examples. Compare them with the grammar in this module."
  - title: "Google Cloud Tech on X — A formula for effective prompts"
    url: https://x.com/GoogleCloudTech/status/1994889105860145655
    note: "Cinematography + Subject + Action + Context + Sound."
  - title: "Kling AI — official user guide"
    url: https://app.klingai.com/global/quickstart/klingai-video-3-model-user-guide
    note: "Read the multi-shot and camera sections."
quiz:
  - q: "Why use a fixed order in prompts?"
    options: ["Models require alphabetical order", "You do not forget elements, and you can compare and change one element at a time", "It makes prompts shorter", "It is cheaper"]
    answer: 1
    explain: "A fixed grammar is a checklist and makes A/B tests clean."
  - q: "A practitioner post says 'model X prefers short prompts'. How do you use this?"
    options: ["As a rule for all models", "As a hypothesis: test short and long versions of the same specs on your eval set, and write the result in that model's prompt adapter", "Ignore it", "Use only short prompts from now on"]
    answer: 1
    explain: "Reported tendencies change with versions. Your own test decides."
  - q: "A shot is perfect except a 6-frame flicker on a sign. Best decision?"
    options: ["Regenerate many times", "Keep, and fix in post (paint-out or trim)", "Change the model", "Increase CFG"]
    answer: 1
    explain: "Small defects are often cheaper to fix in finishing (C09) than to regenerate."
  - q: "Which is a good subject descriptor for consistency?"
    options: ["'a beautiful woman'", "'Mara, 30s, short black bob, small scar on left eyebrow, olive raincoat with brass buttons'", "'the girl from before'", "'someone'"]
    answer: 1
    explain: "Specific, fixed descriptors (plus references) repeat the same person."
  - q: "Your prompt says 'no people in the background', and the model adds people. Why, and what is the fix?"
    options: ["The model is broken", "The words 'people' and 'background' are in the prompt and pull toward them; describe what you want ('an empty street, every window dark') and use a negative prompt only where the model supports one", "Add 'NO' in capitals", "Use more steps"]
    answer: 1
    explain: "Describe the wanted state. Negative words in a positive prompt often add the thing."
  - q: "A 6 s shot spec has five actions. What do you do?"
    options: ["Generate it as it is", "Split it into shots with one action each, with a clear start and end state; keep timing words for the one action", "Make it 30 s", "Remove the camera move only"]
    answer: 1
    explain: "One shot, one action, one camera move. Many actions in one clip are rushed or merged."
deeper:
  - title: "OpenAI cookbook — Video prompting guide (archived concepts still useful)"
    url: https://cookbook.openai.com/examples/sora/sora2_prompting_guide
  - title: "Runway — Gen-4 prompting guide"
    url: https://help.runwayml.com/hc/en-us/articles/39789879462419-Gen-4-Video-Prompting-Guide
---
## Learn

### Prompt grammar
Use one order for every shot:
1. **Cinematography:** shot size, angle, lens, camera move.
2. **Subject:** fixed descriptors (name, age, hair, clothes, one unique mark).
3. **Action:** one clear action, with timing words ("slowly", "after a pause").
4. **Context:** location, time of day, weather.
5. **Light and color:** source, direction, temperature, contrast, palette.
6. **Sound:** dialogue (in quotes), sound effects, ambience, music (or "no music").
7. **Style and format:** film stock or look, aspect ratio, duration.

### Fixed descriptors
Write each character, product, and location once in a "bible" (C04). Copy the same words into every prompt. Do not paraphrase: "olive raincoat" in one prompt and "green coat" in the next are two different coats for the model. Combine words with reference images. The words then confirm what the image shows, and add what it cannot show (the scar on the other side of the face, the brand of the watch).

### Structured (JSON) prompts
For complex shots, a JSON structure separates the elements:
```json
{
  "shot": {"size": "medium close-up", "angle": "eye level", "lens": "85mm", "move": "slow push-in"},
  "subject": "Mara, 30s, short black bob, scar on left eyebrow, olive raincoat",
  "action": "she reads a printed photo, then looks up, surprised",
  "context": "hospital locker room, night",
  "light": "cold fluorescent top light, warm practical from an open locker, 4:1 contrast",
  "audio": {"ambience": "distant hospital beeps", "sfx": "paper rustle", "dialogue": "none", "music": "none"},
  "style": "35mm film grain, muted teal and amber",
  "format": {"ratio": "9:16", "duration_s": 6}
}
```
Many models read JSON well, because their text encoders are LLMs. The main benefit is for you: you change one field at a time and log it. Practitioners on X report that it is best to start with a small structure and add fields only when needed.

### Model behavior
Models react differently to the same prompt. Some prefer short, simple prompts; others reward long, specific ones; almost all improve a lot with reference images (dated examples in the Tool walkthrough). Treat such reports as hypotheses, and test them with your eval set (C01·M07). Keep one "prompt adapter" per model: a short note on what works, with the date and the model version of each rule.

### Negative instructions
Saying what you do not want often adds it: "no text on the wall" can put text on the wall, because the words "text" and "wall" are now in the prompt. Describe what you want instead ("a plain, empty concrete wall"). Use a real negative prompt only where the model supports it (C01·M05).

### One shot, one action
A generated clip of 5–10 s can hold one clear action and one camera move. "She opens the door, walks in, sees the letter, picks it up, and cries" is five actions; the model will rush, skip, or merge them. Split them into shots, each with one action and a clear start and end state. Timing words help inside one action: "after a pause", "slowly, over the whole shot".

### Dialogue in prompts
Put dialogue in quotes, name the speaker, and give the delivery: `Mara (quietly, tired): "It was raining in the photo."` Keep lines short (one sentence per 3–4 s). For exact lines and voices, generate the voice separately and use audio-to-video or lip sync (C06).

### Review against the specification
For each output, check:
- Did it follow the cinematography? subject descriptors? action? light? sound?
- Defects: hands, faces, text, physics, flicker, morphing.

Decide:
- **Keep:** meets the spec.
- **Fix in post:** small defect (C09, C10).
- **Regenerate:** fails a core element (wrong action, wrong identity).
- **Change approach:** fails 3 times → use a reference, a first frame, a different model, or split the shot.

## Tool walkthrough

### Dated model notes (as of 2026-10, from practitioner reports)
- Kling 3.0: short, simple prompts work best; reference images help a lot.
- Seedance 2.x: rewards long, very specific prompts.
- Veo 3.1: structured (JSON-like) prompts with sections for shot, subject, scene, light, and audio work well.
Test each claim on your eval set before you write it in a prompt adapter.

### Log every try
```bash
python starter/tools/promptlog.py add --id S07-try2 --model modelA --prompt-file prompts/S07.json --seed 1234 \
  --cost 0.6 --file out/S07-try2.mp4 --status kept --note "eyeline fixed; photo text replaced in post"
```

## Worked example

Spec: "Shot 7: MCU, eye level, 85 mm, slow push-in. Mara reads a photo, then looks up, surprised. Locker room, night. Cold top light + warm practical. Paper rustle. 6 s, 9:16."

- Try 1 (plain prompt, Model A): good light; she looks into the lens (wrong). → Regenerate with "looks up and slightly off-camera left".
- Try 2: correct; the photo shows unreadable text that changes each frame. → Fix in post: replace the photo with a still insert shot (C09).
- Try 3 for comparison (JSON prompt, Model B): push-in is too fast; face drifts. → Note in the model adapter: "Model B: use 'very slow' for push-ins".

Result: try 2 + insert shot. Total: 3 generations, 18 s generated, 6 s used.

## Lab

**Deliverable:** `C02/M06/` with a shot list of 8 shots, prompts in plain and JSON form, outputs, and a review sheet.

1. Take the treatment from M05. Write 8 shot specifications with the grammar.
2. For each shot, write a plain prompt and a JSON prompt.
3. Generate each shot with 2 models (plain on one, JSON on the other, then swap for 2 shots).
4. Review with the decision rule. Record usable rate.
5. Write a "prompt adapter" note for each model (5 lines).

**Result checklist**
- [ ] 8 specs in the 7-part grammar.
- [ ] Review sheet with keep / fix / regenerate for each try.
- [ ] Two model adapter notes.

## Model answer

A good review sheet shows that most failures come from three places: subject drift (fix with references), wrong eyeline or direction (fix with explicit words), and text or small objects (fix in post or with inserts). The adapters contain practical rules such as "Model A: max. 60 words; name only one move; put dialogue last" and "Model B: long prompts OK; needs 'very slow' for camera speed; JSON accepted".

A strong sheet gives the usable rate per shot and per model (for example "Model A plain: 5 of 8 shots kept or fixable; Model B JSON: 4 of 8"), and notes that 8 shots are too few to rank the models: it is a first impression, to be tested on the eval set (C01·M07).
