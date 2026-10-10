---
title: Light and color language
hours: 8
outcomes:
  - Describe a lighting setup with key, fill, back light, ratio, and direction.
  - Use color temperature and motivated light to create time and mood.
  - Define a color palette and contrast level for a project.
  - Write light and color instructions that models follow.
keywords: [key light, fill light, contrast ratio, color temperature, motivated light]
summary: >
  Light decides mood more than any other element. The key light is the main light. The fill light opens the
  shadows. The back light separates the subject from the background. The ratio between key and fill sets contrast:
  high contrast is dramatic, low contrast is soft. Color temperature, in kelvin, sets time and feeling: warm for
  candle and sunset, cool for moon and screens. Good light is motivated: it seems to come from a real source in the
  scene. In prompts, name the source, direction, quality, and color of the light.
diagram:
  type: flow
  title: Three-point lighting
  nodes: ["Key light: main source, 45° to the side, above eye level", "Fill light: opposite side, softer, sets contrast ratio", "Back light: behind the subject, separates it from background", "Practical lights: lamps and screens visible in the frame"]
  highlight: [0]
watch:
  - title: "Wandering DP — Cinematic lighting breakdowns (channel)"
    url: https://www.youtube.com/@WanderingDP
    note: "Choose any 2 breakdown videos. Note the key direction and contrast in each."
  - title: "StudioBinder — Three-point lighting explained"
    url: https://www.studiobinder.com/blog/three-point-lighting/
    note: "Read the guide and look at the diagrams."
quiz:
  - q: "High key-to-fill ratio (for example 8:1). Effect?"
    options: ["Flat, bright, comedy look", "Dramatic, deep shadows, film-noir feeling", "No shadows at all", "Blue color"]
    answer: 1
    explain: "Little fill means dark shadows and strong contrast."
  - q: "Candle light has a color temperature of about:"
    options: ["1,900 K (very warm)", "5,600 K (daylight)", "7,500 K (cool shade)", "10,000 K"]
    answer: 0
    explain: "Lower kelvin = warmer (more orange). Daylight is about 5,600 K."
  - q: "What is 'motivated light'?"
    options: ["Light that moves", "Light that seems to come from a real source in the scene", "Light from a drone", "Any LED light"]
    answer: 1
    explain: "A window, a lamp, a screen. The viewer believes the light, so the scene feels real."
  - q: "A generated night scene looks flat and grey. Best prompt fix?"
    options: ["Add 'beautiful'", "Name one hard key source, its direction and color, and say 'deep shadows, low fill'", "Increase resolution", "Use more steps"]
    answer: 1
    explain: "Specific light words give structure. Generic quality words do not."
  - q: "The wide shot has the window on the left; in the close-up, the face is lit from the right. What is the problem, and the fix?"
    options: ["No problem", "A light-continuity error: the key must come from the same side in every shot of the scene; write the light direction in the scene bible and in every prompt, and re-generate or flip the close-up if the frame allows it", "Use more fill", "Change the lens"]
    answer: 1
    explain: "Viewers feel continuity errors even when they cannot name them."
  - q: "A person stands in front of a bright window. The prompt does not mention fill. What does the model usually make?"
    options: ["A perfectly lit face", "A silhouette or a dark face with a clipped window, as a real camera would", "A black frame", "A day-for-night look"]
    answer: 1
    explain: "Ask for fill on the face ('soft fill from the room') or move the light, as on a real set."
deeper:
  - title: "Box — Set Lighting Technician's Handbook (book)"
    url: https://www.routledge.com/Set-Lighting-Technicians-Handbook-Film-Lighting-Equipment-Practice-and-Electrical-Distribution/Box/p/book/9781138391727
  - title: "ShotDeck — searchable film stills by light and color (reference library)"
    url: https://shotdeck.com/
---
## Learn

### Three-point light
See the diagram. Real scenes often break this pattern, but the vocabulary stays useful:
- **Key light:** the main light. Its direction makes the shape of the face.
- **Fill light:** opens the shadows. The **contrast ratio** key:fill sets the mood. 2:1 is soft and commercial; 4:1 is natural drama; 8:1 and more is noir.
- **Back light / rim light:** an outline that separates the subject from the background.
- **Practicals:** lamps, neon, screens, candles visible in the frame.

![Three-point lighting seen from above](fig:three-point.svg)

### Quality and direction
- **Hard light:** small source (sun, bare bulb). Sharp shadows.
- **Soft light:** large source (overcast sky, window with curtain). Soft shadows.
- **Direction:** front (flat), side (shape, drama), back (silhouette, rim), top (harsh, interrogation), under (horror).

![Hard and soft light, then five light directions; the orange dot is the source](fig:light-quality.svg)

### Color temperature
| Source | Approx. kelvin | Feeling |
|---|---|---|
| Candle, fire | 1,800–2,000 K | intimate, old |
| Tungsten bulb | 3,200 K | warm interior |
| Golden hour | 3,500–4,500 K | nostalgia, romance |
| Daylight | 5,600 K | neutral |
| Shade, overcast | 6,500–7,500 K | cool, sad |
| Moonlight (film convention) | blue tint | night, mystery |

Mixed temperatures create meaning: warm window inside, cool street outside = safety vs danger.

![Approximate color temperature of common sources](fig:color-temperature.svg)

### Exposure and dynamic range
A camera records a limited range from dark to bright: the **dynamic range**. Bright areas beyond it **clip** to pure white (a window, the sky); dark areas beyond it crush to black. Cinematographers expose for the important area (usually the faces) and accept clipping elsewhere, or add light to the dark side. Generated video imitates this: "bright window behind, face in shadow" gives a silhouette unless you ask for fill on the face. For HDR delivery (C09·M04), highlights can be brighter, but faces stay in the normal range.

![Expose for the face; what falls outside the recorded range clips or crushes](fig:dynamic-range.svg)

### Light continuity
In one scene, the light must come from the same direction in every shot. If the window is on the left in the wide shot, it must light the left side of the face in the close-up. Generated shots break this often, because each shot is generated separately. Write the light direction relative to the room ("window on the east wall, frame left in the master") in the scene bible, and repeat it in every prompt of the scene. Check it in the review of every new shot (C02·M04).

![The window side in the wide shot must be the lit side in the close-up](fig:light-continuity.svg)

### Atmosphere
Haze, smoke, rain, and dust make light visible: beams, halos, and depth (far objects look lighter). A little haze is one of the easiest ways to make a generated frame look "cinematic", because it adds depth and softens contrast in the background. Too much makes everything grey.

![Haze adds beams and depth; too much makes everything grey](fig:atmosphere.svg)

### Palette and contrast
Define for each project:
- 3–5 main colors (for example teal, amber, deep green, off-white).
- Saturation level (muted vs vivid).
- Contrast (lifted blacks vs deep blacks).
- Where the accent color appears (only on the hero product, only on one character).

This is the base of your look bible (C04·M04) and your grade (C09).

![The four palette decisions for a project](fig:palette.svg)

### Skin tones
Viewers forgive many color changes, but not wrong skin. Keep skin natural under strong looks: in a teal-and-orange grade, skin stays in the warm range, and only the background goes teal. Check skin on a vectorscope (C09·M01): skin of every color falls near one line, the skin-tone line.

![A vectorscope: hue is the angle, saturation the distance from the centre](fig:vectorscope.svg)

### Light in prompts
Template: `[quality] [source] from [direction], [color/temperature], [contrast], [practicals], [atmosphere]`
Example: "Hard low sunlight from frame left, warm 3,500 K, deep shadows with little fill, a cool blue rim from a window behind, light haze in the air."

## Worked example

**Same kitchen, three moods** (image model, then I2V):
1. "Soft daylight through a large window from the right, 5,600 K, low contrast, bright white walls" → fresh, product-friendly.
2. "One warm tungsten pendant lamp above the table, 3,000 K, dark room, strong falloff, deep shadows" → intimate, late night.
3. "Cold blue light from an open fridge, the only source, from below, face lit from under, rest of the room black" → suspense.

The model, scene, and character are the same in all three. Only the light changed. The story changed.

## Lab

**Deliverable:** `C02/M03/` with 9 frames and a palette sheet.

1. Choose a simple scene (a person at a desk).
2. Generate 3 setups: high-key commercial, natural window light, low-key noir.
3. For each setup, generate 3 color temperatures (warm, neutral, cool).
4. Make a 3×3 contact sheet.
5. Choose one frame and extract a 5-color palette (any palette tool, or Python k-means).
6. Write a 6-line "light and color rule" for a fictional project using this look.

**Result checklist**
- [ ] 3×3 contact sheet with labels.
- [ ] Palette with hex values.
- [ ] Light rule names key direction, ratio, temperature, practicals.

## Model answer

A good light rule: "Key: soft window light from frame left, 4,500 K. Ratio: 4:1, no extra fill. Rim: none, except practicals. Practicals: one warm desk lamp in frame (2,700 K). Night scenes: blue street light outside windows, warm practicals inside. Accent color: amber only on the main character's items. Blacks: deep, not lifted." Models follow source, direction, and temperature well. They follow "ratio 4:1" weakly; the words "deep shadows, little fill" work better.

In the 3×3 sheet, a strong answer also notes continuity: "in 2 of 9 frames the key moved to the other side when the temperature changed; fixed by naming the window wall in every prompt". The palette has hex values and states where the accent color may appear.
