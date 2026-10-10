---
title: Likeness, voice, and consent
hours: 8
outcomes:
  - Explain personality and publicity rights, digital-replica laws, data protection, and performer agreements as they apply to AI work.
  - Write and store consent for training, cloning, and depiction, with scope, time, approval, and withdrawal.
  - Enforce consent in the pipeline - registry expiry, refusals, deletion on withdrawal.
  - Decide when not to depict a real person at all.
keywords: [personality rights, digital replica, consent record, biometric data, withdrawal]
summary: >
  A person's face and voice are protected in many places: by publicity or personality rights, by new laws on
  digital replicas of voice and likeness, by data-protection law (faces and voices can be biometric data), and by
  performer agreements. In AI work, the answer is documented consent: who, what, where, how long, payment, approval,
  and how to withdraw. Store it, link it to every asset and adapter, and enforce it in code. Some content must not be
  made at all, with or without a request.
diagram:
  type: flow
  title: Consent in the pipeline
  nodes: ["Consent record: who, what, where, how long, withdrawal", "Rights log line + registry entry with expiry", "Pipeline checks: refuse expired or out-of-scope use", "Person approves outputs (if agreed)", "Withdrawal → stop + delete as agreed", "Audit before every delivery"]
  highlight: [2, 4]
watch:
  - title: "SAG-AFTRA — AI resources (digital replicas in contracts)"
    url: https://www.sagaftra.org/contracts-industry-resources/member-resources/artificial-intelligence
    note: "Read what performer contracts require for digital replicas."
  - title: "European Commission — data protection (GDPR) overview"
    url: https://commission.europa.eu/law/law-topic/data-protection_en
    note: "Note biometric data as a special category."
quiz:
  - q: "A public figure's speeches are online. Can you clone their voice for an ad without asking?"
    options: ["Yes, the speeches are public", "No: commercial use of a person's voice or likeness generally needs their permission (publicity rights, digital-replica laws such as Tennessee's ELVIS Act); public material is not consent", "Yes, with a label", "Yes, outside the US"]
    answer: 1
    explain: "Public is not the same as permitted. A label does not replace consent."
  - q: "What must a consent record for a voice clone contain?"
    options: ["A signature only", "Who, what may be made (the clone, the uses), where and in which media, how long, payment, approval rights, the withdrawal process, signature and date", "The voice file", "The price only"]
    answer: 1
    explain: "The starter template (templates/voice_consent.md) has these fields. A lawyer must check it for client work."
  - q: "Why can face and voice data fall under strict data-protection rules?"
    options: ["They are large files", "Used to identify a person, they are biometric data; laws such as the GDPR treat it as a special category that often needs explicit consent", "They are images", "They are copyrighted"]
    answer: 1
    explain: "Data protection applies to the training data and the models made from it, not only to the outputs."
  - q: "The consent for an ambassador's likeness LoRA expired yesterday. What must happen, in the pipeline?"
    options: ["Nothing until someone notices", "The registry marks it expired; the service refuses the adapter; the audit fails; the files are deleted as the consent requires", "The LoRA works for another month", "Ask the client"]
    answer: 1
    explain: "Consent rules must be enforced in code: the registry (C14·M03) and the rights audit (M01)."
  - q: "A person withdraws consent for future use. What do you do?"
    options: ["Ignore it", "Stop new uses at once, delete the voice or likeness models as agreed, record the withdrawal, and handle already-published outputs as the consent record says", "Delete all your files", "Keep using the old outputs only"]
    answer: 1
    explain: "Agree in advance what happens to published material, and follow it."
  - q: "Which content do you never make, even if a client asks?"
    options: ["Animations", "Sexual or intimate content of real people without consent, fake statements of real people presented as real, content that targets a private individual, and children's likeness without guardian consent and safeguards", "Ads", "Music videos"]
    answer: 1
    explain: "These cause serious harm, and many are crimes. Refuse them."
  - q: "A practical test before you publish content with a real person's likeness?"
    options: ["Ask a friend", "Would you show the person the video before publishing, and would they agree it matches what they consented to? If not, do not publish", "Check the file size", "Add music"]
    answer: 1
    explain: "If you would not show it to them, it is probably outside the consent."
deeper:
  - title: "Wikipedia — personality rights (overview by country)"
    url: https://en.wikipedia.org/wiki/Personality_rights
  - title: "Latham & Watkins — The ELVIS Act: Tennessee's right-of-publicity law and generative AI (PDF)"
    url: https://www.lw.com/admin/upload/SiteAttachments/The-ELVIS-Act-Tennessee-Shakes-Up-Its-Right-of-Publicity-Law-and-Takes-On-Generative-AI.pdf
  - title: "Partnership on AI — Responsible Practices for Synthetic Media"
    url: https://syntheticmedia.partnershiponai.org/
---
## Learn

This module is not legal advice. Rules differ by country and state.

### The rights involved
- **Personality and publicity rights:** many US states, EU countries, China, and others give people control over the commercial use of their name, image, and voice.
- **Digital-replica laws:** newer laws target AI copies of a person's voice and likeness. Example: Tennessee's ELVIS Act (2024) added voice to the state's right of publicity. It also covers making tools available whose main purpose is to produce a particular person's voice or likeness without authorization. Other jurisdictions followed with their own rules.
- **Data protection:** face and voice data used to identify a person can be biometric data. Laws such as the GDPR treat it as a special category that often needs explicit consent. This applies to training data and to the models made from it.
- **Performer agreements:** union agreements (for example SAG-AFTRA's) require consent and payment for digital replicas of performers.

### What consent must say
- **Who:** the person (and a guardian for a minor).
- **What:** train a likeness LoRA, clone a voice, depict the person in ads, dub them into other languages.
- **Where and how:** media, platforms, territories, languages; allowed and forbidden content.
- **How long:** a start and an end date; what happens to the models at the end.
- **Payment.**
- **Approval:** whether the person approves every final use, a sample, or nothing within the scope.
- **Withdrawal:** how to withdraw, how fast new uses stop, what happens to published outputs.
- **Disclosure:** that outputs are labeled as AI-generated (M03).
- **Signature and date.**

### Enforce consent in the pipeline
A consent record in a folder is not enough. Connect it:
1. A rights-log line with the consent file and the expiry date.
2. A registry entry for every adapter or voice model made from the person, with the allowed uses and the expiry (C14·M03).
3. The service refuses an expired or out-of-scope adapter.
4. The rights audit runs before every delivery (M01).
5. On withdrawal or expiry: delete the models and the training data as agreed, and record it.

### Look-alikes and sound-alikes
A generated person who looks or sounds like a real, recognizable person can create the same risk as a direct copy, even if you did not ask for that person. Courts have found sound-alike ads infringing in the past. Check outputs for resemblance to well-known people. If a generated character resembles a real person, change the design. Do not prompt with real names unless the person consents.

### Minors, deceased persons, and employees
- **Minors:** a guardian signs; keep the scope narrow and the time short; add safeguards (no public training data, strict deletion).
- **Deceased persons:** some places protect likeness after death (estates control it). Ask the estate.
- **Employees:** consent given to an employer may not be free. Make it optional, and make withdrawal easy when the person leaves.

### Never make
- sexual or intimate content of real people without consent;
- realistic fake statements or actions of real people presented as real;
- content that targets or harasses a private individual;
- the likeness of children without guardian consent and strong safeguards.

### A practical rule
If you would not show the person the video before publishing, do not make it.

## Tool walkthrough

### The consent template
`starter/templates/voice_consent.md` (C06·M01) covers voice and likeness: scope, time, review, disclosure, payment, revocation, storage. Store the signed record as `rights/consent/CONSENT-<name>-<date>.pdf` and add a rights-log line:

```bash
python starter/tools/promptlog.py rights --id CONSENT-ANA-2026-10 --source "Ana Ruiz (voice actor)" \
  --license "consent record" --use "voice clone, The Camera series, online, until 2027-06-30" \
  --consent-file rights/consent/CONSENT-ANA-2026-10.pdf
```

Add `"expires": "2027-06-30"` and `"people": ["Ana Ruiz"]` to the line; the audit uses both.

### Vendor verification
Hosted voice-cloning services usually require a verification step in which the person reads a text. Keep the verification record with the consent.

## Worked example

**Brand ambassador campaign.** The ambassador consents to: (1) a face and voice LoRA; (2) 20 social videos in 6 months; (3) 8 languages; approval of every final video; withdrawal with 30 days' notice; the models deleted at the end. In the pipeline: the LoRA and voice files carry the consent ID in the registry, with `expires: 2027-04-30` and `allowed_uses: ["Ambassador campaign 2026-27"]`. The rights audit on a test date after expiry reported "registry ambassador_v2: expired … the service must refuse it" (the M01 test), and the adapter service refused it.

**A request to refuse:** "Make a video of our competitor's CEO announcing a recall." This is a realistic fake statement of a real person. Refused, with the reason in writing; the alternative offered was a comparison ad with their own spokesperson.

## Lab

**Deliverable:** `C16/M02/` with a consent record, its rights-log and registry entries, an enforcement test, a withdrawal procedure, and a refusal note.

1. Write a consent record (adapt the starter template) for a real use in your project: your own voice, or a consenting friend's likeness.
2. Add the rights-log line and a registry entry with an expiry and allowed uses.
3. Test enforcement: run `rights_audit.py` with a date after the expiry, and show that your service (or a check in your pipeline) refuses the adapter.
4. Write the withdrawal procedure: who receives the request, what stops when, what is deleted, how it is recorded.
5. Write a refusal note for one harmful request (invent a realistic one), with the reason and an alternative.

**Result checklist**
- [ ] Consent record with all fields.
- [ ] Rights-log line and registry entry linked to it.
- [ ] Enforcement test: audit fails after expiry; the pipeline refuses.
- [ ] Withdrawal procedure and refusal note.

## Model answer

**Withdrawal procedure (shape of a strong answer):**

| Step | Who | When |
|---|---|---|
| Receive the request (email to rights@studio) and confirm it | producer | within 2 working days |
| Mark the registry entry `withdrawn: <date>`; the service refuses it at once | engineer | same day |
| Stop scheduled posts that use the likeness | producer | same day |
| Delete the LoRA, the voice model, and the training data; record file hashes and the deletion date | engineer | within 30 days (as agreed) |
| Published outputs: removed or kept as the consent record says (here: removed from owned channels within 30 days) | producer | within 30 days |
| Log the withdrawal in the rights log | producer | when done |

"Enforcement test: on 2027-05-01 the audit reported the expired adapter; the adapter service returned `refused: consent expired 2027-04-30`; the delivery gate failed."
