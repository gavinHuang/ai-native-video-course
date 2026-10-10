#!/usr/bin/env python3
"""A small MCP server for a media studio (C12·M03). MCP Python SDK 2.x (pip install "mcp>=2.3").

Tools (each does one job; results are short JSON with IDs the agent can pass on):
  probe_media(path)                          -> duration, size, fps, codecs, color tags
  qc_check(path, spec)                       -> PASS/FAIL per check, with the fix (spec_check.py)
  contact_sheet(path)                        -> an image of 12 frames, for agents that can see images
  estimate_generation(shot_key, seconds)     -> US$ estimate, no side effects
  queue_generation(shot_key, prompt, seconds, confirm=False)
                                             -> dry run by default; real only with confirm=True and inside the budget
  job_status(shot_key)                       -> state, tries, cost, error
Resource: studio://budget                    -> spent, queued, caps

Safety (the point of this module):
  - every path must be inside STUDIO_ROOT (no "..", no absolute paths outside it); no delete tools
  - queue_generation needs confirm=True; above CONFIRM_ABOVE_USD it also needs a human approval file
  - budget caps per shot and in total are enforced by the queue before any money is spent
  - every call is written to an audit log (JSONL): time, tool, arguments, result summary

  STUDIO_ROOT=~/ai-video-lab python studio_mcp.py              # stdio server for an MCP client
"""
import json
import os
import sys
import time
from pathlib import Path

from mcp.server.mcpserver import MCPServer

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "tools"))
import genqueue  # noqa: E402
import mediakit  # noqa: E402

ROOT = Path(os.environ.get("STUDIO_ROOT", ".")).resolve()
AUDIT = Path(os.environ.get("STUDIO_AUDIT", str(ROOT / "audit.jsonl")))
CONFIRM_ABOVE = float(os.environ.get("CONFIRM_ABOVE_USD", "2.0"))
SHOT_CAP = float(os.environ.get("SHOT_CAP_USD", "3.0"))
SPECS = HERE.parent / "specs"

mcp = MCPServer("studio", instructions=(
    "Media studio tools. Paths are relative to the project root. Always call estimate_generation before "
    "queue_generation, and ask the user before you set confirm=True. Never try to write outside the project."))


def audit(tool, args, result):
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    summary = {k: result[k] for k in list(result)[:6]} if isinstance(result, dict) else str(result)[:200]
    with open(AUDIT, "a") as f:
        f.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "tool": tool, "args": args, "result": summary}) + "\n")


def safe(path):
    """Resolve a path inside ROOT, or refuse."""
    p = (ROOT / path).resolve()
    if p != ROOT and ROOT not in p.parents:
        raise ValueError(f"path {path!r} is outside the project root; refused")
    return p


@mcp.tool()
def probe_media(path: str) -> dict:
    """Technical facts of a media file: duration, width, height, fps, frames, codecs, color tags, audio format.
    Use it before you edit, conform, or deliver a file."""
    try:
        r = mediakit.probe(safe(path))
        r["path"] = path
    except (ValueError, mediakit.MediaError) as e:
        r = {"error": str(e)}
    audit("probe_media", {"path": path}, r)
    return r


@mcp.tool()
def qc_check(path: str, spec: str = "web_1080p") -> dict:
    """Run delivery QC on a file against a named spec (web_1080p, reels_9x16, broadcast_ebu_r128).
    Returns pass/fail and, for each failure, what to fix. Does not change the file."""
    import spec_check
    try:
        spec_file = SPECS / f"{spec}.json"
        if not spec_file.exists():
            raise ValueError(f"unknown spec {spec!r}; known: {sorted(p.stem for p in SPECS.glob('*.json'))}")
        res = spec_check.check(str(safe(path)), json.loads(spec_file.read_text()))
        fails = [{"check": r["check"], "found": r["found"], "want": r["want"], "fix": r["fix"]} for r in res if not r["ok"]]
        out = {"path": path, "spec": spec, "pass": not fails, "checks": len(res), "failures": fails}
    except (ValueError, SystemExit) as e:
        out = {"error": str(e)}
    audit("qc_check", {"path": path, "spec": spec}, out)
    return out


@mcp.tool()
def contact_sheet(path: str) -> dict:
    """Make a 4x3 contact sheet (12 frames) of a clip in work/sheets/, for visual review. Returns its path."""
    try:
        src = safe(path)
        dst = safe(f"work/sheets/{Path(path).stem}.png")
        mediakit.contact_sheet(src, dst, overwrite=True)
        out = {"sheet": str(dst.relative_to(ROOT))}
    except (ValueError, mediakit.MediaError) as e:
        out = {"error": str(e)}
    audit("contact_sheet", {"path": path}, out)
    return out


@mcp.tool()
def estimate_generation(shot_key: str, seconds: float) -> dict:
    """Estimate the cost of one generation (no side effects). shot_key: shot.prompt-version.generation, for example S07.p2.g4."""
    est = genqueue.BACKENDS[os.environ.get("STUDIO_BACKEND", "fake")]().estimate({"seconds": seconds})
    out = {"shot_key": shot_key, "estimated_cost_usd": est, "needs_human_approval": est > CONFIRM_ABOVE}
    audit("estimate_generation", {"shot_key": shot_key, "seconds": seconds}, out)
    return out


@mcp.tool()
def queue_generation(shot_key: str, prompt: str, seconds: float = 5.0, confirm: bool = False) -> dict:
    """Queue one generation. Without confirm=True this is a dry run. Costs above the approval limit also need a
    human approval file approvals/<shot_key>.ok. The same shot_key twice never pays twice (idempotent)."""
    args = {"shot_key": shot_key, "prompt": prompt[:80], "seconds": seconds, "confirm": confirm}
    if not (0.5 <= seconds <= 20):
        out = {"error": "seconds must be between 0.5 and 20"}
    elif len(prompt) > 1500:
        out = {"error": "prompt longer than 1500 characters"}
    else:
        backend = os.environ.get("STUDIO_BACKEND", "fake")
        est = genqueue.BACKENDS[backend]().estimate({"seconds": seconds})
        approval = ROOT / "approvals" / f"{shot_key}.ok"
        if not confirm:
            out = {"dry_run": True, "shot_key": shot_key, "estimated_cost_usd": est, "would_need_approval": est > CONFIRM_ABOVE}
        elif est > CONFIRM_ABOVE and not approval.exists():
            out = {"needs_confirmation": True, "estimated_cost_usd": est,
                   "message": f"cost above US${CONFIRM_ABOVE:.2f}: a person must create approvals/{shot_key}.ok"}
        else:
            try:
                j = genqueue.submit(shot_key, backend, {"prompt": prompt, "seconds": seconds}, cap=SHOT_CAP)
                out = {"queued": True, "shot_key": shot_key, "state": j["state"], "estimated_cost_usd": j["estimate"],
                       "note": j.get("note", "")}
            except SystemExit as e:
                out = {"refused": True, "reason": str(e)}
    audit("queue_generation", args, out)
    return out


@mcp.tool()
def job_status(shot_key: str) -> dict:
    """State of a queued generation: queued, running, succeeded, or dead; with tries, cost, and the last error."""
    row = genqueue.db().execute("SELECT key, state, tries, estimate, cost, error FROM jobs WHERE key=?", (shot_key,)).fetchone()
    out = dict(row) if row else {"error": f"no job {shot_key}"}
    audit("job_status", {"shot_key": shot_key}, out)
    return out


@mcp.resource("studio://budget")
def budget() -> str:
    """Spent and queued money, and the caps."""
    con = genqueue.db()
    spent = con.execute("SELECT COALESCE(SUM(cost),0) FROM jobs").fetchone()[0]
    queued = con.execute("SELECT COALESCE(SUM(estimate),0) FROM jobs WHERE state IN ('queued','running')").fetchone()[0]
    return json.dumps({"spent_usd": round(spent, 2), "queued_usd": round(queued, 2), "total_cap_usd": genqueue.TOTAL_CAP,
                       "shot_cap_usd": SHOT_CAP, "approval_above_usd": CONFIRM_ABOVE})


if __name__ == "__main__":
    mcp.run(transport="stdio")
