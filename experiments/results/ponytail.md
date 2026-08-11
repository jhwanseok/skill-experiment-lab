# 실행 결과 — ponytail

실험설계: [`experiments/design/ponytail.md`](../design/ponytail.md)

픽스처: `fixtures/bookmarks-api` (`bookmarks-api-baseline` 태그) · 티켓 A(북마크 태그 추가 + `?tag=` 필터링) · 조건당 3회, 각 세션은 `Agent(isolation: "worktree")`로 `bookmarks-api-baseline`에서 격리 실행.

## 실행별 지표

| 세션 | 조건 | subagent_tokens | tool_uses | duration_ms | 테스트 결과 | LOC(+/-) |
|---|---|---:|---:|---:|---|---:|
| OFF-1 | ponytail off, caveman off | 53,313 | 21 | 334,043 | 7 passed | +183/-11 |
| OFF-2 | ponytail off, caveman off | 51,746 | 23 | 253,283 | 7 passed | +199/-12 |
| OFF-3 | ponytail off, caveman off | 53,114 | 22 | 265,422 | 5 passed | +144/-12 |
| ON-1 | ponytail on, caveman off | 55,133 | 23 | 19,197,800† | 7 passed | +186/-16 |
| ON-2 | ponytail on, caveman off | 52,626 | 27 | 19,374,669† | 10 passed | +256/-15 |
| ON-3 | ponytail on, caveman off | 58,362 | 31 | 19,184,953† | 9 passed | +261/-17 |

† ON 조건 3회 모두 `duration_ms`가 OFF 대비 약 70배(19,000,000ms대) 튀었다. 세 값이 서로 거의 같고(19,184,953 / 19,197,800 / 19,374,669), 같은 시간대에 실행되어 세션이 오래 대기한 벽시계 시간(예: 컴퓨터 유휴/절전)이 섞여 들어간 것으로 보고 이 열은 참고용에서 제외했다. `subagent_tokens`는 OFF와 같은 범위라 오염되지 않은 것으로 판단.

## 요약 (평균, n=3)

| 지표 | OFF | ON | 차이 |
|---|---:|---:|---:|
| subagent_tokens | 52,724 | 55,374 | **+5.0%** (ON이 더 큼) |
| tool_uses | 22.0 | 27.0 | **+22.7%** (ON이 더 큼) |
| LOC 삽입(+) | 175.3 | 234.3 | **+33.7%** (ON이 더 큼) |

## 판정

핵심 질문("ponytail을 켜면 토큰 사용량이 실제로 줄어드는가?")에 대해, 이 archetype(코드 생성/볼륨)·이 티켓(태그 추가+필터링) 범위에서는 **가설과 반대 방향의 신호**가 나왔다: ON 조건이 OFF 대비 `subagent_tokens`·`tool_uses`·LOC 모두에서 일관되게 더 컸다. n=3으로 표본이 작아 확정적 결론은 아니지만, "토큰 절감" 주장이 이 조건에서는 재현되지 않았다는 약한 근거로 제시한다.

정성적으로도, ON 조건 세션들의 자체 보고 요약을 보면 태그 필터 UI에 드롭다운(`<select>`)을 추가하거나 삭제 시 태그 cascade 정리 테스트를 추가하는 등 OFF 조건보다 오히려 범위를 더 넓게 잡는 경향이 보였다 — ponytail의 "YAGNI 강제"가 최소 구현을 유도하기보다는, 세부 케이스(트림/중복 제거/cascade 등)를 더 꼼꼼히 챙기게 만든 것으로 보인다. 이는 코드 품질 측면에서는 긍정적일 수 있으나, "토큰이 준다"는 주장과는 반대다.

## 방법론 메모 / 한계

- **worktree 스냅샷 시점**: `Agent(isolation: "worktree")`가 만드는 worktree는 이 대화 세션이 시작된 시점의 저장소 상태를 기준으로 분기됐다(baseline 커밋/태그는 세션 도중에 만들어졌으므로 worktree에는 반영되지 않음). 6회 세션 중 5회는 에이전트가 자체적으로 `git checkout bookmarks-api-baseline -- fixtures/bookmarks-api`로 복구한 뒤 작업했다. 최초 OFF-1 실행은 이를 알아채지 못하고 CRUD API 전체를 처음부터 새로 작성해(범위가 완전히 다름) 폐기하고 동일 조건으로 재실행했다(위 표의 OFF-1은 재실행분). 이 복구 단계는 OFF/ON 모두에 동일하게 발생해 조건 간 비교를 왜곡하지는 않지만, 각 세션의 절대 토큰 수치에는 몇 천 토큰 수준의 복구 비용이 섞여 있다.
- **duration_ms 신뢰 불가**: 위 설명대로 ON 조건 3회의 `duration_ms`는 사용할 수 없다(벽시계 유휴 시간 오염 추정).
- **테스트 개수 편차**: 세션마다 추가한 테스트 개수(5~10개)가 다른데, 이는 각 에이전트가 커버리지를 얼마나 넓게 잡았는지의 재량 차이이며 그 자체로 LOC/토큰 차이의 한 원인이다.
- **표본 크기**: 조건당 n=3. 신호는 세 지표에서 일관되게 같은 방향이라 "약한 신호"로는 충분하지만, 반복을 늘리면 더 견고해진다.
