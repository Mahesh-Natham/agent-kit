# Evolution loop details

Idea (from SkillOpt): keep the model frozen, train a small text file against a score, with bounded edits,
a rejected-edit buffer and a held-out check before accepting.

| Idea | Here |
|---|---|
| Trainable skill text | `.evolve/lessons.md`, loaded every session via `@.evolve/lessons.md` in CLAUDE.md |
| Scored rollouts | ledger runs with verifier scores (`log_run.py`) |
| Bounded "learning rate" | max 3 edits per cycle, max 40 lessons, 300 chars each |
| Accept only on improvement | evidence tier (2+ runs) or replay tier (more checks pass, none regress) |
| Rejected-edit buffer | `.evolve/rejected.md`, checked by `gate.py propose` |
| Slow update | every 3rd cycle: merge near-duplicates, delete lessons no recent run supports |

## Writing a good lesson
Shape: `When <trigger>, do <action> (because <what went wrong or right>).`
- Checkable trigger and action: "When editing `firmware/stm32/App/Communication/protocol.h`, update the `STM_*`
  constants in `legacy/jetson/fusion.py` and `aev_protocol.py` in the same change."
- Project facts beat general advice Claude already follows.
- One idea per lesson. Anything longer belongs in CLAUDE.md or a README, suggested to the user.
- `--scope` is a glob of the files it applies to (`legacy/jetson/**`, `firmware/stm32/App/**`); default `**`.

## Replay tier
1. Pick 1 to 3 past `fail` / `corrected` runs whose task can be scored by `verifier.json`.
2. In the scratchpad: `git worktree add <scratch>/replay-base <commit-before-task>` and the same for `replay-cand`.
3. Redo the task in each: `replay-base` with current lessons, `replay-cand` with the candidate lesson applied.
4. `gate.py score --cwd <scratch>/replay-base --out <scratch>/before.json`, same for `after.json`.
5. `gate.py accept --tier replay --before <scratch>/before.json --after <scratch>/after.json`.
6. `git worktree remove` both afterwards.
Replay is expensive; skip it when the lesson is small and the evidence tier is enough.
