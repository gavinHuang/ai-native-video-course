"""Protocol-level tests for studio_mcp.py: a real MCP client starts the server over stdio.
Run: pytest -q test_studio_mcp.py   (needs: pip install "mcp>=2.3" pytest; ffmpeg)"""
import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from mcp import Client, StdioServerParameters

HERE = Path(__file__).resolve().parent


def call(root, steps, extra_env=None):
    """Start the server, run (tool, args) steps, return the parsed results."""
    env = dict(os.environ, STUDIO_ROOT=str(root), GENQUEUE_DB=str(root / "q.sqlite"), STUDIO_BACKEND="fake",
               CONFIRM_ABOVE_USD="1.0", SHOT_CAP_USD="3.0", FAKE_PLAN="ok") | (extra_env or {})
    params = StdioServerParameters(command=sys.executable, args=[str(HERE / "studio_mcp.py")], env=env)

    async def run():
        out = []
        async with Client(params) as c:
            out.append(sorted(t.name for t in (await c.list_tools()).tools))
            for tool, args in steps:
                if tool == "@resource":
                    r = await c.read_resource(args)
                    out.append(json.loads(r.contents[0].text))
                else:
                    r = await c.call_tool(tool, args)
                    out.append(r.structured_content if r.structured_content is not None else json.loads(r.content[0].text))
        return out
    return asyncio.run(run())


@pytest.fixture
def root(tmp_path):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=640x360:r=24:d=2", "-f", "lavfi", "-i", "sine=d=2",
                    "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(tmp_path / "clip.mp4")], check=True)
    return tmp_path


def unwrap(r):
    return r.get("result", r) if isinstance(r, dict) else r


def test_tools_listed_and_probe(root):
    tools, probe = call(root, [("probe_media", {"path": "clip.mp4"})])
    assert tools == ["contact_sheet", "estimate_generation", "job_status", "probe_media", "qc_check", "queue_generation"]
    assert unwrap(probe)["width"] == 640


def test_sandbox_refuses_outside_paths(root):
    _, a, b = call(root, [("probe_media", {"path": "../../etc/passwd"}), ("probe_media", {"path": "/etc/passwd"})])
    assert "outside the project root" in unwrap(a)["error"]
    assert "outside the project root" in unwrap(b)["error"]


def test_qc_reports_fixes(root):
    _, r = call(root, [("qc_check", {"path": "clip.mp4", "spec": "web_1080p"})])
    r = unwrap(r)
    assert r["pass"] is False and any(f["check"] == "width" for f in r["failures"])


def test_dry_run_confirmation_and_idempotency(root):
    steps = [("queue_generation", {"shot_key": "S07.p1.g1", "prompt": "x", "seconds": 6}),               # dry run
             ("queue_generation", {"shot_key": "S07.p1.g1", "prompt": "x", "seconds": 6, "confirm": True}),  # 0.60 > 1.0? no
             ("queue_generation", {"shot_key": "S07.p1.g1", "prompt": "x", "seconds": 6, "confirm": True}),  # idempotent
             ("queue_generation", {"shot_key": "S08.p1.g1", "prompt": "x", "seconds": 12, "confirm": True}), # 1.20 > 1.0
             ("@resource", "studio://budget")]
    _, dry, real, again, needs, budget = call(root, steps)
    assert unwrap(dry)["dry_run"] is True
    assert unwrap(real)["queued"] is True
    assert "existing job" in unwrap(again)["note"]
    assert unwrap(needs)["needs_confirmation"] is True
    assert budget["queued_usd"] == 0.6


def test_shot_cap_refusal(root):
    steps = [("queue_generation", {"shot_key": f"S09.p1.g{i}", "prompt": "x", "seconds": 9, "confirm": True}) for i in range(1, 5)]
    approvals = root / "approvals"
    approvals.mkdir()
    for i in range(1, 5):
        (approvals / f"S09.p1.g{i}.ok").write_text("ok")
    res = call(root, steps, {"CONFIRM_ABOVE_USD": "0.5"})[1:]
    assert [("queued" in unwrap(r)) for r in res] == [True, True, True, False]   # 3 x 0.90 = 2.70; the 4th > 3.00
    assert "cap" in unwrap(res[3])["reason"]


def test_audit_log(root):
    call(root, [("probe_media", {"path": "clip.mp4"}), ("probe_media", {"path": "../x"})])
    lines = [json.loads(x) for x in (root / "audit.jsonl").read_text().splitlines()]
    assert [x["tool"] for x in lines] == ["probe_media", "probe_media"]
    assert "error" in lines[1]["result"]
