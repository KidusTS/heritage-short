# Costs and measurements

Numbers come from `runs.jsonl` (`python tools_costs.py`) or the provider pages named in each row. List prices were read on 26 Nov 2026 and may change.

## Measured per stage (from runs.jsonl)

| stage      | model                                | calls | cache hits | errors | total s | mean s | cost USD |
| ---------- | ------------------------------------ | ----- | ---------- | ------ | ------- | ------ | -------- |
| assemble   | ffmpeg                               | 37    | 2          | 0      | 369.8   | 10.0   | 0.0000   |
| assemble   | ffmpeg-sidechain+loudnorm            | 1     | 0          | 0      | 5.7     | 5.7    | 0.0000   |
| experiment | @cf/black-forest-labs/flux-1-schnell | 4     | 0          | 0      | 17.0    | 4.3    | 0.0000   |
| keyframes  | @cf/black-forest-labs/flux-1-schnell | 10    | 10         | 0      | 42.3    | 4.2    | 0.0000   |
| music      | ffmpeg / placeholder-ffmpeg          | 2     | 1          | 0      | 0.4     | 0.2    | 0.0000   |
| narration  | gemini-2.5-flash-preview-tts         | 5     | 1          | 0      | 48.7    | 9.7    | 0.0000   |
| narration  | gemini-3.8-flash-tts                 | 10    | 20         | 0      | 63.5    | 6.3    | 0.0000   |
| shots      | ffmpeg-kenburns (and ffmpeg)         | 10    | 10         | 0      | 18.5    | 1.9    | 0.0000   |
| smoke      | cloudflare-flux                      | 4     | 0          | 1      | 20.5    | 5.1    | 0.0000   |
| smoke      | gemini-tts                           | 4     | 0          | 3      | 25.9    | 6.5    | 0.0000   |

Reading it: one image takes about 4 s, one TTS line about 6 s (plus waiting when rate-limited), one shot encode about 2 s, and a full assembly of both aspect ratios roughly 110 s in a fresh checkout. Calls from outside the pipeline (two manual API probes, and one image in the clean-clone test) are not in this log.

## GPU time on Kaggle/Colab (not visible to runs.jsonl: note by hand)

| Job              | Model           | Resolution  | Shots | GPU minutes | Session |
| ---------------- | --------------- | ----------- | ----- | ----------- | ------- |
| Wan clips        | Wan 2.2 TI2V-5B | not run yet |       |             |         |
| Score candidates | ACE-Step 1.5 (turbo) | 3 candidates x 75 s in one batch | n/a | **0.33** (19.9 s of generation as printed by `gen.py`; excludes the ~10 GB weight download and model load, which I did not time) | Kaggle T4, 26 Nov |

## Free-tier limits actually seen

| Provider                           | Limit seen                                                                                                                               | Date   |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| Gemini API, `gemini-2.5-flash-tts` | **10 requests per day** on the free tier (error body: "limit: 10 ... Generate content requests per day"); exhausted after about 10 calls | 26 Nov |
| Gemini API, `gemini-3.8-flash-tts` | per-minute 429s absorbed by retry; **no daily cap hit yet**, daily limit unknown (the model pages I found did not state it)              | 26 Nov |
| Cloudflare Workers AI              | not hit. Docs give 10,000 free neurons per day. About 20 images so far, roughly 2,000 neurons                                            | 26 Nov |
| Kaggle GPU | used for ACE-Step on 26 Nov; weekly GPU hours remaining **[YOU: read from your Kaggle account page]** | 26 Nov |

## List-price equivalent (what this run would cost without free tiers)

| Item                                                     | Arithmetic                                                                                                    | Cost                                                              |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- | --------------------------- |
| Cloudflare image, FLUX.1 schnell, 1024x1024, 8 steps     | 4 tiles of 512x512 x 4.8 neurons + 8 steps x 9.6 neurons = 96 neurons; 96 x $0.011 per 1,000 neurons          | **$0.0011 per image**                                             |
| 20 images made so far (incl. experiments, smoke, probes) | 20 x $0.0011                                                                                                  | about $0.02                                                       |
| Final narration, Gemini 3.8 Flash TTS                    | 40.2 s of audio x 25 tokens per s = 1,005 audio tokens x $9 per 1M, plus about 700 text tokens x $0.50 per 1M | about **$0.01** (more if retries and regenerations are counted)   |
| FFmpeg, Pillow, local code                               | runs on my machine                                                                                            | $0                                                                |
| Kaggle / Colab GPU | free tier | $0 (list-price equivalent still to add: 0.33 GPU minutes of generation, plus load and download time) |

Total list-price equivalent so far: about **$0.03 to $0.05**, against **$0** actually paid. Google's TTS price is listed to double on 1 Jan 2027.

Sources: Cloudflare Workers AI pricing (developers.cloudflare.com/workers-ai/platform/pricing), Google Cloud Text-to-Speech pricing (cloud.google.com/text-to-speech/pricing). Prices came via search results, so check the pages before quoting them.

## Frontier comparison

Not done: no frontier access was provided.
