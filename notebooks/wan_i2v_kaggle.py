# Kaggle notebook cell script: Wan 2.2 TI2V-5B image-to-video for each keyframe.
# STATUS: TEMPLATE, NOT YET RUN. Check every call against the model card
# (https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B-Diffusers) before relying on it, and log what you
# actually found in FAILURES.md.
#
# Setup in Kaggle: Accelerator = GPU T4 x2, Internet on. Upload as a Dataset:
#   storyboard.json and outputs/keyframes/*.jpg  (name it "heritage-inputs")
# Then run this file in a notebook cell. Download /kaggle/working/wan/*.mp4 and put them in
# outputs/wan/ in the repo. Re-run `python run.py` to rebuild the film with the real clips.
import json
import time
from pathlib import Path

import torch
from diffusers import WanImageToVideoPipeline
from diffusers.utils import export_to_video
from PIL import Image

IN = Path("/kaggle/input/heritage-inputs")
OUT = Path("/kaggle/working/wan")
OUT.mkdir(exist_ok=True, parents=True)
MODEL = "Wan-AI/Wan2.2-TI2V-5B-Diffusers"
WIDTH, HEIGHT = 832, 480          # draft at 480p to save quota (EXPERIMENTS #6)
FRAMES = 49                        # about 2 s at 24 fps; shorter clips are more consistent
STEPS = 30
LOG = OUT / "gpu_log.jsonl"

sb = json.loads((IN / "storyboard.json").read_text(encoding="utf-8"))
pipe = WanImageToVideoPipeline.from_pretrained(MODEL, torch_dtype=torch.float16)  # T4 has no bf16
pipe.enable_model_cpu_offload()

for shot in sb["shots"]:
    dest = OUT / f"{shot['id']}.mp4"
    if dest.exists():                      # cache: skip finished shots after a session timeout
        continue
    image = Image.open(IN / "keyframes" / f"{shot['id']}.jpg").convert("RGB").resize((WIDTH, HEIGHT))
    gen = torch.Generator("cpu").manual_seed(shot["seed"])
    t0 = time.time()
    frames = pipe(image=image, prompt=shot["motion_prompt"], height=HEIGHT, width=WIDTH,
                  num_frames=FRAMES, num_inference_steps=STEPS, guidance_scale=5.0, generator=gen).frames[0]
    export_to_video(frames, str(dest), fps=24)
    dt = time.time() - t0
    with open(LOG, "a") as f:             # copy these lines into runs.jsonl / COSTS.md
        f.write(json.dumps({"stage": "shots", "shot": shot["id"], "model": "wan2.2-ti2v-5b",
                            "seed": shot["seed"], "latency_s": round(dt, 1),
                            "params": {"w": WIDTH, "h": HEIGHT, "frames": FRAMES, "steps": STEPS}}) + "\n")
    print(shot["id"], f"{dt / 60:.1f} min")
