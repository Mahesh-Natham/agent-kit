"""Shared helpers for self-evolve scripts (stdlib only)."""
import json, os, re, sys
from pathlib import Path

EVOLVE = ".agents/evolve"
SECRET_RE = re.compile(
    r"(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|(?i:api[_-]?key|token|secret|password)\s*[:=]\s*\S+)")

def find_root(start=None):
    p = Path(start or os.getcwd()).resolve()
    for d in [p, *p.parents]:
        if (d / EVOLVE).is_dir():
            return d
    return None

def need_root(start=None):
    r = find_root(start)
    if not r:
        sys.exit("No .agents/evolve/ found. Run scripts/init_project.py --root . first.")
    return r

def read_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default

def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")

def ledger(root):
    out = []
    f = root / EVOLVE / "ledger.jsonl"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try: out.append(json.loads(line))
                except Exception: pass
    return out
