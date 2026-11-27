# Bootstrap procedure (once per project)

1. **State + verifiers**
   `python3 <skill_dir>/scripts/init_project.py --root .`
   Creates `.agents/evolve/{lessons.md,ledger.jsonl,rejected.md,verifier.json,snapshots/}`. Detects likely commands from `package.json`, `pyproject.toml`/`pytest.ini`, `Cargo.toml`, `go.mod`, `Makefile`, `platformio.ini`, `CMakeLists.txt`. It only writes the file; it never runs them. Show the list to the user and correct it. Embedded or hardware projects often have no unit tests: record a build command (compile must succeed) and, if available, a static-analysis command.

2. **Knowledge graph (graphify)**
   - `graphify --help` to confirm it is installed and which platforms `graphify install` supports. Confirm Antigravity (or the closest supported target) before relying on hooks.
   - If not installed, give the user the install commands and wait for approval: `uv tool install graphifyy` (the PyPI name has a double y), then `graphify install`.
   - Build the graph for the repo root, then read `graphify-out/GRAPH_REPORT.md`.
   - If hooks are unsupported on this platform, rely on the AGENTS.md pointer: "read GRAPH_REPORT.md before searching raw files".

3. **Always-on pointer**
   Append `assets/agents-md-snippet.md` to the project's `AGENTS.md` between its markers (idempotent: skip if the begin marker exists).

4. **Skill discovery (find-skills)**
   - Derive 1 to 3 short keyword queries from the detected stack and the user's stated goal, e.g. `npx skills find stm32 firmware`.
   - For each candidate: fetch it to a temp dir, run `python3 <skill_dir>/scripts/vet_skill.py <dir>`, read its SKILL.md yourself, and summarise: source, what it does, scripts it ships, verdict.
   - Install only what the user approves, at project scope (`.agents/skills/`). Record the source and commit hash in `.agents/evolve/installed-skills.md`.

5. **Baseline**
   Run the verifiers once on the untouched repo and log it as run `baseline` (`log_run.py --outcome pass|fail --note baseline`). Later score changes are measured against this.
