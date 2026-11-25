# Failures

Each entry: what broke, what I tried, what fixed or worked around it. Only real events are logged.

## 1. `make` and FFmpeg not installed (setup, 25 Nov)

- **Broke:** the brief suggests `make film`; the Windows machine has no `make`, and no `ffmpeg` on PATH.
- **Tried / fixed:** made the single command `python run.py` instead of a Makefile, and used the `imageio-ffmpeg` pip package, which bundles an FFmpeg binary (found by `pipeline/common.py::ffmpeg_exe`; override with `FFMPEG`). Result: a clean clone needs only `pip install -r requirements.txt`.

## 2. Audio came out at 96 kHz after the loudness pass (found in the first mock run)

- **Broke:** `loudnorm` upsamples internally, so the AAC track was 96 kHz instead of 48 kHz.
- **Fixed:** added `-ar 48000` to the audio encode in `pipeline/assemble.py`.

## 3. Test edit left in the storyboard (found while testing the cache)

- **Broke:** to prove only one shot regenerates I appended text to S03's narration and nearly left it in.
- **Fixed:** reverted it and re-checked with a search for the added text. Lesson: run cache tests on a copy of the storyboard (`load_storyboard(path)` supports it).

## To add as they happen

Quota limits (Cloudflare daily allowance, Kaggle GPU hours), Wan 2.2 out-of-memory on a T4, identity drift between shots, Amharic pronunciation errors in TTS, anything where a model in the brief has moved or been renamed.
