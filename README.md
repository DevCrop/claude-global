# claude-global

Source of truth for the global Claude Code setup on this machine (`~/.claude`).

## Layout

- `claude/CLAUDE.md` — global rules, copied to `~/.claude/CLAUDE.md`
- `claude/settings.json` — global settings, copied to `~/.claude/settings.json`
- `claude/RTK.md`, `claude/agents/` — RTK note and subagents, copied to `~/.claude/`
- `claude/routines/`, `claude/scheduled-tasks/` — daily update routine and the scheduled task body
- `docs/NEXT-MACHINE.md` — full handoff: decisions, links, routine, remaining work, setup order for a new machine
- `PLAN.md` — original plan and decisions

Runtime data (credentials, session history, auto-memory, plugins, caches) is never stored here. See `.gitignore`.

## Applying

Copy the files from `claude/` into `~/.claude/` after reviewing the diff. The repository does not apply changes automatically.

## Status

Applied on the first machine (2026-10-09). Continue on another machine with `docs/NEXT-MACHINE.md`.
