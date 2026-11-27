#!/usr/bin/env python3
"""Validation gate for .evolve/lessons.md.

  propose  --add TEXT [--evidence R0001,R0002 | --user-stated] [--scope GLOB]
           --replace L003 --add TEXT ...   |   --delete L003
  accept   --tier evidence   |   --tier replay --before before.json --after after.json
  reject   --reason TEXT [--op N]
  rollback                    undo the last accept
  score    [--cwd DIR] [--out FILE] [--only NAME,...]   run verifier.json commands
  status
It never commits or pushes; the user decides when .evolve/ goes into git.
"""
import argparse
import datetime
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from _common import (EVOLVE, LESSON_RE, MAX_CHARS, MAX_LESSONS, MAX_OPS, SECRET_RE, ledger, need_root,
                     read_json, write_json)

SIMILAR = 0.6


def toks(s):
    return set(re.findall(r"[a-z0-9_./-]{3,}", s.lower()))


def jac(a, b):
    a, b = toks(a), toks(b)
    return len(a & b) / len(a | b) if a and b else 0.0


def body(line):
    """Lesson text without the id, scope and evidence parts."""
    return re.split(r"\s\|\sscope:", LESSON_RE.sub("", line))[0].strip()


def fmt(lid, text, scope, ev):
    return f"- [{lid}] {text} | scope: {scope or '**'} | ev: {','.join(ev) if ev else 'user-stated'}"


def paths(root):
    d = root / EVOLVE
    return d / "lessons.md", d / "pending.json", d / "rejected.md", d / "snapshots", d / "state.json"


def lesson_map(les):
    out = {}
    for line in les.read_text(encoding="utf-8").splitlines():
        m = LESSON_RE.match(line)
        if m:
            out[m.group(1)] = line
    return out


def cmd_propose(a):
    root = need_root(a.root)
    les, pend, rej, _, _ = paths(root)
    ops = read_json(pend, [])
    if len(ops) >= MAX_OPS:
        sys.exit(f"Budget reached: max {MAX_OPS} edits per cycle. Accept or reject the pending ones first.")
    if a.delete and (a.add or a.replace):
        sys.exit("--delete cannot be combined with --add or --replace.")
    if a.replace and not a.add:
        sys.exit("--replace needs the new text in --add.")
    kind = "delete" if a.delete else "replace" if a.replace else "add" if a.add else None
    if not kind:
        sys.exit("Use --add TEXT, --replace ID --add TEXT, or --delete ID.")
    ids = lesson_map(les)
    target = a.replace or a.delete
    if target and target not in ids:
        sys.exit(f"Unknown lesson {target}.")
    if target and any(o["target"] == target for o in ops):
        sys.exit(f"{target} already has a pending edit.")
    # commas or spaces: PowerShell turns an unquoted R0001,R0002 into "R0001 R0002"
    ev = sorted({e for e in re.split(r"[,\s]+", a.evidence or "") if e})
    known = {e.get("id") for e in ledger(root)}
    missing = [e for e in ev if e not in known]
    if missing:
        sys.exit(f"Unknown evidence run IDs: {missing}")
    text = ""
    if kind != "delete":
        text = " ".join(a.add.split())
        if not text or len(text) > MAX_CHARS:
            sys.exit(f"A lesson must be one non-empty line of at most {MAX_CHARS} characters.")
        if SECRET_RE.search(text):
            sys.exit("Rejected: the text looks like a secret.")
        if not ev and not a.user_stated:
            sys.exit("Evidence required: --evidence R0001,R0002 (or --user-stated if the user dictated the rule).")
        others = [body(line) for k, line in ids.items() if k != target]
        others += [o["text"] for o in ops if o["text"]]
        for o in others:
            if jac(text, o) >= SIMILAR:
                sys.exit(f"Near-duplicate of an existing or pending lesson: {o}")
        for line in rej.read_text(encoding="utf-8").splitlines():
            if line.startswith("- ") and jac(text, line[2:].split(" | reason:")[0]) >= SIMILAR:
                sys.exit(f"A similar edit was rejected before: {line}")
    delta = lambda k: 1 if k == "add" else -1 if k == "delete" else 0  # noqa: E731
    if len(ids) + delta(kind) + sum(delta(o["kind"]) for o in ops) > MAX_LESSONS:
        sys.exit(f"Would exceed {MAX_LESSONS} lessons. Propose a --delete or --replace first.")
    op = {"kind": kind, "target": target, "text": text, "scope": a.scope, "evidence": ev,
          "user_stated": a.user_stated}
    ops.append(op)
    write_json(pend, ops)
    print(f"Pending edit #{len(ops)}: {kind} {target or ''} {text[:80]}".rstrip())
    print("Next: validate (evidence or replay tier), then `gate.py accept`.")


def check_replay(before_f, after_f):
    b, a = read_json(before_f, None), read_json(after_f, None)
    if not b or not a:
        sys.exit("Replay gate: --before and --after must be JSON files written by `gate.py score --out`.")
    if a["passed"] <= b["passed"]:
        sys.exit(f"Replay gate failed: {a['passed']} checks pass after vs {b['passed']} before (needs more).")
    after_ok = {r["name"]: r["status"] for r in a["results"]}
    regressed = [r["name"] for r in b["results"] if r["status"] == "ok" and after_ok.get(r["name"]) == "fail"]
    if regressed:
        sys.exit(f"Replay gate failed: these checks passed before and fail now: {regressed}")
    return f"{b['passed']}->{a['passed']}"


def cmd_accept(a):
    root = need_root(a.root)
    les, pend, _, snaps, st = paths(root)
    ops = read_json(pend, [])
    if not ops:
        sys.exit("Nothing pending.")
    how = a.tier
    if a.tier == "replay":
        if not (a.before and a.after):
            sys.exit("Replay tier needs --before and --after score files.")
        how += " " + check_replay(a.before, a.after)
    else:
        for i, o in enumerate(ops, 1):
            if o["kind"] != "delete" and not o["user_stated"] and len(o["evidence"]) < 2:
                sys.exit(f"Evidence gate failed for edit #{i}: needs 2+ distinct runs (or --user-stated).")
    lines = les.read_text(encoding="utf-8").splitlines()
    ids = [m.group(1) for line in lines if (m := LESSON_RE.match(line))]
    for o in ops:
        if o["target"] and o["target"] not in ids:
            sys.exit(f"{o['target']} no longer exists; reject that edit.")
    snaps.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    shutil.copy(les, snaps / f"lessons_{stamp}.md")
    nxt = max([int(i[1:]) for i in ids] + [0]) + 1

    def idx(t):
        return next(i for i, line in enumerate(lines) if line.startswith(f"- [{t}]"))

    for o in ops:
        if o["kind"] == "delete":
            lines.pop(idx(o["target"]))
        elif o["kind"] == "replace":
            lines[idx(o["target"])] = fmt(o["target"], o["text"], o["scope"], o["evidence"])
        else:
            lines.append(fmt(f"L{nxt:03d}", o["text"], o["scope"], o["evidence"]))
            nxt += 1
    les.write_text("\n".join(lines) + "\n", encoding="utf-8")
    pend.unlink()
    s = read_json(st, {"cycles": 0})
    s["cycles"] = s.get("cycles", 0) + 1
    s["last_cycle_ledger_count"] = len(ledger(root))
    write_json(st, s)
    print(f"Accepted {len(ops)} edit(s) via the {how} gate. Snapshot lessons_{stamp}.md. Cycle {s['cycles']}.")
    print("Not committed: .evolve/lessons.md is changed in the working tree.")
    if s["cycles"] % 3 == 0:
        print("Slow update due: merge near-duplicates and delete lessons that no recent run supports.")


def cmd_reject(a):
    root = need_root(a.root)
    _, pend, rej, _, _ = paths(root)
    ops = read_json(pend, [])
    if not ops:
        sys.exit("Nothing pending.")
    if a.op and not 1 <= a.op <= len(ops):
        sys.exit(f"--op must be between 1 and {len(ops)}.")
    pick = [ops[a.op - 1]] if a.op else ops
    keep = [o for o in ops if o not in pick]
    reason = " ".join(a.reason.split())
    with open(rej, "a", encoding="utf-8") as f:
        for o in pick:
            f.write(f"- {o['text'] or 'delete ' + str(o['target'])} | reason: {reason}\n")
    if keep:
        write_json(pend, keep)
    else:
        pend.unlink()
    print(f"Rejected {len(pick)} edit(s); recorded in rejected.md.")


def cmd_rollback(a):
    root = need_root(a.root)
    les, _, _, snaps, st = paths(root)
    snaps_list = sorted(snaps.glob("lessons_*.md")) if snaps.exists() else []
    if not snaps_list:
        sys.exit("No snapshots to roll back to.")
    shutil.copy(snaps_list[-1], les)
    snaps_list[-1].unlink()
    s = read_json(st, {"cycles": 0})
    s["cycles"] = max(0, s.get("cycles", 0) - 1)
    write_json(st, s)
    print(f"Rolled back to {snaps_list[-1].name}.")


def cmd_score(a):
    root = need_root(a.root)
    cwd = Path(a.cwd).resolve() if a.cwd else root
    v = read_json(root / EVOLVE / "verifier.json", {"commands": []})
    cmds = v.get("commands") or []
    if a.only:
        want = {n.strip() for n in a.only.split(",")}
        cmds = [c for c in cmds if c["name"] in want]
    if not cmds:
        sys.exit("No verifier commands to run (check verifier.json / --only).")
    results = []
    for c in cmds:
        missing = [t for t in c.get("requires", []) if not shutil.which(t)]
        if missing:
            results.append({"name": c["name"], "status": "skip", "why": f"missing {', '.join(missing)}"})
            continue
        try:
            r = subprocess.run(c["cmd"], shell=True, cwd=cwd, capture_output=True, text=True,
                               errors="replace", timeout=a.timeout)
            res = {"name": c["name"], "status": "ok" if r.returncode == 0 else "fail"}
            if r.returncode != 0:
                res["tail"] = (r.stdout + r.stderr).strip()[-600:]
        except subprocess.TimeoutExpired:
            res = {"name": c["name"], "status": "fail", "tail": f"timeout after {a.timeout}s"}
        results.append(res)
    ran = [r for r in results if r["status"] != "skip"]
    passed = sum(r["status"] == "ok" for r in ran)
    out = {"passed": passed, "total": len(ran), "skipped": len(results) - len(ran),
           "score": round(passed / len(ran), 3) if ran else None, "results": results}
    if a.out:
        write_json(a.out, out)
    print(json.dumps(out, indent=2))


def cmd_status(a):
    root = need_root(a.root)
    les, pend, _, _, st = paths(root)
    s, led = read_json(st, {}), ledger(root)
    print(json.dumps({"lessons": len(lesson_map(les)), "runs": len(led),
                      "new_since_cycle": len(led) - s.get("last_cycle_ledger_count", 0),
                      "cycles": s.get("cycles", 0), "pending": read_json(pend, [])}, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root")
    sp = ap.add_subparsers(dest="c", required=True)
    p = sp.add_parser("propose")
    p.add_argument("--add")
    p.add_argument("--replace")
    p.add_argument("--delete")
    p.add_argument("--evidence")
    p.add_argument("--scope", default="")
    p.add_argument("--user-stated", action="store_true")
    p.set_defaults(f=cmd_propose)
    p = sp.add_parser("accept")
    p.add_argument("--tier", choices=["evidence", "replay"], required=True)
    p.add_argument("--before")
    p.add_argument("--after")
    p.set_defaults(f=cmd_accept)
    p = sp.add_parser("reject")
    p.add_argument("--reason", required=True)
    p.add_argument("--op", type=int)
    p.set_defaults(f=cmd_reject)
    sp.add_parser("rollback").set_defaults(f=cmd_rollback)
    p = sp.add_parser("score")
    p.add_argument("--cwd")
    p.add_argument("--out")
    p.add_argument("--only")
    p.add_argument("--timeout", type=int, default=600)
    p.set_defaults(f=cmd_score)
    sp.add_parser("status").set_defaults(f=cmd_status)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
