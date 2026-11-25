"""Shared helpers: storyboard loading and validation, hash cache, retries, run log."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
RUNS = ROOT / "runs.jsonl"
SCHEMA = ROOT / "schema" / "storyboard.schema.json"

try:  # optional: read .env if python-dotenv is installed
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass


def mock() -> bool:
    """MOCK=1 swaps every paid or remote model for a local placeholder (for tests)."""
    return os.getenv("MOCK") == "1"


def need_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise SystemExit(f"Missing {name}. Copy .env.example to .env and fill it in (or run with MOCK=1).")
    return val


# ---------------------------------------------------------------- storyboard
def load_storyboard(path: str | Path | None = None) -> dict:
    import jsonschema

    path = Path(path) if path else ROOT / "storyboard.json"
    sb = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(sb, schema)
    ids = [s["id"] for s in sb["shots"]]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate shot ids")
    known = {c["id"] for c in sb["characters"]}
    for s in sb["shots"]:
        unknown = set(s["characters"]) - known
        if unknown:
            raise ValueError(f"{s['id']}: unknown characters {unknown}")
    return sb


def expand(sb: dict, text: str) -> str:
    """Replace {character_id} tokens by the fixed character description."""
    desc = {c["id"]: c["description"] for c in sb["characters"]}
    return re.sub(r"\{(\w+)\}", lambda m: desc.get(m.group(1), m.group(0)), text)


def image_prompt(sb: dict, shot: dict) -> str:
    return f"{sb['style_block']}. {expand(sb, shot['image_prompt'])}"


# --------------------------------------------------------------------- hash
def sha(*parts) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(json.dumps(p, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    return h.hexdigest()[:16]


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


class Cache:
    """outputs/<stage>/<name>.<ext> plus <name>.meta.json holding the input hash.
    A step is skipped when the file exists and its stored hash equals the new one."""

    def __init__(self, stage: str, name: str, ext: str):
        self.path = OUT / stage / f"{name}.{ext}"
        self.meta = OUT / stage / f"{name}.meta.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def hit(self, key: str) -> bool:
        if not (self.path.exists() and self.meta.exists()):
            return False
        return json.loads(self.meta.read_text()).get("hash") == key

    def save_meta(self, key: str, **extra):
        self.meta.write_text(json.dumps({"hash": key, **extra}, indent=1))


# ---------------------------------------------------------------------- log
def log_run(stage: str, model: str, shot: str | None = None, *, params=None, seed=None,
            latency_s: float = 0.0, cost_usd: float = 0.0, cache_hit: bool = False,
            status: str = "ok", note: str = "") -> None:
    row = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "stage": stage, "shot": shot, "model": model, "params": params or {}, "seed": seed,
        "latency_s": round(latency_s, 3), "cost_usd": cost_usd, "cache_hit": cache_hit,
        "status": status, "note": note,
    }
    with open(RUNS, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def retry(fn, *, tries: int = 4, base: float = 2.0, what: str = "call"):
    """Call fn(); on any exception wait base*2**n seconds and try again."""
    for n in range(tries):
        try:
            return fn()
        except SystemExit:
            raise
        except Exception as e:  # noqa: BLE001
            if n == tries - 1:
                raise
            wait = base * 2 ** n
            print(f"  {what} failed ({e}); retry {n + 1}/{tries - 1} in {wait:.0f}s")
            time.sleep(wait)


# ------------------------------------------------------------------- ffmpeg
def ffmpeg_exe() -> str:
    if os.getenv("FFMPEG"):
        return os.environ["FFMPEG"]
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def run_ffmpeg(args: list[str], *, stage: str, shot: str | None = None, cwd: Path | None = None,
               note: str = "") -> None:
    t0 = time.time()
    cmd = [ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error", *args]
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    dt = time.time() - t0
    if r.returncode:
        log_run(stage, "ffmpeg", shot, latency_s=dt, status="error", note=r.stderr[-300:])
        raise RuntimeError(f"ffmpeg failed: {r.stderr[-800:]}")
    log_run(stage, "ffmpeg", shot, latency_s=dt, note=note)


def wav_seconds(path: Path) -> float:
    import wave

    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


def shot_duration(sb: dict, shot: dict) -> float:
    """Shot length = max(planned minimum, narration length + 1 s), rounded up to 0.5 s."""
    import math

    narr = OUT / "narration" / f"{shot['id']}.wav"
    n = wav_seconds(narr) if narr.exists() else 0.0
    return max(shot["min_duration_s"], math.ceil((n + 1.0) * 2) / 2)
