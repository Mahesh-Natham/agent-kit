---
name: share-to-understand
description: "When the user shares files to \"analyse\", they may want Claude to understand them, not audit or fix"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e9c9f032-ed91-4f4a-bfd7-ad85ad52fef5
  modified: 2026-11-10T13:51:34.847Z
---

When the user asks to "analyse all the files", they may mean "learn who I am and what I work on", not a code audit or fixes.

**Why:** On 2026-11-10 they ran an audit, then said "i gave you this not for fixing anything i just gave you to understand about me".
**How to apply:** For broad "analyse" requests, summarise who they are and what they work on first, and ask before running audits or proposing fixes. See [[user-phd-profile]].
