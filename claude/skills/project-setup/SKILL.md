---
name: project-setup
description: Bootstrap the current project for Claude Code before the first task, covering CLAUDE.md, path-scoped rules, the verification command and project permissions. Run manually with /project-setup.
disable-model-invocation: true
argument-hint: [notes or stack hint]
allowed-tools: Read Grep Glob
---

Set up the current project so Claude Code can work in it and check its own work. Base every line on files you read; never invent a command. Anything you cannot confirm goes in the final "Not verified" list. Notes from the user: $ARGUMENTS

1. Preconditions. Confirm the working directory is a git repository root (`git rev-parse --show-toplevel`); if not, stop and ask. If a `CLAUDE.md` or `.claude/` already exists, improve it as a diff instead of overwriting it.
2. Detect the stack by reading manifests and config: `package.json`, `composer.json`, `pyproject.toml`, `requirements*.txt`, `go.mod`, `Gemfile`, `pom.xml`, `Makefile`, lint and format configs (`.editorconfig`, eslint, prettier, stylelint, phpcs), and file extensions. Classify the areas present: markup and styles (html, css, scss, templates), frontend (js, ts, jsx, tsx, vue), backend (php, py, go, java, rb, cs). Report what you found.
3. Find the verification commands per area. Read them from `package.json` scripts, `composer.json` scripts, `Makefile` targets, test configs, and `.github/workflows/*` (what CI runs is the best source). If an area has no check you can find, ask the user what it should be (tests, lint, build, or a screenshot comparison for visual work). Do not make one up.
4. Draft `CLAUDE.md`, under 200 lines. Include only what Claude cannot learn from the code: the verified commands, style rules that differ from the defaults (from the configs you read), repository etiquette found in README or CONTRIBUTING, and real gotchas. For each line ask whether removing it would cause a mistake; if not, drop it. End the workflow section with: run the verification before reporting done.
5. Draft path-scoped rules in `.claude/rules/<area>.md` only for an area that has rules of its own. Use exactly this frontmatter (`paths` is the only field Claude Code reads, as a YAML list of globs):
   ```
   ---
   paths:
     - "src/**/*.{ts,tsx}"
   ---
   ```
   Do not create a rule file that would only repeat `CLAUDE.md`.
6. Draft `.claude/settings.json` with `permissions.allow` for the verified, read-only check commands (test, lint, typecheck, build). If `rtk` is on PATH (`command -v rtk`), add the `rtk ` twin of every Bash rule. Never allow destructive commands, and never set a bypass mode. Add a hook only if the user asks for one.
7. Plugins: do not install anything. If this is a feature-development project, tell the user the command: `claude plugin install superpowers@claude-plugins-official --scope local` (`--scope project` shares it with the team; each collaborator then installs it on their own machine). Skip it for markup-only or small-fix projects.
8. Show every file you propose in full (or as a diff for existing files) and wait for approval. Write only what was approved.
9. Finish with: the files written, what the user should check in a new session (`/context` lists the project `CLAUDE.md`, `/hooks` shows only intended hooks, `/doctor` suggests cuts), and a "Not verified" list.
