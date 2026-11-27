#!/usr/bin/env bash
# Install self-evolve for Antigravity (IDE + CLI). Usage:
#   bash install.sh              global install (all projects)
#   bash install.sh --project    install into the current project only
#   bash install.sh --uninstall  remove global copies and the GEMINI.md rule
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME=self-evolve
SNIP="$SRC/assets/agents-md-snippet.md"
MODE="${1:-global}"

add_block() {  # file
  mkdir -p "$(dirname "$1")"; touch "$1"
  if grep -q "self-evolve:begin" "$1"; then echo "  rule already present in $1"; else
    { echo; cat "$SNIP"; } >> "$1"; echo "  rule added to $1"; fi
}
rm_block() {
  [ -f "$1" ] && python3 - "$1" <<'PY'
import re,sys
p=sys.argv[1]; s=open(p,encoding="utf-8").read()
open(p,"w",encoding="utf-8").write(re.sub(r"\n?<!-- self-evolve:begin -->.*?<!-- self-evolve:end -->\n?","",s,flags=re.S))
PY
}
copy_to() {  # dest parent dir
  mkdir -p "$1"; rm -rf "$1/$NAME"; cp -R "$SRC" "$1/$NAME"
  rm -rf "$1/$NAME/__pycache__" "$1/$NAME/scripts/__pycache__"; echo "  installed -> $1/$NAME"
}

GLOBAL_DIRS=("$HOME/.agents/skills" "$HOME/.gemini/antigravity/skills" "$HOME/.gemini/antigravity-cli/skills" "$HOME/.gemini/skills" "$HOME/.gemini/config/skills")

case "$MODE" in
  --uninstall)
    for d in "${GLOBAL_DIRS[@]}"; do rm -rf "$d/$NAME" && echo "  removed $d/$NAME"; done
    rm_block "$HOME/.gemini/GEMINI.md"; echo "Uninstalled. Project state in .agents/evolve/ was left untouched." ;;
  --project)
    copy_to "./.agents/skills"; add_block "./AGENTS.md"
    echo "Project install done. Restart the agent session, then ask it to list its skills." ;;
  *)
    echo "Global install (copies, not symlinks, because some scanners skip symlinks):"
    copy_to "$HOME/.agents/skills"
    if [ -d "$HOME/.gemini" ]; then
      for d in "${GLOBAL_DIRS[@]:1}"; do copy_to "$d"; done
    else
      echo "  ~/.gemini not found: Antigravity has not been run on this machine yet."
      echo "  Run Antigravity once, then re-run this script to copy into its folders."
    fi
    add_block "$HOME/.gemini/GEMINI.md"
    echo "Done. Restart Antigravity (IDE and CLI), then ask: 'list your available skills'."
    echo "If the CLI does not list it, see references/paths.md (flat-file variant)." ;;
esac
