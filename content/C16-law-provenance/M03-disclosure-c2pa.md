---
title: Disclosure rules, C2PA, and watermarks
hours: 12
outcomes:
  - Apply EU AI Act Article 50 deployer duties and platform disclosure rules to a delivery.
  - Sign deliverables with C2PA content credentials at the right step, and verify them.
  - Explain what breaks credentials and watermarks, from measurements.
  - Build disclosure and signing into the pipeline as an automatic delivery gate.
keywords: [EU AI Act, C2PA, content credentials, invisible watermark, digital source type]
summary: >
  The EU AI Act's transparency duties (Article 50) apply from 2026-08-02: providers of generative systems must mark
  outputs in a machine-readable way, and deployers who publish deepfakes - realistic content that resembles real
  people, places, or events - must disclose them clearly. Platforms add their own labels. C2PA content credentials are
  a signed manifest in the file that records how it was made; any re-encode removes them, so sign last. Invisible
  watermarks survive some edits and not others. Use both, plus visible labels where required, and gate delivery on them.
diagram:
  type: stack
  title: Layers of disclosure
  nodes: ["Visible label: on screen and in the description, where required", "Platform setting: altered or synthetic content", "C2PA content credentials: signed manifest in the file", "Invisible watermark: added by the model provider (do not remove)", "Prompt and rights logs: the evidence behind all of it"]
  highlight: [2]
watch:
  - title: "European Commission — Code of Practice on transparency of AI-generated content"
    url: https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content
    note: "Read the summary of the marking and labeling commitments."
  - title: "C2PA — Content Credentials (official site)"
    url: https://c2pa.org/
    note: "Read 'How it works'."
quiz:
  - q: "Under EU AI Act Article 50, who must disclose a deepfake, and how?"
    options: ["Nobody", "The deployer who makes it public: clearly and at the latest at the first exposure; artistic, satirical, or fictional works have a lighter duty that must not spoil the work", "Only the model provider", "Only platforms"]
    answer: 1
    explain: "Providers mark outputs machine-readably; deployers disclose deepfakes to viewers. Check the national rules too."
  - q: "What can a breach of Article 50 cost an undertaking?"
    options: ["Nothing", "Fines of up to €15 million or 3 % of worldwide annual turnover, whichever is higher (Article 99(4))", "€100", "Only a warning"]
    answer: 1
    explain: "The €7.5 million / 1 % tier is for supplying incorrect information to authorities, not for Article 50."
  - q: "You sign the master with C2PA, then make the web version with ffmpeg. What happens to the credentials?"
    options: ["They stay", "They are removed: in the course test, a re-encode, a stream-copy trim, and even a plain remux all produced 'No claim found'. Sign each delivery file as the last step", "They become invalid but stay", "They double"]
    answer: 1
    explain: "Signing is the final step of the delivery pipeline, after every encode."
  - q: "One byte in a signed file changes. What does verification show?"
    options: ["Nothing", "Invalid, with a hash mismatch: the credentials prove that the file has not changed since signing", "Valid", "A warning only"]
    answer: 1
    explain: "In the test: 'assertion.bmffHash.mismatch'."
  - q: "Verification says 'signingCredential.untrusted'. What does it mean?"
    options: ["The file is fake", "The signature is valid, but the certificate is not from a trusted issuer (for example a test certificate); use a certificate from a trusted certificate authority for client deliveries", "The file is corrupt", "The manifest is missing"]
    answer: 1
    explain: "The course tests used the c2patool sample certificate, which is untrusted by design."
  - q: "An open invisible watermark survived JPEG at quality 90 and a resize, but not a 10 % crop or JPEG at quality 50. What follows?"
    options: ["Watermarks are useless", "A watermark is one layer of evidence; it can be lost in normal processing, so combine it with credentials, labels, and your logs", "Watermarks are perfect", "Only crop videos"]
    answer: 1
    explain: "Provider watermarks (for example SynthID) are more robust than the simple test method, but no single layer is enough. Never try to remove a provider's watermark."
  - q: "Which digital source type do you declare for a shot made by a video model from a prompt and a key frame?"
    options: ["digitalCapture", "trainedAlgorithmicMedia (or compositeWithTrainedAlgorithmicMedia when mixed with captured material)", "None", "minorHumanEdits"]
    answer: 1
    explain: "The IPTC digital source types tell viewers and platforms how the content was made."
deeper:
  - title: "c2patool — command-line tool (in the c2pa-rs repository)"
    url: https://github.com/contentauth/c2pa-rs
  - title: "Google DeepMind — SynthID"
    url: https://deepmind.google/science/synthid/
  - title: "EU AI Act — Article 50 (text and overview)"
    url: https://artificialintelligenceact.eu/article/50/
---
## Learn

This module is not legal advice. Check the rules of every country where your content is shown.

### EU AI Act Article 50 (applies from 2026-08-02)
- **Providers** of generative AI systems must mark outputs in a machine-readable, detectable way.
- **Deployers** (you, when you publish) must disclose **deepfakes**: image, audio, or video content that resembles real people, objects, places, or events and could falsely appear real. The disclosure must be clear, at the latest at the first exposure. For evidently artistic, creative, satirical, or fictional works, the duty is limited to a disclosure that does not spoil the work.
- **Penalties:** for an undertaking, fines of up to €15 million or 3 % of worldwide annual turnover, whichever is higher (Article 99(4)).
- A Code of Practice from the European Commission describes how to mark and label, with more than one marking layer: signed metadata and an invisible watermark.
Other jurisdictions have their own rules (for example China's labeling rules for AI-generated content, and US state laws on deepfakes in elections and on intimate images).

### Platform rules
Major platforms require a disclosure for realistic altered or synthetic content, through a setting at upload. Some add labels automatically when they detect C2PA credentials or watermarks. Record in the asset record that you set it (C15·M03). Platform rules change often: check the help pages of each platform when you plan a release, and save a copy with the date, as you do with license terms.

### C2PA content credentials
C2PA is an open standard for signed provenance metadata. A **manifest** in the file records who made it, with which tools, from which ingredients, and with which actions; it is signed with a certificate. Viewers and platforms can verify it.
- Declare how the content was made with an IPTC **digital source type**: `trainedAlgorithmicMedia` for generated content, `compositeWithTrainedAlgorithmicMedia` for mixes with captured material.
- **Sign last.** Our tests showed that any later ffmpeg step, even a stream-copy remux, removes the manifest. Sign every delivery file after its final encode.
- Verification shows integrity: one changed byte makes the manifest invalid.
- Use a certificate from a trusted certificate authority for client work. A test certificate gives "untrusted".
- Some generators add credentials to their outputs; your edit removes them. Your signature at delivery describes the whole work.

### Invisible watermarks
A watermark hides a signal in the pixels (or the audio). Provider watermarks (added by some hosted model providers to their outputs) are designed to survive common edits. You usually cannot add a provider's watermark yourself, and you must not remove it. Our test with a simple open watermark library showed the general point: a watermark survives some processing and is lost in other processing. It is one layer of evidence, not proof.

### What credentials do not prove
Valid credentials prove who signed the file and that it has not changed since. They do not prove that the content is true. And a missing manifest does not prove that a file is fake: most real files have none, and many platforms remove metadata on upload. Read credentials as one piece of evidence. Platforms that keep credentials can show a "content credentials" mark to viewers.

### The delivery gate
Before a file leaves the studio:
1. a visible label where the law or the platform requires it;
2. the platform setting recorded for the publishing step;
3. valid C2PA credentials, signed with the studio certificate, as the last step;
4. complete prompt and rights logs (M01).
Fail the delivery if any is missing (C12·M04).

## Tool walkthrough

### Sign, verify, gate

```bash
# c2patool: github.com/contentauth/c2pa-rs (releases); set C2PATOOL if it is not on PATH
python starter/tools/provenance.py sign film_web.mp4 --out film_web_signed.mp4 --title "The Camera ep1" \
  --author "Example Studio" --ai generated --cert certs/studio.pem --key certs/studio.key --tsa <time-stamp URL>
python starter/tools/provenance.py verify film_web_signed.mp4
python starter/tools/provenance.py gate film_web_signed.mp4 --record assets/film_web.json
```

The asset record for the gate holds `realistic_people_or_events`, `platforms`, `disclosure.visible_label`, `disclosure.platform_setting`, `prompt_log`, and `rights_log`.

### Inspect with c2patool directly

```bash
c2patool film_web_signed.mp4          # the manifest store as JSON, with validation_state
```

## Worked example

**C2PA tests** (2026-10-04, c2patool 0.27.22, the sample test certificate, a 6 s H.264 MP4):

| File | Result |
|---|---|
| Signed (actions: created with `trainedAlgorithmicMedia`; edited) | Valid (with `signingCredential.untrusted`: the test certificate) |
| Signed, then re-encoded with ffmpeg | No claim found |
| Signed, then trimmed with stream copy | No claim found |
| Signed, then remuxed (stream copy, metadata mapped) | No claim found |
| Signed, then one byte changed | Invalid: `assertion.bmffHash.mismatch` |

Signing took 0.02 s and added 14 KB to a 3.5 MB file. The gate failed the file twice: for the test certificate, and because the asset record said the video shows realistic synthetic people without a visible label.

**Watermark test** (an open library, `invisible-watermark`, a 32-bit payload in a 960 × 1200 image; PSNR about 41 dB, invisible to the eye):

| Processing | Method dwtDct | Method dwtDctSvd |
|---|---|---|
| none | read | read |
| JPEG quality 90 | lost | read |
| JPEG quality 50 | lost | lost |
| resize to 50 % and back | lost | read |
| crop 10 % of the border | lost | lost |
| brightness +20 | read | read |

**Short film** (fictional, with realistic city shots): end card "Made with generative AI tools: …"; the platform's synthetic-content setting on; C2PA signed with the studio certificate after the final encode; logs archived. **EU ad** with a realistic spokesperson (consented likeness): a visible "AI-generated" label at the start.

## Lab

**Deliverable:** `C16/M03/` with a disclosure decision per deliverable, signed deliverables, verification reports, a break test, and the gate in your pipeline.

1. For each deliverable of your project, decide: deepfake or not? Which visible label, platform setting, and description text? Write the reasons.
2. Get c2patool. Sign each delivery file as the last step (use the sample test certificate for practice; note that client work needs a trusted certificate).
3. Verify each file. Then break one copy: re-encode it, and change one byte of another. Verify again and save the reports.
4. Add `provenance.py gate` (or your own gate) to your delivery pipeline (C12·M04). Show one failing and one passing run.

**Result checklist**
- [ ] Disclosure decision per deliverable.
- [ ] Signed files with verification reports.
- [ ] Break test: re-encode and byte change.
- [ ] The gate in the pipeline: one fail, one pass.

## Model answer

**Disclosure decisions (shape of a strong answer):**

| Deliverable | Realistic people or events? | Visible label | Platform setting | C2PA |
|---|---|---|---|---|
| Short film (fiction, stylized night look, invented characters) | realistic people, clearly fictional work | end card "Made with generative AI" (does not spoil the work) | on | signed, `trainedAlgorithmicMedia` |
| 15 s ad with a realistic AI spokesperson (EU) | yes | "AI-generated" on screen for the first 3 s and in the description | on | signed |
| Behind-the-scenes clip (real footage of the team) | no generated people | none | off | signed with `--ai edited` (captured footage with AI edits) |

"Gate: the first run failed the ad (no visible label recorded). After the label was added and the record updated, the gate passed with the studio certificate."
