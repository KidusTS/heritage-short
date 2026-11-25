import copy
import json
import sys
from pathlib import Path

import jsonschema
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.common import ROOT, expand, load_storyboard, sha  # noqa: E402


def test_storyboard_is_valid():
    sb = load_storyboard()
    assert 8 <= len(sb["shots"]) <= 12


def test_bad_storyboard_rejected(tmp_path):
    sb = copy.deepcopy(load_storyboard())
    del sb["shots"][0]["seed"]
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(sb))
    with pytest.raises(jsonschema.ValidationError):
        load_storyboard(p)


def test_unknown_character_rejected(tmp_path):
    sb = copy.deepcopy(load_storyboard())
    sb["shots"][0]["characters"] = ["nobody"]
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(sb))
    with pytest.raises(ValueError):
        load_storyboard(p)


def test_expand_and_hash_stable():
    sb = load_storyboard()
    assert "{" not in expand(sb, sb["shots"][1]["image_prompt"])
    assert sha({"a": 1, "b": 2}) == sha({"b": 2, "a": 1})
