#!/usr/bin/env python3
"""
score_skill.py — Autoresearch scoring helper.
Reads test cases JSON + scores JSON, computes weighted aggregate, prints report.

Usage:
  python3 score_skill.py <test-cases.json> <scores.json>

scores.json format:
[
  {
    "id": 1,
    "trigger_precision": 8,
    "workflow_coverage": 7,
    "reference_completeness": 9,
    "conciseness": 8,
    "notes": "optional"
  },
  ...
]
"""
import json
import sys
from pathlib import Path

WEIGHTS = {
    "trigger_precision": 0.30,
    "workflow_coverage": 0.30,
    "reference_completeness": 0.20,
    "conciseness": 0.20,
}

def weighted_score(s):
    return sum(s.get(k, 0) * w for k, w in WEIGHTS.items())

def main():
    if len(sys.argv) < 3:
        print("Usage: score_skill.py <test-cases.json> <scores.json>")
        sys.exit(1)

    cases = json.loads(Path(sys.argv[1]).read_text())
    scores = json.loads(Path(sys.argv[2]).read_text())

    cases_by_id = {c["id"]: c for c in cases}
    
    print(f"{'ID':<4} {'Type':<12} {'Trigger':>7} {'Workflow':>8} {'Ref':>4} {'Concise':>8} {'Weighted':>9}  Prompt")
    print("-" * 90)
    
    totals = []
    for s in scores:
        case = cases_by_id.get(s["id"], {})
        ws = weighted_score(s)
        totals.append(ws)
        prompt = (case.get("prompt", "?"))[:40]
        ctype = case.get("case_type", "?")
        print(f"{s['id']:<4} {ctype:<12} {s.get('trigger_precision',0):>7} {s.get('workflow_coverage',0):>8} {s.get('reference_completeness',0):>4} {s.get('conciseness',0):>8} {ws:>9.2f}  {prompt}")

    avg = sum(totals) / len(totals) if totals else 0
    print("-" * 90)
    print(f"Average weighted score: {avg:.2f} / 10.00")

    # Stop condition advice
    if avg >= 8.5:
        print("✅ Score ≥ 8.5 — skill is high quality. Stop.")
    elif avg < 4.0:
        print("⚠️  Score < 4.0 — consider full rewrite.")
    else:
        print(f"🔄 Continue loop. Target: 8.5")

    # Low scorers
    low = [(s, weighted_score(s)) for s in scores if weighted_score(s) < 6.0]
    if low:
        print("\nLow-scoring cases to address:")
        for s, ws in sorted(low, key=lambda x: x[1]):
            case = cases_by_id.get(s["id"], {})
            print(f"  Case {s['id']} ({ws:.1f}): {case.get('prompt','?')[:60]}")
            if s.get("notes"):
                print(f"    Note: {s['notes']}")

if __name__ == "__main__":
    main()
