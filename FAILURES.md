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

## 4. Cloudflare rejected `seed` for FLUX.1 schnell (first smoke test, 26 Nov)

- **Broke:** `python -m pipeline.smoke` returned HTTP 400, code 5006: `Additional or unevaluated properties '/seed' at '/' not allowed`. Token and account ID were fine (the same call without `seed` returned 200 and an image).
- **Tried:** the same call with `prompt`+`steps`+`seed`, then `prompt`+`steps`, then `prompt` only; only the ones without `seed` worked.
- **Fixed:** `seed` is no longer sent unless `CF_SEND_SEED=1` is set (for models that accept it). Consequence: keyframes are not reproducible from the seed alone on this model, so the cache (outputs/keyframes plus the stored prompt hash) is what keeps a result stable. The seed is still kept in the storyboard and the log.

## 5. Gemini TTS sometimes returns no audio (second smoke test, 26 Nov)

- **Broke:** the smoke test failed with `KeyError: 'content'` right after passing on the previous run.
- **Tried:** called the same request 3 times: results were STOP, OTHER (no `content`), STOP. So the API itself is intermittent, about 1 call in 3 in this test.
- **Fixed:** `_gemini_tts` now raises a clear error when audio is missing, so `retry()` (4 tries, exponential backoff) handles it. Sample is only 3 calls, so the real failure rate is unknown; check the `status=error` lines in `runs.jsonl`.

## 6. Gemini free-tier TTS quota exhausted by my own testing (26 Nov)

- **Broke:** after 5 of 10 narration lines, every call returned HTTP 429. The body said `limit: 10 ... requests per day ... model: gemini-2.5-flash-tts` and "retry in 21h25m", which is after the deadline. About 7 of the 10 daily requests had been spent on smoke tests and probes, which was avoidable.
- **Tried:** waiting with backoff (up to 80 s) did nothing because it is a daily cap, not a per-minute one. Listed the models on the key (`GET /v1beta/models`) and found `gemini-3.8-flash-tts`, which has its own quota.
- **Fixed:** switched the default model to `gemini-3.8-flash-tts`. It returns a full WAV file instead of raw PCM, so `_gemini_tts` now accepts both. All 10 lines were regenerated with one model so the voice is consistent. Per-minute 429s still happen and are absorbed by the retry (6 tries, 5 s base).
- **Lesson:** read the quota table before smoke-testing, and make the smoke test one call per provider.

## 7. Mock mode could overwrite real outputs (found by the clean-clone test, 26 Nov)

- **Broke:** `MOCK=1 python run.py` wrote placeholders into `outputs/`, the same folder as the real narration and keyframes, and logged to the real `runs.jsonl`. In a real repo that would silently replace real work.
- **Fixed:** in mock mode `OUT` is `outputs_mock/` and the log is `runs_mock.jsonl` (both git-ignored), chosen at import time from the `MOCK` environment variable.

## 8. Kaggle notebook had no internet (ACE-Step setup, 26 Nov)

- **Broke:** `curl` and `git clone` failed with "Could not resolve host", and a Python check returned `[Errno -3] Temporary failure in name resolution`. `ping` is not installed in the container, so it could not be used to test.
- **Tried / fixed:** Kaggle turns internet off by default. Turned **Internet on** in the notebook session options and restarted the session; the clone then worked. **[YOU: confirm what you did, and whether phone verification was needed.]** Tested with `socket.gethostbyname("github.com")`.

## 9. Wrong `uv` path in my first instructions (26 Nov)

- **Broke:** `/root/.local/bin/uv: No such file or directory` after the installer said it was done.
- **Fixed:** the installer printed `installing to /usr/local/bin`, so plain `uv` works. The path I had given was wrong.

## 10. ACE-Step import crashed on matplotlib (26 Nov)

- **Broke:** `python gen.py` failed at `import matplotlib` with `ValueError: Key backend: 'module://matplotlib_inline.backend_inline' is not a valid value`.
- **Cause:** Kaggle sets `MPLBACKEND=module://matplotlib_inline.backend_inline` for its own Python; ACE-Step runs in a separate `uv` virtual environment without that module.
- **Fixed:** `%env MPLBACKEND=Agg` before `uv run python gen.py`. No reinstall was needed. Generation then finished successfully on the T4 and produced 3 candidates.

## To add as they happen

Quota limits (Cloudflare daily allowance, Kaggle GPU hours), Wan 2.2 out-of-memory on a T4, identity drift between shots, Amharic pronunciation errors in TTS, anything where a model in the brief has moved or been renamed.
