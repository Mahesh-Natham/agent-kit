#!/usr/bin/env python3
"""Append one scored run to .evolve/ledger.jsonl."""
import argparse
import datetime
import json

from _common import EVOLVE, SECRET_RE, ledger, need_root, next_run_id, read_json


def parse_score(s):
    s = (s or "").strip()
    if not s:
        return ""
    try:
        if "/" in s:
            n, d = (int(x) for x in s.split("/", 1))
            return round(n / d, 3) if d else ""
        v = float(s)
    except ValueError:
        raise SystemExit(f"Bad --score {s!r}: use 0-1 or passed/total, e.g. 3/4.")
    if not 0 <= v <= 1:
        raise SystemExit("--score must be between 0 and 1.")
    return v


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
        raise SystemExit("Refusing to log: the text looks like it contains a secret. Remove it and retry.")
    entries = ledger(root)
    rid = next_run_id(entries)
    rec = {"id": rid, "ts": datetime.datetime.now().isoformat(timespec="seconds"),
           "task": a.task.strip()[:200], "outcome": a.outcome, "score": parse_score(a.score),
           "note": a.note.strip()[:400]}
    with open(root / EVOLVE / "ledger.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    st = read_json(root / EVOLVE / "state.json", {"last_cycle_ledger_count": 0})
    new = len(entries) + 1 - st.get("last_cycle_ledger_count", 0)
    print(f"Logged {rid} ({a.outcome}). {new} new run(s) since the last evolve cycle"
          + ("; time to run one." if new >= 5 else "."))


if __name__ == "__main__":
    main()
