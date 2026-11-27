#!/usr/bin/env python3
"""Create .agents/evolve/ state and detect verifier commands. Runs nothing."""
import argparse, json
from pathlib import Path
from _common import EVOLVE, write_json

def detect(root: Path):
    cmds = []
    add = lambda n, c: cmds.append({"name": n, "cmd": c})
    pj = root / "package.json"
    if pj.exists():
        try:
            scripts = json.loads(pj.read_text(encoding="utf-8")).get("scripts", {})
        except Exception:
            scripts = {}
        for n in ("test", "lint", "typecheck", "build"):
            if n in scripts:
                add(n, f"npm run {n}" if n != "test" else "npm test")
    if (root / "pyproject.toml").exists() or (root / "pytest.ini").exists() or (root / "tests").is_dir():
        add("test", "python -m pytest -q")
    if (root / "Cargo.toml").exists():
        add("build", "cargo build"); add("test", "cargo test")
    if (root / "go.mod").exists():
        add("build", "go build ./..."); add("test", "go test ./...")
    if (root / "platformio.ini").exists():
        add("build", "pio run")
    if (root / "CMakeLists.txt").exists() and not (root / "platformio.ini").exists():
        add("build", "cmake -S . -B build && cmake --build build")
    mk = root / "Makefile"
    if mk.exists():
        txt = mk.read_text(encoding="utf-8", errors="ignore")
        for t in ("test", "lint", "all"):
            if f"\n{t}:" in "\n" + txt:
                add(t if t != "all" else "build", f"make {t}")
    seen, out = set(), []
    for c in cmds:
        if c["cmd"] not in seen:
            seen.add(c["cmd"]); out.append(c)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    d = root / EVOLVE
    (d / "snapshots").mkdir(parents=True, exist_ok=True)
    if not (d / "lessons.md").exists():
        (d / "lessons.md").write_text(
            "# Lessons (managed by self-evolve gate.py; max 40 lines; do not hand-edit)\n", encoding="utf-8")
    for f in ("ledger.jsonl", "rejected.md"):
        (d / f).touch()
    if not (d / "verifier.json").exists():
        write_json(d / "verifier.json", {"confirmed": False, "commands": detect(root)})
    write_json(d / "state.json", {"last_cycle_ledger_count": 0, "cycles": 0}) if not (d / "state.json").exists() else None
    (d / ".gitignore").write_text("ledger.jsonl\nsnapshots/\npending.json\nstate.json\n", encoding="utf-8")
    v = json.loads((d / "verifier.json").read_text())
    print(f"Initialised {d}")
    print("Detected verifier commands (NOT confirmed, nothing was run):")
    for c in v["commands"] or []:
        print(f"  - {c['name']}: {c['cmd']}")
    if not v["commands"]:
        print("  (none detected: ask the user for a build/test command and edit verifier.json)")

if __name__ == "__main__":
    main()
