# Instructions for an AI agent setting up this kit

You are an AI coding agent: Claude Code, Codex / ChatGPT, Antigravity, Gemini CLI, Cursor or similar. The owner gave you this repository so you can rebuild their agents, skills and plugins on a new machine or account.

Work through the steps below. Ask before anything that overwrites, deletes, sends or creates an account.

## What is here

| Folder | Content | Portable? |
|---|---|---|
| `skills/` | Agent Skills: folders with `SKILL.md` (YAML `name` + `description`, then instructions) plus `references/` and `scripts/` | Yes. `SKILL.md` is the open Agent Skills format |
| `ports/agents-md/` | The same skills already adapted to the `AGENTS.md` / `.agents/` layout (used for Antigravity) | Yes |
| `routines/` | Scheduled cloud agents: `routines.json` (schedule, model, connectors, tools) and one prompt `.md` each | The prompts are plain text; the scheduler differs per tool |
| `plugins/plugins.json` | Claude Code plugins that were enabled, and their marketplaces | Claude Code only |
| `plugins/vendor/` | Plugin marketplaces that existed only on the old disk, copied here so they can be installed | Claude Code only |
| `memory/` | The owner's profile, projects and working preferences (one fact per file) | Yes. Load it as context or as user memory |
| `scripts/install.ps1` | Installer for Claude Code on Windows | Claude Code |
| `scripts/sync.ps1` | Refreshes this repo from the old machine | Claude Code |

## Steps

1. **Read `memory/MEMORY.md` and the files it links.** That is who the owner is and how they want you to work. Two rules are non-negotiable:
   - never delete, trash or overwrite without asking first;
   - emails to anyone other than the owner are drafts only.
2. **Install the skills.**
   - **Claude Code:** run `scripts/install.ps1`. It copies `skills/*` to `~/.claude/skills/` and skips any skill that already exists.
   - **A tool that supports Agent Skills (`SKILL.md` folders):** copy each `skills/<name>/` folder into that tool's skills directory. Check the tool's current docs for the path; don't guess.
   - **A tool that uses `AGENTS.md` / rules files** (Antigravity, Codex, Cursor): use `ports/agents-md/<name>/` where it exists. Otherwise add the body of `SKILL.md` as a project or global rule, keeping `references/` next to it and fixing the relative paths.
   - **A chat product without skills** (ChatGPT custom GPT / project, Claude.ai project): paste the `SKILL.md` body into the custom instructions and upload the `references/` files as knowledge.
3. **Plugins (Claude Code only).**
   - For each marketplace in `plugins/plugins.json`, run `claude plugin marketplace add <github repo or git url>`.
   - For `directory` marketplaces, use `plugins/vendor/<name>` instead of the old disk path.
   - Then run `claude plugin install <plugin>@<marketplace>` for each enabled plugin. `install.ps1` does all of this when the `claude` CLI is on PATH.
   - Other tools: tell the owner which plugins have no equivalent. Don't try to emulate hooks.
4. **Connectors.** The routines need Gmail, Google Calendar and Google Sheets, and optionally Microsoft 365. The owner must connect these themselves in the new account (OAuth). Never ask for passwords or tokens.
5. **Routines.**
   - **Claude Code:** use `/schedule` (or the RemoteTrigger tool) for each entry in `routines/routines.json`, with the prompt from its `.md` file, the same cron (UTC) and the listed connectors and tools.
   - **Other tools:** use their scheduled-task feature with the same prompt and schedule.
   - Show the owner each routine before creating it.
6. **Report** what you installed, what you skipped and what the owner still has to do (connectors, sign-ins).

## Safety

- The routine prompts and `memory/` contain personal and academic details. Keep this repository **private**.
- Third-party plugins under `plugins/vendor/` keep their own licences. Don't publish them.
