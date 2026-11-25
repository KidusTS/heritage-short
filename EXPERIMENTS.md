# Experiments

Format: hypothesis, change (one thing, seed fixed), result with evidence (a `runs.jsonl` line or a measured number), decision. About ten entries is the target. Results are left blank until the run is done: do not fill them from expectation.

## Planned (fill each in after running it)

| # | Hypothesis | Change | Result | Decision |
|---|---|---|---|---|
| 1 | Repeating the same character description in every prompt keeps faces recognisable across shots | Same seed, with vs without `{character}` description | | |
| 2 | Adding the style block to every prompt keeps the look consistent | With vs without `style_block` | | |
| 3 | FLUX.1 schnell at 8 steps is good enough versus 4 steps | steps 4 vs 8, seed fixed | | |
| 4 | A fixed seed makes two prompts comparable | Same prompt, 3 seeds | | |
| 5 | Short style instruction improves Amharic TTS prosody more than switching voice | style on/off, then voice Kore vs another | | |
| 6 | Wan 2.2 at 480p is fast enough to draft; 720p only for chosen shots | resolution 480p vs 720p on one shot, log GPU minutes | | |
| 7 | Image-to-video with a motion-only prompt beats re-describing the subject | motion-only vs full prompt | | |
| 8 | Ken Burns fallback is acceptable for shots where Wan shows identity drift | blind comparison with 3 viewers | | |
| 9 | A caption with style, mood, instruments and texture gives a better ACE-Step score than one word | 3 candidates each | | |
| 10 | Sidechain ducking at threshold 0.02 / ratio 6 keeps Amharic narration intelligible | listen on phone speaker and headphones | | |
