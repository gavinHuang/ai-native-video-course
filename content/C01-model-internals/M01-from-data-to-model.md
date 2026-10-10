---
title: From data to model
hours: 7
outcomes:
  - Explain the difference between training and inference.
  - Explain what parameters, a loss function, and gradient descent do.
  - Explain why training data decides what a model can make.
  - Estimate the memory that a model needs from its parameter count and precision.
keywords: [model, parameter, training, inference, loss, gradient descent, weights]
summary: >
  A model is a large function with many numbers, called parameters. Training changes the parameters so that the
  function output gets closer to the training data. The loss function measures the error. Gradient descent changes
  each parameter a small amount to make the loss smaller. Inference is when you use the trained model. A model can
  only make what is similar to its training data. The memory that a model needs is about the parameter count
  multiplied by the bytes for each parameter.
diagram:
  type: flow
  title: Training loop vs inference
  nodes: ["Training data (images, video, text)", "Model makes a prediction", "Loss: measure the error", "Gradient descent: change parameters", "Trained weights file", "Inference: your prompt in, media out"]
  highlight: [4]
  loop: "the training loop repeats millions of times"
watch:
  - title: "3Blue1Brown — But what is a neural network?"
    url: https://www.youtube.com/watch?v=aircAruvnKk
    note: "Watch all (19 min). Good visual model of parameters and layers."
  - title: "3Blue1Brown — Gradient descent, how neural networks learn"
    url: https://www.youtube.com/watch?v=IHZwWFHWa-w
    note: "Watch 0:00–12:00. The idea of the loss landscape."
  - title: "Andrej Karpathy — Intro to Large Language Models"
    url: https://www.youtube.com/watch?v=zjkBMFhNj_g
    note: "Watch 0:00–20:00. Parameters file + run file; training vs inference at scale."
quiz:
  - q: "What changes during training?"
    options: ["The prompt", "The parameters (weights)", "The GPU driver", "The output resolution"]
    answer: 1
    explain: "Training changes the parameters so that the loss gets smaller. At inference, the parameters stay fixed."
  - q: "A model has 14 billion parameters in FP16 (2 bytes each). About how much memory do the weights need?"
    options: ["7 GB", "14 GB", "28 GB", "56 GB"]
    answer: 2
    explain: "14 × 10^9 × 2 bytes = 28 GB. Activations, the text encoder, and the VAE need more memory on top of this."
  - q: "Why can a video model fail to make a rare dance move correctly?"
    options: ["The prompt is too short", "The training data had few examples of it", "The seed is wrong", "The GPU is too slow"]
    answer: 1
    explain: "A model learns the distribution of its training data. Rare patterns are learned badly or not at all."
  - q: "What does the loss function do?"
    options: ["It deletes bad data", "It measures how far the output is from the target", "It makes the model smaller", "It chooses the seed"]
    answer: 1
    explain: "The loss is one number for the error. Gradient descent uses it to know in which direction to change each parameter."
  - q: "A tiny model reaches a loss of 0.001 on its training data, but fails on new inputs. What is the name of this problem?"
    options: ["Underfitting", "Overfitting: the model learned the training examples, not the general pattern", "Quantization", "Inference"]
    answer: 1
    explain: "Check a model on data it did not see in training. In C14, you will see the same problem with a LoRA trained on too few images."
  - q: "Why do newer video models follow prompts better than models from 2023?"
    options: ["Larger files only", "Better data: detailed (often machine-written) captions for each training clip, more and cleaner video, and better filtering", "Faster GPUs", "Longer prompts"]
    answer: 1
    explain: "The prompt can only use what the captions taught. Read the data statement in a model card (M04)."
  - q: "A 22B model is offered as a 4-bit file. About how much memory do the weights need?"
    options: ["44 GB", "22 GB", "About 11 GB", "2 GB"]
    answer: 2
    explain: "22 × 10^9 × 0.5 bytes ≈ 11 GB. Add the text encoder, the VAE, and activations."
deeper:
  - title: "Deep Learning (Goodfellow, Bengio, Courville), free online book"
    url: https://www.deeplearningbook.org/
  - title: "Hugging Face — Diffusion course (free)"
    url: https://huggingface.co/learn/diffusion-course/unit0/1
  - title: "Dive into Deep Learning (free, with code)"
    url: https://d2l.ai/
---
## Learn

### A model is a function
A generative model is a function. It takes an input, for example a text prompt and some random noise. It gives an output, for example an image or a video. The function has many internal numbers. These numbers are the **parameters**. A current open video model has between 5 and 30 billion parameters. The file that stores them is the **weights** file.

### Training
Training sets the parameters. The process is a loop:
1. Take a batch of examples from the training data.
2. Let the model make a prediction.
3. Measure the error with the **loss function**.
4. Calculate, for each parameter, the direction that makes the loss smaller. This is the gradient.
5. Change each parameter a small step in that direction. This is **gradient descent**.

The loop repeats millions of times. Training a large video model uses thousands of GPUs for weeks. You will not do this. In C14 you will do a small version: fine-tuning with a LoRA.

### Inference
**Inference** is the use of a trained model. The parameters do not change. You give an input and you get an output. Every time you generate a video, you run inference. Inference cost depends on the model size, the output size (resolution × duration), and the number of steps. With the same input, seed, settings, and software, a run usually gives the same output again; this makes tests repeatable (M07).

### The data decides what the model can make
A model learns the patterns of its training data. It can combine those patterns in new ways. It cannot reliably make things that are rare or absent in the data. This explains many failures:
- Hands, text, and fast complex motion were rare or hard in older data, so older models failed on them.
- A model trained mostly on stock footage makes "stock-looking" shots.
- A model trained with good captions follows prompts better.

When a model fails, ask first: "Was this pattern common in the training data?"

### Generalization and overfitting
A model is useful only if it works on inputs that it did not see in training. This is **generalization**. When a model learns the training examples too exactly, it fails on new inputs. This is **overfitting**. Large models trained on very large data generalize well. But they still overfit rare items: a model can copy a well-known image or logo if it saw it many times. Fine-tuning a small adapter on a few images overfits easily (C14).

### Captions teach the prompt
A text-to-video model learns from pairs: a clip and its caption. What the captions describe, the prompt can control. Model makers now write detailed captions with other AI models: subject, action, camera, light, style. This is a main reason why prompt following improved. When a word has no effect, the captions probably did not use it. Write prompts in the style of the captions, in the order of subject, action, scene, camera, and light (C02·M06).

### Memory estimate
Weights memory ≈ parameter count × bytes per parameter.

| Precision | Bytes per parameter | 14B model |
|---|---|---|
| FP32 | 4 | 56 GB |
| FP16 / BF16 | 2 | 28 GB |
| FP8 / INT8 | 1 | 14 GB |
| 4-bit (NVFP4, GGUF Q4) | about 0.5 | about 7 GB |

At inference, the GPU also needs memory for activations. These grow with resolution and video length. This is why a 720p, 5 s clip can fit on a GPU where a 1080p, 10 s clip does not. C01·M06 and C13 explain this in more detail.

## Worked example

**Task:** Decide if Wan 2.2 14B can run on a 24 GB GPU.

1. Weights in BF16: 14 × 2 = 28 GB. This is more than 24 GB. It does not fit.
2. Weights in FP8: 14 × 1 = 14 GB. It fits, with 10 GB left.
3. The text encoder (a large language model) also needs memory. Typical: 5–11 GB in FP16. The VAE needs about 0.5 GB.
4. Decision: use FP8 weights for the video model, and offload the text encoder to the CPU after it encodes the prompt. ComfyUI does this offload automatically.
5. Activations: start at 480p and 81 frames. Increase only after a successful run.

Result: it runs. The cost is some quality loss from FP8 and slower model loading. This matches the reported requirement (24 GB class with FP8).

## Lab

**Deliverable:** `C01/M01/memory.ipynb` and a one-page note.

1. Write a Python function `weights_gb(params_billion, bits)` that returns the weights memory in GB.
2. Make a table for these models: 1.3B, 5B, 14B, 22B, 27B. Use 16, 8, and 4 bits.
3. Add a column "fits on 24 GB / 32 GB / 80 GB" (weights only, plus 6 GB headroom).
4. Train a tiny model to understand the loop. Use the notebook cell below. Plot the loss for 200 steps.

```python
import torch, torch.nn as nn
x = torch.linspace(-3, 3, 256).unsqueeze(1)
y = torch.sin(x)
model = nn.Sequential(nn.Linear(1, 64), nn.Tanh(), nn.Linear(64, 1))
opt = torch.optim.Adam(model.parameters(), lr=1e-2)
losses = []
for step in range(200):
    loss = ((model(x) - y) ** 2).mean()   # loss function
    opt.zero_grad(); loss.backward()     # gradients
    opt.step()                           # gradient descent
    losses.append(loss.item())
print(sum(p.numel() for p in model.parameters()), "parameters")
```

5. Write 5 sentences: what changed during training, and what stays fixed at inference.

**Result checklist**
- [ ] The table has 15 rows and correct numbers.
- [ ] The loss plot goes down.
- [ ] The note uses the terms parameter, loss, gradient descent, inference correctly.

## Model answer

- 14B at 16 bit = 28 GB, at 8 bit = 14 GB, at 4 bit = 7 GB. With 6 GB headroom: 14B 8-bit fits on 24 GB; 14B 16-bit needs 80 GB class (or 32 GB with offload tricks).
- 27B (for example a large MoE video model) at 8 bit = 27 GB. It does not fit on 24 GB. It fits on 32 GB only with offload. Note: in an MoE model, only some experts are active for each step, but all weights must still be in memory or offloaded.
- The tiny model has 193 parameters. The loss falls from about 0.5–1.0 (it depends on the random start) to below 0.01; in our run with `torch.manual_seed(0)`, from 1.04 to 0.031 after 50 steps and 0.0044 after 200. During training, the 193 numbers change. At inference, they stay fixed, and the model maps each new x to a y.
