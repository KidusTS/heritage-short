# Experiments

Format: hypothesis, change (one thing), result with evidence, decision. Evidence files are in `outputs/experiments/`, calls are in `runs.jsonl` (`stage="experiment"`), and everything is reproducible with `python experiments/run_experiments.py`. Visual judgements are marked **(visual)**: they are a reviewer's reading of the image, so look at the files yourself before relying on them.

Important context: FLUX.1 schnell on Cloudflare rejects `seed` (see FAILURES.md #4), so the image experiments below are single samples with a random seed. They show what is possible, not statistics.

## Done

### E1. Is the same prompt reproducible without a seed?
- **Hypothesis:** regenerating the S01 prompt gives (nearly) the same image.
- **Change:** re-ran the exact S01 prompt once and compared with the shipped `outputs/keyframes/S01.jpg`.
- **Result:** mean absolute pixel difference **50.9 / 255**, and a different composition (visual: same lanterns and house, different framing and layout). Not reproducible.
- **Decision:** the cache is the only reproducibility mechanism for keyframes. Never delete `outputs/keyframes/` casually; regenerate one shot only on purpose.

### E2. 4 steps versus 8 steps (S02)
- **Hypothesis:** 4 steps is much faster and about as good.
- **Change:** `steps` 8 to 4, same prompt.
- **Result:** latency **2.9 s versus 4.4 s** (34% faster). (visual) both are painted, in-style and show the shawl; no clear quality loss in this single sample.
- **Decision:** use 4 steps for drafts and keep 8 for the shipped shots. One sample cannot prove equal quality.

### E3. Does the fixed character description keep the character?
- **Hypothesis:** repeating the character description is what keeps the grandmother consistent.
- **Change:** replaced `{grandmother}` by "an old woman" (S02), style block kept.
- **Result:** (visual) a different woman: no white netela with green border, an orange and green wrap with a dark head cloth, face turned away. The description carried identity and clothing.
- **Decision:** keep the `{character}` expansion in every prompt that shows the character. Supports the suggested "reference sheet before keyframes" practice, though I used text descriptions, not a reference image.

### E4. Does the style block matter?
- **Hypothesis:** without the style block the look drifts.
- **Change:** removed `style_block` from the S05 prompt.
- **Result:** (visual) the image became a bright, photographic-looking scene, far from the warm painted look of the other shots.
- **Decision:** keep one style block prepended to every prompt.

### E5. Does the audio mix reach the loudness target?
- **Hypothesis:** `loudnorm` single pass lands within 1 LU of -14 LUFS with true peak at or under -1 dB.
- **Change:** measured `film_vertical.mp4` with ffmpeg `ebur128`.
- **Result:** integrated **-15.1 LUFS**, true peak **-1.0 dB**. Peak is fine; loudness is 1.1 LU under target, just outside the hypothesis.
- **Re-measure with the real ACE-Step score (same mix, same single-pass `loudnorm`):** integrated **-14.5 LUFS**, true peak **-0.9 dB**, loudness range 7.6 LU. Within 1 LU of the target; the peak is 0.1 dB over the -1 dB ceiling.
- **Decision:** the loudness gap came from the quiet placeholder pad, not from the filter. Two-pass `loudnorm` is still worth doing to bring the peak under -1 dB, but it is no longer urgent.

### E6. How fast is the Amharic narration?
- **Hypothesis:** the brief's planning figure of 2 to 2.5 words per second applies to Amharic.
- **Change:** measured the 10 TTS files against the word counts in `storyboard.json`.
- **Result:** **1.47 words per second**, and 40.2 s of narration in a 72 s film (56%). Amharic words are longer than English ones, so the English guideline underestimates duration.
- **Decision:** time the script from real TTS output, which the pipeline already does (`shot_duration`). It also shows 44% of the film has no voice, so there is room for more narration or music-led moments.

### E7. Does the cache regenerate only what changed?
- **Hypothesis:** an unchanged rerun makes no model calls, and editing one prompt regenerates one shot.
- **Change A:** reran `python run.py` with nothing changed. **Result:** 0.3 s, 33 log lines, all `cache_hit: true`.
- **Change B:** in a fresh clone, appended text to the S03 `image_prompt` and reran. **Result:** exactly **1 Cloudflare call (5.8 s)** and 1 shot encode (S03); narration, the other 9 keyframes and the music were cached. Assembly re-encoded every segment (about 110 s) because the segment cache files are git-ignored and do not exist in a fresh clone; in the working repo I expect only the S03 segment to be rebuilt (not measured).
- **Decision:** the model-call cache is correct. Leave the segment cache local, and say so in the walkthrough.

### E10. Three seeds of one detailed ACE-Step caption: which score?
- **Hypothesis:** one detailed caption (style, mood, instruments, texture, "no lead vocals") with three seeds gives three usable instrumental candidates that differ enough to choose between.
- **Change:** only the seed (2000, 2001, 2002); caption, `bpm=72`, `keyscale`, `duration=75`, `instrumental=True` fixed, `batch_size=3`, turbo model, Kaggle T4. Script: `notebooks/acestep_gen.py`.
- **Result (measured, `ffmpeg ebur128`):**

| Candidate file | Length | Integrated loudness | Loudness range | Peak |
|---|---|---|---|---|
| `171efc4a-...wav` | 75.0 s | -15.8 LUFS | 8.6 LU | -1.0 dBFS |
| `d267adf6-...wav` | 75.0 s | -18.6 LUFS | 12.6 LU | -0.6 dBFS |
| chosen, now `score.wav` (original filename lost on rename) | 75.0 s | -18.4 LUFS | 11.8 LU | -1.0 dBFS |

  All three are 48 kHz stereo WAV. The batch of three took **19.9 s** to generate (printed by `gen.py`; excludes weight download and model load). The chosen one has a wider dynamic range (11.8 LU) than the 171efc4a candidate (8.6 LU).
- **Why this candidate:** **[YOU: one or two sentences, from listening under the narration on a phone speaker and on headphones. What did the other two do wrong: too busy, a strong lead melody, too loud under the voice, wrong mood? I cannot hear audio, so this part has to be yours.]**
- **Decision:** `outputs/music/score.wav` is the chosen file; the pipeline picks it up automatically. With it the final mix measures -14.5 LUFS (see E5).

## Not run yet (need a GPU or quota)

| # | Hypothesis | Why not run |
|---|---|---|
| E8 | Wan 2.2 at 480p is fast enough to draft, 720p only for chosen shots | needs Kaggle/Colab |
| E9 | Image-to-video with a motion-only prompt beats re-describing the subject | needs Kaggle/Colab |
| E10b | A detailed ACE-Step caption beats a one-word caption | only the detailed caption was run; a one-word run (same seed) is still needed to answer this |
| E11 | A style instruction improves Amharic TTS prosody more than changing voice | skipped on purpose: the Gemini free TTS quota is needed for the walkthrough demo |
| E12 | A Ken Burns still is acceptable next to a real Wan clip | needs E8 plus 3 viewers |

Count: 8 done (E1 to E7 and E10), up to 4 more possible (E8, E9, E10b, E11, E12). The brief asks for about ten.
