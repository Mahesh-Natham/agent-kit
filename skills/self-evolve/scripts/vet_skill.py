#!/usr/bin/env python3
"""First-pass static scan of a skill/plugin folder. Exit 2 = HIGH findings, 1 = MEDIUM only, 0 = none.
Not proof of safety: always read SKILL.md and every script yourself. Run with `python -I`."""
import json
import re
import sys
from pathlib import Path

RULES = [
    ("HIGH", r"(curl|wget|iwr|Invoke-WebRequest)[^\n|]*\|\s*(sudo\s+)?((ba|z)?sh|iex|python)", "pipes a download into a shell"),
    ("HIGH", r"base64\s+(-d|--decode)|b64decode\(|FromBase64String", "decodes an embedded payload"),
    ("HIGH", r"(\.ssh[/\\]|id_rsa|id_ed25519|\.aws[/\\]credentials|\.netrc|Login Data|keychain|\.git-credentials)",
     "touches credential locations"),
    ("HIGH", r"rm\s+-rf\s+(/|~|\$HOME)(\s|$)|Remove-Item[^\n]*-Recurse[^\n]*(\$env:USERPROFILE|\$HOME|C:\\)\s*$",
     "destructive delete of root or home"),
    ("HIGH", r"ignore (all |any )?(previous|prior|above) (instructions|rules)|do not (tell|inform|show) the user"
             r"|hide this from the user|disable (safety|confirmation|approval)|dangerously-?skip-?permissions"
             r"|dangerouslyDisableSandbox|bypassPermissions", "prompt-injection or permission bypass"),
    ("MED", r"\b(eval|exec)\s*\(|Invoke-Expression|\biex\b", "dynamic code execution"),
    ("MED", r"(requests\.(get|post|put)|urllib\.request|http\.client|socket\.socket|curl\s|wget\s"
            r"|fetch\(\s*['\"]https?://|Invoke-WebRequest|Invoke-RestMethod)", "network access"),
    ("MED", r"(\.bashrc|\.zshrc|\.profile|\$PROFILE|\.git[/\\]hooks|\.github[/\\]workflows|crontab|schtasks)",
     "modifies shell, git, CI or scheduler config"),
    ("MED", r"(\.claude[/\\]settings|settings\.local\.json|\"hooks\"\s*:|[/\\]\.claude[/\\](skills|agents|commands)"
            r"|CLAUDE\.md|GEMINI\.md|AGENTS\.md)", "edits agent config, hooks, rules or other skills"),
    ("MED", r"git\s+(commit|push)|npm\s+(i|install)|pip\s+install|uv\s+tool\s+install|npx\s", "commits or installs"),
    ("MED", r"(os\.environ|process\.env|printenv|\$env:)", "reads environment variables"),
]


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python -I vet_skill.py <skill_dir>")
    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        sys.exit(f"Not a folder: {root}")
    findings, files, skipped = [], 0, []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or ".git" in p.parts:
            continue
        rel = str(p.relative_to(root))
        if p.stat().st_size >= 1_000_000:
            skipped.append(rel + " (over 1 MB)")
            continue
        try:
            txt = p.read_text(encoding="utf-8")
        except Exception:
            skipped.append(rel + " (binary or not UTF-8)")
            continue
        files += 1
        for sev, rx, why in RULES:
            for m in re.finditer(rx, txt, re.I):
                ln = txt.count("\n", 0, m.start()) + 1
                findings.append({"severity": sev, "file": rel, "line": ln, "why": why, "match": m.group(0)[:80]})
    scripts = [str(p.relative_to(root)) for p in root.rglob("*")
               if p.is_file() and p.suffix.lower() in {".py", ".sh", ".ps1", ".bat", ".cmd", ".js", ".ts", ".mjs"}]
    print(json.dumps({"files_scanned": files, "not_scanned": skipped, "scripts": scripts,
                      "findings": findings}, indent=2))
    sys.exit(2 if any(f["severity"] == "HIGH" for f in findings) else 1 if findings else 0)


if __name__ == "__main__":
    main()
