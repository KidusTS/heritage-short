# Costs and measurements

Every number here must come from `runs.jsonl` (run `python tools_costs.py`) or from the provider's own dashboard. Free-tier limits change often: write down what you actually saw.

## Measured per stage

> Paste the output of `python tools_costs.py` after the real run.

| stage | model | calls | cache hits | errors | total s | mean s | cost USD |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

## GPU time on Kaggle (not visible to `runs.jsonl`: note it by hand)

| Job | Model | Resolution | Shots | GPU minutes | Session |
|---|---|---|---|---|---|
| Wan clips | Wan 2.2 TI2V-5B | | | | |
| Score candidates | ACE-Step 1.5 | | | | |

## Free-tier limits actually found

| Provider | Limit seen | Date |
|---|---|---|
| Gemini API (TTS) | | |
| Cloudflare Workers AI (images) | | |
| Kaggle GPU | | |

## List-price equivalent

The run used free tiers, so the money cost was $0. To estimate what it would cost at list price, multiply the measured calls (images, TTS characters, GPU minutes) by the provider's current price page and show the arithmetic here.

## Frontier comparison

Not done unless frontier access is granted for the cohort.
