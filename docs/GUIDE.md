# Setup guide

End-to-end order for a machine and a project. Sources: Claude Code docs (best-practices, memory, skills, plugins, permissions). Decisions and history: `docs/NEXT-MACHINE.md`.

## Layers

| Layer | What | Where |
|---|---|---|
| Always on, every machine | RTK hook, Ponytail plugin, permissions (deny, ask, bypass mode disabled), short global `CLAUDE.md`, status line, agents `explorer` `reviewer` `worker` | this repo, applied to `~/.claude` |
| On demand | `orchestrate` skill (description match, or `/orchestrate`); Superpowers plugin in project or local scope only; AO as an external app | skills, plugin scope, the user |
| Per project, once | project `CLAUDE.md`, path-scoped rules, verification command, project permissions | the project's `.claude/` |

Never install Superpowers at user scope: an enabled plugin is part of every session, and its SessionStart hook injects the bootstrap each time (plugins doc).

## 0. Machine prerequisites (once per machine)

Needed: `git`, `jq` (status line), `node` (Ponytail hooks), `gh`, `rtk`, current Claude Code. On Windows use Git Bash.

```
echo ${CLAUDE_CONFIG_DIR:-$HOME/.claude}
claude --version
command -v rtk jq node gh
```

Done when every command prints a value. No path is hard-coded anywhere; only the clone location of this repo differs per machine.

## 1. Apply the global setup (each machine)

```
git pull
bash scripts/apply.sh            # backs up first, copies claude/ items
bash scripts/qa-deny.sh          # needs the claude CLI; run it where RTK is installed
claude plugin marketplace add DietrichGebert/ponytail
claude plugin install ponytail@ponytail
```

Open a new session (running sessions do not get the plugin). Done when:
- `qa-deny.sh` prints `all checks passed`
- `claude plugin list` shows `ponytail@ponytail` enabled and `~/.claude/.ponytail-active` is `full`
- `rtk gain` total commands grows after a few Bash calls
- the status line shows `[model] N% context`
- `/context` lists the global `CLAUDE.md`

Undo: copy files back from `~/.claude-backup-<timestamp>/`.

## 2. Bootstrap a project (once, before the first task)

Do it by hand for the first projects; automate only what you repeat.

1. In the project directory run `claude`, then `/init`, then `/doctor` to cut what Claude can derive from the code. Target: under 200 lines. For each line ask whether removing it would cause a mistake.
2. Decide the verification first and write the command in `CLAUDE.md`: tests, lint and type check for backend; build plus screenshot comparison for frontend; browser screenshot comparison plus lint for markup and CSS. Without a check Claude can run, "done" is only its own opinion.
3. Split rules by area in `.claude/rules/*.md` with `paths:` globs (for example styles and templates, frontend, backend). Keep only rules that apply everywhere in `CLAUDE.md`.
4. Pre-approve routine read-only commands with `/permissions` (add the `rtk ` twin of each Bash rule). On macOS, Linux and WSL2 consider `/sandbox`.
5. Feature-development projects only: install Superpowers from `/plugin` and pick project or local scope. Skip it for markup-only or small-fix projects.
6. Check: `/context` shows the project `CLAUDE.md`, `/hooks` lists only intended hooks, `claude plugin list` shows the scope you chose.

## 3. Per task

| Work | Flow |
|---|---|
| Markup, small fix | Ask directly, verify with the check, commit |
| Bug | Give symptom, location and what "fixed" means; reproduce with a failing check; fix; verify |
| Feature, medium | Plan mode (Shift+Tab), approve the plan, implement, verify |
| Feature, large | Let Claude interview you (`AskUserQuestion`), write `SPEC.md`, implement in a fresh session |
| Review | Fresh-context `reviewer` or `/code-review`; only findings that affect correctness or the stated requirements |
| Parallel | Git worktrees; AO is optional and still unverified (see `docs/NEXT-MACHINE.md`) |

Habits: `/clear` between unrelated tasks; after two failed corrections on one issue, `/clear` and restate the task; `/rewind` to undo; changes go through a branch and a PR and a person merges.

## 4. Maintenance

- Monthly: `/doctor` on `CLAUDE.md`, skills and agents; `claude --version` against the changelog.
- After any change to permissions or hooks: `bash scripts/qa-deny.sh` on every machine where RTK is installed.
- Edit `claude/` in this repo, never `~/.claude` directly.

## Not verified

- Windows Git Bash and macOS behavior of `apply.sh`, the plugin hooks and `qa-deny.sh` with the real RTK hook (tested only on Linux without RTK).
- Superpowers install flow at project scope, and the exact `paths:` syntax (read it in the memory doc when writing the first rule).
- Whether `orchestrate` is loaded by description matching often enough; `/orchestrate` is the fallback.

## Deliberately not adopted

User-scope Superpowers, agent teams (experimental), agent view (research preview), hook-based intent detection, global Stop hook or `/goal` gate (enable per project once it has tests), a daily proposal loop (add it when a concrete need shows up).
