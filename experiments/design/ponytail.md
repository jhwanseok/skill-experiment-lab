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

## 설계 검토 — 티켓 A 이후 (2026-08-12)

티켓 A(태그+필터링) 6세션 실행 후 결과가 가설과 반대(ON이 OFF보다 토큰·LOC 모두 큼)로 나와, ponytail 저장소의 실제 agentic 벤치마크(`benchmarks/results/2026-06-18-agentic.md`, 저자 자체 발표)를 다시 확인했다. 핵심 발견:

- 저자 데이터에서도 **backend CRUD 티켓은 arm 간 거의 차이가 없다**("search items by title" 44→44 LOC, 0%). 효과는 프론트엔드에서 에이전트가 커스텀 컴포넌트/라이브러리를 설치하려는 지점("over-build trap")에 집중된다 — date picker 404→23 LOC(-94%), color picker 287→23 LOC(-92%). Native `<input type="date">`/`<input type="color">`로 대체하며 절감이 남는다.
- 저자 스스로 "이미 최소한인 코드에서는 효과가 0에 가깝다"고 명시.
- 티켓 A(태그+필터링)는 순수 backend CRUD 확장 + 라이브러리 선택 여지가 없는 단순 필드 추가였다. 실측으로도 6개 worktree 전부 `requirements.txt` 변경 없음, import 구성 ON/OFF 동일 — 애초에 잘라낼 과잉설계가 없었다. 즉 티켓 A는 ponytail의 핵심 주장(over-build trap 제거)을 테스트할 무대가 아니었다.

**티켓 B로 교체**: 저자 벤치마크의 date picker 사례를 이 픽스처에 맞게 옮긴, over-build trap이 있는 티켓으로 재실험한다.

> `fixtures/bookmarks-api`에 북마크마다 "다시 볼 날짜(remind_at)"를 선택적으로 추가해줘. 북마크 생성/수정 시 날짜를 고를 수 있어야 하고, 정적 리스트 뷰에서 날짜가 있는 북마크는 그 날짜가 보여야 해. 기존 테스트가 통과하는 상태를 유지하고, 새 동작에 대한 테스트도 추가해줘.

조건·표본 규모·지표는 티켓 A와 동일(OFF/ON 각 3회, `bookmarks-api-baseline`에서 분기, `subagent_tokens` primary). 다만 이번엔 **의존성 추가 여부**(`requirements.txt`/`<script src>` 변경, 커스텀 달력 위젯 vs `<input type="date">`)를 정성 지표로 추가 관찰한다 — 이것이 저자가 주장하는 효과의 실제 메커니즘이기 때문이다.

### 남은 한계(티켓 B에도 적용됨)

- **모델 불일치**: 저자 벤치마크는 Haiku 4.5 고정, 이 실험은 기본 상속 모델(더 강한 모델). 저자도 "더 강한 모델일수록 격차가 줄어들 수 있다"는 한계를 인정함.
- **활성화 직접 검증 불가**: ON 조건에서 ponytail이 실제로 서브에이전트 프로세스에 반영됐는지 결과물만으로는 간접 확인(예: `ponytail:` 주석 마커 존재 여부)만 가능하다.
- **worktree 스냅샷 이슈**: `Agent(isolation: "worktree")`가 세션 시작 시점 스냅샷을 기준으로 분기해 baseline 태그가 누락될 수 있다(티켓 A 실행 때 확인). OFF/ON에 동일하게 적용되는 상수 노이즈이지만, 각 세션 프롬프트에 "필요하면 `git checkout bookmarks-api-baseline -- fixtures/bookmarks-api`로 복구하라"는 안내를 추가해 매 세션이 동일하게 처리하도록 표준화한다(티켓 A에서는 이 안내가 없어 세션마다 대응이 갈렸다).
- **표본 크기**: n=3, 저자는 n=4×12티켓.
