# 실행 결과 — ponytail

실험설계: [`experiments/design/ponytail.md`](../design/ponytail.md) · 종합 보고서: [`ponytail-report.md`](ponytail-report.md)

픽스처: `fixtures/bookmarks-api` (`bookmarks-api-baseline` 태그). 티켓 두 개, 조건당 3회씩(OFF/ON), 각 세션은 `Agent(isolation: "worktree")`로 `bookmarks-api-baseline`에서 격리 실행.

- **티켓 A** — 태그 추가 + `?tag=` 필터링.
- **티켓 B** — 리마인드 날짜(`remind_at`) 추가. ponytail 저자 벤치마크의 date-picker 사례를 이 픽스처에 맞춰 옮긴 티켓.

> ⚠️ **이 문서는 두 번의 실행 세대를 담고 있다.** 1세대(ON, 6세션)는 활성화 자체가 실패한 무효 데이터였다(아래 "활성화 검증" 참고). 2세대(ON-v2, 6세션)가 명시적 `Skill` 도구 호출로 실제 활성화를 확인한 유효한 재실행이다. **최종 판정은 OFF(1세대, 유효) vs ON-v2(2세대, 유효) 비교를 기준으로 한다.**

## 최종 판정 (OFF vs ON-v2)

| 티켓 | 지표 | OFF | ON-v2 | 차이 |
|---|---|---:|---:|---:|
| A (태그+필터) | subagent_tokens | 52,724 | 53,126 | +0.8% |
| A | tool_uses | 22.0 | 20.7 | −6.1% |
| A | LOC 삽입(+) | 175.3 | 89.0 | **−49.2%** |
| B (리마인드 날짜) | subagent_tokens | 49,244 | 53,533 | +8.7% |
| B | tool_uses | 24.7 | 22.7 | −8.1% |
| B | LOC 삽입(+) | 154.3 | 101.3 | **−34.4%** |

**핵심 질문("ponytail을 켜면 토큰 사용량이 실제로 줄어드는가?")에 대한 답: 아니오, 적어도 이 실험에서는 아니다 — 하지만 코드량은 확실히 줄어든다.** 두 티켓 모두 LOC이 -34~-49% 감소했고(저자 주장 "~54% less code"와 근접), `tool_uses`도 소폭 감소했다. 그러나 `subagent_tokens`는 거의 그대로(A)이거나 오히려 늘었다(B, +8.7%). 코드가 짧아진 만큼 "왜 이렇게 잘랐는지"를 설명하는 추론·프로즈(`ponytail:` 주석, "skipped: X, add when Y" 요약, 래더를 따라가는 사고 과정)에 토큰이 들어간 것으로 보이며, 이는 ponytail 저장소가 스스로 명시한 한계("a terse reasoning model that spends thinking tokens deliberating the rungs can go the other way")와 정확히 일치한다.

### 정성적 근거 — 실제로 다르게 행동했다

ON-v2에서만 관찰된 구체적 변화:

- **티켓 A**: 3세션 중 2세션이 태그를 별도 join 테이블이 아니라 **콤마로 이어붙인 문자열 컬럼**으로 구현(OFF 6세션 전원이 join 테이블 사용). 그중 1세션은 `app/main.py`에 실제 `ponytail:` 주석으로 한계와 업그레이드 경로를 명시. 나머지 1세션은 join 테이블을 택했지만 "콤마+부분일치 방식은 엣지케이스(태그명에 콤마 포함, `art`가 `cart`에 오탐)에서 부정확하다"는 ponytail 규칙("같은 크기면 정확한 쪽을 택하라")에 근거해 명시적으로 정당화.
- **티켓 B**: 3세션 중 2세션이 범용 편집(PUT, url/title/remind_at 전체 교체) 대신 **`remind_at` 하나만 다루는 좁은 PATCH 엔드포인트**를 만들고 "일반 편집 기능은 스킵, 실제 필요할 때 추가"라고 명시(OFF 6세션 대부분은 범용 PUT/PATCH 엔드포인트로 확장).
- 6세션 전원이 세션 시작 직후 실제 ponytail 룰셋 텍스트("ACTIVE EVERY RESPONSE", 래더 7단계)를 인용해 로드를 확인했다.

## 활성화 검증 — 왜 재실행이 필요했는가

티켓 A/B의 **1세대 ON 조건(6세션)은 무효였다.** `enabledPlugins.ponytail@ponytail`을 전역 설정에서 토글하는 것만으로 `Agent(isolation: "worktree")` 서브에이전트에 ponytail의 "항상-켜짐" 룰셋이 주입될 것이라 가정했으나, 진단 결과 이 가정이 틀렸다:

- OFF/ON 각 1회(진단 전용, worktree), OFF/ON 각 1회(실제 코딩 작업, worktree), ON 1회(worktree 격리 없음), 총 5회 진단에서 **`enabledPlugins` 값 자체는 서브에이전트에 정확히 전달됐지만, 실제 룰셋 텍스트는 5회 모두 주입되지 않았다.** `isolation: "worktree"` 여부와 무관하게 `Agent` 도구로 스폰되는 서브에이전트 전반에서 SessionStart 훅 기반 자동 주입이 작동하지 않는 것으로 보인다.
- `node`는 PATH에 정상 존재(v22.23.2) — README가 언급하는 "node 부재 시 무주입" 실패 모드는 아니었다.
- `~/.claude/.ponytail-active` 마커(`full`)가 1세대 ON 실행 시점에 한 번은 발동한 흔적을 남겼지만, 실제 컨텍스트 주입과는 무관했다.
- **우회책 검증**: 프롬프트에서 `Skill` 도구로 `ponytail:ponytail`을 명시적으로 호출하도록 지시하자 실제 룰셋 전체(래더, "ACTIVE EVERY RESPONSE", 규칙 섹션)가 정상 로드됨을 확인. 이 방식으로 2세대(ON-v2) 6세션을 재실행했다.
- **이 구조적 한계는 ponytail에만 국한되지 않는다.** `Agent(isolation: "worktree")` + 전역 `enabledPlugins` 토글이라는, CLAUDE.md/PLAN.md가 다른 스킬(superpowers, claude-mem) 실험에도 그대로 쓰라고 규정한 방식 자체가 훅 기반 "항상-켜짐" 플러그인에는 작동하지 않는다. **앞으로 이 방식을 쓰는 모든 실험은 조건에 맞게(명시적 `Skill`/커맨드 호출 등) 활성화가 실제로 됐는지 최소 1회 진단으로 확인한 뒤 진행해야 한다.**

## 활성화가 다른 실험에 주는 의미

- **superpowers**: PLAN.md Section B는 `enabledPlugins`를 전역 토글하는 방식을 그대로 가정한다. 같은 문제가 발생할 가능성이 높다 — 실행 전 동일한 진단(진단 전용 서브에이전트로 훅 주입 여부 확인)을 먼저 거쳐야 한다.
- **claude-mem**: 메모리 훅도 같은 종류의 SessionStart/PreCompact 훅에 의존한다면 동일한 위험이 있다.
- **graphify**: pip 패키지로 marketplace 체계 밖이라 이 문제와는 무관할 가능성이 높지만, 확인 없이 단정하지 않는다.

## 설계 검토 (티켓 A → B로 이어진 경위)

티켓 A 1세대 실행 직후 결과가 가설과 반대로 나와, ponytail 저장소의 실제 agentic 벤치마크(`benchmarks/results/2026-06-18-agentic.md`, 저자 자체 발표, Haiku 4.5·`tiangolo/full-stack-fastapi-template` 대상)를 재확인했다. 핵심 발견:

- 저자 데이터에서도 backend CRUD 티켓은 arm 간 거의 차이 없음("search items by title" 44→44 LOC, 0%). 효과는 에이전트가 커스텀 컴포넌트/라이브러리를 설치하려는 지점에 집중(date picker −94%, color picker −92%).
- 저자 스스로 "이미 최소한인 코드에서는 효과가 0에 가깝다"고 명시.

이에 따라 저자 벤치마크의 date-picker 사례를 옮긴 **티켓 B**(리마인드 날짜)로 추가 실험했다. (당시엔 활성화 실패를 몰랐기 때문에, 티켓 B의 1세대 결과도 함께 무효였다 — 이후 활성화 검증에서 밝혀짐.)

## 실행별 지표

### 티켓 A — OFF (유효, 1세대 그대로 사용)

| 세션 | subagent_tokens | tool_uses | duration_ms | 테스트 결과 | LOC(+/-) |
|---|---:|---:|---:|---|---:|
| OFF-1 | 53,313 | 21 | 334,043 | 7 passed | +183/-11 |
| OFF-2 | 51,746 | 23 | 253,283 | 7 passed | +199/-12 |
| OFF-3 | 53,114 | 22 | 265,422 | 5 passed | +144/-12 |

### 티켓 A — ON-v2 (2세대, 명시적 Skill 호출로 유효 확인)

| 세션 | subagent_tokens | tool_uses | 테스트 결과 | LOC(+/-) | 태그 구현 |
|---|---:|---:|---|---:|---|
| ON-v2-A-1 | 54,250 | 22 | 6 passed | +78/-10 | 콤마 문자열 컬럼 |
| ON-v2-A-2 | 53,804 | 19 | 7 passed | +110/-13 | join 테이블(근거 명시) |
| ON-v2-A-3 | 51,324 | 21 | 6 passed | +79/-10 | 콤마 문자열 컬럼 + `ponytail:` 주석 |

### 티켓 A — ON 1세대 (무효 — off vs off였음, 참고용으로만 남김)

| 세션 | subagent_tokens | tool_uses | duration_ms | 테스트 결과 | LOC(+/-) |
|---|---:|---:|---:|---|---:|
| ON-1 | 55,133 | 23 | 19,197,800† | 7 passed | +186/-16 |
| ON-2 | 52,626 | 27 | 19,374,669† | 10 passed | +256/-15 |
| ON-3 | 58,362 | 31 | 19,184,953† | 9 passed | +261/-17 |

† `duration_ms` 벽시계 오염 추정(활성화 실패와는 별개 이슈). 이 표는 "활성화 안 된 ponytail" 즉 사실상 OFF의 또 다른 반복으로만 참고할 것 — ON 지표로 쓰지 않는다.

### 티켓 B — OFF (유효, 1세대 그대로 사용)

| 세션 | subagent_tokens | tool_uses | duration_ms | 테스트 결과 | LOC(+/-) |
|---|---:|---:|---:|---|---:|
| OFF-B-1 | 48,622 | 22 | 185,758 | 8 passed | +190/-6 |
| OFF-B-2 | 50,322 | 28 | 218,155 | 8 passed | +140/-7 |
| OFF-B-3 | 48,788 | 24 | 199,682 | 8 passed | +133/-5 |

### 티켓 B — ON-v2 (2세대, 명시적 Skill 호출로 유효 확인)

| 세션 | subagent_tokens | tool_uses | 테스트 결과 | LOC(+/-) | 편집 엔드포인트 |
|---|---:|---:|---|---:|---|
| ON-v2-B-1 | 54,904 | 23 | 7 passed | +101/-7 | PATCH, `remind_at`만 |
| ON-v2-B-2 | 52,608 | 23 | 7 passed | +97/-5 | PATCH, `remind_at`만 |
| ON-v2-B-3 | 53,086 | 22 | 7 passed | +106/-7 | PUT, 기존 패턴 재사용(전체 교체) |

### 티켓 B — ON 1세대 (무효 — off vs off였음, 참고용으로만 남김)

| 세션 | subagent_tokens | tool_uses | duration_ms | 테스트 결과 | LOC(+/-) |
|---|---:|---:|---:|---|---:|
| ON-B-1 | 48,995 | 22 | 147,860 | 8 passed | +175/-14 |
| ON-B-2 | 50,697 | 24 | 278,346 | 8 passed | +147/-7 |
| ON-B-3 | 53,839 | 26 | 191,559 | 9 passed | +163/-7 |

모든 세션(OFF/ON-v2 12개)에서 date UI는 native `<input type="date">`였고 의존성 추가는 없었다 — 이 부분은 활성화 여부와 무관하게 일관됐다(설계 검토에서 다룬 "모델이 이미 lazy" 현상).

## 방법론 메모 / 한계

- **활성화 검증(위 참고)**: 이 실험의 가장 큰 리스크였고, 2세대 재실행으로 해소했다. 다만 명시적 `Skill` 호출은 ponytail이 스스로 광고하는 "호출 없이 항상 켜짐"과는 다른 조건이다 — 이 결과는 "ponytail을 명시적으로 켰을 때의 효과"이지 "설치만 해두면 자동으로 얻는 효과"가 아니다.
- **worktree 스냅샷 시점**: `Agent(isolation: "worktree")`가 만드는 worktree는 대화 세션 시작 시점의 저장소 상태를 기준으로 분기된다. 프롬프트에 복구 안내를 명시해 모든 세션이 `git checkout bookmarks-api-baseline -- fixtures/bookmarks-api`로 대응했다. OFF/ON 동일 적용이라 비교를 왜곡하지 않지만, 절대 토큰 수치에 복구 비용이 섞여 있다.
- **duration_ms 신뢰성**: 1세대 티켓 A의 ON 조건 3회에서 벽시계 유휴 시간으로 추정되는 이상치가 나타났다(활성화 문제와는 별개). ON-v2에는 `duration_ms`를 수집하지 않았다(무효화 리스크로 판단해 우선순위에서 제외).
- **테스트 개수 재량 편차**: 세션마다 추가한 테스트 개수가 다르다(6~10개) — 조건과 무관한 에이전트별 재량이며 LOC/토큰 차이의 일부를 설명할 수 있다.
- **caveman을 두 조건 모두 꺼둔 것**: 변수 격리 원칙상 맞는 선택이지만, 사용자가 실제로 쓰는 조합(ponytail+caveman 둘 다 on)과는 다른 상태를 측정했다.
- **표본 크기**: 티켓당 n=3(OFF/ON-v2 각 3회). 저자 벤치마크는 n=4×12티켓으로 훨씬 크다.
