#!/usr/bin/env python3
"""First-pass static scan of a skill folder. Exit 2 = HIGH findings, 1 = MEDIUM, 0 = clean. Not proof of safety."""
import re, sys, json
from pathlib import Path

RULES = [
 ("HIGH", r"(curl|wget)[^\n|]*\|\s*(sudo\s+)?(ba|z)?sh", "pipes a download into a shell"),
 ("HIGH", r"base64\s+(-d|--decode)|b64decode\(", "decodes an embedded payload"),
 ("HIGH", r"(\.ssh/|id_rsa|\.aws/credentials|\.netrc|Login Data|keychain)", "touches credential locations"),
 ("HIGH", r"rm\s+-rf\s+(/|~|\$HOME)(\s|$)", "destructive delete of root or home"),
 ("HIGH", r"ignore (all |any )?(previous|prior|above) (instructions|rules)|do not (tell|inform|show) the user|hide this from the user|disable (safety|confirmation|approval)", "prompt-injection style instruction"),
 ("MED",  r"\b(eval|exec)\s*\(", "dynamic code execution"),
 ("MED",  r"(requests\.(post|put)|urllib\.request|curl\s+[^\n]*(-d|--data|-F)|fetch\(\s*['\"]https?://)", "sends or fetches over the network"),
 ("MED",  r"(\.bashrc|\.zshrc|\.profile|\.git/hooks|\.github/workflows|crontab)", "modifies shell, git or CI config"),
 ("MED",  r"(os\.environ|process\.env|printenv|\benv\b\s*\|)", "reads environment variables"),
]

def main():
    if len(sys.argv) != 2: sys.exit("usage: vet_skill.py <skill_dir>")
    root = Path(sys.argv[1]); findings = []; files = 0
    for p in root.rglob("*"):
        if p.is_file() and p.stat().st_size < 1_000_000 and ".git" not in p.parts:
            try: txt = p.read_text(encoding="utf-8")
            except Exception: continue
            files += 1
            for sev, rx, why in RULES:
                for m in re.finditer(rx, txt, re.I):
                    ln = txt.count("\n", 0, m.start()) + 1
                    findings.append({"severity": sev, "file": str(p.relative_to(root)), "line": ln, "why": why})
    has_scripts = any((root / "scripts").glob("*")) if (root / "scripts").exists() else False
    print(json.dumps({"files_scanned": files, "ships_scripts": has_scripts, "findings": findings}, indent=2))
    sys.exit(2 if any(f["severity"] == "HIGH" for f in findings) else 1 if findings else 0)

if __name__ == "__main__":
    main()
