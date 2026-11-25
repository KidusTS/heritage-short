# Architecture

## The contract

`storyboard.json` is the only input to every stage. It is validated against `schema/storyboard.schema.json` (JSON Schema) before any run, plus two checks the schema cannot express: unique shot ids and known character ids. Prompts, seeds, camera moves, narration text and music settings all live in the file, not in code, so a run is reproducible and explainable.

```
storyboard.json --validate--> narration --> keyframes --> shots --> music --> assemble
                                 |             |           |         |          |
                           outputs/narration  /keyframes  /shots   /music     /final
```

| Stage | Reads | Writes | Model |
|---|---|---|---|
| narration | `shots[].narration.text_native`, `voice` | `outputs/narration/<id>.wav` | Gemini TTS |
| keyframes | `style_block`, `characters`, `shots[].image_prompt`, `seed` | `outputs/keyframes/<id>.jpg` | FLUX.1 schnell on Cloudflare |
| shots | keyframe, `camera`, shot duration, optional `outputs/wan/<id>.mp4` | `outputs/shots/<id>.mp4` | Wan 2.2 (Kaggle) or FFmpeg Ken Burns |
| music | `music`, optional `outputs/music/score.*` | placeholder or the chosen score | ACE-Step 1.5 (Kaggle) |
| assemble | all of the above | `outputs/final/film_{vertical,horizontal}.mp4`, `subs.srt` | FFmpeg |

Narration runs first because it sets shot length: `shot_duration = max(min_duration_s, narration seconds + 1 s)`, rounded up to 0.5 s. The edit is cut to the voice.

## Caching

Each output has a sidecar `<name>.meta.json` holding a hash of its inputs (model, prompt, seed, upstream file hashes, duration). A stage skips a shot when the output exists and the hash matches. Verified behaviour: after editing one narration line, only that shot's narration and the final assembly re-ran; keyframes, shots and music stayed cached.

## Failure handling

- **Retries:** every remote call goes through `retry()` with exponential backoff (2, 4, 8 s, 4 tries).
- **Fallbacks:** no Wan clip, so Ken Burns over the keyframe. No ACE-Step score, so a placeholder pad (flagged in `runs.jsonl`). Both let the film complete.
- **Logging:** every call, including cache hits and errors, appends one line to `runs.jsonl` (stage, shot, model, params, seed, latency, cost, cache_hit, status).
- **Secrets:** read from the environment or `.env` (git-ignored); missing keys stop the run with a clear message.
- **Mock mode:** `MOCK=1` swaps remote models for local placeholders, which lets the assembly be tested without quota.

## Assembly

Keyframes are square (1024 px) with the subject centred, so one clip crops cleanly to 9:16 and 16:9. Narration is placed on a single track at each shot start (0.4 s lead-in). The score is looped, faded in and out, ducked with `sidechaincompress` (threshold 0.02, ratio 6, attack 300 ms, release 1500 ms), mixed under the voice and normalised with `loudnorm` to -14 LUFS, true peak -1 dB. English subtitles (max 2 lines of 40 characters) are burned in from `subs.srt`, with a higher margin in the vertical cut for the safe area. A 3 s end card reading "Made with AI" closes both cuts.
