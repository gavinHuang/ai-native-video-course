---
title: Copyright and licenses in AI production
hours: 10
outcomes:
  - Explain the main open legal questions - training data, output ownership, style, similarity - and why answers differ by country.
  - Read the license of every model file, hosted service, music track, stock asset, and font, and record it.
  - Keep a rights log that proves the origin of every asset, and audit it before delivery.
  - Reduce risk in client work with contract clauses and a data rule.
keywords: [copyright, license, rights log, human authorship, indemnity]
summary: >
  Generative AI raises open legal questions: whether training on protected works is allowed, who owns outputs, and
  when an output is too similar to an existing work. The answers differ by country and are still changing, so this
  course gives a method, not legal advice. Read the license of every model file and service you use, save the
  terms with a date, and keep a rights log for every asset you did not make. Audit the log before delivery, and agree
  the use of AI with clients in writing.
diagram:
  type: layers2d
  title: What to check for each asset type
  rows: ["Open model files", "Hosted model / app", "Music, stock, fonts", "Client assets"]
  cols: ["Check", "Record"]
  cells:
    - ["The license of EACH file (weights, VAE, encoder)", "License per file in models.lock"]
    - ["Terms: output ownership, commercial use, plan, indemnity", "Plan + saved terms PDF + date"]
    - ["Commercial, streaming, broadcast, territory", "Rights-log line + license copy"]
    - ["Contract: may it go to AI tools? which?", "Data rule per project (C13·M05)"]
watch:
  - title: "U.S. Copyright Office — Copyright and Artificial Intelligence (reports)"
    url: https://www.copyright.gov/ai/
    note: "Read the summary of Part 2 (copyrightability of outputs)."
  - title: "Creative Commons — licenses overview"
    url: https://creativecommons.org/share-your-work/cclicenses/
    note: "Know the meaning of BY, SA, NC, and ND."
quiz:
  - q: "An open image model is Apache-2.0, but its official workflow loads a VAE file from a repository with a non-commercial license. Can you use the outputs for a client ad?"
    options: ["Yes, the model is Apache-2.0", "Not without checking: the workflow uses a non-commercial file, so either confirm the license allows your use or replace that file with one whose license does", "Yes, VAEs do not matter", "Only on weekends"]
    answer: 1
    explain: "Licenses attach to files. The starter lock file shows exactly this case (C11·M01)."
  - q: "In the US (Copyright Office guidance, as of 2026-10), what can be protected in an AI-assisted video?"
    options: ["Everything", "The human-authored parts: your script, your selection and arrangement, your edits, and human-made elements; purely generated material without human authorship is not protected", "Nothing", "Only the music"]
    answer: 1
    explain: "Document your human contribution (script, shot list, edit decisions). Other countries have different positions."
  - q: "An output looks very much like a famous cartoon character. It was made from a text prompt only. Is it safe because a model made it?"
    options: ["Yes", "No: similarity to a protected work, character, or trademark can infringe regardless of how it was made; do not use it", "Yes, if you add a label", "Only in the EU"]
    answer: 1
    explain: "How a work was made does not remove infringement risk. Check outputs for recognizable characters, logos, and works."
  - q: "Why save a PDF of a service's terms on the day you use it?"
    options: ["For decoration", "Terms change; you must be able to show which terms applied when you made and used the asset", "Services require it", "For taxes"]
    answer: 1
    explain: "A rights-log line points to the saved terms."
  - q: "What does 'NC' mean in a Creative Commons license?"
    options: ["No credit", "Non-commercial: no commercial use without separate permission", "New content", "No copies"]
    answer: 1
    explain: "BY = attribution, SA = share alike, NC = non-commercial, ND = no derivatives."
  - q: "A client's contract says nothing about AI. What do you do before you put their product photos into a hosted model?"
    options: ["Go ahead", "Agree in writing: whether AI is used, which tools, whether their assets may go to third-party services, who owns what, and how outputs are labeled", "Use the photos only at night", "Ask after delivery"]
    answer: 1
    explain: "Write the data rule into the contract. Many clients allow AI only on self-hosted models for their confidential assets."
  - q: "What is an indemnity in a service's terms?"
    options: ["A discount", "A promise by the vendor to defend or pay for certain legal claims arising from the use of its outputs, with conditions and limits", "A license for music", "A refund"]
    answer: 1
    explain: "Some enterprise plans include it. Read the conditions; it does not cover everything."
deeper:
  - title: "WIPO — Generative AI and intellectual property (overview)"
    url: https://www.wipo.int/about-ip/en/frontier_technologies/ai_and_ip.html
  - title: "Apache License 2.0 (text)"
    url: https://www.apache.org/licenses/LICENSE-2.0
  - title: "LTX-2.x Community License (an example of a custom model license with a revenue threshold)"
    url: https://github.com/Lightricks/LTX-2/blob/main/LICENSE
---
## Learn

This module is not legal advice. Laws differ by country and change quickly. It gives you a working method: know the questions, read the terms, keep records, and ask a lawyer when the stakes are high.

### The open questions (as of 2026-10)
- **Training data:** many lawsuits against AI companies about training on protected works; some licensing deals (for example music labels with music-generation services in 2026). Results differ by country and case.
- **Output ownership:** in the US, the Copyright Office's guidance is that protection needs human authorship. Human selection, arrangement, editing, and human-made parts can be protected; purely generated material without human authorship is not. Other countries have taken different positions in some cases.
- **Similarity:** an output that is substantially similar to a protected work, or shows a trademark or a protected character, can infringe, regardless of how it was made.
- **Style:** a style is generally not protected, but prompts that name living artists, and outputs that copy a recognizable work, raise legal and ethical risk. Describe features, not names (C06·M03).

### Licenses to read
| Item | What to check |
|---|---|
| Open model files | The license of each file: weights, VAE, text encoder, LoRAs. Apache-2.0, custom community licenses (often with revenue thresholds), research-only. |
| Hosted models and apps | Terms of service: who owns outputs, commercial use, plan limits, attribution, indemnity, use of your inputs for training. |
| Music | The plan's terms: commercial use, streaming, broadcast, territory (C06·M03). |
| Stock, fonts, LUTs, sound effects | The usage license: commercial, editorial only, number of projects, territory. |
| Client assets | The contract: may they be processed with AI, and with which tools? |

A workflow is only as free as its most restricted file. The starter kit's lock file (C11·M01) shows a real case: an Apache-2.0 image model whose official template loads a VAE from a non-commercial repository.

### The rights log
Write one line per asset that you did not make yourself. Record the ID, source, license or consent, allowed use, and the saved terms or license file. Also record people or brands shown, consent IDs, the date, and an expiry date if there is one. Generated assets have their origin in the prompt log (C04·M01). Together, the two logs prove where every asset came from. Audit them before every delivery.

### Document the human contribution
Keep the script, the shot list, the review sheets, the take notes, and the edit history. They show the human authorship (selection, arrangement, editing) that protection may depend on, and they make disputes easier to answer.

### When to ask a lawyer
Ask a lawyer before you start in these cases: the work is broadcast or a large campaign; a real person or a brand is shown; a client asks for an indemnity from you; or a license term is not clear. Bring the rights log and the saved terms: a lawyer can then answer quickly.

### Client work
Agree in writing:
- that AI tools are used, and which kinds;
- whether the client's assets may go to third-party services (the data rule, C13·M05);
- who owns the deliverables and the intermediate assets (prompts, LoRAs);
- disclosure and labeling (M03);
- limits of liability, and any indemnity that you rely on.

## Tool walkthrough

### Record licenses

```bash
python starter/tools/promptlog.py rights --id STOCK-0042 --source "Stock site, image 0042" --license "standard, web and social" \
  --use "background plate, online ad" --file plates/stock_0042.jpg
python starter/comfyui/download_models.py --list        # the license of every starter model file
```

### Audit before delivery

```bash
python starter/tools/rights_audit.py --project "The Camera" --registry registry.yaml
```

The audit runs the prompt-log and rights-log checks, flags risky licenses (non-commercial, editorial only, research, unknown), expired licenses and consents, missing consent files for people, and registry adapters that are expired or not allowed for the project.

### Model licenses (as of 2026-10, from the starter lock file)
FLUX.2 klein 4B: Apache-2.0. The FLUX.2 VAE file from the FLUX.2-dev repository: non-commercial. Wan 2.2: Apache-2.0. LTX-2.3 and LTX-2.5: the LTX-2.x Community License (a paid license for companies with annual revenue of US$10 million or more). Gemma encoders: the Gemma terms.

## Worked example

**Rights audit test** (2026-10-04) on a small project log:

```
WARN    STOCK-77: license 'editorial only' - check that it allows this use (background)
WARN    registry leo_v1: not allowed for 'The Camera' (allowed: The Camera (series))
PROBLEM VOICE-ANA: expired on 2026-09-30 - remove the asset or renew the license/consent
PROBLEM FACE-JO: shows people ['Jo'] but has no consent file
PROBLEM registry ambassador_v2: expired on 2026-06-30 - the service must refuse it
3 problems, 2 warnings
```

Each finding is something a fast manual review misses: an expiry date passed during production, a photo of a person without its consent file, and a stock image licensed for editorial use placed in an ad.

**Ad project:** 40 generated shots (2 hosted models + 1 open model), 1 generated music track, 1 font, client product photos. The rights log shows: hosted model A allows commercial use on the paid plan (terms saved with the date); model B the same, plus a vendor indemnity; the open model's files are Apache-2.0; the music plan allows streaming; the font is licensed for video; the client contract allows its product photos only on self-hosted models, so those shots were made with the open model.

## Lab

**Deliverable:** `C16/M01/` with a license table, a complete rights log, an audit report, and a contract checklist.

1. List every model file, service, music track, stock asset, font, and LUT used in your project. Record the license of each, and save the terms with the date.
2. Find at least one file in your workflows whose license differs from the model family's license. Decide what to do.
3. Complete the rights log; make sure every reference in the prompt log is covered.
4. Run `rights_audit.py`. Fix every problem; answer every warning in writing.
5. Write a one-page contract checklist for AI use in client work.

**Result checklist**
- [ ] License table with saved terms and dates.
- [ ] Rights log complete; the audit has 0 problems.
- [ ] A file-level license finding and its decision.
- [ ] Contract checklist.

## Model answer

**License table (extract, shape of a strong answer):**

| Item | License / terms | Saved | Allows this project? |
|---|---|---|---|
| flux-2-klein-4b.safetensors | Apache-2.0 | lock file | yes |
| flux2-vae.safetensors | non-commercial (FLUX.2-dev repository) | lock file | no → replaced in our workflow with a VAE whose license allows commercial use, re-tested |
| Video API (plan Pro) | outputs owned by us; commercial use; no indemnity | terms_2026-10-04.pdf | yes |
| Music track MUS-1 | plan Pro: commercial incl. streaming, no broadcast | terms PDF | yes (online only) |
| Font | desktop + video license | license.pdf | yes |

"Audit: 2 problems on the first run (a consent expired during production; a stock image without a rights line). The voice line was re-recorded with the renewed consent; the stock image was replaced by a generated plate. Second run: 0 problems, 1 accepted warning (editorial-only stock used only in an internal mood board, not in the film)."
