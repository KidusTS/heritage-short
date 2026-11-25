"""One command for the whole pipeline:  python run.py   (add --help for options)."""
from __future__ import annotations

import argparse
import importlib
import sys
import time

STAGES = ["narration", "keyframes", "shots", "music", "assemble"]  # narration first: it sets shot lengths


def main():
    ap = argparse.ArgumentParser(description="Heritage Short pipeline")
    ap.add_argument("--only", choices=STAGES, nargs="+", help="run only these stages")
    ap.add_argument("--shot", nargs="+", help="restrict narration/keyframes/shots to these shot ids, e.g. S03")
    ap.add_argument("--force", action="store_true", help="ignore the cache")
    ap.add_argument("--validate", action="store_true", help="only validate storyboard.json")
    args = ap.parse_args()

    from pipeline.common import load_storyboard

    sb = load_storyboard()
    print(f"storyboard OK: {len(sb['shots'])} shots, language={sb['language']}")
    if args.validate:
        return
    t0 = time.time()
    for name in args.only or STAGES:
        mod = importlib.import_module(f"pipeline.{name}")
        mod.run(only=args.shot, force=args.force) if name in ("narration", "keyframes", "shots") else mod.run(force=args.force)
    print(f"done in {time.time() - t0:.1f}s. See outputs/final/ and runs.jsonl")


if __name__ == "__main__":
    sys.exit(main())
