# 다른 컴퓨터에서 이어서 세팅하기

작성일: 2026-10-09. 이 문서 하나로 지금까지의 결정, 링크, 루틴, 남은 작업을 이어받을 수 있다.
언어 규칙: 사용자에게는 한국어로 답한다. 코드·경로·명령은 원문 그대로 둔다.

## 1. 한눈에 보기

| 항목 | 상태 |
|---|---|
| 전역 규칙 `claude/CLAUDE.md`, `RTK.md` | 완료, 첫 컴퓨터에 적용됨 |
| `claude/settings.json` (sonnet, deny 20개, RTK 훅) | 완료, deny 동작 확인됨 |
| 에이전트 `reviewer`, `explorer` | 완료, `/context`에서 인식 확인 |
| RTK 0.50.0 | 완료, 훅 동작 확인 (명령 카운트 99 → 100) |
| 일일 루틴 `daily-claude-update` | 완료, 수동 실행 1회 성공 |
| 모델을 Sonnet으로 (루틴) | 미완, 앱 UI에서 사용자가 설정 |
| CLI 2.1.294 | 대기, npm 최신이 2.1.293 |
| Archify | 미설치, 다이어그램 요청 시 |
| Ponytail | 미설치, 의도적 보류 |
| 프로젝트 셋업·최적화 | 나중 단계 |

소스 오브 트루스는 이 저장소(`DevCrop/claude-global`, branch `main`)다. 라이브 설정은 `~/.claude`이며 `claude/` 폴더에서 복사해 만든다.

## 2. 새 컴퓨터 세팅 순서

각 단계 끝에 확인 방법이 있다. 확인되기 전에 다음 단계로 넘어가지 않는다.

1. Claude Code 설치 후 로그인한다. 자격 증명은 저장소에 없다. 새로 로그인해야 한다.
   - 확인: `claude --version`이 2.1.293 이상.
2. 저장소를 받는다.
   ```bash
   git clone https://github.com/DevCrop/claude-global.git
   ```
3. 기존 `~/.claude`가 있으면 먼저 백업한다. 덮어쓰기 전에 차이를 본다.
   - `claude/CLAUDE.md` → `~/.claude/CLAUDE.md`
   - `claude/RTK.md` → `~/.claude/RTK.md`
   - `claude/settings.json` → `~/.claude/settings.json`
   - `claude/agents/` → `~/.claude/agents/`
   - 확인: Claude 세션에서 `/context`의 Memory files에 `CLAUDE.md`, `RTK.md`가 보이고 Custom agents에 `explorer`, `reviewer`가 보인다.
4. RTK를 설치한다. Windows 기준:
   ```bash
   winget install rtk-ai.rtk
   ```
   - `settings.json`에 이미 RTK 훅(`rtk hook claude`)이 들어 있다. `rtk init -g`를 실행하면 설정이 바뀔 수 있으니 실행 전후 `settings.json` 차이를 비교한다.
   - `rtk`가 PATH에 있어야 훅이 동작한다. 새 터미널·앱 재시작 후 `rtk --version`으로 확인한다.
   - 확인: Bash 명령 몇 개 실행 뒤 `rtk gain`의 Total commands가 늘어난다.
5. 예약 루틴을 만든다 (4번 항목 참고, 경로 수정 필요).
6. 아래 "남은 작업"을 순서대로 진행한다.

## 3. 규칙 요약 (`claude/CLAUDE.md`와 동일, 원문이 우선)

- 한국어 응답. 요청을 먼저 되풀이하고, 모호하면 2~3개 해석을 제시.
- 요청한 것만 바꾼다. 3단계 이상이면 번호 계획과 완료 기준을 먼저 쓴다.
- 완료 선언은 명령 결과·테스트·출처 확인으로만 한다.
- 단일 에이전트로 시작. 분리는 컨텍스트 경계(기능+테스트)로. 검증은 별도 `reviewer`가 한다. 같은 오류는 2회까지만 재시도.
- 금지: `.credentials*`, `.env*` 읽기·커밋. 승인 없는 force push, `reset --hard`, `git clean`, `rm -rf`. 외부 공개·push는 승인 후.

## 4. 예약 루틴 `daily-claude-update`

- 목적: Claude Code 변경 로그와 Anthropic 뉴스를 매일 확인하고 보고서만 쓴다. 설정은 절대 바꾸지 않는다.
- 일정: cron `0 9 * * *` (로컬 09:00, 실제 약 09:03에 시작).
- 정의 파일: `claude/routines/daily-update.md` (단계·출력 형식), `claude/scheduled-tasks/daily-claude-update/SKILL.md` (예약 작업 본문).
- 출력: `reports/YYYY-MM-DD.md` (로컬 전용, `.gitignore`에 있음), 상태 `state/last-seen.json` (추적됨).
- 제한: 앱이 켜져 있을 때만 실행된다. 예약 도구에는 모델 필드가 없다.
- 새 컴퓨터에서 만들기:
  1. Claude 앱의 예약 작업 기능으로 `daily-claude-update`를 만들고 본문에 `SKILL.md` 내용을 넣는다.
  2. `SKILL.md` 안의 `D:\project\claude-global`과 `C:\Users\edn_y\.claude` 경로를 새 컴퓨터의 실제 경로로 바꾼다.
  3. 모델은 앱의 Scheduled 화면에서 Sonnet으로 지정한다. 첫 실행은 결정에 따라 Haiku였다.
  4. 한 번 수동 실행해 보고서가 생기는지 확인한다.
- 같은 루틴을 두 컴퓨터에서 켜면 보고서가 중복된다. 한쪽만 켜는 것을 권장한다.

## 5. 남은 작업 (순서대로)

1. 루틴 모델을 Sonnet으로 설정 (앱 UI). 다음 자동 실행 세션의 모델이 sonnet인지 확인한다.
2. CLI 2.1.294: npm에 올라오면 업데이트. 승인 필요.
   ```bash
   npm install -g @anthropic-ai/claude-code@latest
   ```
   Windows 첫 컴퓨터는 `--prefix "C:/Users/edn_y/AppData/Roaming/npm"`을 썼다. 확인: `claude --version`.
3. Archify: 다이어그램이 필요할 때만. 설치 전 `SKILL.md`를 읽어 검토하고 승인받는다.
   ```bash
   npx skills add tt-a1i/archify -g
   ```
   현재 흐름도는 앱 내장 시각화로 그렸다.
4. Ponytail: 설치하지 않는다. 매 세션 상시 지침이 추가되므로 프로젝트별로만 재검토한다.
5. 프로젝트 셋업·최적화 (`PLAN.md` phase 7): 별도 계획으로. 컨텍스트에서 큰 비중은 시스템·MCP 도구(약 50k)이며 Chrome 연동, Browser 도구가 많다. 쓰지 않는 커넥터를 끄는 것이 후보다.
6. `rm -rf` deny 확장 여부: 현재는 `/*`, `~*`, `$HOME*`, `%USERPROFILE%*`만 deny. 일반 경로는 권한 프롬프트에 의존한다. 일반 `rm -rf *`까지 deny로 막으면 명시적으로 요청한 정리도 막히므로 현재는 추가하지 않기로 했다.

## 6. 링크 모음

| 용도 | URL |
|---|---|
| Claude Code 변경 로그 (공식, 최종 기준) | https://code.claude.com/docs/en/changelog |
| Anthropic 뉴스 (공식) | https://www.anthropic.com/news |
| 이 저장소 | https://github.com/DevCrop/claude-global |
| Archify (설치 전 검토) | https://github.com/tt-a1i/archify |
| 입문 가이드 글 (X, 2026-09-28, @dravenip) | https://x.com/dravenip/status/2104402058963026288 |

가이드 글은 자동 fetch가 아니라 앱 내장 브라우저로 읽었다. 내용은 입문 수준이고 현재 세팅이 이미 대부분 반영한다 (짧은 `CLAUDE.md`, deny 규칙, 서브에이전트, 훅, 모델 구분, 비대화형 자동화). 글 속 수치(연 매출, 커밋 비중)는 출처를 확인하지 못했다. 새로 적용할 항목은 없었고, `/rewind`가 `git reset --hard` 금지 규칙의 대안으로 쓸 만하다는 정도다.

## 7. 확인된 사실과 한계

- 확인됨: deny 규칙 동작(`rm -rf ~/...` 거부), `/context` 결과(모델 sonnet-5-5, `CLAUDE.md` 841토큰, `RTK.md` 151토큰, 에이전트 2개, 전체 77.5k/1m), RTK 훅 동작, `origin/main` push 완료.
- RTK 절감 42.8% (입력 5.9K, 출력 3.5K, 99회 기준)는 표본이 작다. 절감은 거의 `git status`(2.3K)에서 나왔다. 장기 수치가 나와야 판단 가능하다.
- 아직 확인 못 함: 루틴이 Sonnet으로 도는지, 나머지 deny 규칙 19개의 개별 동작, 새 컴퓨터에서의 모든 단계.

## 8. 주의할 점

- x.com은 자동 fetch에 HTTP 402를 돌려준다. 앱 내장 브라우저로는 열린다. 공식 정보의 기준은 위 공식 링크다.
- PowerShell 도구가 막힌 세션이 있었다. Bash와 Windows 경로를 쓴다. JSON 확인은 Node와 `cygpath -w`를 쓴다.
- 데스크톱 앱은 자체 claude-code를 번들한다. npm CLI와 별개다.
- 프로세스 확인 시 `--chrome-native-host`는 제외한다 (Chrome이 띄운다).
- 첫 컴퓨터의 백업(`D:\backup\...`)은 저장소에 없다. 대화 기록·자격 증명은 옮기지 않는다.
- `.credentials*`, `.env*`는 읽지도 커밋하지도 않는다.
