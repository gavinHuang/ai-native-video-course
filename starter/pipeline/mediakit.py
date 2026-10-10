"""Media functions as tested pipeline stages (C12·M02). Needs ffmpeg and ffprobe on PATH.

Rules that every function follows:
  - one function, one job; never overwrite an input; refuse to overwrite an output unless overwrite=True
  - return a dict (paths, durations, warnings), never print
  - raise MediaError with the ffmpeg message on failure
Use them from scripts, from the queue workers, and as MCP tools (C12·M03).
"""
import json
import re
import subprocess
from pathlib import Path


class MediaError(Exception):
    pass


def _run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise MediaError(f"{' '.join(cmd[:6])} ...: {r.stderr.strip()[-600:]}")
    return r


def _out(dst, overwrite):
    dst = Path(dst)
    if dst.exists() and not overwrite:
        raise MediaError(f"{dst} exists (use overwrite=True)")
    dst.parent.mkdir(parents=True, exist_ok=True)
    return dst


def probe(path):
    """Duration, size, frame rate, frame count, codecs, color tags, audio format."""
    r = _run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)])
    d = json.loads(r.stdout)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    out = {"path": str(path), "duration": float(d["format"].get("duration", 0))}
    if v:
        num, den = map(int, v.get("avg_frame_rate", "0/1").split("/"))
        out |= {"width": v["width"], "height": v["height"], "fps": round(num / den, 3) if den else 0,
                "frames": int(v["nb_frames"]) if v.get("nb_frames", "").isdigit() else None,
                "vcodec": v["codec_name"], "pix_fmt": v.get("pix_fmt"),
                "color": {k: v.get(f) for k, f in (("primaries", "color_primaries"), ("transfer", "color_transfer"),
                                                    ("matrix", "color_space"), ("range", "color_range"))}}
    if a:
        out |= {"acodec": a["codec_name"], "sample_rate": int(a["sample_rate"]), "channels": a["channels"]}
    return out


def intermediate(src, dst, overwrite=False):
    """10-bit ProRes 422 HQ + 24-bit PCM: the grading intermediate (C09·M01)."""
    dst = _out(dst, overwrite)
    _run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le",
          "-c:a", "pcm_s24le", str(dst)])
    return probe(dst)


def make_proxy(src, dst, height=540, overwrite=False):
    """Small H.264 proxy with the same frame rate and length, for editing (C08·M01)."""
    dst = _out(dst, overwrite)
    _run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", f"scale=-2:{height}", "-c:v", "libx264", "-preset", "veryfast",
          "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", str(dst)])
    return probe(dst)


def trim(src, t_in, t_out, dst, overwrite=False):
    """Frame-accurate trim (re-encodes to an intermediate). t_in/t_out in seconds."""
    if t_out <= t_in:
        raise MediaError("t_out must be after t_in")
    dst = _out(dst, overwrite)
    _run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ss", f"{t_in:.4f}", "-to", f"{t_out:.4f}",
          "-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le", "-c:a", "pcm_s24le", str(dst)])
    return probe(dst)


def concat(clips, dst, fps=24, size=None, overwrite=False):
    """Join clips with the concat filter: works when sizes, rates, or audio differ (each clip is conformed)."""
    dst = _out(dst, overwrite)
    infos = [probe(c) for c in clips]
    w, h = size or (infos[0]["width"], infos[0]["height"])
    args, parts = [], []
    for i, (c, inf) in enumerate(zip(clips, infos)):
        args += ["-i", str(c)]
        parts.append(f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
                     f"setsar=1,fps={fps},format=yuv422p10le[v{i}]")
        if "acodec" in inf:
            parts.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}]")
        else:
            parts.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={inf['duration']}[a{i}]")
    parts.append("".join(f"[v{i}][a{i}]" for i in range(len(clips))) + f"concat=n={len(clips)}:v=1:a=1[v][a]")
    _run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", ";".join(parts), "-map", "[v]", "-map", "[a]",
          "-c:v", "prores_ks", "-profile:v", "3", "-c:a", "pcm_s24le", str(dst)])
    return probe(dst) | {"inputs": len(clips)}


def extract_audio(src, dst, overwrite=False):
    dst = _out(dst, overwrite)
    _run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vn", "-ar", "48000", "-c:a", "pcm_s24le", str(dst)])
    return probe(dst)


def loudness(src):
    """Integrated loudness (LUFS), loudness range (LU), true peak (dBTP)."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    t = r.stderr
    try:
        return {"I": float(re.findall(r"I:\s+(-?[\d.]+) LUFS", t)[-1]), "LRA": float(re.findall(r"LRA:\s+(-?[\d.]+) LU", t)[-1]),
                "TP": float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", t)[-1])}
    except IndexError:
        raise MediaError(f"no audio to measure in {src}") from None


def contact_sheet(src, dst, cols=4, rows=3, width=320, overwrite=False):
    """One image with cols x rows frames across the clip: for review sheets and agents with vision."""
    dst = _out(dst, overwrite)
    d = probe(src)
    n = cols * rows
    every = max(1, int((d.get("frames") or d["duration"] * d.get("fps", 24)) / n))
    _run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", f"select='not(mod(n\\,{every}))',scale={width}:-2,tile={cols}x{rows}",
          "-frames:v", "1", "-fps_mode", "passthrough", str(dst)])
    return {"path": str(dst), "frames_every": every}
