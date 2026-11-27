#!/usr/bin/env python3
"""Validation gate for lessons.md: propose / accept / reject / rollback / score / promote / status."""
import argparse, datetime, json, re, shutil, subprocess, sys
from pathlib import Path
from _common import EVOLVE, SECRET_RE, need_root, ledger, read_json, write_json

MAX_OPS, MAX_LINES, MAX_CHARS = 3, 40, 300

def toks(s): return set(re.findall(r"[a-z0-9_./-]{3,}", s.lower()))
def jac(a, b):
    a, b = toks(a), toks(b)
    return len(a & b) / len(a | b) if a and b else 0.0

def lesson_lines(p):
    return [l for l in p.read_text(encoding="utf-8").splitlines() if re.match(r"\[L\d+\]", l)]

def body(line):  # lesson text without id/scope/ev
    line = re.sub(r"^\[L\d+\]\s*", "", line)
    return re.split(r"\s\|\sscope:", line)[0]

def fmt(lid, text, scope, ev):
    return f"[{lid}] {text} | scope: {scope or '**'} | ev: {','.join(ev) if ev else 'user-stated'}"

def paths(root):
    d = root / EVOLVE
    return d, d / "lessons.md", d / "pending.json", d / "rejected.md", d / "snapshots", d / "state.json"

def cmd_propose(a):
    root = need_root(a.root); d, les, pend, rej, snaps, st = paths(root)
    ops = read_json(pend, [])
    if len(ops) >= MAX_OPS:
        sys.exit(f"Budget reached: max {MAX_OPS} edits per cycle. Accept or reject pending first.")
    kind = "add" if a.add and not a.replace else "replace" if a.replace and a.add else "delete" if a.delete else None
    if not kind: sys.exit("Use --add TEXT, --replace ID --add TEXT, or --delete ID.")
    cur = lesson_lines(les)
    ids = {re.match(r"\[(L\d+)\]", l).group(1): l for l in cur}
    target = a.replace or a.delete
    if target and target not in ids: sys.exit(f"Unknown lesson {target}.")
    if kind != "delete":
        t = a.add.strip()
        if "\n" in t or len(t) > MAX_CHARS: sys.exit(f"Lesson must be one line, <= {MAX_CHARS} chars.")
        if SECRET_RE.search(t): sys.exit("Rejected: text looks like a secret.")
        known = {e["id"] for e in ledger(root)}
        ev = [e for e in (a.evidence or "").split(",") if e]
        missing = [e for e in ev if e not in known]
        if missing: sys.exit(f"Unknown evidence run IDs: {missing}")
        if not ev and not a.user_stated: sys.exit("Evidence required: --evidence R0001,R0002 (or --user-stated if the user dictated the rule).")
        others = [body(l) for k, l in ids.items() if k != target]
        rej_lines = [l for l in rej.read_text(encoding="utf-8").splitlines() if l.startswith("- ")]
        for o in others:
            if jac(t, o) >= 0.6: sys.exit(f"Near-duplicate of existing lesson: {o}")
        for r in rej_lines:
            if jac(t, r) >= 0.6: sys.exit(f"Similar edit was rejected before: {r}")
    projected = len(cur) + (1 if kind == "add" else -1 if kind == "delete" else 0) + sum(
        1 if o["kind"] == "add" else -1 if o["kind"] == "delete" else 0 for o in ops)
    if projected > MAX_LINES: sys.exit(f"Would exceed {MAX_LINES} lessons. Propose a --delete or --replace first.")
    op = {"kind": kind, "target": target, "text": (a.add or "").strip(), "scope": a.scope,
          "evidence": [e for e in (a.evidence or "").split(",") if e], "user_stated": a.user_stated}
    ops.append(op); write_json(pend, ops)
    print(f"Pending op #{len(ops)}: {kind} {target or ''} {op['text'][:80]}\nNext: validate (tier evidence or replay), then `gate.py accept`.")

def git_commit(root, msg):
    try:
        if subprocess.run(["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"], capture_output=True).returncode == 0:
            subprocess.run(["git", "-C", str(root), "add", "-f", f"{EVOLVE}/lessons.md", f"{EVOLVE}/verifier.json"], capture_output=True)
            subprocess.run(["git", "-C", str(root), "commit", "-m", msg, "--", f"{EVOLVE}/lessons.md", f"{EVOLVE}/verifier.json"], capture_output=True)
    except Exception:
        pass

def cmd_accept(a):
    root = need_root(a.root); d, les, pend, rej, snaps, st = paths(root)
    ops = read_json(pend, [])
    if not ops: sys.exit("Nothing pending.")
    if a.tier == "replay":
        if a.before is None or a.after is None or not (a.after > a.before):
            sys.exit("Replay gate failed: need --before and --after with after strictly greater than before.")
    else:
        for i, o in enumerate(ops, 1):
            if o["kind"] != "delete" and not o["user_stated"] and len(set(o["evidence"])) < 2:
                sys.exit(f"Evidence gate failed for op #{i}: needs 2+ distinct runs (or --user-stated).")
    snaps.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    shutil.copy(les, snaps / f"lessons_{stamp}.md")
    lines = les.read_text(encoding="utf-8").splitlines()
    nums = [int(m.group(1)) for l in lines if (m := re.match(r"\[L(\d+)\]", l))]
    nxt = max(nums + [0]) + 1
    def idx(t): return next(i for i, l in enumerate(lines) if l.startswith(f"[{t}]"))
    for o in ops:
        if o["kind"] == "delete": lines.pop(idx(o["target"]))
        elif o["kind"] == "replace":
            lines[idx(o["target"])] = fmt(o["target"], o["text"], o["scope"], o["evidence"])
        else:
            lines.append(fmt(f"L{nxt:03d}", o["text"], o["scope"], o["evidence"])); nxt += 1
    les.write_text("\n".join(lines) + "\n", encoding="utf-8")
    pend.unlink()
    s = read_json(st, {"cycles": 0}); s["cycles"] = s.get("cycles", 0) + 1
    s["last_cycle_ledger_count"] = len(ledger(root)); write_json(st, s)
    git_commit(root, f"self-evolve: accept {len(ops)} lesson edit(s) via {a.tier} gate")
    print(f"Accepted {len(ops)} edit(s) via {a.tier} gate. Snapshot: lessons_{stamp}.md. Cycle {s['cycles']}.")
    if s["cycles"] % 3 == 0: print("Slow update due: merge near-duplicates and delete lessons with no recent supporting runs.")

def cmd_reject(a):
    root = need_root(a.root); d, les, pend, rej, snaps, st = paths(root)
    ops = read_json(pend, [])
    if not ops: sys.exit("Nothing pending.")
    pick = [ops[a.op - 1]] if a.op else ops
    keep = [o for o in ops if o not in pick]
    with open(rej, "a", encoding="utf-8") as f:
        for o in pick: f.write(f"- {o['text'] or 'delete ' + str(o['target'])} | reason: {a.reason}\n")
    if keep: write_json(pend, keep)
    else: pend.unlink()
    print(f"Rejected {len(pick)} edit(s); recorded in rejected.md.")

def cmd_rollback(a):
    root = need_root(a.root); d, les, pend, rej, snaps, st = paths(root)
    s = sorted(snaps.glob("lessons_*.md")) if snaps.exists() else []
    if not s: sys.exit("No snapshots.")
    shutil.copy(s[-1], les); s[-1].unlink()
    git_commit(root, "self-evolve: rollback last lesson change")
    print("Rolled back to previous snapshot.")

def cmd_score(a):
    root = need_root(a.root); cwd = Path(a.cwd).resolve() if a.cwd else root
    v = read_json(root / EVOLVE / "verifier.json", {"commands": []})
    if not v.get("commands"): sys.exit("No verifier commands configured.")
    res, passed = [], 0
    for c in v["commands"]:
        try:
            r = subprocess.run(c["cmd"], shell=True, cwd=cwd, capture_output=True, text=True, timeout=a.timeout)
            ok = r.returncode == 0
        except subprocess.TimeoutExpired:
            ok = False
        passed += ok; res.append({"name": c["name"], "ok": ok})
    out = {"passed": passed, "total": len(res), "score": round(passed / len(res), 3), "results": res}
    print(json.dumps(out))

def cmd_promote(a):
    root = need_root(a.root); les = root / EVOLVE / "lessons.md"
    line = next((l for l in lesson_lines(les) if l.startswith(f"[{a.id}]")), None)
    if not line: sys.exit("Unknown lesson.")
    g = Path.home() / ".agents" / "evolve" / "global-lessons.md"
    g.parent.mkdir(parents=True, exist_ok=True)
    if not g.exists(): g.write_text("# Global lessons (promoted from projects with user approval)\n", encoding="utf-8")
    t = body(line)
    if any(jac(t, body(x)) >= 0.6 for x in g.read_text(encoding="utf-8").splitlines() if x.startswith("- ")):
        sys.exit("Already present in global lessons.")
    with open(g, "a", encoding="utf-8") as f: f.write(f"- {t}\n")
    print(f"Promoted {a.id} to {g}")

def cmd_status(a):
    root = need_root(a.root); d, les, pend, rej, snaps, st = paths(root)
    s = read_json(st, {}); led = ledger(root)
    print(json.dumps({"lessons": len(lesson_lines(les)), "ledger": len(led),
          "new_since_cycle": len(led) - s.get("last_cycle_ledger_count", 0),
          "cycles": s.get("cycles", 0), "pending": len(read_json(pend, []))}))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--root")
    sp = ap.add_subparsers(dest="c", required=True)
    p = sp.add_parser("propose"); p.add_argument("--add"); p.add_argument("--replace"); p.add_argument("--delete")
    p.add_argument("--evidence"); p.add_argument("--scope", default=""); p.add_argument("--user-stated", action="store_true"); p.set_defaults(f=cmd_propose)
    p = sp.add_parser("accept"); p.add_argument("--tier", choices=["evidence", "replay"], required=True)
    p.add_argument("--before", type=float); p.add_argument("--after", type=float); p.set_defaults(f=cmd_accept)
    p = sp.add_parser("reject"); p.add_argument("--reason", required=True); p.add_argument("--op", type=int); p.set_defaults(f=cmd_reject)
    sp.add_parser("rollback").set_defaults(f=cmd_rollback)
    p = sp.add_parser("score"); p.add_argument("--cwd"); p.add_argument("--timeout", type=int, default=600); p.set_defaults(f=cmd_score)
    p = sp.add_parser("promote"); p.add_argument("id"); p.set_defaults(f=cmd_promote)
    sp.add_parser("status").set_defaults(f=cmd_status)
    a = ap.parse_args(); a.f(a)

if __name__ == "__main__":
    main()
