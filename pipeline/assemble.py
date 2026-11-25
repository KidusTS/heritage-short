"""Stage: assembly. Cuts the shots, builds the narration track, ducks the score under it,
burns English subtitles, adds the AI end card, normalises loudness, exports 9:16 and 16:9."""
from __future__ import annotations

import time
import wave

from .common import OUT, ROOT, Cache, load_storyboard, log_run, run_ffmpeg, sha, sha_file, shot_duration
from .music import chosen_score

ASPECTS = {
    "vertical": {"w": 1080, "h": 1920, "crop": "crop=min(iw\\,ih*9/16):min(ih\\,iw*16/9)", "font": 10, "margin": 55},
    "horizontal": {"w": 1920, "h": 1080, "crop": "crop=min(iw\\,ih*16/9):min(ih\\,iw*9/16)", "font": 12, "margin": 20},
}
FPS = 24
LEAD_IN = 0.4  # seconds of silence before each narration line


def _srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def _wrap(text: str, width: int = 40) -> str:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    return "\n".join(lines[:2] if len(lines) > 2 else lines)


def _timeline(sb):
    t, rows = 0.0, []
    for s in sb["shots"]:
        d = shot_duration(sb, s)
        nwav = OUT / "narration" / f"{s['id']}.wav"
        with wave.open(str(nwav), "rb") as w:
            n_s = w.getnframes() / w.getframerate()
        rows.append({"shot": s, "start": t, "dur": d, "narr_s": n_s})
        t += d
    return rows, t


def _narration_track(rows, total: float, path):
    """Place each narration line (24 kHz mono) at its shot start on one silent track."""
    rate = 24000
    out = bytearray(int(total * rate) * 2)
    for r in rows:
        with wave.open(str(OUT / "narration" / f"{r['shot']['id']}.wav"), "rb") as w:
            pcm = w.readframes(w.getnframes())
        off = int((r["start"] + LEAD_IN) * rate) * 2
        out[off:off + len(pcm)] = pcm[: max(0, len(out) - off)]
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(out))


def _end_card(sb, path):
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (1920, 1920), (15, 12, 10))
    d = ImageDraw.Draw(img)
    font = None
    for f in ("C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/System/Library/Fonts/Helvetica.ttc"):
        try:
            font = ImageFont.truetype(f, 120)
            break
        except OSError:
            continue
    font = font or ImageFont.load_default()
    text = sb["end_card"]["text"]
    box = d.textbbox((0, 0), text, font=font)
    d.text(((1920 - (box[2] - box[0])) / 2, 880), text, fill=(240, 220, 180), font=font)
    img.save(path)


def run(only=None, force: bool = False):
    sb = load_storyboard()
    rows, vid_total = _timeline(sb)
    card_s = sb["end_card"]["duration_s"]
    total = vid_total + card_s
    final = OUT / "final"
    final.mkdir(parents=True, exist_ok=True)
    score = chosen_score()
    sb_hash = sha(sb)
    deps = sha(sb_hash, sha_file(score), [sha_file(OUT / "shots" / f"{r['shot']['id']}.mp4") for r in rows],
               [sha_file(OUT / "narration" / f"{r['shot']['id']}.wav") for r in rows])

    # ---- audio: narration + ducked score + loudness
    nar = final / "narration.wav"
    _narration_track(rows, total, nar)
    mix = final / "mix.m4a"
    c_audio = Cache("final", "mix", "m4a")
    if not (c_audio.hit(deps) and not force):
        t0 = time.time()
        fade_out_at = max(0, total - 3)
        fc = (f"[1:a]aloop=loop=-1:size=2000000000,atrim=0:{total},afade=t=in:d=2,"
              f"afade=t=out:st={fade_out_at}:d=3,aformat=sample_rates=48000:channel_layouts=stereo[m];"
              "[0:a]aresample=48000,aformat=channel_layouts=stereo,asplit=2[v][sc];"
              "[m][sc]sidechaincompress=threshold=0.02:ratio=6:attack=300:release=1500[d];"
              "[v][d]amix=inputs=2:weights=1.6 0.8:normalize=0[mx];"
              "[mx]loudnorm=I=-14:TP=-1:LRA=11[a]")
        run_ffmpeg(["-i", str(nar), "-i", str(score), "-filter_complex", fc, "-map", "[a]", "-t", str(total),
                    "-c:a", "aac", "-ar", "48000", "-b:a", "192k", str(c_audio.path)], stage="assemble", note="audio mix")
        c_audio.save_meta(deps)
        log_run("assemble", "ffmpeg-sidechain+loudnorm", None, latency_s=time.time() - t0, note="audio")

    # ---- subtitles (SRT from narration timing)
    srt = final / "subs.srt"
    with open(srt, "w", encoding="utf-8") as f:
        for i, r in enumerate(rows, 1):
            a = r["start"] + LEAD_IN
            f.write(f"{i}\n{_srt_time(a)} --> {_srt_time(a + r['narr_s'])}\n{_wrap(r['shot']['narration']['text_en'])}\n\n")

    # ---- end card image
    card_img = final / "endcard.png"
    _end_card(sb, card_img)

    # ---- video per aspect
    for name, a in ASPECTS.items():
        out_mp4 = Cache("final", f"film_{name}", "mp4")
        vkey = sha(deps, name, card_s, a)
        if out_mp4.hit(vkey) and not force:
            log_run("assemble", "ffmpeg", None, cache_hit=True, note=name)
            print(f"[assemble] {name} cached")
            continue
        t0 = time.time()
        scale = f"{a['crop']},scale={a['w']}:{a['h']}:flags=lanczos,fps={FPS},format=yuv420p"
        segs = []
        for r in rows:
            sid = r["shot"]["id"]
            seg = final / f"seg_{name}_{sid}.mp4"
            seg_cache = Cache("final", f"seg_{name}_{sid}", "mp4")
            skey = sha(sha_file(OUT / "shots" / f"{sid}.mp4"), name, a["w"])
            if not seg_cache.hit(skey):
                run_ffmpeg(["-i", str(OUT / "shots" / f"{sid}.mp4"), "-vf", scale, "-an", "-c:v", "libx264",
                            "-crf", "18", str(seg)], stage="assemble", shot=sid, note=f"segment {name}")
                seg_cache.save_meta(skey)
            segs.append(seg)
        card = final / f"seg_{name}_card.mp4"
        run_ffmpeg(["-loop", "1", "-framerate", str(FPS), "-i", str(card_img), "-vf", scale, "-t", str(card_s),
                    "-an", "-c:v", "libx264", "-crf", "18", str(card)], stage="assemble", note="end card")
        segs.append(card)
        lst = final / f"list_{name}.txt"
        lst.write_text("".join(f"file '{p.name}'\n" for p in segs), encoding="utf-8")
        silent = final / f"silent_{name}.mp4"
        run_ffmpeg(["-f", "concat", "-safe", "0", "-i", lst.name, "-c", "copy", silent.name], stage="assemble",
                   cwd=final, note=f"concat {name}")
        style = f"FontSize={a['font']},Alignment=2,MarginV={a['margin']},Outline=2,Shadow=0,PrimaryColour=&H00FFFFFF"
        run_ffmpeg(["-i", silent.name, "-i", "mix.m4a", "-vf", f"subtitles=subs.srt:force_style='{style}'",
                    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "18", "-c:a", "copy", "-shortest",
                    "-movflags", "+faststart", out_mp4.path.name], stage="assemble", cwd=final, note=f"burn subs {name}")
        out_mp4.save_meta(vkey, seconds=total)
        log_run("assemble", "ffmpeg", None, params={"aspect": name, "seconds": total}, latency_s=time.time() - t0)
        print(f"[assemble] {name} -> {out_mp4.path.relative_to(ROOT)} ({total:.1f}s)")
