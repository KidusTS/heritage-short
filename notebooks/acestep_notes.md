# ACE-Step 1.5 score on Kaggle or Colab

STATUS: instructions only. I have not run this yet, and I did not write ACE-Step API calls from memory because I cannot verify the current interface. Follow the official guide: https://github.com/ACE-Step/ACE-Step-1.5

1. Open a Kaggle or Colab notebook with a GPU and install ACE-Step 1.5 as the guide describes.
2. Take the inputs from `storyboard.json` -> `music`: `caption`, `bpm`, `key`, `duration_s`, `instrumental`, `seed`. Put tempo and key in the metadata fields, not in the caption, and mark it instrumental.
3. Generate three candidates (change only the seed or the caption wording between them).
4. Listen under the narration at low volume on a phone speaker and on headphones. Pick one and write why in `EXPERIMENTS.md` (#9).
5. Save the chosen file as `outputs/music/score.wav` (keep the others in `outputs/music/candidates/`). The next `python run.py` uses it and the placeholder is ignored.
6. Note the GPU minutes per candidate in `COSTS.md`.
