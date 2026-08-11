# 실험설계 — ponytail

## 핵심 질문

ponytail(YAGNI를 강제하는 "게으른 시니어 개발자" 스킬)을 켰을 때, 신규 기능 구현에 드는 **토큰 사용량이 실제로 줄어드는가**?

## 대상 archetype / 픽스처 / 티켓

- Archetype: 코드 생성/볼륨
- 픽스처: `fixtures/bookmarks-api` (`bookmarks-api-baseline` 태그)
- 티켓 A: "북마크에 태그를 추가하고 태그로 필터링" — 새 테이블 vs JSON 컬럼 등 구현 선택지가 갈리는 지점이 있어 코드 볼륨/토큰 차이가 드러나기 좋음.

티켓 A 원문(각 세션에 동일하게 제공):

> `fixtures/bookmarks-api`에 북마크 태그 기능을 추가해줘. 북마크에 태그를 여러 개 붙일 수 있어야 하고, `GET /bookmarks?tag=...`처럼 태그로 필터링해서 조회할 수 있어야 해. 정적 리스트 뷰에서도 태그가 보이고 필터링이 되면 좋겠어. 기존 테스트가 통과하는 상태를 유지하고, 새 동작에 대한 테스트도 추가해줘.

## 조건

- **OFF**: `ponytail@ponytail: false`, `caveman@caveman: false` (전역 설정)
- **ON**: `ponytail@ponytail: true`, `caveman@caveman: false`

`caveman`은 응답 산문을 압축하는 별개 스킬로 이미 이 머신에 전역 설치되어 있어, 두 조건 모두에서 꺼서 독립 변수를 ponytail 하나로 격리한다. `superpowers`는 이미 전역 OFF 상태를 유지한다.

세션마다 `bookmarks-api-baseline` 태그에서 분기한 격리된 git worktree(`Agent` 도구, `isolation: "worktree"`)에서 실행하고, 각 조건 내에서는 병렬로 3회씩 돌리되 조건 간에는 순차 실행한다(전역 설정 토글이 섞이지 않도록).

## 표본 규모

조건당 3회, 총 6세션. 신호가 뚜렷하면 여기서 멈추고, 애매하면 반복 횟수를 늘리는 것을 다음 단계로 남긴다.

## 지표

- **Primary**: `subagent_tokens` (조건별 3회 평균/범위)
- **Secondary(무료)**: `duration_ms`, `tool_uses`, `git diff --stat` 기준 LOC(추가/삭제 라인 수)

## 가설

ponytail README/스킬 정의(YAGNI 강제, stdlib/네이티브 우선, 불필요한 추상화 금지)가 사실이라면, ON 조건에서 `subagent_tokens`와 LOC가 OFF 대비 낮게 나타날 것으로 예상한다. 반대로 차이가 없거나 오히려 늘어난다면, "토큰 절감" 주장이 이 archetype(작은 CRUD 볼륨 티켓)에서는 재현되지 않는다는 근거가 된다.

## 검증 방법

- 각 실행 후 `git log`/`git diff --stat`으로 실제 코드 변경이 발생했는지 확인.
- 새로 추가된 테스트가 실제로 통과하는지 확인(구현 완성도 확보, 지표 비교의 전제).
- 지표 파일이 조건당 3개씩 총 6개 쌓였는지 확인.
