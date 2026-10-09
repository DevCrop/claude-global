# claude-global

Source of truth for the global Claude Code setup on this machine (`~/.claude`).

## Layout

- `claude/CLAUDE.md` — global rules, copied to `~/.claude/CLAUDE.md`
- `claude/settings.json` — global settings, copied to `~/.claude/settings.json`
- `claude/RTK.md`, `claude/agents/` — RTK note and subagents, copied to `~/.claude/`
- `claude/routines/`, `claude/scheduled-tasks/` — daily update routine and the scheduled task body
- `docs/NEXT-MACHINE.md` — full handoff: decisions, links, routine, remaining work, setup order for a new machine
- `PLAN.md` — original plan and decisions (see its correction note)
- `state/last-seen.json` — baseline for the daily routine
- `scripts/apply.sh` — copies `claude/` into `~/.claude/` with a backup
- `scripts/reset-claude.ps1` — first-machine partial reset. Windows only, hardcoded paths. Do not run on another machine.

Runtime data (credentials, session history, auto-memory, plugins, caches) is never stored here. See `.gitignore`.

## Applying

Run `scripts/apply.sh` (macOS bash or Git Bash on Windows). It backs up the managed files, then copies `CLAUDE.md`, `RTK.md`, `settings.json`, `agents/` and `routines/` into `~/.claude/` (or `CLAUDE_CONFIG_DIR`). Nothing else in that directory is touched. Update with `git pull && scripts/apply.sh`.

Scope: local machines only. Cloud sessions read the project's own `.claude/`, not `~/.claude/`.

## Status

Applied on the first machine (2026-10-09). Continue on another machine with `docs/NEXT-MACHINE.md`.
