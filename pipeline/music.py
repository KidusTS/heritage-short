"""Stage: music.

Preferred: an ACE-Step 1.5 score generated on Kaggle/Colab (see notebooks/) and saved as
outputs/music/score.wav (or .mp3). Candidates go in outputs/music/candidates/ and the choice is
written up in EXPERIMENTS.md. Fallback: a synthetic placeholder pad so the pipeline still runs."""
from __future__ import annotations

import time

from .common import OUT, Cache, load_storyboard, log_run, run_ffmpeg, sha, sha_file


def chosen_score():
    """Return the path of the real score if present, else the placeholder (made by run())."""
    for ext in ("wav", "mp3", "flac", "m4a"):
        p = OUT / "music" / f"score.{ext}"
        if p.exists():
            return p
    return OUT / "music" / "placeholder.wav"


def run(only=None, force: bool = False):
    sb = load_storyboard()
    real = [p for p in (OUT / "music").glob("score.*") if p.suffix != ".json"] if (OUT / "music").exists() else []
    if real:
        log_run("music", "ace-step-1.5", None, cache_hit=True, note=f"using {real[0].name}")
        print(f"[music] using {real[0].name}")
        return
    dur = sb["music"]["duration_s"]
    key = sha("placeholder", dur, sb["music"]["bpm"])
    c = Cache("music", "placeholder", "wav")
    if c.hit(key) and not force:
        log_run("music", "placeholder", None, cache_hit=True)
        print("[music] placeholder cached (no real score found; add outputs/music/score.wav)")
        return
    t0 = time.time()
    # soft A-minor pad with slow tremolo, a temp track only
    expr = ("sine=frequency=220:duration={d}[a];sine=frequency=261.63:duration={d}[b];"
            "sine=frequency=329.63:duration={d}[c];[a][b][c]amix=inputs=3:normalize=0,"
            "tremolo=f=0.3:d=0.4,volume=0.5,aformat=sample_rates=48000:channel_layouts=stereo").format(d=dur)
    run_ffmpeg(["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-filter_complex", expr, "-t", str(dur), str(c.path)],
               stage="music", note="placeholder")
    c.save_meta(key)
    log_run("music", "placeholder-ffmpeg", None, params={"duration": dur}, latency_s=time.time() - t0,
            note="temp track; replace with ACE-Step score")
    print("[music] placeholder written")
