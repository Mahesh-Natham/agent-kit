#!/usr/bin/env python3
"""Append one scored run to the ledger."""
import argparse, datetime, json
from _common import EVOLVE, need_root, ledger, read_json, SECRET_RE

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--task", required=True)
    ap.add_argument("--outcome", required=True, choices=["pass", "fail", "corrected", "abandoned"])
    ap.add_argument("--score", default="", help="0-1 or passed/total")
    ap.add_argument("--note", default="")
    a = ap.parse_args()
    root = need_root(a.root)
    if SECRET_RE.search(a.task + " " + a.note):
        raise SystemExit("Refusing to log: text looks like it contains a secret. Remove it and retry.")
    score = a.score
    if "/" in score:
        n, d = score.split("/", 1)
        score = round(int(n) / int(d), 3) if int(d) else ""
    elif score != "":
        score = float(score)
    entries = ledger(root)
    rid = f"R{len(entries) + 1:04d}"
    rec = {"id": rid, "ts": datetime.datetime.now().isoformat(timespec="seconds"),
           "task": a.task[:200], "outcome": a.outcome, "score": score, "note": a.note[:400]}
    with open(root / EVOLVE / "ledger.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    st = read_json(root / EVOLVE / "state.json", {"last_cycle_ledger_count": 0})
    new = len(entries) + 1 - st.get("last_cycle_ledger_count", 0)
    print(f"Logged {rid} ({a.outcome}). {new} new entries since last evolve cycle"
          + ("; time to run one." if new >= 5 else "."))

if __name__ == "__main__":
    main()
