# Evolution loop (SkillOpt-style, adapted for an IDE agent)

Mapping from SkillOpt (Microsoft Research) to this skill:

| SkillOpt idea | Here |
|---|---|
| Frozen model, trainable skill text | Frozen Antigravity model; trainable `lessons.md` |
| Scored rollouts | Ledger entries with verifier scores |
| Reflect on success vs failure batches | Evolve cycle step 1 |
| Bounded add/delete/replace edits ("learning rate") | Max 3 edits per cycle, 40-line cap |
| Accept only if a held-out score improves | Tier 1 evidence gate, Tier 2 replay gate |
| Rejected-edit buffer | `rejected.md`, checked by `gate.py propose` |
| Slow / epoch update | Every 3rd cycle: merge near-duplicates, delete lessons with no supporting runs in the last 20 entries |
| Deployed artifact is one compact file | `lessons.md` only; no optimizer memory loaded at runtime |

## Writing a good lesson
Format: `[L012] When <trigger>, do <action> (because <observed failure/success>). scope: <glob> | ev: R0003,R0007`
- Trigger and action must be checkable, e.g. "When editing files under `firmware/`, run `make -C firmware` before declaring done."
- Prefer project facts (commands, conventions, pitfalls) over generic advice the model already knows.
- One idea per line. If a lesson needs a paragraph, it belongs in a `references/` file of a project skill, not here.

## Replay gate (Tier 2)
1. Pick 1 to 3 past `fail` or `corrected` runs whose task can be re-run and scored by `verifier.json`.
2. `git worktree add ../replay-base <commit-before-task>` and `../replay-cand`.
3. Run the task in `replay-base` with current lessons and in `replay-cand` with candidate lessons (same prompt).
4. `python3 scripts/gate.py score --cwd ../replay-base` and `--cwd ../replay-cand`.
5. Accept only if candidate score is strictly higher and no previously passing check regressed. Remove the worktrees afterwards.
Skip Tier 2 if replay would cost more than the lesson is worth; Tier 1 is then the ceiling.

## Optional Tier 3 (skillopt / skillopt-sleep)
`pip install skillopt` exists, but it trains against a benchmark with an optimizer-model API, and its "sleep" plugins target Claude Code, Codex and Copilot, not Antigravity. Check the project docs before using; if you build a benchmark from this project's replayable tasks, SkillOpt can use `lessons.md` as its seed skill and return a validated `best_skill.md`. Ask the user before installing or spending API credit.
