---
name: orchestrate
description: Use when splitting work across subagents or parallel agents, before delegating to explorer, worker or reviewer, or when deciding whether to delegate at all.
---

Default to one agent. Delegate only when the part does not block the main thread's next step, or its output is large and mostly irrelevant to it. Otherwise work inline.

1. Split by context boundary (a feature with its tests), not by role (planner, coder, tester).
2. A delegate does not see this conversation. Brief it with: Task (one sentence), Files (paths it needs), Return format (what, how long), Done criteria (checkable by a command or a file read), Out of scope.
3. At most 3 delegates at once. Each owns one unit: a feature with its tests (`worker`), one search question (`explorer`), or one verification (`reviewer`).
4. Give the reviewer the criteria and the changed file list only, never the author's reasoning or a verdict to confirm.
5. A delegate's report is a claim. Check the evidence it cites before relaying it as done.
6. High-volume, well-defined subagent tasks run on Haiku.
