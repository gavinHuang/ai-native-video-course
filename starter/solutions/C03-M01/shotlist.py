#!/usr/bin/env python3
"""Treatment -> validated JSON shot list, with a validate-and-repair loop (C03·M01).

    python shotlist.py treatment.md --target-s 60 > shots.json            # uses ANTHROPIC_API_KEY
    python shotlist.py treatment.md --target-s 60 --fake fake_reply.json  # offline test

Prompts live in files next to this script (system.md, examples.json); every call is logged to calls.jsonl.
"""
import argparse, json, os, sys, time
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

HERE = Path(__file__).resolve().parent
MAX_SHOT_S = 10.0  # the longest shot your video route can make


class Shot(BaseModel):
    id: str
    duration_s: float = Field(ge=1, le=15)
    size: Literal["EWS", "WS", "FS", "MS", "MCU", "CU", "ECU"]
    angle: str
    lens_mm: int = Field(ge=8, le=600)
    move: str
    subject: str
    action: str
    light: str
    audio: str
    purpose: str = Field(min_length=3)


class ShotList(BaseModel):
    title: str
    ratio: Literal["16:9", "9:16", "1:1", "4:5", "2.39:1"]
    shots: list[Shot] = Field(min_length=1)


def checks(sl: ShotList, target_s: float, tol: float = 2.0) -> list[str]:
    """Checks that a schema cannot express. Returns a list of problems (empty = pass)."""
    p = []
    total = sum(s.duration_s for s in sl.shots)
    if abs(total - target_s) > tol:
        p.append(f"total duration {total:.1f} s, target {target_s} ± {tol} s")
    for s in sl.shots:
        if s.duration_s > MAX_SHOT_S:
            p.append(f"{s.id}: {s.duration_s} s is longer than the route limit {MAX_SHOT_S} s - split it")
        for f in ("subject", "action", "light"):
            if not getattr(s, f).strip():
                p.append(f"{s.id}: empty {f}")
    ids = [s.id for s in sl.shots]
    if len(ids) != len(set(ids)):
        p.append("duplicate shot ids")
    return p


def call_llm(system, messages, model):
    import anthropic  # pip install anthropic
    client = anthropic.Anthropic()
    t = time.time()
    r = client.messages.create(model=model, max_tokens=8000, system=system, messages=messages)
    text = "".join(b.text for b in r.content if b.type == "text")
    log = {"t": time.strftime("%FT%T"), "model": model, "in": r.usage.input_tokens, "out": r.usage.output_tokens,
           "s": round(time.time() - t, 1)}
    with open(HERE / "calls.jsonl", "a") as f:
        f.write(json.dumps(log) + "\n")
    return text


def extract_json(text):
    a, b = text.find("{"), text.rfind("}")
    return text[a:b + 1] if a >= 0 and b > a else text


def run(treatment, target_s, llm, max_repairs=2):
    system = (HERE / "system.md").read_text()
    examples = (HERE / "examples.json").read_text()
    task = (f"<examples>\n{examples}\n</examples>\n<treatment>\n{treatment}\n</treatment>\n"
            f"Target duration: {target_s} s. Answer with JSON only, matching this schema:\n"
            f"{json.dumps(ShotList.model_json_schema())}")
    messages = [{"role": "user", "content": task}]
    for attempt in range(max_repairs + 1):
        text = llm(system, messages)
        try:
            sl = ShotList.model_validate_json(extract_json(text))
            problems = checks(sl, target_s)
        except ValidationError as e:
            problems = [str(e)]
            sl = None
        if not problems:
            return sl, attempt
        messages += [{"role": "assistant", "content": text},
                     {"role": "user", "content": "Fix these problems and answer with the full corrected JSON only:\n- "
                      + "\n- ".join(problems)}]
    raise SystemExit(f"no valid shot list after {max_repairs} repairs: {problems}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("treatment")
    ap.add_argument("--target-s", type=float, required=True)
    ap.add_argument("--model", default=os.environ.get("SHOTLIST_MODEL", "claude-sonnet-5-5"))
    ap.add_argument("--fake", nargs="+", help="JSON files returned in order instead of calling a model (tests)")
    a = ap.parse_args(argv)
    if a.fake:
        replies = [Path(f).read_text() for f in a.fake]
        llm = lambda system, messages: replies[min(len([m for m in messages if m["role"] == "assistant"]), len(replies) - 1)]
    else:
        llm = lambda system, messages: call_llm(system, messages, a.model)
    sl, repairs = run(Path(a.treatment).read_text(), a.target_s, llm)
    print(sl.model_dump_json(indent=2))
    print(f"valid after {repairs} repair(s)", file=sys.stderr)


if __name__ == "__main__":
    main()
