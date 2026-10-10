---
title: Color science essentials
hours: 15
outcomes:
  - Explain color space, gamut, transfer function, white point, and range, and read them from a file.
  - Explain bit depth and chroma subsampling, and why 8-bit 4:2:0 sources need a 10-bit intermediate for grading.
  - Set up a color-managed project for mixed sources (generated, phone HDR, stock), and tag every source.
  - Tag delivery files correctly, and prove it with a check.
  - Explain SDR and HDR delivery basics, and when not to deliver HDR.
keywords: [color space, gamut, transfer function, bit depth, chroma subsampling, ACES]
summary: >
  A color space has four parts: primaries (which colors exist), white point, transfer function (how values map to
  light), and encoding (range, bit depth, subsampling). A video file carries tags for them; a missing or wrong tag
  makes players guess, and a guess changes how the picture looks. Generated clips are usually 8-bit 4:2:0 with
  Rec.709-like color: fine to watch, weak to grade, so convert them once to a 10-bit intermediate. A color-managed
  project converts every tagged source into one working space and makes the delivery with one output transform.
diagram:
  type: stack
  title: What a color space defines
  nodes: ["Primaries / gamut: which colors (Rec.709, P3, Rec.2020)", "White point: D65 for video", "Transfer function: Rec.709 / BT.1886, PQ, HLG, log", "Range: video (16–235) or full (0–255)", "Encoding: bit depth (8/10/12) and subsampling (4:2:0, 4:2:2, 4:4:4)"]
  highlight: [2]
watch:
  - title: "Cullen Kelly — color management fundamentals (YouTube channel)"
    url: https://www.youtube.com/@CullenKelly
    note: "Choose one video on color management; note the working space and the output transform."
  - title: "ACES — Academy Color Encoding System (official site)"
    url: https://acescentral.com/
    note: "Read the 'What is ACES' introduction."
quiz:
  - q: "A file has no color tags. One player shows it with richer blacks than another. Why?"
    options: ["One player is broken", "Without tags, each player guesses the primaries, transfer, and range; different guesses give different pictures", "The file is damaged", "The screens are the same"]
    answer: 1
    explain: "Tags tell the player how to show the values. Tag every delivery, and check the tags (C09·M04)."
  - q: "You export with the output options primaries=bt709 and transfer=bt709 from an untagged source, and the check still shows 'unknown' for both. What is a reliable fix in ffmpeg?"
    options: ["Export again", "Set the tags on the frames with the setparams filter (or with the h264_metadata bitstream filter), then check again with ffprobe", "Use a higher bitrate", "Use another container"]
    answer: 1
    explain: "In the module test (ffmpeg 9), the output options alone wrote only the matrix and range tags. The setparams filter wrote all four."
  - q: "A JPEG (full range, 0–255) becomes a frame of an H.264 video in video range (16–235) without conversion. What do the scopes show?"
    options: ["Nothing changes", "Values below 16 and above 235: blacks and whites outside the legal range, and players may clip them", "Only the colors change", "The frame is smaller"]
    answer: 1
    explain: "In the module test, 5 % of the pixels were at or below 16 and 10 % at or above 235 in the converted frame. Convert the range explicitly."
  - q: "Why convert 8-bit 4:2:0 generated clips to a 10-bit 4:2:2 intermediate before grading?"
    options: ["They look better at once", "Grading stretches values; 8-bit has 256 steps per channel and shows bands in gradients, and 4:2:0 keeps color at a quarter of the resolution; 10-bit 4:2:2 keeps more steps and color detail for the grade", "It is required for upload", "It makes files smaller"]
    answer: 1
    explain: "The intermediate does not add detail, but the grade does not lose more on the way."
  - q: "Your project mixes generated clips (Rec.709), phone clips (HLG HDR), and stock (Rec.709). The phone clips look washed out on the timeline. What is wrong?"
    options: ["The phone is bad", "The phone clips are not tagged or managed as Rec.2100 HLG; in a color-managed project, tag their input color space so they convert correctly into the working space", "They need more saturation", "Delete them"]
    answer: 1
    explain: "HLG shown as Rec.709 looks flat and grey. Color management with the right input tags fixes it."
  - q: "You have no HDR monitor. The client asks for an HDR master. What do you do?"
    options: ["Grade HDR on the laptop", "Explain that you cannot judge an HDR grade without an HDR reference display; deliver SDR, or rent a calibrated HDR setup or a colorist", "Convert SDR to HDR automatically and send it", "Ignore the request"]
    answer: 1
    explain: "HDR highlights and blacks cannot be judged on an SDR screen. An HDR grade needs an HDR reference display."
  - q: "What does a model card tell you that you need for color management?"
    options: ["Nothing", "The output color space, transfer, and bit depth of the model, so that you can tag its clips correctly instead of guessing", "The price", "The training data size"]
    answer: 1
    explain: "Some models output Rec.709-like 8-bit video, some 10-bit or HDR. Read the card; do not assume."
deeper:
  - title: "Poynton — Digital Video and HD: Algorithms and Interfaces (book)"
    url: https://www.elsevier.com/books/digital-video-and-hd/poynton/978-0-12-391926-7
  - title: "Netflix Partner Help Center — color and delivery specifications"
    url: https://partnerhelp.netflixstudios.com/
  - title: "ITU-R BT.709 — parameter values for HDTV (the Rec.709 standard)"
    url: https://www.itu.int/rec/R-REC-BT.709
---
## Learn

### Why color science matters in AI-native video
A film made from generated shots mixes sources from several models, plus phone clips, stock, and graphics. Each source has its own color encoding. If the encodings are not known and managed, the same grade looks different on each shot, and the delivery looks different on each screen. Color science is the set of facts that makes all of this predictable.

### The four parts of a color space
1. **Primaries and gamut:** the red, green, and blue that the system uses, and so the range of colors it can show. Rec.709 (HD video, sRGB-like) is the smallest common gamut. DCI-P3 is larger. Rec.2020 is larger again.
2. **White point:** the color of "white". Video uses D65.
3. **Transfer function:** how code values map to light. SDR video uses the Rec.709 / BT.1886 gamma. HDR uses PQ (absolute brightness, up to 10,000 nits) or HLG (relative, compatible with SDR screens). Cameras record log curves to keep more range for grading.
4. **Encoding:** how the values are stored. This includes range, bit depth, and chroma subsampling (below).

### Range
- **Video (limited) range:** luma from 16 to 235 in 8-bit. Values below 16 are "blacker than black", above 235 "whiter than white". This is the normal range for video files.
- **Full range:** 0 to 255. Normal for images (JPEG, PNG) and some cameras.
When a full-range image becomes video without a range conversion, its blacks and whites fall outside the legal range. Players may clip them, and the image looks harsher.

### Bit depth and chroma subsampling
- **8-bit:** 256 steps per channel. A grade stretches the values, and a smooth gradient (a sky, a wall) shows bands.
- **10-bit:** 1,024 steps. The standard for grading and HDR.
- **4:4:4:** full color resolution. **4:2:2:** half the horizontal color resolution. **4:2:0:** a quarter (half in each direction). Detail is in the luma, so 4:2:0 looks fine, but color keys and strong color grades show the loss.
Most generated clips arrive as 8-bit 4:2:0 H.264 or H.265: good to watch, weak to grade. Convert each clip once to a 10-bit 4:2:2 intermediate (for example ProRes 422 HQ or DNxHR HQX) before finishing. This adds no detail, but the grade loses less.

### File tags
A video file stores tags for the primaries, the transfer, the matrix (how RGB becomes Y′CbCr), and the range. Players use them to show the picture. If a tag is missing, the player guesses, and different players guess differently. Check the tags of every source and every delivery. Tag what you deliver, and prove it with a check (C09·M04).

### Color management
A color-managed project works in three steps:
1. **Input:** tag each source with its real color space (for example "Rec.709" for most generated clips, "Rec.2100 HLG" for a phone's HDR clips).
2. **Working space:** the software converts every source into one large working space (for example a wide-gamut log space, or ACES with ACEScct). You grade there.
3. **Output:** one output transform makes the delivery (Rec.709 SDR; HDR if you deliver it).
With this setup, shots from different sources start from comparable contrast and color.

### Generated sources
Most models output Rec.709-like or sRGB-like 8-bit video. Some report 10-bit or HDR output. Read the model card and tag accordingly. If the card says nothing, test: generate a clip with a known grey and color patch in the prompt, and look at it on the scopes.

### HDR basics
HDR10 is Rec.2020 primaries + PQ transfer + 10-bit + static metadata. You can only judge an HDR grade on an HDR reference display. Without one, deliver SDR.

## Tool walkthrough

### Read the tags and the scopes

```bash
ffprobe -v error -select_streams v:0 -show_entries \
  stream=pix_fmt,color_range,color_space,color_primaries,color_transfer -of compact clip.mp4
python starter/tools/scopes.py clip.mp4 --at 2.0 --out scopes.png      # waveform, vectorscope, histogram + numbers
```

### Make a 10-bit intermediate

```bash
ffmpeg -i gen.mp4 -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le -c:a pcm_s24le gen_hq.mov
```

### Tag a delivery so that the tags stick

```bash
ffmpeg -i master.mov -vf "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -ar 48000 web.mp4
python starter/tools/spec_check.py web.mp4 --spec starter/specs/web_1080p.json
```

### Color management in DaVinci Resolve (as of 2026-10)
Project Settings → Color Management: set the color science to "DaVinci YRGB Color Managed", the working space to DaVinci Wide Gamut / Intermediate, and the output to Rec.709 Gamma 2.4 (or Rec.709-A for web viewing on Macs; follow the client spec). Then, in the Media Pool, right-click clips → Input Color Space, and set each source correctly.

## Worked example

**Tagging test** (2026-10-04, ffmpeg 9.0.2, an untagged H.264 source):

| Method | primaries | transfer | matrix | range |
|---|---|---|---|---|
| Output options `-color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv` | unknown | unknown | bt709 | tv |
| `setparams` filter on the frames | bt709 | bt709 | bt709 | tv |
| `h264_metadata` bitstream filter | bt709 | bt709 | bt709 | tv |

The output options alone did not tag the primaries and the transfer. `spec_check.py` found it. Only a check shows this; the picture looks the same on your screen.

**Range test:** a full-range JPEG portrait put into an H.264 video without a range conversion. `scopes.py` on one frame: luma minimum 0, maximum 255, 5.1 % of the pixels at or below 16, and 9.9 % at or above 235. A legal web master must keep these within the video range.

**Mixed project:** 20 generated clips (H.264 8-bit, Rec.709), 6 phone clips (HLG HDR), 4 stock clips (Rec.709 ProRes).
1. Generated clips to ProRes 422 HQ 10-bit.
2. Color management: wide-gamut working space; output Rec.709 Gamma 2.4.
3. Input tags: generated and stock Rec.709; phone Rec.2100 HLG.
4. Result: the phone clips no longer look washed out; all sources start from comparable contrast.

## Lab

**Deliverable:** `C09/M01/` with a source table, scope images, a color-management screenshot, and a tagged delivery with its check.

1. Collect 10 clips: 6 generated (from at least 2 models), 2 phone clips (one HDR if your phone records HDR), and 2 stock clips.
2. Read the tags of each with `ffprobe`. Fill in a source table: codec, bit depth, subsampling, primaries, transfer, matrix, range, and what the model card says.
3. Make scopes for one frame of each with `scopes.py`. Note any values outside the video range.
4. Make 10-bit intermediates of the generated clips.
5. Set up a color-managed project. Tag each source. Take before and after screenshots of the phone HDR clip.
6. Export one tagged delivery. Prove the tags with `spec_check.py`.

**Result checklist**
- [ ] Source table for 10 clips.
- [ ] Scope images with notes on range problems.
- [ ] Color-management setup with input tags; before/after of the HDR clip.
- [ ] A delivery that passes the tag checks.

## Model answer

**Source table (extract):**

| Clip | Codec, depth, subsampling | Primaries / transfer / range (file) | Model card says | Action |
|---|---|---|---|---|
| S03 (model A) | H.264 8-bit 4:2:0 | unknown / unknown / tv | "Rec.709" | Tag Rec.709; 10-bit intermediate |
| S05 (model B) | H.265 10-bit 4:2:0 | bt709 / bt709 / tv | "10-bit color" | Tag Rec.709; intermediate |
| PHONE_02 | HEVC 10-bit 4:2:0 | bt2020 / arib-std-b67 (HLG) / tv | — | Tag Rec.2100 HLG |
| KF still in an insert | PNG 8-bit | full range | — | Convert range to video |

"4 of 6 generated clips had no primaries or transfer tags. All were Rec.709-like on the scopes (a grey patch in the prompt read neutral at the expected level), so I tagged them Rec.709. The phone HLG clip looked flat before tagging and correct after."

The delivery check prints `PASS (19/19 checks)`, including all four color tags.
