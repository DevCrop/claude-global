# claude-global

Source of truth for the global Claude Code setup on this machine (`~/.claude`).

## Layout

- `claude/CLAUDE.md` — global rules, copied to `~/.claude/CLAUDE.md`
- `claude/settings.json` — global settings, copied to `~/.claude/settings.json`

Runtime data (credentials, session history, auto-memory, plugins, caches) is never stored here. See `.gitignore`.

## Applying

Copy the files from `claude/` into `~/.claude/` after reviewing the diff. The repository does not apply changes automatically.

## Status

Draft. Not yet applied to `~/.claude`. Open decisions:

- Whether to keep the `@../.codex/AGENTS.md` import (Codex config is managed separately).
- Whether to add hooks (session start, RTK rewrite, token report) back in, and which ones.
- Whether the `encoding-safety` and `official-source-workflow` skills belong here.
