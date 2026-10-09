# claude-global

Source of truth for the global Claude Code setup on this machine (`~/.claude`).

## Layout

- `claude/CLAUDE.md` — global rules, copied to `~/.claude/CLAUDE.md`
- `claude/settings.json` — global settings, copied to `~/.claude/settings.json`
- `claude/RTK.md`, `claude/agents/`, `claude/skills/` — RTK note, subagents (`explorer`, `reviewer`, `worker`) and skills (`orchestrate`, `project-setup`), copied to `~/.claude/`
- `claude/routines/`, `claude/scheduled-tasks/` — daily update routine and the scheduled task body
- `docs/GUIDE.md` — setup order for a machine and for a project, and the per-task flow
- `docs/NEXT-MACHINE.md` — full handoff: decisions, links, routine, remaining work, setup order for a new machine
- `state/last-seen.json` — per-machine baseline for the daily routine (gitignored, created by the routine)
- `scripts/apply.sh` — copies `claude/` into `~/.claude/` with a backup
- `scripts/verify.sh` — read-only checks: repo, `--live` for this machine's applied state, `--full` adds the deny/ask QA
- `scripts/docs-watch.sh` — diffs the official docs pages this setup depends on (used by the daily routine)
- `scripts/qa-deny.sh` — checks that the deny rules still block dangerous commands on this machine, with hooks such as rtk active

Runtime data (credentials, session history, auto-memory, plugins, caches) is never stored here. See `.gitignore`.

## Applying

Run `bash scripts/apply.sh` (macOS bash or Git Bash on Windows). On Windows, Git Bash `$HOME` must equal `%USERPROFILE%`; otherwise set `CLAUDE_CONFIG_DIR` to `%USERPROFILE%\.claude`. It backs up the managed files, then copies `CLAUDE.md`, `RTK.md`, `settings.json`, `agents/` and `routines/` into `~/.claude/` (or `CLAUDE_CONFIG_DIR`). Nothing else in that directory is touched. Update with `git pull && bash scripts/apply.sh`. The status line in `settings.json` needs `jq` on PATH.

Scope: local machines only. Cloud sessions read the project's own `.claude/`, not `~/.claude/`.

## Verifying

Run `bash scripts/qa-deny.sh` on each machine after `apply.sh`. It first checks without the CLI that every Bash deny pattern has an `rtk ` twin, then needs the `claude` CLI, uses a throwaway repo with no remote and the haiku model, and prints PASS or FAIL per command. Undo an apply by copying files back from `~/.claude-backup-<timestamp>/`.

## Status

Applied on the first machine and verified on a Mac earlier (2026-10-09); the permissions, agents, skills, verify and routine changes after that are untested on Windows Git Bash and macOS. On each machine run the steps in `docs/GUIDE.md` and `bash scripts/verify.sh --live`.
