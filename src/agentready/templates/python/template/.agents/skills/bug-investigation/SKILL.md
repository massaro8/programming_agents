---
name: bug-investigation
description: Use when investigating a reported defect with observable or reproducible incorrect behavior.
---

Input: one READY BUGFIX item with expected and observed behavior. Follow [the canonical workflow](../../../docs/agent/workflows/bugfix.md). Reproduce, establish root cause, add a regression test, then make the minimum fix. Done when the regression and neighboring checks pass and the item is DONE; otherwise record the blocker.
