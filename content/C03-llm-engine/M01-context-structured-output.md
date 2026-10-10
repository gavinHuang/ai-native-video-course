---
title: Context engineering and structured output
hours: 8
outcomes:
  - Build a project context (bible, constraints, examples) for an LLM.
  - Get structured output that matches a JSON schema, and validate it.
  - Explain the difference between instructions, context, and examples.
  - Choose an LLM for a task with a small test, not with a leaderboard only.
keywords: [context engineering, JSON schema, structured output, system prompt, few-shot]
summary: >
  An LLM only knows what is in its training and in its context. Context engineering means you give it the right
  information at the right time: the project bible, constraints, examples, and the task. Structured output makes the
  model answer in a fixed JSON schema, so code can read and check it. Always validate the output. Put stable rules in
  the system prompt, project facts in context documents, and two or three good examples to show the format. Choose
  the model with a small test on your own task.
diagram:
  type: stack
  title: What goes into the context
  nodes: ["System prompt: role, rules, output format", "Project bible: characters, look, tone, brand rules", "Constraints: platform, duration, budget, legal", "Examples (few-shot): 2–3 good outputs", "Task: the current request + input data", "Output schema: JSON schema the answer must match"]
  highlight: [5]
watch:
  - title: "Anthropic — Prompt engineering overview (docs)"
    url: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
    note: "Read 'Be clear and direct', 'Use examples', and 'Use XML tags'."
  - title: "Anthropic — Effective context engineering for AI agents"
    url: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
    note: "Read all. Context is a limited resource; choose what goes in."
quiz:
  - q: "Where do you put the brand rules that apply to every request in a project?"
    options: ["In each user message, rewritten", "In the system prompt or a stable project document in context", "Nowhere; the model knows them", "In the output schema"]
    answer: 1
    explain: "Stable rules belong in stable context. Rewriting them each time causes drift."
  - q: "Why validate structured output with code?"
    options: ["LLMs never make mistakes", "Models can still return missing fields or wrong types; downstream tools would fail", "It is faster", "To make the JSON shorter"]
    answer: 1
    explain: "Validate, and on failure send the error back to the model to repair."
  - q: "What do few-shot examples do best?"
    options: ["Teach new facts", "Show the exact format, length, and style you want", "Reduce cost", "Increase the context window"]
    answer: 1
    explain: "Examples are the strongest format signal."
  - q: "Best way to choose an LLM for writing shot lists?"
    options: ["The #1 model on any leaderboard", "Run 10 real briefs through 2–3 models and score the shot lists blind", "The cheapest", "The newest"]
    answer: 1
    explain: "Same method as C01·M07, applied to text."
  - q: "Your shot list passes the JSON schema, but its shots add up to 74 s for a 60 s target. Whose job is it to catch this?"
    options: ["The schema's", "A check function after validation; send its message back in the repair step like a schema error", "The video model's", "Nobody's"]
    answer: 1
    explain: "Schemas check shape. Code checks meaning across fields."
  - q: "You call the model 200 times a day with the same 6,000-token bible and a short task. What lowers cost most?"
    options: ["Shorter task text", "Put the bible first as a stable prefix so the API can cache it, and send only the scene's part of the bible", "Higher temperature", "More examples"]
    answer: 1
    explain: "Stable prefix first, changing task last. Send only what the task needs."
  - q: "Which temperature setting suits a JSON extraction step?"
    options: ["A high value for creativity", "A low value, for stable and repeatable output", "It does not matter", "The maximum"]
    answer: 1
    explain: "Use variety where you want options (hooks, titles), not where you want correct data."
deeper:
  - title: "JSON Schema — Getting started"
    url: https://json-schema.org/learn/getting-started-step-by-step
  - title: "Pydantic — Models and validation (docs)"
    url: https://docs.pydantic.dev/latest/concepts/models/
  - title: "Anthropic — Structured outputs / tool use for JSON"
    url: https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview
---
## Learn

### The model knows only two things
1. What it learned in training (general knowledge, until its cutoff date).
2. What is in its **context** now.

It does not know your character's name, your client's colors, or the platform you deliver to. **Context engineering** is the work of choosing what goes into the context, in which form, and when.

### Layers of context
See the diagram. Put each type of information in its own layer:
- **System prompt:** role, rules, output format. Stable.
- **Project documents:** bible, look, tone. Stable per project.
- **Constraints:** platform, duration, legal limits.
- **Examples:** 2–3 outputs that you like.
- **Task:** the current request.
- **Output schema:** the JSON shape the answer must have.

Use clear separators (headings or XML-like tags) so the model knows which part is which.

### Structured output
Downstream tools need data, not prose. Define a **JSON schema**, and ask the model to answer in it. Most APIs (2026) support structured output or tool-call schemas that enforce the format. Then:
1. Parse the JSON.
2. Validate it (for example with Pydantic).
3. If it fails, send the validation error back and ask for a repair.
4. Log the final valid output.

### Context is a budget
A long context costs money and time on every call, and models use information in very long contexts less reliably than information in short ones. Rules:
- Put only what the task needs: the scene's part of the bible, not the whole series bible.
- Put stable material first (system prompt, bible, examples) and the changing task last. Many APIs then **cache** the stable prefix: later calls with the same prefix are cheaper and faster.
- Repeat the most important constraint near the end, next to the task ("Total duration: 60 s").
- Prefer references by ID ("CHAR-MARA-01") and let a tool fetch details, instead of pasting everything (M04).

### Settings that change outputs
- **Temperature** (or similar settings): low values give stable, repeatable answers (good for JSON, checks, and extraction); higher values give more variety (good for 10 hook ideas).
- **Maximum output length:** set it high enough for the full JSON; a cut-off answer is invalid JSON.
- **Reasoning or "thinking" modes:** better on planning and constraint tasks (fit 14 shots into 60 s), slower and more expensive. Test whether your task needs them.

### Checks beyond the schema
A schema checks the shape: field names, types, allowed values. It cannot check meaning across fields: the total duration, a shot longer than the video route allows, the same ID twice, a character not in the bible. Write these as small functions, test them, and send their messages back in the repair step, exactly like schema errors.

### Instructions vs examples
- Instructions say *what* and *why*.
- Examples show *how it looks*.
- When they disagree, the model often follows the examples. Keep them consistent.

### Choose the model
Public leaderboards rank the large hosted model families near the top, with open-weight models close behind on many tasks (dated names in the Tool walkthrough). For your task, run a small blind test: 10 real inputs, 2–3 models, score with criteria. Note cost and speed too.

## Tool walkthrough

### Run the starter solution
```bash
pip install anthropic pydantic
export ANTHROPIC_API_KEY=...            # or adapt call_llm() to your provider
python starter/solutions/C03-M01/shotlist.py treatment.md --target-s 60 > shots.json
python -m pytest -q starter/solutions/C03-M01/test_shotlist.py   # 5 offline tests with a fake model
```
The prompts are files (`system.md`, `examples.json`); every call is logged to `calls.jsonl` with tokens and time. The `--fake` option replays saved replies, so you can test the repair loop without a key.

### Models (as of 2026-10)
Public leaderboards put the Claude, GPT, and Gemini families near the top; open-weight Qwen and DeepSeek models are close behind on many tasks and can run on your own hardware for private projects (C13·M05).

## Worked example

**Pydantic schema for a shot list:**
```python
from pydantic import BaseModel, Field
from typing import Literal

class Shot(BaseModel):
    id: str
    duration_s: float = Field(ge=1, le=15)
    size: Literal["EWS","WS","FS","MS","MCU","CU","ECU"]
    angle: str
    lens_mm: int
    move: str
    subject: str
    action: str
    light: str
    audio: str
    purpose: str

class ShotList(BaseModel):
    title: str
    ratio: Literal["16:9","9:16","1:1","4:5","2.39:1"]
    shots: list[Shot]
```
Call (pseudo-code, any provider):
```python
resp = llm.generate(system=SYSTEM, context=[BIBLE, CONSTRAINTS, EXAMPLES],
                    task=treatment_text, schema=ShotList.model_json_schema())
try:
    shots = ShotList.model_validate_json(resp.text)
except ValidationError as e:
    resp = llm.generate(..., task=f"Fix this JSON. Errors: {e}. JSON: {resp.text}")
```
Check after validation: total duration = target duration ± 2 s; every shot has a purpose; no shot longer than the model's limit.

## Lab

**Deliverable:** `C03/M01/` with schema, prompt files, a script, and 3 valid shot lists.

1. Write a project bible (1 page) for the story from C02·M05.
2. Write the system prompt and 2 example shots.
3. Implement the schema and the validate-repair loop in Python.
4. Run it on 3 different treatments.
5. Add 3 automatic checks (total duration, max shot length, required fields not empty).
6. Run the same task on 2 LLMs. Compare validity rate, quality (blind), cost, and time.

**Result checklist**
- [ ] The script runs from the command line: `python shotlist.py treatment.md > shots.json`.
- [ ] 3 valid JSON shot lists.
- [ ] Comparison table for 2 models.

## Model answer

A good solution keeps prompts in files (not in code), logs every call (model, tokens, cost), and has the checks as functions with unit tests. In comparisons, both models usually give valid JSON when the API enforces the schema. The quality difference is in shot variety, use of the bible, and timing. A typical finding: one model writes better "purpose" fields; the other follows duration limits more exactly. The decision is based on these facts.

**Comparison table (shape):**

| Model | Valid on first try | After repair | Blind quality (1–5) | Cost per list | Time |
|---|---|---|---|---|---|
| A | 3/3 | 3/3 | 4.0 | US$0.04 | 21 s |
| B | 2/3 (total duration off) | 3/3 | 3.3 | US$0.01 | 9 s |

"3 treatments are too few for a final choice; the table shows the method. Model B's errors were all caught by the duration check and fixed in one repair."

