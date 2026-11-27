# agent-kit

My AI agents, skills, plugins, scheduled routines and memory in one place. Give this repository to Claude Code, Antigravity, Codex / ChatGPT or another agent, and it can rebuild the same setup in a new account.

**Keep this repository private.** It contains personal details and supervisor contacts.

## Contents

- **Skills** (`skills/`)
  - `phd-copilot`: PhD assistant with deadlines, meetings, papers and the tech radar.
  - `self-evolve`: evidence-gated learning loop for coding projects.
- **Routines** (`routines/`), all run in the cloud:
  - daily deadline scan to calendar reminders, 09:00 IST;
  - Sunday weekly review email, 09:00 IST;
  - tech-radar news brief, 08:00 and 19:00 IST.
- **Plugins** (`plugins/`): ponytail, taste-skill, skins, reflect-mod, the token-saving mods and others. Local-only marketplaces are copied into `plugins/vendor/`.
- **Memory** (`memory/`): who I am, my projects and how I like to work.
- **Ports** (`ports/agents-md/`): versions for tools that use `AGENTS.md` (Antigravity).

## Use on a new machine or account

Tell the agent:

> Read AGENTS.md in this repository and set everything up for me. Ask before overwriting anything.

To do it by hand in Claude Code on Windows, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install.ps1
```

Then connect Gmail, Google Calendar and Google Sheets in the new account, and ask Claude to recreate the routines from `routines/`.

## Keep it up to date

After adding a skill, plugin or routine on this machine:
1. Run `powershell -ExecutionPolicy Bypass -File scripts\sync.ps1`. It refreshes skills, plugins and memory, and runs a secret check.
2. Ask Claude to "export my routines into agent-kit/routines".
3. Commit and push.
