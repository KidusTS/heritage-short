# ACE-Step 1.5 score on Kaggle (worked on a T4, 26 Nov 2026)

Official guide: https://github.com/ACE-Step/ACE-Step-1.5 . These are the steps that worked, including the three fixes (FAILURES.md #8 to #10).

1. New Kaggle notebook. Accelerator **GPU T4**, **Internet On** (session options), then restart the session.
2. Check internet: `import socket; print(socket.gethostbyname("github.com"))`.
3. Install (uv installs to /usr/local/bin, so call plain `uv`):
   ```
   !curl -LsSf https://astral.sh/uv/install.sh | sh
   !git clone https://github.com/ACE-Step/ACE-Step-1.5.git
   %cd ACE-Step-1.5
   !uv sync
   ```
4. Save `notebooks/acestep_gen.py` from this repo as `gen.py` inside `ACE-Step-1.5` (use `%%writefile gen.py`).
5. Run it with the matplotlib fix: `%env MPLBACKEND=Agg` then `!uv run python gen.py`. The first run downloads about 10 GB of weights.
6. Zip and download `/kaggle/working/candidates`. Put the files in `outputs/music/candidates/`, listen under the narration, copy the chosen one to `outputs/music/score.wav`, and run `python run.py`.
7. Note the `seconds:` printed by the script in COSTS.md, and the reason for your choice in EXPERIMENTS.md (E10).
