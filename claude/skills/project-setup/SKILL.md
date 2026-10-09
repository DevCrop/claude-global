---
name: project-setup
description: Bootstrap the current project for Claude Code before the first task, covering CLAUDE.md, path-scoped rules, the verification command and project permissions. Run manually with /project-setup.
disable-model-invocation: true
argument-hint: [notes or stack hint]
allowed-tools: Read Grep Glob Bash(git rev-parse *) Bash(command -v *)
---

Set up the current project so Claude Code can work in it and check its own work. Base every line on files you read; never invent a command. Anything you cannot confirm goes in the final "Not verified" list. Do not open `.env*` or credential files; name them only. Write your reports and questions in the language the global `CLAUDE.md` sets for replies, even though this skill is written in English. Notes from the user: $ARGUMENTS

1. Preconditions. Confirm the working directory is a git repository root (`git rev-parse --show-toplevel`); if not, stop and ask. If a `CLAUDE.md` or `.claude/` already exists, improve it as a diff instead of overwriting it.
2. Read the global layer first: `CLAUDE.md` and `settings.json` in `${CLAUDE_CONFIG_DIR:-~/.claude}`, plus the names of its skills and agents. They already apply to every project, so the project files must not restate them. If the directory is missing, say so in "Not verified" and continue.
3. Detect the stack by reading manifests and config: `package.json`, `composer.json`, `pyproject.toml`, `requirements*.txt`, `go.mod`, `Gemfile`, `pom.xml`, `Makefile`, lint and format configs (`.editorconfig`, eslint, prettier, stylelint, phpcs), and file extensions. Classify the areas present: markup and styles (html, css, scss, templates), frontend (js, ts, jsx, tsx, vue), backend (php, py, go, java, rb, cs). Report what you found.
4. Find the verification commands per area. Read them from `package.json` scripts, `composer.json` scripts, `Makefile` targets, test configs, and `.github/workflows/*` (what CI runs is the best source). If an area has no check you can find, ask the user what it should be (tests, lint, build, or a screenshot comparison for visual work). Do not make one up. Then propose how hard the check gates the work and let the user pick: (a) a line in `CLAUDE.md` telling Claude to run it before reporting done (default), (b) a `/goal` condition per session, (c) a Stop hook that blocks until it passes, (d) a fresh-context reviewer subagent. Add a hook only if the user picks (c).
5. Draft `CLAUDE.md`, under 200 lines. Include only what Claude cannot learn from the code and the global layer: the verified commands, style rules that differ from the defaults (from the configs you read), repository etiquette found in README or CONTRIBUTING, and real gotchas. For each line ask whether removing it would cause a mistake; if not, drop it. End the workflow section with: run the verification before reporting done.
6. Draft path-scoped rules in `.claude/rules/<area>.md` only for an area that has rules of its own. Use exactly this frontmatter (`paths` is the only field Claude Code reads, as a YAML list of globs):
   ```
   ---
   paths:
     - "src/**/*.{ts,tsx}"
   ---
   ```
   Do not create a rule file that would only repeat `CLAUDE.md`.
7. Draft `.claude/settings.json` with `permissions.deny` for `Read(**/.env*)`, `Read(**/.credentials*)` and `Read(**/credentials.json)`. This repeats the global deny on purpose: cloud sessions and teammates do not read `~/.claude`. Add `permissions.allow` for the verified read-only check commands (test, lint, typecheck); leave out builds and anything else that writes files. It matters for teammates and cloud, since the global default mode ignores allow rules. If `rtk` is on PATH (`command -v rtk`), add the `rtk ` twin of every Bash rule. Never allow destructive commands, never set `defaultMode`, and never set a bypass mode.
8. Propose `.gitignore` lines for `CLAUDE.local.md` and `.claude/settings.local.json` if they are absent.
9. Plugins: do not install anything. If this is a feature-development project, tell the user the command: `claude plugin install superpowers@claude-plugins-official --scope local` (`--scope project` shares it with the team; each collaborator then installs it on their own machine). Skip it for markup-only or small-fix projects.
10. Show every file you propose in full (or as a diff for existing files) and wait for an explicit yes. Write only what was approved; permission prompts may be off, so this step is the approval.
11. Finish with: the files written, what the user should check in a new session (`/context` lists the project `CLAUDE.md`, `/hooks` shows only intended hooks, `/doctor` suggests cuts), and a "Not verified" list.
