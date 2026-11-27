<!-- self-evolve:begin -->
## Self-evolving agent (always on)
- Before any task: follow the `self-evolve` skill's Preflight. If `.agents/evolve/` is missing, run its Bootstrap first.
- After any non-trivial task: run the project verifiers in `.agents/evolve/verifier.json` and log the outcome with `self-evolve` Postflight.
- Apply lessons from `.agents/evolve/lessons.md`. Change them only through `self-evolve`'s `gate.py`.
- Never install third-party skills or tools without vetting and explicit user approval.
<!-- self-evolve:end -->
