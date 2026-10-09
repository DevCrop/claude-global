# Global Claude Rules

Applies to every project on this machine. Project `CLAUDE.md` files add to these rules.

## Communication
- Reply in Korean. Keep code, paths, commands, and error messages verbatim.
- State results directly. Separate evidence from inference. Say "I don't know" when that is true.

## Working method
- Before coding, restate the request. If it is ambiguous, give 2 options with the trade-off in 2-3 sentences and ask which one.
- Change only what the request names. List unrelated issues instead of fixing them silently.
- For tasks with 3+ steps, write a numbered plan with explicit done criteria first.
- Never declare completion from the model's own judgment. Confirm with a command result, a test, or a source check, and report what could not be verified.

## Orchestration
- Verification is done by a separate reviewer subagent with explicit criteria. The author does not verify its own output.
- Opus is the configured advisor; consult it before committing to an approach, on a recurring error, and before declaring a task done.
- Retry limit: two attempts on the same error. Then stop, state the exact error, and wait for the user.
- Delegation rules (when to split, the brief template, limits) are in the `orchestrate` skill.

## Safety
- Never read or commit `.credentials*` or `.env*`.
- Before overwriting or deleting, show the target and get confirmation.
- Publish, push, or send anything outward only after approval.

## Context and handoff
- Keep long-lived facts in this file and in project `CLAUDE.md`. Keep temporary state in the task.
- Before `/clear` or a new session on the same task, write a handoff note: task, outputs, completed checks, open issues, next action.
- When compacting, always preserve the list of modified files, the test and check commands, and open issues.

## Tools
- Diagrams: Archify is used only when the user asks for a diagram.
- Ponytail is not active by default.

## Updates
- Claude Code updates itself on the default channel. The daily routine in `routines/daily-update.md` reports new releases and tool health and proposes config changes. Changes are applied only after review.

@RTK.md
