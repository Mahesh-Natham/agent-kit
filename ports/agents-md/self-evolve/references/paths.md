# Antigravity locations (documentation conflicts; verify on your install)

Sources disagree and differ between the IDE and the CLI (`agy`), so install.sh places the skill in every plausible location and you verify after restart.

| Scope | Candidate path |
|---|---|
| Project (current docs, older docs) | `.agents/skills/<name>/SKILL.md`, `.agent/skills/<name>/SKILL.md` |
| Cross-client shared | `~/.agents/skills/<name>/SKILL.md` |
| IDE global (codelab) | `~/.gemini/antigravity/skills/<name>/` |
| CLI global | `~/.gemini/antigravity-cli/skills/<name>/` |
| Shared across Antigravity products (one report) | `~/.gemini/skills/<name>/` |
| Other report | `~/.gemini/config/skills/<name>/` (scanned one level deep; point symlinks at the folder containing SKILL.md) |
| Global rules | `~/.gemini/GEMINI.md` (read by CLI and IDE) |
| Project rules | `AGENTS.md` or `GEMINI.md` (CLI), `.agents/rules/*.md` (IDE 2.0) |

One report says the CLI may expect flat markdown files (`skills/<name>.md`). If the CLI does not list the skill after install, copy `SKILL.md` to `<dir>/self-evolve.md` as well.

Verify: restart the session, then ask the agent "list your available skills" and confirm `self-evolve` appears.
