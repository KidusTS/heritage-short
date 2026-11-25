"""Stage: moving shots.

Preferred: a Wan 2.2 clip per shot, generated on Kaggle (see notebooks/) and dropped in
outputs/wan/<shot>.mp4. Fallback: a Ken Burns pan/zoom over the keyframe, built with FFmpeg.
Each shot is cached on (keyframe hash, source, camera move, duration)."""
from __future__ import annotations

import time

from .common import OUT, Cache, load_storyboard, log_run, run_ffmpeg, sha, sha_file, shot_duration

FPS = 24
SIZE = 1024  # keyframes are square; assembly crops to 9:16 and 16:9


def _kenburns_filter(camera: str, frames: int) -> str:
    inc = 0.25 / frames
    pre = f"scale={SIZE * 2}:{SIZE * 2}:flags=lanczos"
    common = f"d={frames}:s={SIZE}x{SIZE}:fps={FPS}"
    if camera == "push_in":
        z = f"z='min(1+{inc:.6f}*on,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    elif camera == "pull_out":
        z = f"z='max(1.25-{inc:.6f}*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    elif camera == "pan_right":
        z = f"z=1.15:x='(iw-iw/zoom)*on/{frames}':y='ih/2-(ih/zoom/2)'"
    elif camera == "pan_left":
        z = f"z=1.15:x='(iw-iw/zoom)*(1-on/{frames})':y='ih/2-(ih/zoom/2)'"
    else:  # static: a very slight push so it never looks frozen
        z = f"z='min(1+{inc / 4:.6f}*on,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    return f"{pre},zoompan={z}:{common},format=yuv420p"


def run(only: list[str] | None = None, force: bool = False):
    sb = load_storyboard()
    for shot in sb["shots"]:
        sid = shot["id"]
        if only and sid not in only:
            continue
        key_img = OUT / "keyframes" / f"{sid}.jpg"
        if not key_img.exists():
            raise SystemExit(f"{sid}: keyframe missing. Run the keyframes stage first.")
        dur = shot_duration(sb, shot)
        wan = OUT / "wan" / f"{sid}.mp4"
        source = "wan" if wan.exists() else "kenburns"
        key = sha(source, sha_file(wan) if wan.exists() else sha_file(key_img), shot["camera"], dur, FPS)
        c = Cache("shots", sid, "mp4")
        if c.hit(key) and not force:
            log_run("shots", source, sid, cache_hit=True)
            print(f"[shots] {sid} cached ({source})")
            continue
        t0 = time.time()
        frames = int(dur * FPS)
        if source == "wan":
            # hold the last frame if the clip is shorter than the shot, trim if longer
            vf = f"fps={FPS},scale=-2:{SIZE},tpad=stop_mode=clone:stop_duration={dur},format=yuv420p"
            args = ["-i", str(wan), "-vf", vf, "-t", str(dur), "-an", "-c:v", "libx264", "-crf", "18", str(c.path)]
        else:
            args = ["-loop", "1", "-framerate", str(FPS), "-i", str(key_img),
                    "-vf", _kenburns_filter(shot["camera"], frames), "-t", str(dur),
                    "-an", "-c:v", "libx264", "-crf", "18", str(c.path)]
        run_ffmpeg(args, stage="shots", shot=sid, note=source)
        c.save_meta(key, source=source, duration=dur)
        log_run("shots", f"ffmpeg-{source}", sid, params={"camera": shot["camera"], "duration": dur},
                seed=shot["seed"], latency_s=time.time() - t0)
        print(f"[shots] {sid} done ({source}, {dur}s)")
