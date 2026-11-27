"""Shared helpers for the self-evolve scripts (standard library only)."""
import json
import os
import re
import sys
from pathlib import Path

EVOLVE = ".evolve"
MAX_OPS, MAX_LESSONS, MAX_CHARS = 3, 40, 300
LESSON_RE = re.compile(r"^- \[(L\d+)\]\s*")
SECRET_RE = re.compile(
    r"(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}"
    r"|xox[abprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|(?i:api[_-]?key|token|secret|passw(?:or)?d)\s*[:=]\s*\S{6,})")

# Lesson text can contain non-ASCII; never crash on a cp1252 Windows console.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(errors="replace")
    except Exception:
        pass


def find_up(marker, start=None):
    p = Path(start or os.getcwd()).resolve()
    for d in [p, *p.parents]:
        if (d / marker).exists():
            return d
    return None


def need_root(start=None):
    r = find_up(EVOLVE, start)
    if not r:
        sys.exit("No .evolve/ folder found. Run init_project.py first.")
    return r


def project_root(start=None):
    """Repo root (folder with .git), else the given/current folder."""
    base = Path(start or os.getcwd()).resolve()
    return find_up(".git", base) or base


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
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    return out


def next_run_id(entries):
    nums = [int(e["id"][1:]) for e in entries if re.fullmatch(r"R\d+", str(e.get("id", "")))]
    return f"R{max(nums + [0]) + 1:04d}"
