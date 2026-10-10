---
title: End-to-end character pipeline
hours: 16
outcomes:
  - Build a pipeline from character references and a script line to a lip-synced dialogue shot.
  - Measure identity automatically with face embeddings, and set a reject threshold from your own data.
  - Retry failed takes automatically and keep a report of every try.
  - Package the pipeline with named inputs, a README, and a lock file, so another person can run it in 30 minutes.
keywords: [character pipeline, identity score, lip sync, subgraph, cosine similarity]
summary: >
  A character pipeline turns a script line into a finished shot with the same character every time. The stages are:
  references, a start frame made from the references and the shot prompt, image-to-video with the spoken line as
  audio input, and an identity check. A face embedding model turns each face into a vector. Cosine similarity with
  the reference vector gives the identity score. Set the reject threshold from takes that you judged by eye. On a
  reject, the pipeline tries the next seed. A LoRA makes identity stronger; you add it in C14 and measure the gain.
diagram:
  type: flow
  title: Character pipeline (references first)
  nodes: ["Character refs + place ref (C04·M03)", "Start frame: 2-reference graph + shot prompt", "Line audio: fixed voice (C06·M01)", "Image + audio → video: lip sync (LTX-2.3)", "Identity score: face embeddings vs refs", "PASS → deliver · REJECT → next seed"]
  highlight: [4]
watch:
  - title: "OpenCV — face detection (YuNet) and face recognition (SFace) tutorial"
    url: https://docs.opencv.org/4.x/d0/dd4/tutorial_dnn_face.html
    note: "Read how detection, alignment, and the cosine score work. The starter scorer uses these two models."
  - title: "The Daring Creatives — Mickmumpitz publishes the workflow file with every video"
    url: https://www.thedaringcreatives.com/creator-stories/mickmumpitz-comfyui-workflows/
    note: "Read how a creator structures and shares character workflows."
  - title: "Lightricks — LTX-2.3 model card (audio-to-video input)"
    url: https://huggingface.co/Lightricks/LTX-2.3
    note: "Read what the model does with an input audio track."
quiz:
  - q: "Your identity scorer gives 0.67 for two real photos of the same person and 0.14 for a different person. A generated take scores median 0.52, minimum 0.20. What do you check first?"
    options: ["Nothing; the median passes", "The frames near the minimum: a head turn, a hand over the face, or a short identity drift", "The audio track", "The file size"]
    answer: 1
    explain: "The median says the take is mostly on-model. The minimum says that some frames are not. Look at the worst frame that the report names. If the drift is on screen for more than a few frames, reject or cut around it."
  - q: "Why does the pipeline compare against the mean of several reference embeddings, not one?"
    options: ["It is faster", "One photo carries its own angle and light; the mean of front, 3/4, and side refs is a more stable identity", "The model needs exactly three images", "It makes the score higher for every face"]
    answer: 1
    explain: "A single reference also encodes its pose and lighting. Averaging several normalized embeddings reduces that bias."
  - q: "How do you choose the reject threshold?"
    options: ["Use 0.5 because it is the middle", "Score 20 or more takes that you judged by eye as on-model or off-model, then choose the value that separates the two groups best", "Use the highest score you ever saw", "Ask the model"]
    answer: 1
    explain: "Generated faces, lighting, and styles change the score range. A threshold is a decision rule that you calibrate on labeled examples, like any classifier threshold."
  - q: "When do you use a separate lip-sync stage instead of letting a joint audio-video model invent the voice?"
    options: ["Never", "When the voice must be the same fixed voice in every episode, for example a cloned or designed voice with consent", "Only for music videos", "Only when the character is animated"]
    answer: 1
    explain: "If the model invents the voice, it changes between shots. A fixed voice from C06 gives series consistency. The video model then follows the audio."
  - q: "The pipeline rejects 4 of 5 takes for one shot, always at a profile view. What is the best change?"
    options: ["Lower the threshold until it passes", "Add a profile view to the references (or train a LoRA in C14), and plan the shot with less profile time", "Use more steps", "Remove the identity check"]
    answer: 1
    explain: "The failure has a cause: the references do not show that angle. Fix the input. Do not move the threshold to hide a real problem."
  - q: "Which face embedding model can you use in a client pipeline without a licensing problem?"
    options: ["Any model on GitHub", "A model whose weights have a license that permits your use, for example the OpenCV zoo SFace model (Apache-2.0); check the weights, not only the code", "Only paid APIs", "Any model, because scores are not published"]
    answer: 1
    explain: "Some popular face-analysis packages have permissive code but non-commercial pretrained weights. The license of the weights decides."
  - q: "Another student runs your packaged pipeline and gets a different start frame from the same seed. What is the most likely cause?"
    options: ["Seeds are random", "A different model file, ComfyUI version, or GPU kernel; compare their run log with yours field by field", "The README is too short", "The internet connection"]
    answer: 1
    explain: "Same inputs and same versions give the same or nearly the same output. The run log (C11·M04) shows which version differs."
deeper:
  - title: "OpenCV model zoo — SFace (face recognition) model card"
    url: https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface
  - title: "SFace: Sigmoid-Constrained Hypersphere Loss for Robust Face Recognition (paper)"
    url: https://arxiv.org/abs/2205.12010
  - title: "Runflow — ComfyUI consistent character with FLUX (2026)"
    url: https://www.runflow.io/blog/comfyui-consistent-characters-flux
---
## Learn

### What the pipeline must do
A series needs the same character in every shot. The face, the hair, the clothes, and the voice must not drift. You cannot check every frame by eye at scale. So the pipeline has two jobs: make the shot, and measure whether the shot is on-model.

The stages:
1. **References.** The character sheet from C04·M03: front, 3/4, and side views, on plain light. One place image per location.
2. **Start frame.** A reference-image graph puts the character into the place, with the shot size, angle, and light from the shot list.
3. **Line audio.** The spoken line in the character's fixed voice (C06·M01). Record consent for any cloned voice (C16·M02).
4. **Video with lip sync.** An image-and-audio-to-video model animates the start frame. It moves the mouth to the audio.
5. **Identity score.** A face embedding model compares the faces in the video with the references.
6. **Decision.** PASS goes to the edit. REJECT tries the next seed. After N tries, a person looks at the report.

The starter kit has the workflows for stages 2 and 4 (`02_ref_edit_flux2_klein_4b`, `07_lipsync_ia2v_ltx23`), the scorer (`identity_score.py`), and a script that chains them (`character_shot.py`).

### References versus LoRA
References put identity into each generation through the conditioning. They need no training. They are weaker at angles and expressions that the references do not show.

A character LoRA puts identity into the model weights (C14). It holds identity at more angles. It costs a dataset, a training run, and an evaluation.

Build the pipeline with references first. In C14·M03 you add your LoRA to the same pipeline and measure the change in identity score. Then you know what the LoRA is worth for your character.

### How the identity score works
1. **Detect** the face in a frame. The detector gives a box and 5 landmarks (eyes, nose, mouth corners).
2. **Align** the face. Rotate and scale it so that the landmarks are in standard positions. Crop it.
3. **Embed** the face. A recognition network turns the crop into a vector (128 numbers for SFace). Faces of the same person give vectors that point in similar directions.
4. **Compare** with cosine similarity: `score = dot(a, b) / (|a| × |b|)`. 1.0 means the same direction. Values near 0 mean unrelated faces.

Do this for frames sampled across the clip. Compare each frame with the mean of the normalized reference vectors. Report:
- **median score:** is the take mostly on-model?
- **minimum score and its frame:** where is the worst moment?
- **face rate:** in how many sampled frames was a face found? A low rate means the face is turned away, covered, or broken.

### Set the threshold from data
A threshold is a decision rule. Calibrate it like any classifier threshold:
1. Generate 20–30 takes of your character, including some that drift.
2. Label each take by eye: on-model or off-model.
3. Score all takes.
4. Choose the threshold that separates the two groups with the fewest errors.
5. Prefer false rejects to false passes. A false reject costs one more take. A false pass reaches the client.

Recalibrate when you change the model, the style, or the character.

### Retries and the report
When a take fails, the cheapest fix is often a new seed. The pipeline tries seed, seed+1, and seed+2. It writes a report with every try: seed, start frame, video, scores, worst frame, and result. A person reads the report only when all tries fail. Usually the report then shows a pattern, for example "always fails at the profile view". That pattern tells you what to fix in the input.

### Packaging
Another person (or an agent, C12) must run the pipeline without opening the graphs:
- **Named inputs.** Each workflow has a map file (`*.map.json`): `prompt`, `seed`, `start_image`, `line_audio`. Code uses names, not node IDs.
- **One entry point.** `character_shot.py --shot S07.json --char-ref ... --place-ref ... --line ...`.
- **Requirements.** The README states the GPU memory, the model files (with the lock file), and the ComfyUI version.
- **Example inputs.** One shot file, one reference set, one line audio file, and the expected report.

In the ComfyUI editor you can also group the nodes of one stage into a subgraph with named inputs. This helps people who work in the editor. The API export expands it again.

## Worked example

**Calibration on real faces.** We tested the starter scorer on public-domain NASA portraits (2026-10-04, OpenCV YuNet + SFace, CPU):

| Input (reference: Neil Armstrong, 1964 portrait) | Median | Minimum | Result at 0.45 |
|---|---|---|---|
| Armstrong, a different photo, as a 3 s push-in video | 0.668 | 0.650 | PASS |
| Armstrong, the same different photo, as a still | 0.676 | 0.676 | PASS |
| Buzz Aldrin (a different person), still | 0.135 | 0.135 | REJECT |
| 3 s video: 1.5 s Armstrong, then 1.5 s Aldrin | 0.345 | 0.111 (frame 43) | REJECT |

Two facts come from this test:
1. Same person, different photos: about 0.67. Different person: about 0.14. There is a wide gap. OpenCV states 0.363 as its "same person" cosine threshold for SFace on real photos.
2. The mixed clip fails, and the report names frame 43, inside the second half. The minimum and its frame show where the drift is.

**One shot through the pipeline.** Shot S07: `@MARA: "That's my locker."` Medium close-up, 85 mm look, night, locker room.

```bash
python character_shot.py --shot shots/S07.json \
  --char-ref refs/CHAR-MARA_front.png --char-ref refs/CHAR-MARA_34.png \
  --place-ref refs/LOC-LOCKER.png --line audio/S07_mara.wav --out shots/S07/
```

The script runs the start-frame workflow (seed 1000), then the lip-sync workflow with the line audio, then the scorer. A typical run (illustrative numbers): the first try fails, median 0.41, worst frame at a head turn. The second try (seed 1001) passes: median 0.58, face rate 100 %. The report keeps both tries.

## Lab

**Deliverable:** `pipelines/character/` with the packaged pipeline, a calibration report, 5 dialogue shots, and an identity report.

1. **Inputs.** Use your character sheet (C04·M03) and two locations. Make 5 line audio files in the character's fixed voice (C06·M01). Write 5 shot files from your shot list.
2. **Run the stages by hand.** Run `02_ref_edit_flux2_klein_4b`, then `07_lipsync_ia2v_ltx23`, for one shot, with `comfy_run.py`. Check the outputs.
3. **Calibrate the scorer.** Make 20 takes or more. Label each take by eye. Score them with `identity_score.py`. Choose your threshold and write why in `calibration.md`, with a table.
4. **Automate.** Chain the stages with retries. Use your own script, or read and run `starter/solutions/C11-M03/character_shot.py`.
5. **Produce.** Make the 5 dialogue shots in at least 3 shot sizes. Keep every report.
6. **Package.** Write the README: requirements, model files and licenses, one command, expected output. Ask another student (or a fresh container) to run it from the README. Time it.
7. **Prepare C14.** Write down the 2 shots where identity was weakest. In C14·M03 you will rerun them with a LoRA.

**Result checklist**
- [ ] 5 shots, each with a report (all tries).
- [ ] `calibration.md` with 20+ labeled takes and the chosen threshold.
- [ ] README that another person followed in under 30 minutes.
- [ ] Rejection rate and its main cause.
- [ ] Two "weak" shots chosen for the C14 comparison.

## Model answer

**`calibration.md` (shape of a strong answer):**

| Group | Takes | Median score range |
|---|---|---|
| On-model (by eye) | 17 | 0.49–0.71 |
| Off-model (by eye) | 7 | 0.18–0.47 |

"Overlap is between 0.47 and 0.49 (2 takes). We choose 0.48. Error check: 0 false passes, 1 false reject (a take with a hand over the mouth). Rule: also reject if face rate < 80 %."

**Production summary:**

```
pipelines/character/
  README.md                 # requires 48 GB GPU or 32 GB with offload; ComfyUI 0.38.0; models.lock.json
  character_shot.py
  shots/S01..S05.json
  refs/CHAR-MARA_front.png CHAR-MARA_34.png CHAR-MARA_side.png LOC-LOCKER.png LOC-STREET.png
  out/S01..S05/report.json
  calibration.md
```

| Shot | Size | Tries | Chosen median | Failure cause of rejected tries |
|---|---|---|---|---|
| S01 | MS | 1 | 0.61 | — |
| S03 | MCU | 2 | 0.58 | head turn at 2 s |
| S04 | CU | 1 | 0.66 | — |
| S07 | MCU | 2 | 0.58 | head turn |
| S09 | profile MS | 3 | 0.50 | profile view (2 tries) |

"Rejection rate 4 / 9 tries (44 %). Main cause: profile and three-quarter-back angles that the references do not cover. For C14: S07 and S09."

The README test: a classmate ran it in a new container in 24 minutes, most of it model download.
