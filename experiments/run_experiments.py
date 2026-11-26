"""Reproducible experiments for EXPERIMENTS.md. Uses 5 Cloudflare images; no TTS calls (quota).
Run:  python experiments/run_experiments.py      Writes outputs/experiments/ and results.json,
and logs every model call to runs.jsonl with stage="experiment"."""
import json
import os
import re
import subprocess
import sys
import time
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from PIL import Image, ImageChops, ImageStat  # noqa: E402

from pipeline import keyframes  # noqa: E402
from pipeline.common import OUT, expand, ffmpeg_exe, image_prompt, load_storyboard, log_run, retry  # noqa: E402

sb = load_storyboard()
model = os.getenv("CF_IMAGE_MODEL", keyframes.DEFAULT_MODEL)
dest = OUT / "experiments"
dest.mkdir(parents=True, exist_ok=True)
shots = {s["id"]: s for s in sb["shots"]}
res = {}


def gen(label, prompt, steps=8):
    t0 = time.time()
    data = retry(lambda: keyframes._cloudflare(prompt, 0, model, steps), what=label)
    dt = time.time() - t0
    (dest / f"{label}.jpg").write_bytes(data)
    log_run("experiment", model, label, params={"steps": steps, "prompt_chars": len(prompt)}, latency_s=dt)
    return dt


def diff(a, b):
    A, B = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    return round(sum(ImageStat.Stat(ImageChops.difference(A, B)).mean) / 3, 1), A.size


# E1 reproducibility: same prompt as the S01 keyframe, no seed
p1 = image_prompt(sb, shots["S01"])
gen("e1_s01_repeat", p1)
d, size = diff(OUT / "keyframes" / "S01.jpg", dest / "e1_s01_repeat.jpg")
res["E1_same_prompt_mean_pixel_diff_0to255"] = d
res["image_size"] = size

# E2 steps 4 vs 8 on S02 (the 8-step reference is the shipped keyframe)
p2 = image_prompt(sb, shots["S02"])
res["E2_latency_s_steps4"] = round(gen("e2_s02_steps4", p2, steps=4), 1)
ship = [r for r in map(json.loads, (OUT.parent / "runs.jsonl").read_text(encoding="utf8").splitlines())
        if r["stage"] == "keyframes" and r["shot"] == "S02" and not r["cache_hit"]]
res["E2_latency_s_steps8_shipped_S02"] = round(ship[-1]["latency_s"], 1) if ship else None

# E3 character description present (shipped S02) vs replaced by a generic noun
p3 = f"{sb['style_block']}. " + re.sub(r"\{grandmother\}", "an old woman", shots["S02"]["image_prompt"])
gen("e3_s02_no_character_desc", p3)

# E4 style block present (shipped S05) vs absent
p4 = expand(sb, shots["S05"]["image_prompt"])
gen("e4_s05_no_style_block", p4)

# E5 loudness of the final film (no API)
out = subprocess.run([ffmpeg_exe(), "-hide_banner", "-nostats", "-i", str(OUT / "final" / "film_vertical.mp4"),
                      "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
tail = out[out.rfind("Summary:"):]
res["E5_loudness"] = {k: float(re.search(rf"{k}:\s+(-?[\d.]+)", tail).group(1)) for k in ("I", "Peak")}

# E6 narration pace (no API): words per second of the Amharic narration
rows = []
for s in sb["shots"]:
    with wave.open(str(OUT / "narration" / f"{s['id']}.wav"), "rb") as w:
        secs = w.getnframes() / w.getframerate()
    words = len(s["narration"]["text_native"].replace("።", " ").split())
    rows.append((s["id"], words, round(secs, 2)))
res["E6_narration"] = rows
res["E6_words_per_s"] = round(sum(r[1] for r in rows) / sum(r[2] for r in rows), 2)
res["E6_total_narration_s"] = round(sum(r[2] for r in rows), 1)
(dest / "results.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
print(json.dumps(res, indent=1, ensure_ascii=False))
