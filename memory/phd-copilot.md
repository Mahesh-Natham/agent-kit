---
name: phd-copilot
description: "The PhD co-pilot agent built 2026-11-19 — skill location, two cloud routines, never-delete rule, Outlook via M365 connector pending"
metadata:
  node_type: memory
  type: project
  originSessionId: 542d8779-6129-4bf1-bea4-e544fc020f00
  modified: 2026-11-27T16:45:50.580Z
---

Skill `phd-copilot` lives at `C:\Users\mahes\.claude\skills\phd-copilot` (packaged copy: `D:\Ph.D 2026-2027\Extra\phd-copilot.skill`). Uses the Command Center sheet `1EQhgXFWA8MRJCgLbdHtVmNkvTTZa5Iwi765dqSZJLQo` as source of truth.

Cloud routines (run with laptop off, Default cloud env, Sonnet 5.5):
- `trig_014Q68zZiiKQ1wn3KbDg7SCk` daily 09:00 IST: mail + sheet scan → `[PhD]` Google Calendar events with phone reminders. Never sends email.
- `trig_01JWF6SGMzud2F7f2eHjVm5T` Sunday 09:00 IST: weekly review email to his own address only.

- `trig_01NHKsCuBir8wL6P5fYRALti` daily 08:00 + 19:00 IST (cron `30 2,13 * * *`): tech-radar news brief (AI agents, ML, dev tools, EV, power electronics, autonomy, startups, career), emailed to himself and appended to the Command Center `Tech_Radar` tab (sheetId 357748855, header row 7). Skill reference: `references/tech-radar.md`. Added 2026-11-27.

**Why:** user wants continuous PhD help, reminders even when laptop is off, and NEVER deletion without asking.
**How to apply:** ask before any delete/trash/overwrite; emails to others are drafts only. Outlook: user chose the Microsoft 365 connector — once connected, add it to both routines (RemoteTrigger update mcp_connections). When in France (Feb–Jul), 09:00 IST = 04:30 Paris — offer to shift times. See [[user-phd-profile]].
