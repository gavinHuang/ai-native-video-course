"""Start media_mcp.py over stdio with a real MCP client. Run: pytest -q test_media_mcp.py (needs ffmpeg)."""
import asyncio, json, os, subprocess, sys
from pathlib import Path
import pytest
from mcp import Client, StdioServerParameters

HERE = Path(__file__).resolve().parent


def session(root, steps):
    params = StdioServerParameters(command=sys.executable, args=[str(HERE / "media_mcp.py")],
                                   env=dict(os.environ, MEDIA_ROOT=str(root)))

    async def run():
        out = []
        async with Client(params) as c:
            out.append(sorted(t.name for t in (await c.list_tools()).tools))
            for tool, args in steps:
                if tool == "@resource":
                    out.append(json.loads((await c.read_resource(args)).contents[0].text))
                else:
                    r = await c.call_tool(tool, args)
                    out.append((r.is_error, r.content[0].text))
        return out
    return asyncio.run(run())


@pytest.fixture
def root(tmp_path):
    (tmp_path / "day2").mkdir()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=640x360:r=24:d=2",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(tmp_path / "day2" / "C014A.mp4")], check=True)
    return tmp_path


def test_tools_and_calls(root):
    tools, listed, probed, missing, outside, res = session(root, [
        ("list_media", {"pattern": "day2/*.mp4"}),
        ("probe", {"path": "day2/C014A.mp4"}),
        ("probe", {"path": "day2/C014.mp4"}),
        ("probe", {"path": "../etc/passwd"}),
        ("@resource", "media://summary")])
    assert tools == ["list_media", "probe"]
    assert json.loads(listed[1])["count"] == 1
    p = json.loads(probed[1]); assert p["width"] == 640 and abs(p["duration_s"] - 2) < 0.1
    m = json.loads(missing[1]); assert "C014A.mp4" in m["similar"][0]
    assert outside[0] is False and "outside the media root" in json.loads(outside[1])["error"]
    assert res[".mp4"]["files"] == 1
