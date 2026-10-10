# Writing Rules (ASD-STE100 profile for this program)

All student text follows these rules. `tools/build.py --check` counts long sentences in "Learn" sections.

## Sentences
1. Procedural sentence (an instruction): max. 20 words. Descriptive sentence: max. 25 words.
2. One instruction per sentence. Write instructions in the imperative ("Set the seed to 42.").
3. Use the active voice. Write "The model removes noise", not "Noise is removed by the model".
4. One topic per paragraph. Max. 6 sentences per paragraph.
5. Put a warning or a condition before the instruction ("If VRAM is less than 24 GB, use the FP8 model.").
6. Use a vertical list for 3 or more items or steps.

## Words
1. Use one word for one meaning. Use the same term every time (see the glossary).
2. Use simple verbs: "use" (not "utilize"), "make" (not "fabricate"), "start" (not "initiate"), "show" (not "demonstrate"), "help" (not "facilitate").
3. Do not use phrasal verbs when a simple verb exists: "examine" not "look into"; "remove" not "take out".
4. Do not use "-ing" forms as nouns where a noun exists ("generation", not "generating", as the subject).
5. Do not use slang, idioms, or marketing words ("game-changer", "magic", "stunning").

## Technical names (STE "technical nouns" and "technical verbs")
STE allows technical names that are specific to the field. In this program these include:
- Model terms: model, weights, parameter, token, embedding, transformer, attention, diffusion, latent, VAE, DiT, flow matching, sampler, scheduler, step, seed, CFG, LoRA, adapter, checkpoint, quantization, FP16, FP8, INT8, NVFP4, GGUF, MoE, distillation, inference, fine-tune, prompt, reference, conditioning, ControlNet, IP-Adapter, eval.
- Video terms: shot, frame, frame rate, fps, shutter, aperture, focal length, depth of field, white balance, log, RAW, codec, container, bitrate, chroma subsampling, bit depth, color space, gamut, gamma, HDR, SDR, LUT, grade, scope, timeline, NLE, cut, trim, J-cut, L-cut, B-roll, plate, matte, roto, key, composite, proxy, render, LUFS, stem, mix.
- Infrastructure terms: GPU, VRAM, CUDA, Metal, MLX, NVMe, NAS, RAID, container, Docker, endpoint, API, webhook, queue, cold start, autoscale, spot instance, object storage, CDN, MCP, MCP server, MCP client, agent, tool call.
- Product names are allowed in labs and in the landscape page. Do not put them in concept text.

## Format
- Headings are short noun phrases.
- Code, prompts, and settings go in code blocks.
- Numbers use digits and units with a space: "24 GB", "30 s", "US$0.10/s".
- Each claim about a product has a date ("as of 2026-10").
