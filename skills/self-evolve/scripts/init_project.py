#!/usr/bin/env python3
"""Create .evolve/ state and guess verifier commands. Runs none of them.

  init_project.py [--root DIR]            create state (idempotent)
  init_project.py --link-claude-md        also add the @.evolve/lessons.md import to CLAUDE.md
"""
import argparse
import json
from pathlib import Path

from _common import EVOLVE, project_root, write_json

LESSONS_HEADER = (
    "# Project lessons (self-evolve)\n"
    "<!-- Managed by .claude/skills/self-evolve/scripts/gate.py: evidence-gated, max 40, do not hand-edit. -->\n"
)
IMPORT_BLOCK = (
    "\n## Learned lessons\n\n"
    "Evidence-gated lessons from the `self-evolve` skill (change them only through its `gate.py`):\n\n"
    "@.evolve/lessons.md\n"
)


def has_tests(root):
    if (root / "tests").is_dir() or (root / "pytest.ini").exists():
        return True
    skip = {".git", "node_modules", ".venv", "venv", "__pycache__"}
    for p in root.rglob("test_*.py"):
        if not skip & set(p.parts):
            return True
    return False


def detect(root: Path):
    cmds = []

    def add(name, cmd, requires=None):
        c = {"name": name, "cmd": cmd}
        if requires:
            c["requires"] = requires
        cmds.append(c)

    pj = root / "package.json"
    if pj.exists():
        try:
            scripts = json.loads(pj.read_text(encoding="utf-8")).get("scripts", {})
        except Exception:
            scripts = {}
        for n in ("lint", "typecheck", "build", "test"):
            if n in scripts:
                add(n, "npm test" if n == "test" else f"npm run {n}", ["npm"])
    pyproject = root / "pyproject.toml"
    py_txt = pyproject.read_text(encoding="utf-8", errors="ignore") if pyproject.exists() else ""
    if "[tool.ruff" in py_txt or (root / "ruff.toml").exists():
        add("lint", "ruff check .", ["ruff"])
    if has_tests(root):
        add("test", "python -m pytest -q", ["python"])
    if (root / "Cargo.toml").exists():
        add("build", "cargo build", ["cargo"])
        add("test", "cargo test", ["cargo"])
    if (root / "go.mod").exists():
        add("build", "go build ./...", ["go"])
        add("test", "go test ./...", ["go"])
    if (root / "platformio.ini").exists():
        add("build", "pio run", ["pio"])
    elif (root / "CMakeLists.txt").exists():
        add("build", "cmake -S . -B build && cmake --build build", ["cmake"])
    mk = root / "Makefile"
    if mk.exists():
        txt = "\n" + mk.read_text(encoding="utf-8", errors="ignore")
        for t in ("test", "lint", "all"):
            if f"\n{t}:" in txt:
                add("build" if t == "all" else t, f"make {t}", ["make"])
    seen, out = set(), []
    for c in cmds:
        if c["cmd"] not in seen:
            seen.add(c["cmd"])
            out.append(c)
    return out


def link_claude_md(root):
    f = root / "CLAUDE.md"
    txt = f.read_text(encoding="utf-8") if f.exists() else ""
    if "@.evolve/lessons.md" in txt:
        print("CLAUDE.md already imports .evolve/lessons.md")
        return
    new = txt.rstrip("\n") + "\n" + IMPORT_BLOCK if txt.strip() else IMPORT_BLOCK.lstrip("\n")
    f.write_text(new, encoding="utf-8")
    print(f"Added @.evolve/lessons.md import to {f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--link-claude-md", action="store_true")
    a = ap.parse_args()
    root = Path(a.root).resolve() if a.root else project_root()
    d = root / EVOLVE
    (d / "snapshots").mkdir(parents=True, exist_ok=True)
    if not (d / "lessons.md").exists():
        (d / "lessons.md").write_text(LESSONS_HEADER, encoding="utf-8")
    for name in ("ledger.jsonl", "rejected.md"):
        (d / name).touch()
    if not (d / "state.json").exists():
        write_json(d / "state.json", {"last_cycle_ledger_count": 0, "cycles": 0})
    (d / ".gitignore").write_text("ledger.jsonl\nsnapshots/\npending.json\nstate.json\nscore*.json\n", encoding="utf-8")
    if not (d / "verifier.json").exists():
        write_json(d / "verifier.json", {"confirmed": False, "commands": detect(root)})
    if a.link_claude_md:
        link_claude_md(root)
    v = json.loads((d / "verifier.json").read_text(encoding="utf-8"))
    print(f"Initialised {d}")
    state = "confirmed" if v.get("confirmed") else "guessed, NOT confirmed, nothing was run"
    print(f"Verifier commands ({state}):")
    for c in v.get("commands") or []:
        req = f"  [needs {', '.join(c['requires'])}]" if c.get("requires") else ""
        print(f"  - {c['name']}: {c['cmd']}{req}")
    if not v.get("commands"):
        print("  (none found: ask the user for build/test commands and edit verifier.json)")


if __name__ == "__main__":
    main()
