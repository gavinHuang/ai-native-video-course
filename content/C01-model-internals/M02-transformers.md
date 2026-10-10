---
title: Tokens, embeddings, and attention
hours: 9
outcomes:
  - Explain how text, images, video, and audio become tokens.
  - Explain what an embedding is and why similar meanings are near each other.
  - Explain self-attention and cross-attention in one paragraph each.
  - Explain why attention cost grows fast with video length and resolution.
keywords: [token, embedding, transformer, attention, context window, patch]
summary: >
  A transformer works on tokens. A token is a small piece of the input: part of a word, a patch of an image, or a
  small block of video in space and time. Each token becomes an embedding, a list of numbers that holds its meaning.
  Attention lets every token look at every other token and take the information it needs. Self-attention connects
  tokens of the same input. Cross-attention connects the video tokens to the prompt tokens. Attention cost grows with
  the square of the token count. This is why long, high-resolution video is expensive.
diagram:
  type: flow
  title: From input to transformer
  nodes: ["Input: text / image / video", "Tokenize: words or space-time patches", "Embed: each token → vector", "Self-attention: tokens exchange information", "Cross-attention: video tokens read the prompt", "Output tokens → decode"]
  highlight: [3, 4]
watch:
  - title: "3Blue1Brown — Transformers, the tech behind LLMs"
    url: https://www.youtube.com/watch?v=wjZofJX0v4M
    note: "Watch all (27 min). Tokens and embeddings explained visually."
  - title: "3Blue1Brown — Attention in transformers, step by step"
    url: https://www.youtube.com/watch?v=eMlx5fFNoYc
    note: "Watch all (26 min). Query, key, value."
  - title: "Andrej Karpathy — Let's build GPT: from scratch, in code"
    url: https://www.youtube.com/watch?v=kCc8FmEb1nY
    note: "Optional, 2 h. For students who want to write attention in code."
quiz:
  - q: "In a video transformer, what is a typical token?"
    options: ["One full frame", "A small space-time patch, for example 2×16×16 pixels over 2 frames in latent space", "One second of audio", "One word of the prompt only"]
    answer: 1
    explain: "Video models cut the (latent) video into small blocks in space and time. Each block becomes one token."
  - q: "What does cross-attention do in a text-to-video model?"
    options: ["It compresses the video", "It lets video tokens take information from the prompt tokens", "It removes noise", "It sets the frame rate"]
    answer: 1
    explain: "Cross-attention is the bridge between the prompt and the picture. Weak cross-attention = weak prompt adherence."
  - q: "You double the duration of a clip. Full attention cost grows by about:"
    options: ["1.4×", "2×", "4×", "No change"]
    answer: 2
    explain: "Token count doubles. Full attention compares every token with every other token, so cost grows with the square: 2² = 4×."
  - q: "Why are words with similar meaning near each other in embedding space?"
    options: ["A human placed them there", "Training puts tokens that are used in similar contexts at similar vectors", "Alphabetical order", "Random chance"]
    answer: 1
    explain: "The embedding is learned. Tokens that behave in a similar way get similar vectors."
  - q: "A model uses windowed attention: each token looks only at tokens near it in space and time. What is the typical cost of this saving?"
    options: ["None", "Weaker long-range consistency: details far apart in time (a logo at second 1 and second 9) can drift", "Lower frame rate", "No audio"]
    answer: 1
    explain: "Sparse and windowed attention trade global consistency for speed. Test long shots with returning details (M07)."
  - q: "You double both the width and the height of a clip. How do tokens and full attention cost change?"
    options: ["2× and 4×", "4× tokens and about 16× attention cost", "No change", "8× and 64×"]
    answer: 1
    explain: "Tokens grow with the area; full attention grows with the square of the tokens: 4² = 16."
  - q: "What does a transformer block contain?"
    options: ["Only a VAE", "An attention layer and a small feed-forward network, each with a skip connection and normalization; a model stacks many blocks", "A tokenizer", "A sampler"]
    answer: 1
    explain: "Depth (the number of blocks) and width (the embedding size) set most of the parameter count."
deeper:
  - title: "Vaswani et al. (2017) — Attention Is All You Need"
    url: https://arxiv.org/abs/1706.03762
  - title: "Dosovitskiy et al. (2020) — An Image is Worth 16x16 Words (ViT)"
    url: https://arxiv.org/abs/2010.11929
  - title: "The Illustrated Transformer (Jay Alammar)"
    url: https://jalammar.github.io/illustrated-transformer/
---
## Learn

### Tokens
A transformer does not see words or pixels directly. It sees **tokens**.
- **Text:** a tokenizer cuts text into pieces. "Cinematic" can be one token or two. A 100-word prompt is about 130 tokens.
- **Image:** the image is first compressed (see M03). Then it is cut into small squares. Each square is a **patch**, and each patch is a token.
- **Video:** the compressed video is cut into small blocks in space *and* time. One block can be 2×2 latent pixels over 1 latent frame. Each block is a token.
- **Audio:** the sound is compressed into a sequence of short frames. Each frame becomes a token.

### Embeddings
Each token becomes an **embedding**: a vector of, for example, 3,072 numbers. Training places tokens with similar use near each other. So "dusk" and "sunset" are near, and "dusk" and "spreadsheet" are far. A position signal is added, so the model knows where each token is in the sequence, in the frame, and in time.

### Attention
**Attention** is the core operation. For each token, the model asks: "Which other tokens are important for me?" Each token makes three vectors:
- a **query** (what I look for),
- a **key** (what I contain),
- a **value** (what I give).

The model compares each query with all keys. High similarity means high weight. The token then takes a weighted mix of the values.

- **Self-attention:** tokens of the video look at other tokens of the same video. This keeps a face the same from frame 1 to frame 120. It also keeps motion smooth.
- **Cross-attention:** video tokens look at the prompt tokens. This is how "red umbrella" in the prompt becomes a red umbrella in the frame. Some new models do not use separate cross-attention. They put text and video tokens in one sequence (joint attention). The effect is the same.

### The cost of attention
Full attention compares every token with every other token. If there are N tokens, the cost is about N². A 5 s, 720p clip has tens of thousands of tokens. Double the duration and the cost is about 4×. Double the width and height and the token count is 4×, so the cost is about 16×. This one fact explains:
- why clip length is limited (5–15 s, now up to 30 s in the best models),
- why high resolution is often made by upscaling (C09),
- why "extend" and multi-shot features exist (C05).

### Blocks and layers
A transformer is a stack of identical **blocks**. Each block has two parts: an attention layer (tokens exchange information) and a small **feed-forward network** (each token is changed on its own). Each part adds its result to its input (a skip connection) and normalizes the numbers. A large video model has 30–60 blocks with embeddings of 3,000–5,000 numbers. The number of blocks and the embedding size set most of the parameter count (M01). In diffusion models, each block also receives the noise level (the timestep), so the same blocks work at every step (M03).

### Saving attention cost
Because full attention grows with N², model makers save cost in several ways:
- **windowed or sparse attention:** each token looks only at tokens near it, or at a chosen subset;
- **separate space and time attention:** first within a frame, then across frames at the same position;
- **efficient kernels** (for example FlashAttention) that compute the same result with less memory traffic.
The first two can weaken long-range consistency: a detail at second 1 may change by second 9. Efficient kernels give the same result, only faster.

### Context window
An LLM also has a limit on tokens: the **context window**. In C03 you will use it to hold a whole script, a style guide, and a shot list at the same time.

## Worked example

**Task:** Estimate the token count of a video clip.

Settings: 1280×720, 5 s at 16 fps = 81 frames. Typical video VAE compression: 8× in width and height, 4× in time. Patch size in the transformer: 2×2 in space, 1 in time.

1. Latent size: 1280/8 = 160, 720/8 = 90, time (81−1)/4+1 = 21 latent frames.
2. Tokens per latent frame: (160/2) × (90/2) = 80 × 45 = 3,600.
3. Total tokens: 3,600 × 21 = 75,600.
4. Attention pairs: 75,600² ≈ 5.7 billion for each attention layer and step.

Now change to 1920×1080: tokens = 120 × 67.5 × 21 ≈ 170,000. That is about 2.25× more tokens and about 5× more attention cost. This is why many models make 720p natively and then upscale.

## Lab

**Deliverable:** `C01/M02/tokens.ipynb`.

1. Use a tokenizer to count prompt tokens:
```python
import tiktoken
enc = tiktoken.get_encoding("o200k_base")
p = "Low-angle medium shot, a cyclist at dusk, rain, neon reflections, 35mm, slow dolly in"
print(len(enc.encode(p)), [enc.decode([t]) for t in enc.encode(p)])
```
2. Write a function `video_tokens(w, h, frames, s=8, t=4, patch=2)`.
3. Make a table of tokens and relative attention cost for: 480p/5 s, 720p/5 s, 720p/10 s, 1080p/10 s, 4K/10 s.
4. Explain in 4 sentences why a vendor limits clip length and why "4K" output is often an upscale.

**Result checklist**
- [ ] Token function gives about 75,600 for 720p, 81 frames.
- [ ] The table shows the square growth of attention cost.
- [ ] The explanation uses the terms token, attention, and upscale.

## Model answer

| Setting | Tokens (approx.) | Attention cost vs 720p/5 s |
|---|---|---|
| 480p, 5 s | 33,600 | 0.2× |
| 720p, 5 s | 75,600 | 1× |
| 720p, 10 s | 147,600 | 3.8× |
| 1080p, 10 s | 332,000 | 19× |
| 4K, 10 s | 1,330,000 | 310× |

A vendor limits clip length because attention cost grows with the square of the token count. A 4K, 10 s clip with full attention costs hundreds of times more than a 720p, 5 s clip. For this reason, most systems generate at a lower resolution and then upscale. Some use sparse or windowed attention to reduce the cost, and this can reduce long-range consistency.
