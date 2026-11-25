"""Summarise runs.jsonl by stage/model: calls, cache hits, total and mean latency, cost.
Paste the output into COSTS.md.   Run: python tools_costs.py"""
import json
from collections import defaultdict
from pathlib import Path

rows = [json.loads(l) for l in Path(__file__).with_name("runs.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
agg = defaultdict(lambda: {"calls": 0, "hits": 0, "errors": 0, "lat": 0.0, "cost": 0.0})
for r in rows:
    a = agg[(r["stage"], r["model"])]
    if r["cache_hit"]:
        a["hits"] += 1
        continue
    a["calls"] += 1
    a["errors"] += r["status"] != "ok"
    a["lat"] += r["latency_s"]
    a["cost"] += r["cost_usd"]
print("| stage | model | calls | cache hits | errors | total s | mean s | cost USD |")
print("|---|---|---|---|---|---|---|---|")
for (stage, model), a in sorted(agg.items()):
    mean = a["lat"] / a["calls"] if a["calls"] else 0
    print(f"| {stage} | {model} | {a['calls']} | {a['hits']} | {a['errors']} | {a['lat']:.1f} | {mean:.1f} | {a['cost']:.4f} |")
