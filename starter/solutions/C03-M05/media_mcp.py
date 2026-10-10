#!/usr/bin/env python3
"""A minimal, read-only MCP server for a media folder (C03·M05). MCP Python SDK 2.x: pip install "mcp>=2.3".

    MEDIA_ROOT=~/work python media_mcp.py          # stdio server; add it to your MCP host's config

Tools: list_media(pattern), probe(path). Resource: media://summary. No write tools: start read-only.
The full studio server with write tools, budgets, and confirmations is pipeline/studio_mcp.py (C12·M03).
"""
import json
import os
import subprocess
from pathlib import Path

from mcp.server.mcpserver import MCPServer

ROOT = Path(os.environ.get("MEDIA_ROOT", ".")).resolve()
EXT = {".mp4", ".mov", ".mxf", ".wav", ".mp3", ".png", ".jpg"}

mcp = MCPServer("media-files", instructions="Read-only access to the media folder. Paths are relative to the root.")


def safe(path: str) -> Path:
    p = (ROOT / path).resolve()
    if p != ROOT and ROOT not in p.parents:
        raise ValueError(f"path {path!r} is outside the media root; refused")
    return p


@mcp.tool()
def list_media(pattern: str = "**/*") -> dict:
    """List media files under the root that match a glob pattern (for example 'day2/*.mp4').
    Returns up to 200 relative paths with sizes in MB. Use probe() for details of one file."""
    files = [p for p in sorted(ROOT.glob(pattern)) if p.suffix.lower() in EXT and p.is_file()]
    return {"count": len(files), "files": [{"path": str(p.relative_to(ROOT)), "mb": round(p.stat().st_size / 1e6, 1)}
                                           for p in files[:200]]}


@mcp.tool()
def probe(path: str) -> dict:
    """Return duration (s), resolution, frame rate, and codecs of one media file (relative path)."""
    try:
        p = safe(path)
    except ValueError as e:  # return errors as results: an exception reaches the model only as "Error executing tool"
        return {"error": str(e)}
    if not p.exists():
        near = [str(x.relative_to(ROOT)) for x in p.parent.glob(p.stem[:4] + "*")][:5] if p.parent.exists() else []
        return {"error": f"file not found: {path}", "similar": near}
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration:stream=codec_type,codec_name,width,height,avg_frame_rate",
                        "-of", "json", str(p)], capture_output=True, text=True)
    d = json.loads(r.stdout or "{}")
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), {})
    return {"path": path, "duration_s": round(float(d.get("format", {}).get("duration", 0)), 3),
            "width": v.get("width"), "height": v.get("height"), "fps": v.get("avg_frame_rate"),
            "video_codec": v.get("codec_name"), "audio_codec": a.get("codec_name")}


@mcp.resource("media://summary")
def summary() -> str:
    """Number of files and total size per extension."""
    out = {}
    for p in ROOT.rglob("*"):
        if p.is_file() and p.suffix.lower() in EXT:
            e = out.setdefault(p.suffix.lower(), {"files": 0, "mb": 0.0})
            e["files"] += 1
            e["mb"] = round(e["mb"] + p.stat().st_size / 1e6, 1)
    return json.dumps(out)


if __name__ == "__main__":
    mcp.run()
