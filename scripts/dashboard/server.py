#!/usr/bin/env python3
"""Local live dashboard for the global Claude setup. Read-only, stdlib only, 127.0.0.1 only.

Run: python3 scripts/dashboard/server.py [--port 8787]
Optional: PROJECT_DIRS or state/projects.txt lists project roots; the "프로젝트 셋업" dialog shows only file presence and line counts.
Reads: git history, gh PR list, scripts/verify.sh --live, reports/*.md, claude/settings.json,
and the tool-call names and timestamps of the newest session log in ~/.claude/projects.
It parses the log tail in memory but emits only tool names, times, a file basename, and a command's first word plus a plain subcommand
(never arguments, so a pasted token or `KEY=value` cannot leave the machine). Message text is never emitted.
"""
import json, os, re, subprocess, sys, threading, time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CONFIG = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
PROJECTS = CONFIG / "projects"
CACHE = {}  # key -> (time, value)
REFRESHING = set()
LOCK = threading.Lock()


def find_bash():
    # On Windows, `bash` on PATH can be WSL's with another HOME; verify.sh needs Git Bash.
    for c in (os.environ.get("BASH"), "C:/Program Files/Git/bin/bash.exe", "C:/Program Files (x86)/Git/bin/bash.exe"):
        if c and Path(c).exists():
            return c
    return "bash"


BASH = find_bash()
ENV = {**os.environ, "HOME": os.environ.get("USERPROFILE", os.environ.get("HOME", ""))} if os.name == "nt" else None


def run(cmd, timeout=60):
    try:
        p = subprocess.run(cmd, cwd=ROOT, env=ENV, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        return p.stdout
    except Exception:
        return ""


def cached(key, ttl, fn, slow=False, placeholder=None):
    """Return the cached value. A slow source (verify.sh, gh) refreshes in a thread, so a request never waits on it."""
    now = time.time()
    with LOCK:
        hit = CACHE.get(key)
        if hit and now - hit[0] < ttl:
            return hit[1]
        if slow:
            if key not in REFRESHING:
                REFRESHING.add(key)
                threading.Thread(target=refresh, args=(key, fn), daemon=True).start()
            return hit[1] if hit else placeholder
    return refresh(key, fn)


def refresh(key, fn):
    try:
        val = fn()
        with LOCK:
            CACHE[key] = (time.time(), val)
        return val
    finally:
        with LOCK:
            REFRESHING.discard(key)


def git_history():
    out = run(["git", "log", "-60", "--date=iso-strict", "--pretty=format:%h\x1f%ad\x1f%s\x1f%an"])
    commits = []
    for line in out.splitlines():
        h, ad, s, an = (line.split("\x1f") + ["", "", "", ""])[:4]
        merge = re.match(r"Merge pull request #(\d+) from \S+", s)
        commits.append({"hash": h, "at": ad, "subject": s, "author": an, "pr": int(merge.group(1)) if merge else None})
    return {"commits": commits, "branch": run(["git", "branch", "--show-current"]).strip(),
            "dirty": len([l for l in run(["git", "status", "--short"]).splitlines() if l.strip()])}


def pull_requests():
    out = run(["gh", "pr", "list", "--state", "all", "--limit", "30", "--json", "number,title,state,createdAt,mergedAt,additions,deletions,changedFiles"])
    try:
        return json.loads(out)
    except Exception:
        return []


def verify():
    out = run([BASH, "-l", "scripts/verify.sh", "--live"], timeout=120)
    lines = [re.sub(r"\x1b\[[0-9;]*m", "", l) for l in out.splitlines() if l.strip()]
    counts = {"PASS": 0, "FAIL": 0, "WARN": 0}
    for l in lines:
        k = l.split(" ", 1)[0]
        if k in counts:
            counts[k] += 1
    return {"at": datetime.now(timezone.utc).isoformat(), "counts": counts, "lines": lines[-80:]}


def settings():
    try:
        s = json.loads((ROOT / "claude" / "settings.json").read_text(encoding="utf-8"))
        p = s.get("permissions", {})
        live = json.loads((CONFIG / "settings.json").read_text(encoding="utf-8")).get("permissions", {})
        return {"mode": p.get("defaultMode"), "deny": len(p.get("deny", [])), "ask": len(p.get("ask", [])),
                "liveMode": live.get("defaultMode"), "liveDeny": len(live.get("deny", [])), "liveAsk": len(live.get("ask", [])),
                "model": s.get("model"), "advisor": s.get("advisorModel")}
    except Exception:
        return {}


def reports():
    d = ROOT / "reports"
    items = []
    if d.is_dir():
        for f in sorted(d.glob("20*.md"), reverse=True)[:7]:
            items.append({"name": f.name, "mtime": datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).isoformat(),
                          "text": f.read_text(encoding="utf-8", errors="replace")[:4000]})
    return items


def safe_command(cmd):
    """First word, plus the second only when it is a plain subcommand or script path (no '=', no leading '-')."""
    w = cmd.split()
    if not w:
        return ""
    head = os.path.basename(w[0])[:20]
    if len(w) > 1 and re.fullmatch(r"[A-Za-z0-9_./-]{1,40}", w[1]) and not w[1].startswith("-") and head in ("git", "gh", "bash", "python3", "python", "npm", "npx", "rtk", "winget"):
        return head + " " + w[1]
    return head


def session_events(limit=120):
    """Tool-call name, time and a safe target (file basename or command head) from the newest session log."""
    files = list(PROJECTS.glob("*/*.jsonl")) if PROJECTS.is_dir() else []
    if not files:
        return {"session": None, "events": []}
    f = max(files, key=lambda p: p.stat().st_mtime)
    try:
        with open(f, "rb") as fh:
            fh.seek(0, 2)
            size = fh.tell()
            fh.seek(max(0, size - 1_500_000))
            raw = fh.read().decode("utf-8", errors="replace").splitlines()
    except Exception:
        return {"session": None, "events": []}
    events = []
    for line in raw:
        try:
            d = json.loads(line)
        except Exception:
            continue
        ts = d.get("timestamp")
        if not ts:
            continue
        t = d.get("type")
        c = (d.get("message") or {}).get("content")
        if t == "assistant" and isinstance(c, list):
            for x in c:
                if x.get("type") == "tool_use":
                    inp = x.get("input") or {}
                    target = ""
                    if inp.get("file_path"):
                        target = os.path.basename(str(inp["file_path"]))
                    elif inp.get("command"):
                        target = safe_command(str(inp["command"]))
                    elif inp.get("pattern"):
                        target = "search"
                    events.append({"at": ts, "kind": "tool", "name": str(x.get("name", "?")).split("__")[-1], "target": target})
        elif t == "user" and isinstance(c, str) and not c.startswith("<"):
            events.append({"at": ts, "kind": "user", "name": "user message", "target": ""})
    return {"session": f.stem[:8], "mtime": datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).isoformat(), "events": events[-limit:]}


def project_dirs():
    """Project roots to inspect: PROJECT_DIRS (path-separated) or state/projects.txt, one path per line."""
    raw = os.environ.get("PROJECT_DIRS", "")
    paths = [p for p in raw.split(os.pathsep) if p.strip()]
    f = ROOT / "state" / "projects.txt"
    if not paths and f.is_file():
        paths = [l.strip() for l in f.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip() and not l.startswith("#")]
    return [Path(p).expanduser() for p in paths]


def project_setup(d):
    """Setup facts of one project as booleans and counts. File contents never leave this function."""
    def lines(p):
        try:
            return p.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            return []
    agents, claude = d / "AGENTS.md", d / "CLAUDE.md"
    cl = lines(claude)
    first = next((l.strip() for l in cl if l.strip()), "")
    try:
        cfg = json.loads((d / ".claude" / "settings.json").read_text(encoding="utf-8"))
    except Exception:
        cfg = None
    perm = (cfg or {}).get("permissions", {})
    gi = "\n".join(lines(d / ".gitignore"))
    rules = list((d / ".claude" / "rules").glob("*.md")) if (d / ".claude" / "rules").is_dir() else []
    al = lines(agents)
    f = {"name": d.name, "found": d.is_dir(),
         "agents": agents.is_file(), "agentsLines": len(al),
         "claude": claude.is_file(), "claudeLines": len(cl), "imports": first.startswith("@AGENTS.md"),
         "settings": cfg is not None, "denyEnv": any(".env" in str(r) for r in perm.get("deny", [])),
         "defaultMode": "defaultMode" in perm, "rules": len(rules),
         "gitignore": "CLAUDE.local.md" in gi and "settings.local.json" in gi}
    if d.is_dir():
        f["checks"] = practice_checks(d, f, al, cl, perm, rules, "\n".join(al + cl).lower())
    return f


def git_tracked(d, *pats):
    try:
        p = subprocess.run(["git", "ls-files", "--", *pats], cwd=d, env=ENV, capture_output=True, text=True, timeout=10)
        return [l for l in p.stdout.splitlines() if l.strip()] if p.returncode == 0 else []
    except Exception:
        return []


def practice_checks(d, f, al, cl, perm, rules, text):
    """Best-practice gaps as {act: add|fix|remove, level, what, why, fix, src}. Rules come from the Claude Code docs pages
    memory, best-practices and permissions (read 2026-10-10). Only the finding text leaves this function, never file content."""
    out = []

    def add(act, level, what, why, fix, src):
        out.append({"act": act, "level": level, "what": what, "why": why, "fix": fix, "src": src})
    local = (d / "CLAUDE.local.md").is_file()
    if not (f["agents"] or f["claude"]):
        add("add", "warn", "지침 파일 없음", "Claude는 매 세션 CLAUDE.md(또는 AGENTS.md)를 읽습니다. 없으면 빌드·테스트 명령과 프로젝트 규칙을 매번 추측합니다.", "AGENTS.md 또는 CLAUDE.md를 추가: 검증 명령, 기본값과 다른 스타일 규칙, 함정만 (/project-setup).", "memory")
    if f["agents"] and f["claude"] and not f["imports"]:
        add("fix", "bad", "CLAUDE.md가 @AGENTS.md를 가져오지 않음", "AGENTS.md와 CLAUDE.md가 둘 다 있으면 Claude는 CLAUDE.md만 읽습니다. AGENTS.md의 규칙이 Claude에게 전달되지 않습니다.", "CLAUDE.md 첫 줄을 @AGENTS.md로 하고 Claude 전용 내용만 그 아래에 둡니다.", "memory")
    if f["agents"] and not f["claude"] and local:
        add("fix", "warn", "CLAUDE.local.md 때문에 AGENTS.md가 읽히지 않을 수 있음", "AGENTS.md는 CLAUDE.md와 CLAUDE.local.md가 모두 없을 때만 단독으로 로드됩니다.", "프로젝트 CLAUDE.md(첫 줄 @AGENTS.md)를 만들거나 CLAUDE.local.md 첫 줄에 @AGENTS.md를 넣습니다.", "memory")
    norm = lambda ls: [l.strip() for l in ls if l.strip()]
    if f["agents"] and f["claude"] and not f["imports"] and norm(al) == norm(cl):
        add("remove", "warn", "CLAUDE.md가 AGENTS.md의 복사본", "같은 내용이 두 곳에 있으면 한쪽만 고쳐져 어긋납니다.", "CLAUDE.md를 @AGENTS.md 한 줄(+Claude 전용 몇 줄)로 줄입니다.", "memory")
    if f["claudeLines"] > 200:
        add("fix", "warn", "CLAUDE.md %d줄 (권장 200 이하)" % f["claudeLines"], "길수록 컨텍스트를 더 쓰고 지침이 묻혀 따르는 비율이 떨어집니다.", "영역별 규칙은 .claude/rules/<영역>.md(paths:)로 옮기고, 코드에서 알 수 있는 내용은 지웁니다 (/doctor가 제안).", "memory")
    if f["agentsLines"] > 200 and not f["claude"]:
        add("fix", "warn", "AGENTS.md %d줄 (Claude가 전부 로드)" % f["agentsLines"], "Claude는 AGENTS.md를 통째로 읽습니다. 200줄을 넘으면 같은 이유로 지침이 묻힙니다.", "Codex와 공유하는 정본이라 사용자가 판단: 영역 규칙을 .claude/rules/로 옮기거나 AGENTS.md를 줄입니다.", "memory")
    ph = sum(l.count("[REPLACE:") for l in al + cl)
    if ph:
        add("fix", "warn", "템플릿 자리표시자 [REPLACE:] %d개 남음" % ph, "채워지지 않은 자리표시자는 Claude에게 잘못된 지침이 됩니다.", "실제 값으로 채우거나 해당 줄을 지웁니다.", "best-practices")
    if not f["settings"]:
        add("add", "warn", ".claude/settings.json 없음", "팀원과 클라우드 세션은 ~/.claude를 읽지 않습니다. 프로젝트 쪽 deny가 없으면 .env 보호가 개인 설정에만 의존합니다.", "permissions.deny에 Read(**/.env*), Read(**/.credentials*)를 추가합니다.", "permissions")
    else:
        if not f["denyEnv"]:
            add("add", "bad", "deny에 .env 읽기 차단이 없음", "deny는 모든 모드에서 적용되는 보호 규칙입니다.", "permissions.deny에 Read(**/.env*)를 추가합니다.", "permissions")
        if f["defaultMode"]:
            add("remove", "bad", "프로젝트 settings에 defaultMode", "권한 모드는 사용자·팀이 정할 일입니다. 프로젝트 파일에 두면 모두에게 강제됩니다.", "defaultMode 줄을 지웁니다.", "permissions")
        risky = [a for a in perm.get("allow", []) if re.search(r"(build|install|deploy|sass|rm |push)", str(a))]
        if risky:
            add("remove", "warn", "allow에 파일을 쓰거나 배포하는 명령 %d개" % len(risky), "허용 목록에는 읽기 전용 검사(test, lint, typecheck)만 두는 것이 안전합니다.", "build/install/deploy/push류 allow를 지웁니다.", "permissions")
    if not f["gitignore"]:
        add("add", "warn", ".gitignore에 로컬 파일 줄 누락", "CLAUDE.local.md와 settings.local.json은 개인용입니다. 커밋되면 개인 설정이 팀에 퍼집니다.", ".gitignore에 CLAUDE.local.md, .claude/settings.local.json을 추가합니다.", "memory")
    badrules = []
    for r in rules:
        parts = r.read_text(encoding="utf-8", errors="replace").split("---")
        if len(parts) > 2 and re.search(r"^(?!paths:)[A-Za-z_-]+:", parts[1], re.M):
            badrules.append(r.name)
    if badrules:
        add("fix", "warn", "rules frontmatter에 paths 외 필드 (%d개 파일)" % len(badrules), "paths가 규칙 파일에서 Claude Code가 읽는 유일한 필드입니다.", "paths: 목록만 남깁니다.", "memory")
    env = [t for t in git_tracked(d, ".env", ".env.*", "**/.env") if not re.search(r"\.(example|sample|template|dist)$", t)]
    if env:
        add("remove", "bad", "git에 .env 파일 %d개 추적 중" % len(env), "커밋된 비밀은 히스토리에 남습니다.", "git rm --cached 후 .gitignore에 추가하고, 노출된 값은 폐기합니다.", "permissions")
    if git_tracked(d, "CLAUDE.local.md", ".claude/settings.local.json"):
        add("remove", "warn", "개인용 로컬 파일이 git에 추적됨", "로컬 파일은 개인 설정입니다.", "git rm --cached 후 .gitignore에 추가합니다.", "memory")
    names = []
    for fn in ("package.json", "composer.json"):
        try:
            names += list((json.loads((d / fn).read_text(encoding="utf-8")).get("scripts") or {}).keys())
        except Exception:
            pass
    for mk in ("Makefile", "makefile"):
        if (d / mk).is_file():
            names += re.findall(r"^([A-Za-z0-9_.-]+):", (d / mk).read_text(encoding="utf-8", errors="replace"), re.M)
    checks = [c for c in names if re.search(r"(test|lint|typecheck|check|phpunit|stylelint|phpcs)", c, re.I)]
    ci = (d / ".github" / "workflows").is_dir()
    f["verify"] = len(checks) + (1 if ci else 0)
    if not checks and not ci:
        add("add", "warn", "검증 명령을 찾지 못함", "Claude가 실행할 수 있는 검사가 없으면 '끝났다'는 Claude의 판단뿐이고 사용자가 검증 루프가 됩니다.", "테스트·lint·타입체크 중 하나를 스크립트로 만들고(마크업은 스크린샷 비교나 lint) 지침에 적습니다.", "best-practices")
    elif checks and (f["agents"] or f["claude"]) and not any(c.lower() in text for c in checks):
        add("add", "warn", "검증 명령이 지침에 적혀 있지 않음", "Claude는 어떤 명령이 이 프로젝트의 검사인지 추측해야 합니다.", "지침에 실제 명령 한 줄을 적습니다. 후보: " + ", ".join(checks[:3]), "best-practices")
    if (f["agents"] or f["claude"]) and any((d / n).is_file() for n in ("docker-compose.yml", "docker-compose.yaml", "compose.yaml", "Makefile", "makefile")) and not re.search(r"docker|container|컨테이너|make up", text):
        add("add", "info", "명령이 컨테이너/호스트 어디서 도는지 안 적혀 있음", "Claude는 환경 특이점을 코드에서 알 수 없습니다. 잘못된 곳에서 실행하면 실패합니다.", "지침에 한 줄: 검증 명령을 컨테이너에서 실행하는지, 호스트에서 실행하는지.", "best-practices")
    return out


def projects():
    return [project_setup(d) for d in project_dirs()]


def state():
    return {
        "now": datetime.now(timezone.utc).isoformat(),
        "git": cached("git", 5, git_history),
        "prs": cached("prs", 60, pull_requests, slow=True, placeholder=[]),
        "verify": cached("verify", 60, verify, slow=True, placeholder={"at": datetime.now(timezone.utc).isoformat(), "counts": {"PASS": 0, "FAIL": 0, "WARN": 0}, "lines": ["검증 실행 중..."]}),
        "settings": cached("settings", 5, settings),
        "reports": cached("reports", 30, reports),
        "activity": session_events(),
        "projects": cached("projects", 10, projects),
    }


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        # Refuse foreign Host headers (DNS rebinding against a local server).
        if self.headers.get("Host", "").split(":")[0] not in ("127.0.0.1", "localhost"):
            self.send_error(403)
            return
        if self.path.startswith("/api/state"):
            body, ctype = json.dumps(state()).encode(), "application/json"
        elif self.path in ("/", "/index.html"):
            body, ctype = (HERE / "index.html").read_bytes(), "text/html; charset=utf-8"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8787
    print(f"dashboard on http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
