#!/usr/bin/env bash
# Unit-test claude/hooks/secret-guard.sh with no model calls: feed it PreToolUse JSON in a throwaway git repo.
# Usage: bash scripts/qa-hooks.sh [hook-path]   (a mutated copy can be passed to prove the checks discriminate)
set -u
repo="$(cd "$(dirname "$0")/.." && pwd)"
hook="${1:-$repo/claude/hooks/secret-guard.sh}"
t="$(mktemp -d)"; trap 'rm -rf "$t"' EXIT
export TMPDIR="$t"
r="$t/r"; mkdir "$r"; cd "$r"
git init -q . && git config user.email a@b.c && git config user.name t
echo x > ok.txt; git add ok.txt; git commit -qm init
mkdir sub; echo s > sub/.env.local; echo s > .ENV.PROD; echo s > id_rsa.pub; echo s > .env.production.example; echo s > .credentials.json; echo s > .env.production; echo s > k.pem; echo s > .env.example; echo y > b.txt
mkdir other; (cd other && git init -q . && git config user.email a@b.c && git config user.name t && echo s > .env && echo y > ok2.txt)
fail=0
run() { # expect cmd
  out="$(jq -n --arg c "$2" --arg d "${CWD:-$r}" '{tool_name:"Bash",cwd:$d,tool_input:{command:$c}}' | bash "$hook" 2>&1)"; rc=$?
  if [ "$rc" = "$1" ]; then echo "PASS rc=$rc  $2"; else echo "FAIL want=$1 got=$rc  $2  [$out]"; fail=$((fail+1)); fi
}
# block (exit 2)
run 2 'git add -A'
run 2 'git add .'
run 2 'git add -f .credentials.json'
run 2 'git add -u .env.production'
run 2 'git add .env.production'
run 2 'git add k.pem'
run 2 'rtk git add -A'
run 2 "git -C $r add -A"
run 2 'GIT_AUTHOR_NAME=x git add -A'
run 2 'echo hi && git add -A'
run 2 "git -C $r/other add ."
run 2 'git add ".env.production"'
run 2 "git add 'k.pem'"
run 2 'git add sub'
run 2 'git add sub/'
run 2 'git add ./'
run 2 'git add .ENV.PROD'
run 2 'git add -vA'
run 2 'git add -fA'
run 2 'git --no-pager add -A'
run 2 'git stage -A'
run 2 '/usr/bin/git add -A'
run 2 '(git add -A)'
run 2 'bash -c "git add -A"'
run 2 'git add $(echo .env)'
run 2 'git add *.pem'
mkdir "$t/clean"; (cd "$t/clean" && git init -q . && echo y > c.txt)
CWD="$t/clean" run 2 "cd $r && git add -A"
CWD="$t/clean" run 0 'git add -A'
TMPDIR=/nonexistent run 2 'git add -A'
# allow (exit 0)
run 0 'git add id_rsa.pub'
run 0 'git add .env.production.example'
run 0 'git add ok.txt'
run 0 'git add .env.example'
run 0 'git status'
run 0 'git log --oneline'
run 0 'ls -la'
run 0 'git branch'
run 0 'git diff'
run 0 'git add b.txt'
# commit/push with a tracked secret
git add -f .credentials.json 2>/dev/null
run 2 'git commit -m x'
run 2 'git push origin main'
git rm -q --cached .credentials.json
run 0 'git commit -m x'
echo "failures: $fail"; [ "$fail" = 0 ]
