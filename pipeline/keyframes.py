"""Stage: keyframes. One still per shot from Cloudflare Workers AI (FLUX), or a placeholder with MOCK=1."""
from __future__ import annotations

import base64
import os
import time

import requests

from .common import Cache, image_prompt, load_storyboard, log_run, mock, need_env, retry, sha

DEFAULT_MODEL = "@cf/black-forest-labs/flux-1-schnell"  # override with CF_IMAGE_MODEL
STEPS = 8  # schnell maximum on Workers AI


def _cloudflare(prompt: str, seed: int, model: str) -> bytes:
    acct, token = need_env("CF_ACCOUNT_ID"), need_env("CF_API_TOKEN")
    url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/{model}"
    body = {"prompt": prompt, "steps": STEPS}
    if os.getenv("CF_SEND_SEED") == "1":  # flux-1-schnell on Workers AI rejects "seed" (HTTP 400, code 5006)
        body["seed"] = seed
    r = requests.post(url, json=body,
                      headers={"Authorization": f"Bearer {token}"}, timeout=120)
    r.raise_for_status()
    return base64.b64decode(r.json()["result"]["image"])


def _mock_image(shot_id: str, prompt: str) -> bytes:
    import io

    from PIL import Image, ImageDraw

    hue = (int(shot_id[1:]) * 37) % 255
    img = Image.new("RGB", (1024, 1024), (60 + hue // 3, 40 + hue // 4, 90))
    d = ImageDraw.Draw(img)
    d.ellipse((312, 312, 712, 712), fill=(230, 180, 90))
    d.text((40, 40), f"{shot_id} (mock)", fill=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, "JPEG")
    return buf.getvalue()


def run(only: list[str] | None = None, force: bool = False):
    sb = load_storyboard()
    model = os.getenv("CF_IMAGE_MODEL", DEFAULT_MODEL)
    for shot in sb["shots"]:
        if only and shot["id"] not in only:
            continue
        prompt = image_prompt(sb, shot)
        key = sha("mock" if mock() else model, prompt, shot["seed"], STEPS)
        c = Cache("keyframes", shot["id"], "jpg")
        if c.hit(key) and not force:
            log_run("keyframes", model, shot["id"], cache_hit=True)
            print(f"[keyframes] {shot['id']} cached")
            continue
        t0 = time.time()
        data = _mock_image(shot["id"], prompt) if mock() else retry(
            lambda: _cloudflare(prompt, shot["seed"], model), what="Cloudflare")
        c.path.write_bytes(data)
        c.save_meta(key, prompt=prompt)
        log_run("keyframes", "mock" if mock() else model, shot["id"],
                params={"steps": STEPS, "prompt_chars": len(prompt)}, seed=shot["seed"],
                latency_s=time.time() - t0)
        print(f"[keyframes] {shot['id']} done")
