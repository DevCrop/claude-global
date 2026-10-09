# 다른 컴퓨터에서 이어서 세팅하기

작성일: 2026-10-09. 검증 후 보강판 (별도 reviewer 에이전트가 누락·오류를 찾아 반영함).
언어 규칙: 사용자에게는 한국어로 답한다. 코드·경로·명령은 원문 그대로 둔다.

이 문서는 첫 컴퓨터(Windows 10, 사용자명 `edn_y`)에서 한 작업을 기준으로 쓰였다. 첫 컴퓨터에만 있는 것(백업, 로그인, 대화 기록)은 저장소에 없다. 그 부분은 섹션 3에 따로 적었다.

## 목차
1. 한눈에 보기
2. 새 컴퓨터 세팅 순서
3. 첫 컴퓨터에만 있는 것 (백업, 리셋, 로그인)
4. 설정 내용 (settings.json, 에이전트, 규칙)
5. 도구 상태 (CLI, RTK, Archify, Ponytail)
6. 예약 루틴 `daily-claude-update`
7. 남은 작업
8. 링크 모음
9. 확인된 사실과 한계 (측정값 전부)
10. 사용자 결정 기록
11. 함정과 주의사항
12. 저장소 이력

## 1. 한눈에 보기

| 항목 | 상태 |
|---|---|
| 전역 규칙 `claude/CLAUDE.md`, `RTK.md` | 완료, 첫 컴퓨터에 적용됨 |
| `claude/settings.json` | 완료, deny 동작 확인됨 |
| 에이전트 `reviewer`, `explorer` | 완료, `/context`에서 인식 확인 |
| RTK 0.50.0 | 완료, 훅 동작 확인 |
| 일일 루틴 `daily-claude-update` | 완료, 수동 실행 1회 성공, 활성(enabled) |
| 루틴 모델 | 첫 자동 실행은 sonnet-5-5로 확인. UI에서 명시 지정은 사용자가 할 일 |
| Claude Code CLI | npm 최신 2.1.295 (2026-10-09 확인). 머신마다 `claude --version`으로 확인 |
| Archify | 미설치, 다이어그램 요청 시 |
| Ponytail | 미설치, 의도적 보류 |
| 프로젝트 셋업·최적화 | 나중 단계 |

소스 오브 트루스는 이 저장소(`DevCrop/claude-global`, branch `main`)다. 라이브 설정은 `~/.claude`이며 `claude/` 폴더에서 복사해 만든다.

## 2. 새 컴퓨터 세팅 순서

범위: 이 저장소는 로컬 머신(Windows, Mac)의 `~/.claude`용이다. 클라우드 세션(claude.ai/code)은 `~/.claude/settings.json`을 읽지 않고 clone한 프로젝트의 `.claude/settings.json`만 읽는다(공식 settings 문서). 클라우드용 설정은 각 프로젝트 저장소에 커밋한다.

각 단계 끝에 확인 방법이 있다. 확인되기 전에 다음 단계로 넘어가지 않는다.

1. Claude Code를 설치하고 로그인한다. 자격 증명은 저장소에 없으므로 새로 로그인해야 한다.
   - 확인: `claude --version`이 npm 최신(2026-10-09 기준 2.1.295) 이상.
   - 설치 방법은 공식 문서를 따른다. 첫 컴퓨터(Windows)는 npm으로 설치했다: `npm install -g @anthropic-ai/claude-code@latest` (첫 컴퓨터는 `--prefix`로 `AppData/Roaming/npm`을 지정했다).
2. 저장소를 받는다. HTTPS 주소이므로 새 컴퓨터에서 GitHub 인증(예: `gh auth login` 또는 자격 증명 관리자)이 먼저 필요하다. private이면 인증 없이는 clone이 안 된다.
   ```bash
   git clone https://github.com/DevCrop/claude-global.git
   ```
3. 설정을 적용한다. Mac bash 또는 Windows Git Bash에서 실행한다.
   ```bash
   cd claude-global && scripts/apply.sh
   ```
   - 스크립트가 `CLAUDE.md`, `RTK.md`, `settings.json`, `agents/`, `routines/`만 `~/.claude`(또는 `CLAUDE_CONFIG_DIR`)로 복사한다. 덮어쓰기 전에 대상 파일을 `~/.claude-backup-<시각>/`에 백업한다. 자격 증명, `projects/`, 플러그인은 건드리지 않는다.
   - `CLAUDE.md` 마지막 줄 `@RTK.md`가 `RTK.md`를 import하므로 두 파일이 같은 폴더에 있어야 한다. 스크립트가 함께 복사한다.
   - 이후 갱신은 `git pull && scripts/apply.sh`.
   - 복사하지 말 것: `scripts/reset-claude.ps1` (섹션 3의 경고 참고).
   - 확인: Claude 세션에서 `/context`의 Memory files에 `CLAUDE.md`, `RTK.md`가 보이고 Custom agents에 `explorer`, `reviewer`가 보인다.
4. RTK를 설치한다 (RTK 공식 README 기준).
   ```bash
   winget install rtk-ai.rtk   # Windows
   brew install rtk            # macOS
   ```
   - RTK가 없어도 Bash는 동작한다. 훅은 non-blocking이라 실패해도 도구 호출이 진행된다(Claude Code hooks 문서). 필터링만 꺼진다.
   - `settings.json`에 RTK 훅(`rtk hook claude`)이 이미 들어 있다. `rtk init -g`를 실행하면 설정이 바뀔 수 있으니 실행 전후 `settings.json` 차이를 비교한다. (`PLAN.md`는 `rtk init -g`를 적었지만, 이미 훅이 들어 있는 현재 상태에서는 필수가 아니다.)
   - `rtk`가 PATH에 있어야 훅이 동작한다. 첫 컴퓨터에서는 winget 설치 직후 Git Bash PATH에 없었고, 훅은 앱 재시작 뒤 활성화됐다. 이후 같은 컴퓨터의 세션에서 `command -v rtk`가 WinGet 경로를 찾는 것을 확인했다. 새 컴퓨터에서는 새 터미널·앱 재시작 후 `rtk --version`으로 직접 확인한다.
   - 확인: Bash 명령 몇 개 실행 뒤 `rtk gain`의 Total commands가 늘어난다.
5. 예약 루틴을 만든다 (섹션 6, 경로 수정 필요).
6. 섹션 7의 남은 작업을 순서대로 진행한다.

## 3. 첫 컴퓨터에만 있는 것

저장소에 없고, 새 컴퓨터로 옮기지 않는 것들이다.

백업 (첫 컴퓨터 `D:\backup` 아래):
- `D:\backup\claude-20261008`: `~/.claude` 전체. `.git`, `.credentials.json`, `projects/`를 포함하고 `~/.claude.json` 사본도 있다.
- `D:\backup\claude-20261009-projects`: `projects/` 스냅샷 (51개 파일, 대화 기록).
- `D:\backup\settings.before-rtk-20261009.json`: RTK 훅을 넣기 전의 `settings.json`.

레거시 리셋 (`scripts/reset-claude.ps1`):
- `PLAN.md`는 "Full: 전부 삭제"라고 적었지만 실제로는 부분 리셋을 했다. 설정 계층만 지웠다.
- 유지한 것: `.credentials.json`(로그인), `projects/`(대화 기록·메모리), `sessions/`, `session-env/`, `plugins/`, `cache/`, `ide/`, `shell-snapshots/`, `history.jsonl`, `chrome/`(Chrome 연동).
- 스크립트는 Windows 전용이고 `D:\backup\claude-20261008`과 `$env:USERPROFILE`이 하드코딩되어 있다. 실행하면 `~/.claude.json`을 삭제한다. 새 컴퓨터에서 실행하지 않는다. 백업이 없으면 스크립트 스스로 멈추게 되어 있다.

로그인과 설정 파일:
- 로그인은 새 컴퓨터에서 새로 한다.
- `~/.claude.json`은 `.gitignore`에 있고 저장소에 없다. 새 컴퓨터에서 따로 다루지 않는다.
- 대화 기록(`projects/`)과 `history.jsonl`은 옮기지 않는다.

## 4. 설정 내용

`claude/settings.json` (전부):
- `model`: `sonnet`
- `effortLevel`: `high` (공식 기본은 medium, xhigh는 토큰 소모 증가. 되돌리려면 `/effort`로 세션 중 변경하거나 이 값을 바꾼다. Sonnet 5.5는 세션 중 변경해도 캐시 유지)
- `advisorModel`: `opus`
- 제거한 키(공식 settings-reference의 기본값과 같아서 vanilla 기준으로 삭제, 2026-10-09): `autoUpdatesChannel: latest`(미설정 시 latest), `theme: dark`(기본 dark), `enableAllProjectMcpServers: false`(미설정 시 서버마다 승인 요청). 프로젝트 설정이 같은 키를 true로 두면 사용자 설정보다 우선하므로 false를 명시해도 보호가 되지 않는다.
- `env.ENABLE_PROMPT_CACHING_1H`: 제거함. 공식 문서상 구독 플랜의 메인 대화는 기본이 1시간 TTL이라 중복이고, 이 변수는 서브에이전트·압축 요청까지 1시간으로 올려 쓰기 비용만 늘린다 (짧은 작업에는 손해).
- `permissions.deny` 53개 (원래 20개 + 변형 우회 8개 + 같은 Bash 패턴 25개를 `rtk ` 접두어로 복제한 것. 아래 함정 절 참고):
  - `Bash(rm -rf /*)`, `Bash(rm -rf ~*)`, `Bash(rm -rf $HOME*)`, `Bash(rm -rf %USERPROFILE%*)`
  - `Bash(git push --force *)`, `Bash(git push --force)`, `Bash(git push -f *)`, `Bash(git push -f)`
  - `Bash(git reset --hard *)`, `Bash(git reset --hard)`
  - `Bash(git clean -f *)`, `Bash(git clean -fd *)`, `Bash(git clean -fdx *)`
  - `Bash(git checkout -- *)`, `Bash(git checkout .)`, `Bash(git restore .)`, `Bash(git restore --staged .)`
  - `Read(**/.credentials*)`, `Read(**/.env*)`, `Read(**/credentials.json)`
- `hooks.PreToolUse`: matcher `Bash`, command `rtk hook claude`

에이전트 (`claude/agents/`):
- `reviewer`: model sonnet, effort high, 도구 Read/Grep/Glob/Bash. 다른 에이전트의 작업을 기준에 맞춰 검증한다.
- `explorer`: model haiku, 도구 Read/Grep/Glob (읽기 전용), `omitClaudeMd: true`(호출마다 CLAUDE.md 로딩 생략, Claude Code v2.1.271 이상). 질문 하나를 넓게 검색해 10줄 이내로 답한다.

규칙 요약 (`claude/CLAUDE.md`, 원문이 우선):
- 한국어 응답. 요청을 먼저 되풀이하고, 모호하면 2~3개 해석을 제시.
- 요청한 것만 바꾼다. 3단계 이상이면 번호 계획과 완료 기준을 먼저 쓴다.
- 완료 선언은 명령 결과·테스트·출처 확인으로만 한다.
- 단일 에이전트로 시작. 분리는 컨텍스트 경계(기능+테스트)로. 검증은 별도 `reviewer`가 한다. 같은 오류는 2회까지만 재시도.
- 모델 역할: 메인은 Sonnet. Opus는 advisor로 접근 방식 확정 전, 반복 오류, 완료 선언 전에 자문(공식 advisor 문서: Sonnet 5.5 메인 + Opus 5 이상 advisor는 허용된 조합). 대량 소작업 서브에이전트는 Haiku.
- 금지: `.credentials*`, `.env*` 읽기·커밋. 승인 없는 force push, `reset --hard`, `git clean`, `rm -rf`. 외부 공개·push는 승인 후.
- 세션 전환 전 인계 노트: 작업, 산출물, 완료한 확인, 열린 이슈, 다음 행동.

## 5. 도구 상태

Claude Code CLI:
- 2.1.233에서 2.1.293으로 올렸다 (npm latest). 첫 컴퓨터 설치 위치: `C:\Users\edn_y\AppData\Roaming\npm`.
- 변경 로그에는 2.1.294(2026-10-08)가 있으나 npm은 아직 2.1.293이다. `state/last-seen.json`에 `latest_changelog_version: 2.1.294`로 기록됨.
- 데스크톱 앱은 자체 claude-code를 번들한다 (`AppData\Roaming\Claude\claude-code`). npm CLI와 별개이며 건드리지 않는다.

RTK 0.50.0:
- 설치: `winget install rtk-ai.rtk`. 첫 컴퓨터 바이너리: `C:\Users\edn_y\AppData\Local\Microsoft\WinGet\Packages\rtk-ai.rtk_Microsoft.Winget.Source_8wekyb3d8bbwe\rtk.exe`
- 훅은 Bash 도구 호출만 가로챈다. Read, Grep, Glob은 필터되지 않는다 (`PLAN.md` Known limits).
- 절감률은 표본에 따라 크게 다르다. 수치는 섹션 9.

Archify (미설치):
- 다이어그램을 요청할 때만 쓴다. 설치 전 `SKILL.md`를 읽어 검토하고 사용자 승인을 받는다.
- 명령: `npx skills add tt-a1i/archify -g`. 최신 릴리스 v3.0.1(2026-09-28), MIT. README는 업데이트 명령을 주지 않고 "업데이트는 자동 설치되지 않는다"고만 한다. 같은 설치 명령 재실행이 업데이트일 가능성이 높지만 확인하지 못했다.
- 지금까지의 흐름도·차트는 앱 내장 시각화로 그렸다.

Ponytail (미설치, 의도적 보류):
- 출처: `DietrichGebert/ponytail`(MIT). 매 세션 상시 지침이 추가되므로 기본 비활성이다. 프로젝트별로만 재검토한다. 같은 이름의 다른 저장소(`mikrammullah/PonyTail` 등)와 헷갈리지 않는다.
- 최신 버전 5.1.0(2026-10-08, `.claude-plugin/plugin.json`의 `version`). 릴리스 태그는 없어서 이 파일이 버전 기준이다.
- 설치(두 프롬프트로 따로): `/plugin marketplace add DietrichGebert/ponytail`, `/plugin install ponytail@ponytail`. 끄기: `/ponytail off`. Node.js 훅을 쓴다는 설치 가이드 설명이 있다(README 원문 미확인).
- 업데이트 경로 `/plugin marketplace update ponytail` + `/reload-plugins`는 설치 가이드 출처이며 README에서는 확인하지 못했다.

두 도구의 최신 버전은 일일 루틴이 추적한다(섹션 6). 설치는 루틴이 하지 않는다.

## 6. 예약 루틴 `daily-claude-update`

- 목적: Claude Code 변경 로그, Anthropic 뉴스, Claude Code와 RTK의 최신 버전을 매일 확인하고 도구 상태(설정 드리프트, rtk PATH, rtk 사용량)를 점검해 보고서만 쓴다. `~/.claude`는 바꾸지 않고 아무것도 설치하지 않는다. 업데이트 명령은 보고서에 적고 사용자가 실행한다.
- 일정: cron `0 9 * * *` (로컬 09:00, 실제로는 약 09:03에 시작, 몇 분 지연 있음). 상태: 활성(enabled).
- 정의 파일: `claude/routines/daily-update.md`(단계·출력 형식), `claude/scheduled-tasks/daily-claude-update/SKILL.md`(예약 작업 본문 참조본).
- 출력: `reports/YYYY-MM-DD.md`(로컬 전용, `.gitignore`), 기준 상태 `state/last-seen.json`(추적됨). 첫 보고서는 `reports/2026-10-09.md`.
- 실행 이력: 수동 실행 1회 성공(2026-10-08T15:28Z, 결정에 따라 Haiku). 첫 자동 실행은 2026-10-09T02:37Z(11:37 KST)에 시작했다. 09:03 슬롯이 아니라 2시간 반쯤 늦은 보충 실행이었다. 앱이 꺼져 있었거나 절전 중이었던 것으로 추정되며 원인은 확인하지 못했다. 작성 시점에는 실행 중이었다.
- 모델 확인: 이 자동 실행 세션은 `claude-sonnet-5-5`, effort medium이었다 (`get_session`). 앱 UI에서 지정한 값인지, 기본 모델(`settings.json`의 sonnet)을 따른 것인지는 구분하지 못했다.
- 제한: 앱이 켜져 있을 때만 실행된다. 예약 도구에는 모델 필드가 없고, 예약 작업 본문(`SKILL.md`)에도 name, description만 있다.
- 새 컴퓨터에서 만들기:
  1. Claude 앱의 예약 작업 기능으로 `daily-claude-update`를 만들고 본문에 `SKILL.md` 내용을 넣는다.
  2. 본문 안의 `<repo>`를 새 컴퓨터의 claude-global clone 절대 경로로 바꾼다.
  3. 모델은 앱의 Scheduled 화면에서 Sonnet으로 지정한다.
  4. 한 번 수동 실행해 보고서가 생기는지 확인한다.
- 두 컴퓨터에서 같은 루틴을 켜면 보고서가 중복되고 `state/last-seen.json`이 충돌한다. 한쪽만 켠다.
- 루틴 절차(`claude/routines/daily-update.md`): `claude --version` → 공식 변경 로그와 Anthropic 뉴스 확인 → 항목 분류(관련/참고/무시) → 보고서 작성 → `last-seen.json` 갱신. 설치·push·`~/.claude` 수정은 하지 않는다.

## 7. 남은 작업 (순서대로)

0. 2026-10-09 실행 QA 결과는 섹션 9의 "하네스 QA" 참고. 반영함(되돌릴 수 있음): `effortLevel`을 high로, `explorer`에 `omitClaudeMd: true`. 결정 대기: `rm -rf /*` 과차단 유지 여부, 루틴 자동 설치 허용 여부. 브랜치 `claude/add-apply-script`의 커밋은 push 전이다. 맥과 Windows Git Bash에서 `scripts/apply.sh`를 한 번씩 실행해 확인한다. RTK는 0.51.0으로 올린다.

1. 루틴 모델을 Sonnet으로 고정 (앱 UI). 첫 자동 실행은 sonnet-5-5로 돌았지만 그것이 UI 설정 때문인지 기본값 때문인지 모른다. UI에서 명시적으로 지정한 뒤, 내일 이후 자동 실행 세션의 모델을 `get_session`으로 다시 확인한다.
2. CLI 최신화: 일일 루틴 보고서에 업데이트 명령이 나오면 실행한다. 승인 필요. 확인: `claude --version`.
   ```bash
   npm install -g @anthropic-ai/claude-code@latest
   ```
   (첫 컴퓨터는 `--prefix "C:/Users/edn_y/AppData/Roaming/npm"`이 필요했다.)
3. Archify: 다이어그램이 필요할 때만 (섹션 5).
4. Ponytail: 설치하지 않는다 (섹션 5).
5. 프로젝트 셋업·최적화 (`PLAN.md` phase 7): 별도 계획으로. 컨텍스트에서 큰 비중은 시스템 도구와 MCP 도구이며 Chrome 연동·Browser 도구가 많다. 쓰지 않는 커넥터를 끄는 것이 후보다.
6. `reports/` 버전 관리: 현재 로컬 전용으로 결정함 (섹션 10).
7. `scripts/reset-claude.ps1`을 다른 OS·컴퓨터에서 쓸 일이 생기면 경로를 일반화한다 (지금은 하드코딩).

## 8. 링크 모음

| 용도 | URL |
|---|---|
| Claude Code 변경 로그 (공식, 최종 기준) | https://code.claude.com/docs/en/changelog |
| Anthropic 뉴스 (공식) | https://www.anthropic.com/news |
| 이 저장소 | https://github.com/DevCrop/claude-global |
| Archify (설치 전 검토) | https://github.com/tt-a1i/archify |
| 입문 가이드 글 (X, 2026-09-28, @dravenip) | https://x.com/dravenip/status/2104402058963026288 |

입문 가이드 글 요약 (앱 내장 브라우저로 읽음):
- 구성: 에이전트 루프, 사용 환경 4가지, 컨텍스트 관리(`/clear`, `/compact`, 서브에이전트), 권한 모드(Shift+Tab), 짧은 `CLAUDE.md`, 탐색→계획→실행→검증, 확장(skills, commands, subagents, hooks, MCP, plugins), `-p` 비대화형 자동화, 보안·비용, 초보 실수 목록.
- 현재 세팅과 비교하면 짧은 `CLAUDE.md`, deny 규칙, 서브에이전트, 훅, 모델 구분, 비대화형 자동화가 이미 반영돼 있다. 새로 적용할 항목은 없었다.
- `/rewind`(Esc 두 번)가 `git reset --hard` 금지 규칙의 대안으로 쓸 만하다.
- 글 속 수치(연 매출, 커밋 비중)는 글쓴이가 인용한 것이고 출처를 확인하지 못했다.

## 9. 확인된 사실과 한계 (측정값 전부)

deny 규칙 시험:
- 명령 `rm -rf ~/__deny_test_nonexistent__`가 `Bash(rm -rf ~*)`에 걸려 거부됨. 대상이 없는 경로라 실패해도 피해가 없는 시험이다.
- 2026-10-09 추가 시험(격리 스크래치 저장소, `claude -p --settings`, 존재하지 않는 경로와 원격 없는 저장소만 사용, 모델 haiku). `permission_denials`로 판정:
  - 차단 확인: `rm -rf ~/x`, `rm -rf $HOME/x`, `git push --force`, `git push -f`, `git reset --hard`, `git clean -fd`, `git checkout .`, `git restore .`, `git restore --staged .`, `git checkout -- f`, `Read .env`.
  - 우회 발견 2건(차단 안 됨): `rm -fr ~/x`, `git push origin main --force`(플래그가 뒤). 이후 패턴 8개를 추가해 두 건과 `git push origin main -f`가 모두 차단됨을 재확인했다.
  - 과차단 확인: `Bash(rm -rf /*)`의 `*`가 슬래시를 포함해 `rm -rf /tmp/x` 같은 모든 절대경로 삭제를 막는다. 결정 기록(위험 경로만 deny)의 의도보다 넓다. 유지할지 정해야 한다.
  - 미시험: `rm -rf /*` 자체와 `%USERPROFILE%*`(파괴적이라 실행하지 않음), `rm -r -f` 같은 다른 분리 플래그 변형, 변수나 따옴표를 거친 우회. deny 패턴 매칭은 완전한 방어가 아니다.

`/context` (모델 `claude-sonnet-5-5`, 첫 컴퓨터 세션):
- 전체 77.5k / 1m (8%). 시스템 프롬프트 4.3k, 시스템 도구 19.7k(+deferred 20.3k), MCP 도구 12.2k(+deferred 45.7k), MCP 서버 지침 733, Skills 7.9k, 메시지 31.6k, 여유 889.5k, 자동 압축 버퍼 33k.
- Memory files: `CLAUDE.md` 841토큰, `RTK.md` 151토큰. Custom agents: `explorer`(34), `reviewer`(41).
- 훅 자체는 `/context`에 나오지 않는다.

`/usage` 대체 조회 (앱 도구, 2026-10-08 시점):
- 플랜 Pro. 5시간 한도 4%, 주간 한도 0%, 추가 사용량(extra usage) 꺼짐(월 한도 20.00 USD).

하네스 QA (2026-10-09, 클라우드 컨테이너, `claude -p` 2.1.295, 이 리포의 설정을 `--settings`로 적용, 스크래치 저장소):
- 메인 모델: `model: sonnet`은 `claude-sonnet-5-5`로 해석됐다. 같은 호출에서 `claude-haiku-5-5` 토큰이 소량(입력 약 1.2k) 별도로 잡혔다. 내장 보조 작업으로 보이며 원인은 확인하지 못했다.
- 서브에이전트 라우팅: `explorer`와 `reviewer`가 각각 1회 spawn되고 완료됐다(`subagent_stats`). Haiku 토큰(입력 1337, 출력 1404)이 explorer 작업과 일치하고 Sonnet이 메인과 reviewer를 맡았다. 모델별 토큰이 에이전트별로 직접 귀속되지는 않아 explorer=Haiku는 추정에 가깝다.
- `omitClaudeMd`: 프로젝트 CLAUDE.md의 마커 줄을 reviewer는 인용했고 explorer는 보지 못했다. 동작 확인.
- advisor: 반복 호출에서 `iterations`에 `advisor_message`(모델 `claude-opus-5-5`)가 기록됐다. 입력 33,791토큰, 출력 754토큰, 비용 약 0.15 USD로 같은 호출의 메인 Sonnet 비용(약 0.04 USD)의 약 3.6배였다. 질문이 짧아도 시스템 프롬프트와 도구 정의를 포함한 전체 대화를 읽는다. CLAUDE.md의 "접근 확정 전, 반복 오류, 완료 전에 자문" 규칙을 모델이 충실히 따르면 작업당 여러 번 호출될 수 있다.
- effort: 같은 프롬프트에서 설정(high)은 thinking 105토큰, `--effort low`는 0토큰이었다. 설정이 low가 아님은 확인했지만 high인지 medium인지 구분하지는 못했다.
- rtk 미설치 + 실제 settings.json: `git status`는 정상 실행, `git push --force`는 차단.
- 한계: 모두 이 컨테이너(Linux)에서 `claude -p`로 한 시험이다. Windows, Mac, 대화형 세션, 실제 RTK 바이너리는 시험하지 못했다. 앱의 루틴 예약 실행도 시험하지 못했다.

RTK 절감 (시점별로 값이 다르다):
- 99회 시점: 입력 5.9K, 출력 3.5K, 절감 2.5K (42.8%). 절감은 거의 `git status`(2.3K, 26회, 56.1%)에서 나왔다. `git diff` 171(37.3%), `ls -la` 68(71.6%), 나머지 약 49회는 0이다.
- 158회 시점(2026-10-09 재측정): 입력 11.5K, 출력 9.0K, 절감 2.7K (23.1%).
- 해석: 표본이 작고 작업 종류에 따라 절감이 갈린다. 초기의 42.8%를 기대값으로 삼지 말고, `rtk gain`으로 누적 수치를 직접 본다.
- 훅 동작 확인: `git status` 1회에 Total commands가 99에서 100으로 증가.

미확인:
- 루틴이 Sonnet으로 "고정"됐는지. 첫 자동 실행이 sonnet-5-5였다는 것만 확인했다 (섹션 6).
- 첫 자동 실행이 09:03에 못 돌고 11:37에 돈 정확한 원인.
- 새 컴퓨터에서의 모든 단계. 이 문서는 읽어서 검토했을 뿐 새 컴퓨터에서 실행해 보지 않았다.
- 입문 가이드 글의 수치와 외부 URL 유효성.

## 10. 사용자 결정 기록

- 일반 `rm -rf *`를 deny에 추가하지 않는다. 전부 막으면 명시적으로 요청한 정리도 막힌다. 위험 경로(`/*`, `~*`, `$HOME*`, `%USERPROFILE%*`)만 deny다.
- `HANDOFF.md`(첫 컴퓨터의 로컬 인계 메모)는 커밋하지 않는다. 내용은 이 문서에 흡수됐다. `.gitignore`에도 없으니 `git add .`로 실수로 올리지 않도록 주의한다.
- `reports/`는 로컬 전용(`.gitignore`)으로 유지한다.
- Ponytail은 설치하지 않는다. Archify는 요청 시에만, 검토 후 승인받고 설치한다.
- 루틴 모델은 첫 실행만 Haiku, 이후 Sonnet.
- `/context`, `/usage` 같은 슬래시 명령은 사용자가 직접 실행해야 한다 (대화형 UI 명령).

## 11. 함정과 주의사항

- x.com은 자동 fetch에 HTTP 402를 돌려준다. 앱 내장 브라우저로는 열린다. 공식 정보의 기준은 섹션 8의 공식 링크다.
- PowerShell 도구가 막힌 세션이 있었다. Bash와 Windows 경로를 쓴다. JSON 확인은 Node와 `cygpath -w`를 쓴다. Windows용 Python은 `/c/...` 형태의 경로를 읽지 못한다.
- 프로세스 확인 시 `--chrome-native-host`는 제외한다 (Chrome이 띄우며, 리셋 스크립트도 `chrome/`을 지우지 않는다).
- push는 자동 모드 분류기가 거부할 수 있다. 사용자가 채팅에서 명시적으로 승인해야 한다. `git push origin main`만 쓰고 force는 쓰지 않는다.
- `.credentials*`, `.env*`는 읽지도 커밋하지도 않는다.
- `PLAN.md`는 원래 계획이다. 실제와 다른 곳(전체 삭제 리셋)은 `PLAN.md` 상단의 정정 메모와 이 문서를 따른다.
- 예약 작업 `SKILL.md`(첫 컴퓨터 라이브와 저장소 참조본 모두 원본에서 `routines/` 경로 표기가 틀려 있었다). 저장소 참조본은 `claude/routines/daily-update.md`로 고쳤다. 라이브 쪽은 아직 원본 그대로이며 동작에는 영향이 없다 (본문이 곧바로 올바른 경로로 보정한다).

- RTK 훅과 deny 규칙: 공식 문서상 권한 규칙은 훅이 돌려준 입력을 기준으로 평가되고, RTK는 Bash 명령을 `git status` -> `rtk git status`로 다시 쓴다. 2026-10-09 시뮬레이션 QA(RTK 대신 같은 방식으로 `rtk ` 접두어를 붙이는 모의 훅과 스텁 `rtk`)에서 원래 deny 패턴은 `rtk git push --force origin main`, `rtk git reset --hard HEAD`, `rtk rm -fr ~/x`를 막지 못했고 명령이 실제 실행됐다(훅이 `allow`를 돌려주든 안 주든 동일). Bash deny 패턴 25개를 `rtk ` 접두어로 복제해 53개로 늘린 뒤 같은 시험에서 전부 차단됐고, 대조군 `git status`는 정상 실행됐다. 실제 RTK 바이너리로는 아직 시험하지 못했다(컨테이너에서 `rtk-ai/rtk` 접근 불가). RTK가 설치된 머신에서 스크래치 저장소로 `git push --force`, `git reset --hard HEAD`가 차단되는지 한 번 확인한다.
- deny/ask 규칙은 보안 경계가 아니다(공식 permissions 문서). `/bin/rm -rf`, `bash -c '...'`, `git -C . push`처럼 다른 형태의 호출은 못 막는다. 명령 텍스트와 무관한 강제는 샌드박스(`/sandbox`)로 한다. 샌드박스는 기본 꺼짐이고 macOS, Linux, WSL2에서만 동작하며 네이티브 Windows에서는 명령이 샌드박스 없이 실행된다.
- 공식 비용 문서 권장 중 미적용: 상태줄로 컨텍스트 사용량 상시 표시(스크립트 필요, 보류), 미사용 MCP 서버 비활성화(`/mcp`, 사용자 조치), 프롬프트 제안 끄기(배경 토큰 소량, 선택).

## 12. 저장소 이력

- `aac7c5c` feat: global Claude setup v1 (rules, settings, agents, daily routine)
- `ff85572` chore: default model to sonnet; partial legacy reset script
- `558b4b4` fix: reset script ignores Chrome bridge and keeps chrome/
- `47a2263` chore: sync RTK hook into repo settings and add routine baseline
- `0ff4efe` docs: routine model note (first run Haiku by decision, later Sonnet)
- `0757a18` docs: add next-machine handoff and scheduled task reference
- 그 이후: 이 보강판 커밋 (`git log`로 확인)
