---
name: aev-project
description: "The user's autonomous ground vehicle repo (Jetson + STM32, v1.0 legacy -> ROS 2 v2 migration) and audit findings from 2026-11-10"
metadata:
  node_type: memory
  type: project
  originSessionId: e9c9f032-ed91-4f4a-bfd7-ad85ad52fef5
  modified: 2026-11-10T13:51:32.114Z
---

Repo: `Projects/AEV/MU_AutonomousGroundVehicle`. Jetson runs `legacy/jetson/fusion.py` (frozen v1.0, ~7.9k lines); STM32 NUCLEO-H723ZG runs `firmware/stm32/App`; v2 ROS 2 port lives in `src/aev_core` with golden tests against legacy. Follow its CLAUDE.md and docs/MIGRATION_PLAN.md.

Audit on 2026-11-10 (report only, nothing changed): leftover mutant in steering.py (`progress < 1.0`, should be 1.5); safety timeouts use time.time() not monotonic; fault-latch clear via MANUAL releases brake; invalid-mode DRIVE frames still feed the link watchdog; three throttle ramps disagree; manual_test.c duplicates actuator code.

**Why:** the user shared the folder to be understood, not to have fixes made.
**How to apply:** don't fix these unless asked; mention them if relevant to a later task. See [[user-phd-profile]], [[share-to-understand]].
