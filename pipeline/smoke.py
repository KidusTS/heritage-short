"""Smoke test: call each remote provider once and log its latency to runs.jsonl.
Run:  python -m pipeline.smoke"""
from __future__ import annotations

import os
import time

from .common import log_run, need_env


def main():
    from . import keyframes, narration

    ok = True
    for name, fn in (
        ("gemini-tts", lambda: narration._gemini_tts("ሰላም", {"voice_name": "Kore", "style": "Say calmly"},
                                                    os.getenv("GEMINI_TTS_MODEL", narration.DEFAULT_MODEL))),
        ("cloudflare-flux", lambda: keyframes._cloudflare("a small clay coffee pot, painted style", 1,
                                                          os.getenv("CF_IMAGE_MODEL", keyframes.DEFAULT_MODEL))),
    ):
        t0 = time.time()
        try:
            data = fn()
            dt = time.time() - t0
            log_run("smoke", name, latency_s=dt, note=f"{len(data)} bytes")
            print(f"OK   {name}: {dt:.1f}s, {len(data)} bytes")
        except SystemExit as e:
            print(f"SKIP {name}: {e}")
            ok = False
        except Exception as e:  # noqa: BLE001
            log_run("smoke", name, latency_s=time.time() - t0, status="error", note=str(e)[:200])
            print(f"FAIL {name}: {e}")
            ok = False
    print("Kaggle (Wan 2.2, ACE-Step) cannot be called from here: run the notebooks in notebooks/.")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
