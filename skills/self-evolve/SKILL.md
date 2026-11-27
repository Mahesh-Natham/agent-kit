---
name: self-evolve
description: Evidence-gated learning loop for a project. Logs how coding tasks went (verifier results, failures, user corrections) and turns repeated, proven patterns into short project lessons that load automatically through CLAUDE.md. Use when the user says /self-evolve, "learn from this", "remember this for the project", "evolve", or "set up self-evolve"; after finishing a non-trivial code change in a repo that has a .evolve/ folder (log the run); when a build or test failed and the fix was non-obvious; when the user corrects a project-specific behaviour that will come up again; or before installing any third-party skill (vetting).
---

# self-evolve

Goal: each task leaves Claude a little better at *this project*, without drift, bloat, or untrusted code.

How: act -> score with real verifiers (build / lint / tests) -> log the run -> propose a small lesson ->
accept it only with evidence (2+ runs, or the user stated it) or a better replay score -> snapshot for rollback.
An edit with no score or evidence is a guess, so it is never accepted.

Scripts live in `scripts/` next to this file. From the repo root (in this repo):
`python .claude/skills/self-evolve/scripts/<name>.py ...` (use `python3` on Linux). They find the
project by walking up to the folder that holds `.evolve/`, so any working directory inside the repo works.

## Where things live (and what does NOT go here)

| What | Where | Shared? |
|---|---|---|
| Accepted lessons (max 40, one line each) | `.evolve/lessons.md`, imported by `CLAUDE.md` with `@.evolve/lessons.md` | committed |
| Verifier commands | `.evolve/verifier.json` | committed |
| Run ledger, snapshots, pending edits | `.evolve/ledger.jsonl`, `snapshots/`, `pending.json` | git-ignored |

- **Lessons** = technical facts about this project, proven by runs (commands, pitfalls, conventions).
- **Claude's auto-memory** = things about the user and how they like to work. Keep using memory for that.
- **CLAUDE.md** = rules the user wrote. If a fact is already in CLAUDE.md or memory, do not add it as a lesson.
  If a lesson becomes a permanent rule, suggest moving it into CLAUDE.md and deleting the lesson.

## Hard rules
1. Lessons change only through `gate.py` (never edit `lessons.md` by hand). At most 3 edits per cycle.
2. Every lesson cites ledger run IDs (`--evidence R0003,R0007`) or is `--user-stated`.
3. No secrets, tokens, personal data or code dumps in lessons or the ledger (the scripts refuse obvious ones).
4. Evolving never changes source code, commits, or pushes. The user decides when `.evolve/` is committed.
5. Never install a third-party skill, plugin or tool without vetting it and getting the user's approval.
6. If a verifier needs a tool that is missing, it is reported as skipped. Say so; do not invent commands.

## 1. Setup (once per project)
1. `python <scripts>/init_project.py` creates `.evolve/` and guesses verifier commands (it runs nothing).
2. Show the guessed commands to the user in one line each and fix `verifier.json` with them. Mark tools that
   may be missing with `"requires": ["gcc"]` so the run is skipped instead of failed. Set `"confirmed": true`.
3. With the user's OK: `python <scripts>/init_project.py --link-claude-md` adds the `@.evolve/lessons.md` import.
4. Baseline: `python <scripts>/gate.py score`, then log it: `log_run.py --task baseline --outcome pass|fail --score P/T`.

## 2. Log a run (after each non-trivial task)
Run the verifiers (`gate.py score`, or the subset that covers the files you touched), then:
```
python <scripts>/log_run.py --task "<one line>" --outcome pass|fail|corrected|abandoned --score <P/T> --note "<what mattered>"
```
- `corrected`: the user fixed or redirected you. `fail`: verifiers failed and you needed another attempt.
- A **lesson candidate** exists when a failure needed a non-obvious fix, the user corrected something that
  will repeat, or the same dead end happened twice. Mention it to the user in one line.
- Skip logging for questions, reading-only tasks and one-line edits.

## 3. Evolve cycle
Trigger: `log_run.py` says 5+ new runs, the user says /self-evolve or "learn from this", or a candidate is waiting.
1. `python <scripts>/gate.py status`, then read the new ledger lines. Split successes and failures; find patterns.
2. Propose up to 3 edits:
   `gate.py propose --add "<lesson>" --evidence R0003,R0007 --scope "legacy/jetson/**"`
   (also `--replace L004 --add "<text>"`, `--delete L002`, or `--user-stated` when the user dictated the rule).
   The gate rejects bad bounds, unknown evidence, near-duplicates, previously rejected ideas and secrets.
3. Validate, then accept:
   - **Evidence tier:** 2+ distinct runs support it (or user-stated) -> `gate.py accept --tier evidence`.
   - **Replay tier:** a past failed task can be replayed in a scratch git worktree -> score both sides with
     `gate.py score --cwd <dir> --out <file>.json` and `gate.py accept --tier replay --before b.json --after a.json`.
     Accepted only if more checks pass and none that passed before now fails. See `references/evolution-loop.md`.
4. Not good enough -> `gate.py reject --reason "<why>"` (stored so it is not proposed again).
5. Every accept is snapshotted; `gate.py rollback` undoes the last one.
6. Tell the user in 2 lines: what changed, why, and the evidence. Remind them `.evolve/lessons.md` is uncommitted.

## 4. Vetting a third-party skill
Download to an empty scratch folder (run nothing from it), then
`python -I <scripts>/vet_skill.py <folder>`, read SKILL.md and every script yourself, and report: source,
what it does, what it runs, findings, verdict. Details: `references/skill-vetting.md`. A clean scan is not proof
of safety. Note: this skill's own `vet_skill.py` flags itself, because it contains the patterns it searches for.

## Limits (say so when asked)
- It improves Claude through context (lessons loaded each session), not model weights.
- Gains depend on verifier quality; a project with no checks only gets the evidence tier.
