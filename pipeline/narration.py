"""Stage: narration. One WAV per shot via Gemini TTS (or a placeholder tone with MOCK=1)."""
from __future__ import annotations

import base64
import math
import os
import struct
import time
import wave

import requests

from .common import Cache, load_storyboard, log_run, mock, need_env, retry, sha

RATE = 24000  # Gemini TTS returns 24 kHz 16-bit mono PCM
DEFAULT_MODEL = "gemini-2.5-flash-preview-tts"  # override with GEMINI_TTS_MODEL (brief names Gemini 3.8 Flash TTS)


def _write_wav(path, pcm: bytes):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm)


def _gemini_tts(text: str, voice: dict, model: str) -> bytes:
    key = need_env("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {
        "contents": [{"parts": [{"text": f"{voice['style']}:\n{text}"}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice["voice_name"]}}},
        },
    }
    r = requests.post(url, json=body, headers={"x-goog-api-key": key}, timeout=120)
    r.raise_for_status()
    part = r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]
    return base64.b64decode(part["data"])


def _mock_tone(text: str) -> bytes:
    """Placeholder: a quiet tone whose length follows the word count (~2.2 words/s)."""
    secs = max(2.0, len(text.split()) / 2.2)
    n = int(RATE * secs)
    return b"".join(struct.pack("<h", int(2500 * math.sin(2 * math.pi * 180 * i / RATE))) for i in range(n))


def run(only: list[str] | None = None, force: bool = False):
    sb = load_storyboard()
    model = os.getenv("GEMINI_TTS_MODEL", DEFAULT_MODEL)
    for shot in sb["shots"]:
        if only and shot["id"] not in only:
            continue
        text = shot["narration"]["text_native"]
        key = sha(model if not mock() else "mock", text, sb["voice"])
        c = Cache("narration", shot["id"], "wav")
        if c.hit(key) and not force:
            log_run("narration", model, shot["id"], cache_hit=True)
            print(f"[narration] {shot['id']} cached")
            continue
        t0 = time.time()
        pcm = _mock_tone(text) if mock() else retry(lambda: _gemini_tts(text, sb["voice"], model), what="TTS")
        _write_wav(c.path, pcm)
        c.save_meta(key, text=text)
        log_run("narration", "mock" if mock() else model, shot["id"],
                params={"voice": sb["voice"]["voice_name"], "chars": len(text)},
                latency_s=time.time() - t0)
        print(f"[narration] {shot['id']} done")
