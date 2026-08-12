# 실행 결과 — superpowers

실험설계: [`experiments/design/superpowers.md`](../design/superpowers.md)

픽스처: `fixtures/bookmarks-api` (`bookmarks-api-baseline-bug` 태그 — `GET /bookmarks?sort=title`에 `COLLATE NOCASE` 없이 대소문자 구분 정렬 버그를 심고 재현 테스트는 없앤 상태). 버그 리포트 티켓(자연스러운 1인칭 문장, 에이전트 아키텍처 언급 없음) 동일 문구를 OFF/ON 각 3회에 제공.

> ⚠️ **측정 방식이 `Agent` 도구에서 헤드리스 `claude -p` CLI로 바뀌었다.** `Agent(isolation:"worktree")`로는 superpowers가 카탈로그에도 없고 명시적 `Skill` 호출도 전부 `Unknown skill` 에러 — 완전히 도달 불가능했다(ponytail보다 심각한 실패). `bookmarks-api-baseline-bug`에서 `git worktree add`로 수동 생성한 워크트리 안에서 `claude -p "<티켓>" --output-format json --permission-mode bypassPermissions`을 직접 실행하는 방식으로 전환했고, 스모크 테스트로 실제 SessionStart 훅 주입을 확인했다(아래 "활성화 검증" 참고). 지표는 `Agent` 도구가 주던 `subagent_tokens`/`tool_uses`/`duration_ms` 대신 CLI의 `--output-format json`에서 직접 파싱했다 — CLAUDE.md의 "별도 계측 스크립트를 새로 만들지 않는다" 원칙에서 벗어난 명시적 예외.

## 활성화 검증

스모크 테스트(코드 작업 없이 "using-superpowers 내용이 있는지"만 질문):

| 조건 | 결과 |
|---|---|
| OFF | "using-superpowers"라는 스킬 없음, SUBAGENT-STOP 텍스트 없음 |
| ON | 전체 본문 주입 확인(SUBAGENT-STOP 섹션 포함), `cache_creation_input_tokens` 7,378→9,350으로 스킬 로딩 비용만큼 증가 |

진짜 최상위 세션(`claude -p`)이므로 "파견된 서브에이전트"에 해당하지 않아 SUBAGENT-STOP에 걸릴 근거가 없다 — 실제로 본 실행 6세션 전부 이 문제 없이 정상 진행됐다(아래 참고).

## 실행별 지표

| 세션 | cost_usd | duration_ms | num_turns | total_tokens(in+cache_creation+out) | 커밋 수 | RED→GREEN 분리 | 스킬 사용 |
|---|---:|---:|---:|---:|---:|---|---|
| OFF-1 | 0.3089 | 68,160 | 12 | 23,838 | 1 | 아니오 | 없음 |
| OFF-2 | 0.3615 | 67,870 | 14 | 26,697 | 1 | 아니오 | 없음 |
| OFF-3 | 0.3543 | 62,193 | 15 | 24,809 | 1 | 아니오 | 없음 |
| ON-1 | 0.5074 | 88,002 | 18 | 36,887 | 2 | **예** | `systematic-debugging` |
| ON-2 | 0.5779 | 105,035 | 22 | 38,713 | 1 | 아니오 | `systematic-debugging` |
| ON-3 | 0.3837 | 71,719 | 14 | 28,470 | 1 | 아니오 | 인지했으나 의도적으로 생략 |

## 요약 (평균, n=3)

| 지표 | OFF | ON | 차이 |
|---|---:|---:|---:|
| cost_usd | 0.3416 | 0.4897 | **+43.4%** |
| duration_ms | 66,074 | 88,252 | **+33.6%** |
| num_turns | 13.7 | 18.0 | **+31.7%** |
| total_tokens | 25,115 | 34,690 | **+38.1%** |
| 근본 원인 수정(COLLATE NOCASE) | 3/3 | 3/3 | 차이 없음 |
| 회귀 테스트가 실제로 버그를 잡는지(사후 검증) | 3/3 | 3/3 | 차이 없음 |
| RED→GREEN 별도 커밋 | 0/3 | 1/3 | 약한 신호 |

## 판정

**결과 수정(correctness)은 두 조건 모두 완벽했다.** OFF/ON 6세션 전부 `ORDER BY title COLLATE NOCASE`로 근본 원인을 정확히 고쳤고, 추가한 회귀 테스트를 `bookmarks-api-baseline-bug`(미수정 상태)에 적용해 실제로 실패하는 걸 직접 확인했다(6/6 유효). 즉 **이 버그(원인이 한 파일 안에서 SQLite collation 지식만으로 명확히 설명되는 종류)는, superpowers 없이도 이미 강한 모델이라면 근본 원인까지 정확히 고친다.** 정확성 차이로는 superpowers의 가치를 증명하지 못했다.

**하지만 프로세스에는 실제로 관찰 가능한 차이가 있었다:**
- ON 3세션 중 2세션이 자기 판단으로 `superpowers:systematic-debugging`을 호출했고, 세션 시작 시 주입된 `using-superpowers` 훅의 "버그 수정 요청 → systematic-debugging 먼저"라는 규칙을 그 이유로 정확히 지목했다. **SUBAGENT-STOP도, 코칭도 없이 자발적으로 스킬 체인이 작동한 것**을 확인한 것이 이 실험의 핵심 성과다.
- ON-1은 실패하는 테스트를 먼저 커밋하고 그다음 수정 커밋을 분리해서 남겼다 — 설계에서 기대한 RED→GREEN 커밋 패턴이 실제로 관찰된 유일한 사례.
- ON-3은 흥미로운 예외다: 훅이 systematic-debugging을 먼저 쓰라고 요구한다는 걸 스스로 인지하고도, "이 정도 난이도엔 다단계 가설-검증 절차가 과하다"고 판단해 의도적으로 생략했다 — 스킬을 맹목적으로 따르지 않고 상황에 맞게 판단한 사례로, 이것도 "프로세스가 개선됐다"고 볼지는 해석의 여지가 있다.
- 반면 ON은 비용·시간·토큰·턴 수 전부 OFF보다 30~43% 높았다. `using-superpowers`(+`systematic-debugging`, 경우에 따라 TDD 관련 내용까지) 로딩 자체의 고정비용에 더해, 다단계 프로세스를 실제로 밟는 데 드는 추가 턴이 원인으로 보인다 — ponytail 실험에서 본 것과 같은 패턴("코드/프로세스는 개선되지만 총비용은 늘어난다")이 여기서도 재현됐다.

**종합**: 이 실험(원인이 비교적 명확한 단일 파일 버그, n=3, 강한 모델)에서는 superpowers가 **정확성을 끌어올리진 못했지만(이미 천장에 가까웠음), 자발적 스킬 판단·TDD RED 우선 확인 같은 프로세스 규율을 실제로 유도**했다 — 다만 그 대가로 비용이 30~40%대 늘었다. "프로세스가 실제로 개선되는가"라는 핵심 질문에는 조건부로 "그렇다"고 답할 수 있지만, 정확성이 이미 높은 쉬운 버그에서는 그 개선이 눈에 보이는 산출물 품질 차이로 이어지지 않았고 비용만 늘었다 — 더 어렵거나 원인이 모호한 버그였다면 결과가 달라질 가능성이 있다(아래 한계 참고).

## 방법론 메모 / 한계

- **표본 크기**: n=3. 특히 "RED→GREEN 분리"(1/3)와 "스킬 생략"(1/3, ON-3) 같은 개별 사례성 관찰은 반복을 늘려야 안정적인 비율로 볼 수 있다.
- **버그 난이도 천장 효과**: 이 버그는 SQLite collation이라는 잘 알려진 단일 원인이라 강한 모델이라면 스킬 없이도 원인을 놓치기 어려웠다. superpowers의 가치가 더 크게 드러나려면 원인이 다층적이거나(여러 컴포넌트에 걸친 버그) 그럴듯한 오답(symptom fix)에 빠지기 쉬운 케이스가 필요하다 — `systematic-debugging`의 Phase 1 "다중 컴포넌트 시스템" 절이 정확히 그런 상황을 겨냥하고 있다.
- **claude -p 방식의 대가**: `Agent` 도구의 자동 계측(subagent_tokens 등)을 포기하고 `--output-format json`을 직접 파싱했다 — CLAUDE.md 원칙에서 벗어난 예외이며, 향후 동일 문제(훅 기반 플러그인이 `Agent` 서브에이전트에 도달 못함)를 겪는 실험은 이 방식을 표준 대안으로 참고할 수 있다.
- **cost_usd/total_tokens 산정 방식**: `total_tokens = input_tokens + cache_creation_input_tokens + output_tokens`로 정의했다(`cache_read_input_tokens`는 제외 — 저렴한 재사용 토큰이라 "비용"을 대표하기엔 부적합 판단). `cost_usd`는 CLI가 캐시 할인까지 반영해 계산한 값이라 가장 신뢰할 수 있는 단일 지표로 취급했다.
- **정성 판정의 주관성**: 근본 원인 수정 여부·회귀 테스트 유효성은 diff·재실행으로 직접 검증했지만("검증 방법" 절 그대로 수행), "프로세스가 개선됐다"는 종합 판단 자체는 세션 자기보고 + git log 교차검증에 의존한다.
