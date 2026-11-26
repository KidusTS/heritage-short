# The Night of the Millennium: a Heritage Short pipeline

A 60 to 90 second AI short film about a fictional Ethiopian family celebrating the Millennium at home, narrated in Amharic with English subtitles, an original score and an "Made with AI" end card. One file, `storyboard.json`, drives every stage; change one shot and only that shot regenerates.

## Run it

```bash
git clone <this repo> && cd heritage-short
pip install -r requirements.txt
cp .env.example .env          # add GEMINI_API_KEY, CF_ACCOUNT_ID, CF_API_TOKEN
python run.py                 # the whole pipeline
```

Outputs: `outputs/final/film_vertical.mp4` (9:16) and `outputs/final/film_horizontal.mp4` (16:9).

| Command | What it does |
|---|---|
| `python run.py` | all stages, cached |
| `python run.py --validate` | validate `storyboard.json` against `schema/` only |
| `python run.py --only keyframes --shot S03` | regenerate one stage for one shot |
| `python run.py --force` | ignore the cache |
| `python -m pipeline.smoke` | call each provider once, log latency |
| `MOCK=1 python run.py` | run offline with placeholders (no keys needed); writes to `outputs_mock/` and `runs_mock.jsonl`, never to the real ones |
| `python tools_costs.py` | summarise `runs.jsonl` for COSTS.md |

No `make` is needed (not available on the author's Windows machine); `python run.py` is the single documented command. FFmpeg is bundled through the `imageio-ffmpeg` pip package, or set `FFMPEG=/path/to/ffmpeg`.

## Stages

`narration` (Gemini TTS) then `keyframes` (Cloudflare FLUX) then `shots` (Wan 2.2 clips from Kaggle, or Ken Burns fallback) then `music` (ACE-Step score from Kaggle, or placeholder) then `assemble` (FFmpeg). Details in [ARCHITECTURE.md](ARCHITECTURE.md).

Two steps run on borrowed GPUs and cannot be called from this repo. Run `notebooks/wan_i2v_kaggle.py` and `notebooks/acestep_notes.md`, then drop the results in `outputs/wan/<shot>.mp4` and `outputs/music/score.wav`. The next `python run.py` picks them up. Without them, the pipeline still produces a complete film from stills and a placeholder track.

## Documents

[DESIGN.md](DESIGN.md) audience, intent, user tests · [ARCHITECTURE.md](ARCHITECTURE.md) · [EXPERIMENTS.md](EXPERIMENTS.md) · [FAILURES.md](FAILURES.md) · [COSTS.md](COSTS.md) · [ETHICS.md](ETHICS.md)

## Cost

Everything uses free tiers; measured numbers are in COSTS.md. Secrets live only in `.env`, which is git-ignored.
