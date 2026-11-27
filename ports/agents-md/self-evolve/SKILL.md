---
name: self-evolve
description: Makes the coding agent measurably better on every project by bootstrapping each new repo (knowledge graph via graphify, verifier commands, vetted skill discovery via find-skills) and running a validation-gated learning loop that turns real successes, failures and user corrections into small, evidence-backed lessons (SkillOpt-style). Use this at the START of any new project, repo or session, whenever the user says set up, bootstrap, improve yourself, learn from this, evolve, or /evolve, after finishing any non-trivial task (postflight logging), and whenever a test or build fails, you are corrected, or you repeat a mistake. Use it even if the user does not mention skills or self-improvement.
---

# self-evolve

Goal: each task leaves the agent slightly better for the next one, without drifting, bloating, or installing untrusted code.

Why it is built this way: a skill or rules file can only be improved reliably against a **score**. So the loop is: act, score with real verifiers (tests/lint/build), log, propose a small edit, **accept only if evidence or a replay score justifies it**, snapshot for rollback. Without a score, edits are guesses, so unscored edits are never accepted automatically.

All state lives in `<project>/.agents/evolve/`. Scripts are in this skill's `scripts/` (call them with `python3 <skill_dir>/scripts/<name>.py`; on Windows use `python` or `py -3` if `python3` is not found).

## Hard rules (never break)
1. **Never auto-install third-party skills.** Discover, vet (`scripts/vet_skill.py`), show the user the verdict, install only after approval, project scope only. See `references/skill-vetting.md`.
2. **Lessons change only through `scripts/gate.py`.** No hand-editing `lessons.md`.
3. **Bounded edits:** at most 3 lesson changes per cycle; `lessons.md` capped at 40 lines. Merge or delete before adding.
4. **Evidence required:** a lesson cites ledger run IDs. No evidence, no lesson.
5. **No secrets, tokens, personal data, or raw code dumps** in lessons or the ledger.
6. **Do not change the user's source code as part of evolving.** Evolution touches only `.agents/evolve/` (and, with approval, `AGENTS.md` / `.agents/skills/`).
7. If a step needs a tool that is missing or a path that differs, say so plainly and continue with what works. Do not invent commands.

## 1. Preflight (every task, keep it under a minute)
- If `.agents/evolve/` does not exist: run **Bootstrap** (section 2) first.
- Read `.agents/evolve/lessons.md` and `~/.agents/evolve/global-lessons.md` (if present). Apply lessons whose `scope` matches the files you will touch.
- If `graphify-out/GRAPH_REPORT.md` exists, read it before searching raw files; query the graph for structural questions.
- Note the verifier commands in `.agents/evolve/verifier.json`; you will run them at the end.

## 2. Bootstrap (once per project)
Follow `references/bootstrap.md`. Summary:
1. `python3 scripts/init_project.py --root .` creates state files and detects verifier commands (it runs nothing).
2. Confirm the verifier commands with the user in one line; fix `verifier.json` if wrong.
3. Knowledge graph: check `graphify --help`; if missing, tell the user the install command (`uv tool install graphifyy`, then `graphify install`) and ask before installing. Then build the graph for the repo.
4. Add the always-on pointer from `assets/agents-md-snippet.md` to the project's `AGENTS.md` (create if absent).
5. Skill discovery: up to 3 candidate skills via `npx skills find <stack/task keywords>`; vet each; present verdicts; install only approved ones.

## 3. Postflight (after every non-trivial task)
Run the verifiers, then log:
```
python3 scripts/log_run.py --task "<one line>" --outcome pass|fail|corrected|abandoned \
  --score <passed/total or 0-1> --note "<what mattered>"
```
Log `corrected` whenever the user fixed or redirected you, and `fail` when verifiers failed and you needed more than one attempt. A **lesson candidate** exists when: a failure was resolved by a non-obvious fix, the user corrected a repeatable behaviour, or the same dead end happened twice.

## 4. Evolve cycle
Trigger: 5+ new ledger entries since last cycle, the user says `/evolve`, or a session is ending with unprocessed candidates. Details: `references/evolution-loop.md`.
1. Read new ledger entries; split into successes and failures; find recurring patterns.
2. Propose up to 3 edits: `python3 scripts/gate.py propose --add "<lesson>" --evidence R0003,R0007 --scope "<glob>"` (or `--replace L004` / `--delete L002`).
3. The gate checks bounds, evidence, duplicates, rejected buffer, secrets. Then validate by tier:
   - **Tier 1, evidence:** 2+ independent runs support it (1 if the user explicitly stated the rule). Accept with `gate.py accept --tier evidence`.
   - **Tier 2, replay:** if verifiers exist and a past failed task can be replayed in a scratch git worktree, score baseline vs candidate with `gate.py score`; accept only if strictly higher: `gate.py accept --tier replay --before X --after Y`.
   - **Tier 3, optimizer:** if the user has `skillopt` installed with API credentials and a benchmark, hand it `lessons.md` as the seed skill. Never install it or spend API credit without approval.
4. Rejected edits go to `rejected.md` with a reason (`gate.py reject --reason ...`), so they are not proposed again.
5. Every accepted change is snapshotted (and git-committed if the repo exists). To undo: `gate.py rollback`.
6. Report to the user in 2 lines: what changed, why, and the evidence.

## 5. Promotion
A lesson accepted in 2+ different projects can be promoted to `~/.agents/evolve/global-lessons.md` via `gate.py promote L00X` (ask the user first; global lessons affect every project).

## Honest limits to state when asked
- It improves through the context it loads (lessons, graph, vetted skills), not model weights.
- Gains depend on verifier quality. Projects with no tests get Tier 1 only.
- Description-based skill triggering is not guaranteed, so the installer also adds a short always-on rule to the global `GEMINI.md`.
