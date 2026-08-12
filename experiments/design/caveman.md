# 실험설계 — caveman

## 핵심 질문

caveman(응답을 "caveman 말투"로 압축하는 스킬)을 켰을 때, **여러 archetype에 걸쳐 토큰 사용량이 실제로 줄고 품질 저하는 없는가**? (SKILLS_BACKLOG 원안 그대로.)

## 저장소 확인 결과 — 저자 스스로 밝힌 한계

`docs/HONEST-NUMBERS.md`(저자 자체 발표, 마케팅 없는 정직한 수치 문서)의 핵심 내용:

- **출력 토큰**: 평균 65% 감소(22~87% 범위) — 이건 진짜다.
- **입력 토큰**: 0% 감소 — caveman은 출력 스타일만 압축, 입력/컨텍스트/파일은 건드리지 않는다.
- **입력 비용 증가**: 턴당 ~1,000~1,500토큰(SKILL.md ~5KB가 컨텍스트에 주입되는 비용) — ponytail의 SKILL.md 로딩 비용과 같은 종류.
- **저자 스스로 명시**: "에이전틱 코딩에서는 입력 토큰(프롬프트·컨텍스트·파일·주입되는 규칙)이 출력 토큰을 압도한다" — 세션 전체 기준으로는 **14~21% 절감**(출력이 많은 워크로드), **터스(terse)한 코딩 Q&A에서는 오히려 순손실**. 한 Cursor 사용 사례는 caveman 켰을 때 토�큰이 4배 이상 늘어난 경우도 보고됨(재현은 안 됐지만 저자가 정직하게 실어둠).
- **트리거 조건이 ponytail과 다르다**: ponytail은 "ANY coding task"에 자동 트리거되지만, caveman의 SKILL.md description은 "사용자가 caveman mode/간결함을 요청할 때, 또는 토큰 효율이 요청될 때"로 더 좁다 — 일반 코딩 티켓("태그 기능 추가해줘", "버그 고쳐줘")만으로는 자연스럽게 트리거되지 않을 가능성이 높다.
- **활성화 메커니즘은 ponytail과 동일**: `plugin.json`에 Node.js 기반 SessionStart/UserPromptSubmit 훅이 인라인 선언돼 있다 — ponytail/superpowers 실험에서 확인한 대로 `Agent(isolation:"worktree")` 서브에이전트에는 자동 주입이 안 될 가능성이 높다.

이 실험은 저자가 스스로 예고한 "에이전틱 코딩에서는 세션 전체 절감폭이 작거나 마이너스일 수 있다"는 주장을 실측으로 검증하는 실험이 된다 — ponytail/superpowers처럼 저자의 자체 caveat이 우리 결과 해석의 기준선이 된다.

## 대상 archetype / 픽스처 / 티켓 — 기존 실험 재사용

SKILLS_BACKLOG 권장대로 caveman은 특정 archetype에 묶이지 않으므로, 이미 검증된 두 archetype·픽스처·OFF 데이터를 재사용한다(표본 규모 원칙 — 과도한 재실행 금지):

| Archetype | 픽스처/티켓 | 실행 메커니즘 | 재사용할 OFF 데이터 |
|---|---|---|---|
| 코드 생성/볼륨 | `bookmarks-api-baseline`, ponytail 티켓 A(태그+필터링) | `Agent(isolation:"worktree")` | ponytail 실험 OFF 3세션 (`subagent_tokens` avg 52,724) — [`ponytail.md`](ponytail.md) |
| 디버깅/프로세스 | `bookmarks-api-baseline-bug`, superpowers 버그 티켓(대소문자 정렬) | 헤드리스 `claude -p` CLI | superpowers 실험 OFF 3세션 (`cost_usd` avg 0.3416) — [`superpowers.md`](superpowers.md) |

두 OFF 데이터셋 모두 `caveman@caveman: false`로 실행됐으므로(각 실험이 변수 격리 원칙에 따라 caveman을 꺼뒀음) 그대로 유효한 대조군이다. **새로 실행하는 건 ON 조건뿐** — 조건당 3회, 총 6세션.

## 활성화 검증 (본 실행 전 필수)

ponytail·superpowers 경험상 훅 기반 플러그인은 실행 메커니즘마다 다르게 반응했다. 본 실행 전 각 메커니즘에서 1회씩 저비용 진단:

1. **`Agent(isolation:"worktree")` 경로**: 진단 전용 서브에이전트를 띄워 (a) `caveman` 룰셋 본문이 자동 주입되는지, (b) 안 된다면 `Skill` 도구로 `caveman:caveman`을 명시적으로 호출했을 때 로드되는지 확인.
2. **`claude -p` 경로**: `enabledPlugins.caveman: true`로 설정한 뒤 스모크 테스트(`claude -p "질문" --output-format json`)로 실제 응답이 caveman 스타일로 압축되는지, 그리고 `cache_creation_input_tokens` 증가폭(로딩 비용 추정치)을 확인.
3. 두 경로 모두 명시적 호출 없이도 되면 자연 상태로, 안 되면 최소한의 우회(명시적 `Skill` 호출 1회 또는 `/caveman` 커맨드)를 프롬프트에 추가해 본 실행 진행.
4. 이 진단도 전역 설정(`caveman`)을 건드리므로 시작 전 알린다.

## 조건

- **OFF**: 기존 데이터 재사용(위 표) — 새로 실행 안 함.
- **ON**: `enabledPlugins.caveman@caveman: true`, 나머지(`ponytail`, `superpowers`)는 false로 고정. 활성화 검증에서 결정된 방식(자연 발동 또는 명시적 호출)으로 각 archetype의 원래 티켓을 동일하게 실행.

## 표본 규모

archetype당 ON 3회, 총 6세션(신규 실행). OFF는 기존 6세션(각 archetype 3회씩) 재사용.

## 지표

- **Primary**: 세션 전체 토큰(archetype 1은 `subagent_tokens`, archetype 2는 `total_tokens`/`cost_usd` — 각 archetype의 기존 OFF 데이터와 동일한 정의 사용) — OFF 대비 몇 % 차이인지. 저자 주장(에이전틱 세션 14~21% 절감, 터스한 경우 마이너스)과 직접 비교.
- **Secondary — 품질 저하 여부(정성)**: caveman 자신의 규칙("never drop not/never/no/only/except", "errors quoted exact", "code blocks unchanged")을 기준으로, 코드 정확성(테스트 통과·근본 원인 수정 — 각 archetype의 기존 판정 기준 그대로 적용)과 커뮤니케이션 명확성(응답에서 부정어·정확한 값이 실수로 생략되지 않았는지)에 저하가 있는지 확인.
- **Secondary — 산문 압축률**: 세션 최종 응답(요약문)의 길이가 OFF 대비 얼마나 줄었는지(저자 주장 "출력 65% 감소"와 비교할 수 있는 유일한 축).

## 가설

저자 자신의 caveat("에이전틱 코딩에서는 입력이 출력을 압도해 절감폭이 작거나 마이너스")이 맞다면, 두 archetype 모두에서 세션 전체 토큰은 거의 변화 없거나 오히려 소폭 증가(로딩 비용 때문)하고, 최종 응답 산문 길이만 뚜렷이 줄어들 것으로 예상한다. 코드 정확성(테스트 통과, 근본 원인 수정)에는 차이가 없을 것으로 예상한다(caveman은 "코드 블록은 그대로 유지"를 명시).

## 검증 방법

- archetype 1: `git diff --stat`으로 LOC, `pytest` 결과로 정확성 확인(ponytail 검증 방법 재사용).
- archetype 2: `git log`·`git diff`로 근본 원인 수정 여부, 회귀 테스트를 `bookmarks-api-baseline-bug`에 적용해 실패 확인(superpowers 검증 방법 재사용).
- 두 archetype 모두: 세션 최종 응답 텍스트 길이(문자 수) 비교, 부정어/정확한 값 누락 여부 육안 검토.

## 리스크 / 한계

- **전역 설정 변경**: `caveman` on/off 토글이 전역 설정을 건드린다 — 활성화 검증·본 실행 각각 시작 전 알리고, 종료 후 원래 상태(`caveman: true`, `ponytail: true`, `superpowers: false`)로 복원.
- **기존 OFF 데이터 재사용의 전제**: 두 OFF 데이터셋이 실행됐을 때 caveman이 실제로 꺼져 있었다는 건 각 실험 설계상 보장되지만, 그 시점엔 caveman 활성화 여부를 직접 진단하지 않았다 — 다만 `enabledPlugins.caveman: false`였고 두 실험 모두 caveman 룰셋 흔적(말투 압축)이 응답에 없었다는 걸 결과 문서에서 육안으로도 확인 가능하다.
- **서로 다른 두 실행 메커니즘을 한 실험에서 섞음**: archetype 1은 `subagent_tokens`, archetype 2는 `cost_usd`/`total_tokens` — 단위가 달라 직접 비교는 안 되고, 각자 자기 OFF 대비 %로만 비교한다.
- **명시적 호출 조건이라면**: ponytail 때와 같은 한계 — "설치해두면 자동으로 얻는 효과"가 아니라 "명시적으로 켰을 때의 효과"일 수 있다.
