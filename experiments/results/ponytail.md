# 실행 결과 — ponytail

실험설계: [`experiments/design/ponytail.md`](../design/ponytail.md)

픽스처: `fixtures/bookmarks-api` (`bookmarks-api-baseline` 태그). 티켓 두 개, 조건당 3회씩(OFF/ON), 각 세션은 `Agent(isolation: "worktree")`로 `bookmarks-api-baseline`에서 격리 실행.

- **티켓 A** — 태그 추가 + `?tag=` 필터링. 순수 backend CRUD 확장, over-build trap 없음.
- **티켓 B** — 리마인드 날짜(`remind_at`) 추가. ponytail 저자 벤치마크의 date-picker 사례를 이 픽스처에 맞춰 옮긴, over-build trap이 있게 설계한 티켓. (티켓 A 실행 후 설계 검토 결과 추가됨 — 아래 "설계 검토" 참고.)

> ⚠️ **읽기 전 확인**: 아래 결과를 해석하기 전에 "활성화 검증" 절을 먼저 읽을 것. `Agent(isolation: "worktree")`로 띄운 ON 조건 서브에이전트들이 ponytail 룰셋을 실제로 주입받았는지 자체가 불확실하다 — 확실하다면 OFF/ON 비교가 무효(사실상 off vs off)였을 위험이 있다.

## 총괄 요약 (평균, n=3, 두 티켓)

| 티켓 | 지표 | OFF | ON | 차이 |
|---|---|---:|---:|---:|
| A (태그+필터) | subagent_tokens | 52,724 | 55,374 | **+5.0%** |
| A | tool_uses | 22.0 | 27.0 | **+22.7%** |
| A | LOC 삽입(+) | 175.3 | 234.3 | **+33.7%** |
| B (리마인드 날짜) | subagent_tokens | 49,244 | 51,177 | **+3.9%** |
| B | tool_uses | 24.7 | 24.0 | −2.7% |
| B | LOC 삽입(+) | 154.3 | 161.7 | **+4.8%** |

두 티켓 모두 ON이 OFF보다 `subagent_tokens`가 더 컸다(방향은 같지만 티켓 B에서 격차가 훨씬 작아짐 — 아래 판정 참고). LOC도 두 티켓 모두 ON이 더 크다. tool_uses만 티켓 B에서 방향이 뒤집혔다(거의 동률, ON이 약간 낮음).

**티켓 B 정성 관찰**: over-build trap(날짜 선택 UI)을 설계에 넣었음에도, **OFF/ON 6세션 전원이 네이티브 `<input type="date">`를 사용**했다 — 커스텀 캘린더 위젯이나 날짜 라이브러리를 추가한 세션은 하나도 없었고, `requirements.txt`도 6세션 전부 변경 없음. ponytail 저자의 date-picker 사례(baseline이 flatpickr 등을 설치, 404→23 LOC)에서 가정한 "베이스라인이 라이브러리로 과잉설계한다"는 전제 자체가 이번 실험의 모델(Sonnet 계열)에서는 성립하지 않았다.

## 판정

핵심 질문("ponytail을 켜면 토큰 사용량이 실제로 줄어드는가?")에 대해, 두 티켓 모두 **가설과 반대이거나 유의미한 차이가 없는 방향**의 신호가 나왔다. 다만 원인은 티켓별로 다르게 해석해야 한다.

- **티켓 A**: 애초에 over-build trap이 없는 순수 backend CRUD 티켓이었다(설계 검토 참고) — ponytail이 잘라낼 과잉설계 자체가 없는 조건에서 측정한 것이므로, "ponytail이 효과 없다"보다는 "이 조건은 ponytail의 주장을 테스트할 무대가 아니었다"는 해석이 맞다.
- **티켓 B**: over-build trap을 의도적으로 설계했음에도 OFF 조건조차 이미 네이티브 `<input type="date">`를 선택했다 — 즉 **이번 실험에 쓰인 모델은 ponytail 없이도 이미 저자가 말하는 "lazy 선택"을 기본으로 한다.** 이는 ponytail 저자 스스로 명시한 한계("Bigger models may close the over-build gap")와 정확히 일치하는 결과다. 두 조건이 이미 같은 최소 구현에서 출발하니 ON이 더 잘라낼 게 없고, 남은 차이(+3.9% 토큰, +4.8% LOC)는 세션 간 자연 변동(테스트 개수 등)에 가깝다.

**종합**: 이 실험(작은 FastAPI+SQLite 픽스처, Sonnet 계열 모델, n=3×2×2티켓)에서는 ponytail의 "토큰 사용량 감소" 주장이 재현되지 않았다. 그러나 이것이 ponytail이 효과가 없다는 증거는 아니다 — 오히려 **효과가 나타나려면 필요한 두 전제조건(① over-build trap이 실제로 존재하는 티켓, ② 그 트랩에 빠질 만큼 상대적으로 약한 모델)** 중 최소 하나가 이번 실험 환경에는 없었다는 게 더 정확한 결론이다. 저자 자신의 agentic 벤치마크(Haiku 4.5, 실제 대형 오픈소스 레포)도 동일한 구조를 보여준다: backend CRUD는 arm 간 거의 차이 없고, 효과는 프론트엔드 컴포넌트 라이브러리 함정에서만 크게 난다.

## 설계 검토 (티켓 A → B로 이어진 경위)

티켓 A 실행 직후 결과가 가설과 반대로 나와, ponytail 저장소의 실제 agentic 벤치마크(`benchmarks/results/2026-06-18-agentic.md`, 저자 자체 발표, Haiku 4.5·`tiangolo/full-stack-fastapi-template` 대상)를 재확인했다. 핵심 발견:

- 저자 데이터에서도 backend CRUD 티켓은 arm 간 거의 차이 없음("search items by title" 44→44 LOC, 0%). 효과는 에이전트가 커스텀 컴포넌트/라이브러리를 설치하려는 지점에 집중(date picker −94%, color picker −92%).
- 저자 스스로 "이미 최소한인 코드에서는 효과가 0에 가깝다"고 명시.
- 티켓 A는 순수 backend CRUD + 라이브러리 선택 여지 없는 단순 필드 추가였다. 실측으로도 6개 worktree 전부 의존성 변경 없음 — 애초에 잘라낼 과잉설계가 없었다.

이에 따라 저자 벤치마크의 date-picker 사례를 옮긴 **티켓 B**(리마인드 날짜)로 재실험했다. 조건·표본 규모·지표는 티켓 A와 동일. worktree 스냅샷 이슈(아래)에 대응하기 위해 이번엔 프롬프트에 "필요하면 `git checkout bookmarks-api-baseline -- fixtures/bookmarks-api`로 복구하라"는 안내를 OFF/ON 모두에 동일하게 추가해 표준화했다.

## 실행별 지표

### 티켓 A

| 세션 | 조건 | subagent_tokens | tool_uses | duration_ms | 테스트 결과 | LOC(+/-) |
|---|---|---:|---:|---:|---|---:|
| OFF-1 | ponytail off, caveman off | 53,313 | 21 | 334,043 | 7 passed | +183/-11 |
| OFF-2 | ponytail off, caveman off | 51,746 | 23 | 253,283 | 7 passed | +199/-12 |
| OFF-3 | ponytail off, caveman off | 53,114 | 22 | 265,422 | 5 passed | +144/-12 |
| ON-1 | ponytail on, caveman off | 55,133 | 23 | 19,197,800† | 7 passed | +186/-16 |
| ON-2 | ponytail on, caveman off | 52,626 | 27 | 19,374,669† | 10 passed | +256/-15 |
| ON-3 | ponytail on, caveman off | 58,362 | 31 | 19,184,953† | 9 passed | +261/-17 |

† ON 조건 3회 모두 `duration_ms`가 OFF 대비 약 70배(19,000,000ms대) 튀었다. 세 값이 서로 거의 같고, 같은 시간대에 실행되어 세션이 오래 대기한 벽시계 시간(예: 컴퓨터 유휴/절전)이 섞여 들어간 것으로 보고 이 열은 참고용에서 제외했다. `subagent_tokens`는 OFF와 같은 범위라 오염되지 않은 것으로 판단.

### 티켓 B

| 세션 | 조건 | subagent_tokens | tool_uses | duration_ms | 테스트 결과 | LOC(+/-) | date UI |
|---|---|---:|---:|---:|---|---:|---|
| OFF-B-1 | ponytail off, caveman off | 48,622 | 22 | 185,758 | 8 passed | +190/-6 | native `<input type="date">` |
| OFF-B-2 | ponytail off, caveman off | 50,322 | 28 | 218,155 | 8 passed | +140/-7 | native |
| OFF-B-3 | ponytail off, caveman off | 48,788 | 24 | 199,682 | 8 passed | +133/-5 | native |
| ON-B-1 | ponytail on, caveman off | 48,995 | 22 | 147,860 | 8 passed | +175/-14 | native |
| ON-B-2 | ponytail on, caveman off | 50,697 | 24 | 278,346 | 8 passed | +147/-7 | native |
| ON-B-3 | ponytail on, caveman off | 53,839 | 26 | 191,559 | 9 passed | +163/-7 | native |

티켓 B에서는 `duration_ms`가 모든 세션에서 정상 범위(15만~28만 ms)였다 — 티켓 A에서 관찰된 ON 조건 벽시계 오염은 이번엔 재현되지 않았다(우연히 그 시간대에 컴퓨터가 유휴 상태였을 가능성이 높다는 추정을 뒷받침).

## 활성화 검증 (2026-08-12 추가) — 중대한 미해결 리스크

이전 버전에 남겨둔 "검증 공백"(ON 세션 12개 전부에서 `ponytail:` 주석 마커가 없었음)을 직접 확인하기 위해, 코드 작업 없이 진단만 하는 서브에이전트를 OFF/ON 각 1회(worktree 격리, `Agent` 도구) 띄워 자기 컨텍스트를 점검하게 했다.

- **OFF (1회)**: `enabledPlugins.ponytail@ponytail: false` 정확히 읽힘. 룰셋 텍스트 없음(스킬 카탈로그의 한 줄 설명만 존재). `~/.claude/.ponytail-active` 마커 파일에 `full`이 남아있었음(이전 세션의 잔재로 추정, 이 시점 설정과 불일치).
- **ON (1회)**: `enabledPlugins.ponytail@ponytail: true` 정확히 읽힘. 마커 파일도 `full`. **하지만 OFF와 마찬가지로 룰셋 텍스트는 여전히 없음** — 래더 나열, "ACTIVE EVERY RESPONSE" 배너, 무허가 추상화 금지 같은 규칙 어디에도 없고 스킬 카탈로그 한 줄 설명뿐이었음.
- `node`는 PATH에 정상 존재(v22.23.2) — README가 언급하는 "node 미존재 시 조용히 무주입" 실패 모드는 아니었다.
- `.ponytail-active` 마커의 타임스탬프(2026-08-11 23:11)는 이 대화에서 티켓 A ON 조건을 처음 켰던 시점과 일치한다 — 즉 훅 자체가 그 시점엔 최소 한 번 발동해 상태 파일을 남겼다. 그런데도 이번 진단 서브에이전트 둘 다 룰셋 주입을 못 봤다는 건, "훅이 상태 파일은 쓰지만 이 방식으로 spawn된 worktree 서브에이전트의 시스템 프롬프트에는 룰셋을 주입하지 않는다"는 뜻일 수 있다.
- 참고 정황: 이 대화 맨 처음, `superpowers`가 전역 `enabledPlugins.superpowers: false`였는데도 메인 세션에는 "SessionStart hook additional context: You have superpowers..."가 실제로 주입됐다 — 훅 발동 여부가 `enabledPlugins` 값과 항상 일치하지는 않는다는 별개의 정황 증거.

**결론**: `enabledPlugins` 값 자체가 서브에이전트 프로세스에 정확히 반영된다는 것은 이제 확실하다. 그러나 **`Agent(isolation: "worktree")`로 띄운 서브에이전트가 ponytail의 "항상-켜짐 룰셋 주입" 훅을 실제로 받는지는 이번 진단으로도 확인되지 않았고, 오히려 받지 않을 가능성이 있다는 쪽으로 근거가 늘었다.** 이게 사실이라면 위 티켓 A/B의 ON 조건 12세션 전부가 실제로는 ponytail 룰셋 없이(다만 스킬 카탈로그에 설명이 있으니 모델이 과제 관련성을 보고 자발적으로 `Skill` 도구를 호출했을 가능성은 남아있다) 실행됐을 수 있다는 뜻이며, 그렇다면 위 "판정" 절의 OFF/ON 비교는 사실상 "off vs off"였을 위험이 있다. 이 리스크는 이번 진단(코드 작업 없는 1회씩)만으로는 완전히 해소되지 않는다 — 확실히 하려면 실제 코딩 티켓을 수행하는 세션 안에서 모델이 `ponytail` 스킬을 실제로 호출했는지(트랜스크립트에서 `Skill` 도구 호출 여부 확인) 별도로 검증해야 한다.

## 방법론 메모 / 한계

- **worktree 스냅샷 시점**: `Agent(isolation: "worktree")`가 만드는 worktree는 이 대화 세션이 시작된 시점의 저장소 상태를 기준으로 분기된다(baseline 커밋/태그는 세션 도중에 만들어졌으므로 초기 worktree에는 반영되지 않았다). 티켓 A의 6세션 중 5세션은 에이전트가 자체적으로 `git checkout bookmarks-api-baseline -- fixtures/bookmarks-api`로 복구했고, 1세션(최초 OFF-1)은 이를 알아채지 못해 CRUD API 전체를 처음부터 새로 작성(범위가 완전히 다름)해 폐기하고 재실행했다. 티켓 B부터는 프롬프트에 복구 안내를 명시해 6세션 전원이 동일하게 대응했다. 이 복구 단계는 OFF/ON 모두에 동일하게 발생해 조건 간 비교를 왜곡하지는 않지만, 각 세션의 절대 토큰 수치에는 복구 비용이 몇 천 토큰 수준 섞여 있다.
- **duration_ms 신뢰성**: 티켓 A의 ON 조건 3회에서만 벽시계 유휴 시간으로 추정되는 이상치(19,000,000ms대)가 나타났다. 티켓 B는 정상 범위였다. 조건-특이적 현상이 아니라 우연한 시간대 문제로 보고, 반복 실행 시 항상 검산 필요.
- **활성화 직접 검증 불가**: ON 조건에서 ponytail이 서브에이전트 프로세스에 실제로 반영됐는지는 결과물만으로 간접 확인할 수밖에 없다(`ponytail:` 주석 마커 유무 등). 두 티켓 12개 ON 세션 전부에서 `ponytail:` 마커가 하나도 없었다 — "자를 코너가 없어서"인지 "활성화가 안 됐는지" 결과물만으로는 구분 불가능하다는 검증 공백이 남는다.
- **모델 불일치**: ponytail 저자 벤치마크는 Haiku 4.5 고정, 이 실험은 기본 상속 모델(더 강한 모델). 저자도 "더 강한 모델일수록 격차가 줄어들 수 있다"는 한계를 인정했고, 티켓 B에서 OFF 조건조차 이미 네이티브 date input을 선택한 것이 바로 그 현상으로 보인다.
- **테스트 개수 재량 편차**: 세션마다 추가한 테스트 개수(티켓 A: 5~10개, 티켓 B: 5~6개)가 다르다 — 조건과 무관한 에이전트별 재량이며 LOC/토큰 차이의 상당 부분을 설명할 수 있다.
- **caveman을 두 조건 모두 꺼둔 것**: 변수 격리 원칙상 맞는 선택이지만, 사용자가 실제로 쓰는 조합(ponytail+caveman 둘 다 on)과는 다른 상태를 측정했다 — "실사용 조합에서의 전체 효과"는 별개 질문으로 남는다.
- **표본 크기**: 티켓당 n=3(OFF/ON 각 3회). 저자 벤치마크는 n=4×12티켓으로 훨씬 크다.
