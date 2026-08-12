# 실험설계 — superpowers

## 핵심 질문

superpowers 전체(메타 규칙 `using-superpowers`가 유도하는 "관련 스킬을 스스로 판단해 호출하는" 프로세스)를 켰을 때, **버그 수정 프로세스가 실제로 개선되는가** — 근본 원인까지 올바르게 고치는지, 재현 테스트를 먼저 작성하는 TDD RED→GREEN 순서를 따르는지, 그리고 애초에 그 스킬 체인(`using-superpowers` → `systematic-debugging` → `test-driven-development`)이 자발적으로 작동하는지.

## 설계 경위 (두 번 바뀜)

**1차 설계**: `Agent` 도구로 파견된 서브에이전트에게 `superpowers:systematic-debugging`을 명시적으로 강제 호출시키는 방식. 레포 확인 결과 이건 superpowers 전체가 아니라 개별 스킬 하나를 강제 주입한 효과만 재는 것이라 판단해 폐기.

**2차 설계**(재검토로 폐기): "너는 파견된 서브에이전트가 아니라 주 세션이다, SUBAGENT-STOP은 너한테 적용 안 된다"고 프롬프트에서 직접 코칭하는 방식. 다시 검토하니 이것도 문제였다 — **모델에게 결론을("너는 서브에이전트가 아니다") 미리 정해주는 것**이라, "superpowers가 실제로 자발적으로 발동하는가"가 아니라 "발동하라고 강요하면 발동하는가"를 재는 꼴이 된다. 이것도 폐기.

**3차 설계(현재)**: 프롬프트에서 에이전트 아키텍처에 대한 메타 설명을 아예 뺀다. 대신 **실제 사용자가 1인칭으로 자연스럽게 버그를 리포트하는 문장**으로만 티켓을 쓴다. 그러면 모델이 "나는 좁은 작업에 파견된 서브에이전트인가, 아닌가"를 강요 없이 스스로 판단하게 되고, 이게 superpowers의 SUBAGENT-STOP 로직이 우리 하네스(`Agent` 도구를 통한 호출)에서 실제로 어떻게 작동하는지에 대한 정직한 관찰이 된다. 만약 이렇게 자연스러운 프레이밍을 줘도 자발적으로 발동을 안 한다면 — 그 자체가 "이런 종류의 자동화된/헤드리스 호출로는 superpowers의 자율 발동 메커니즘을 못 쓴다"는, 그 자체로 보고할 가치가 있는 발견이다.

## 4차 설계 — `Agent` 도구를 버리고 헤드리스 `claude -p` CLI로 전환

활성화 검증(아래)에서 `superpowers`가 `Agent(isolation:"worktree")` 서브에이전트에는 **완전히 도달 불가능**하다는 게 확인됐다(카탈로그에도 없고 명시적 `Skill` 호출도 전부 `Unknown skill` 에러). ponytail보다 심각한 실패였다. 이 제약은 스킬 자체의 문제가 아니라 이 실험이 "파견된 서브에이전트"를 통해서만 스킬을 켜려 했다는, 하네스가 스스로 만든 제약이었다 — 원래 질문(스킬이 실제로 프로세스를 개선하는가)과는 무관하다.

그래서 `Agent` 도구를 완전히 버리고, 진짜 최상위 세션인 **헤드리스 `claude -p` CLI 프로세스**(Bash로 직접 실행, `--output-format json`)로 전환한다:

- 세션 격리: `Agent` 도구의 자동 worktree 대신, `git worktree add`로 `bookmarks-api-baseline-bug`에서 직접 분기한 worktree를 조건×반복 수만큼 수동 생성.
- 실행: 각 worktree 안에서 `claude -p "<티켓>" --output-format json --permission-mode bypassPermissions`.
- 지표: `Agent` 도구가 주던 `subagent_tokens`/`tool_uses`/`duration_ms` 대신, `claude -p`의 JSON 출력에 담긴 `usage`(input/output/cache tokens), `total_cost_usd`, `duration_ms`, `num_turns`를 직접 파싱해서 쓴다. CLAUDE.md의 "별도 계측 스크립트를 새로 만들지 않는다" 원칙에서 벗어나는 예외이며, 사용자가 이 원칙보다 "스킬이 실제로 작동하는지 확인"이라는 실험의 원래 목적을 우선하기로 명시적으로 결정했다.
- **활성화 재확인 완료**: 이 방식으로 스모크 테스트한 결과, OFF에서는 `using-superpowers` 내용이 전혀 없고 ON에서는 SUBAGENT-STOP을 포함한 전체 본문이 정상 주입됨을 확인했다(cache_creation_input_tokens가 7,378→9,350으로 스킬 로딩 비용만큼 증가 — ponytail 때와 같은 패턴). 진짜 최상위 세션이므로 SUBAGENT-STOP에 걸릴 근거도 없다.

이하 픽스처·티켓·조건·표본·1차 지표(근본 원인 수정, 재현 테스트 유효성, RED→GREEN 커밋 패턴)는 이전 설계와 동일하다. 아래 "조건"과 "활성화 검증" 절의 실행 메커니즘 설명만 `claude -p` 기준으로 대체된 것으로 읽는다.

## 대상 archetype / 픽스처 / 티켓

- Archetype: 디버깅/프로세스
- 픽스처: `fixtures/bookmarks-api`, 새 태그 `bookmarks-api-baseline-bug`
- `bookmarks-api-baseline`에서 분기해 다음을 추가한 뒤 태그를 찍는다(baseline 자체는 건드리지 않음):
  - `GET /bookmarks`에 `?sort=title` 파라미터를 추가. 구현은 raw SQL `ORDER BY title`(즉 `COLLATE NOCASE` 없음) — SQLite 기본 정렬은 대소문자를 구분해 대문자로 시작하는 제목이 소문자로 시작하는 제목보다 항상 앞에 온다(ASCII상 `'A' < 'a'`). 예: `zebra`가 `Apple`보다 알파벳상 뒤인데도 `Apple`이 항상 위로 온다.
  - 이 기능에 대한 테스트는 전혀 추가하지 않는다(재현 테스트 없음 — "시딩된 버그" 요건).
  - 커밋 후 `bookmarks-api-baseline-bug` 태그 생성.

**티켓(버그 리포트) 원문**(자연스러운 1인칭 사용자 요청, 에이전트 아키텍처에 대한 메타 언급 없음, 두 조건에 동일하게 제공, "대소문자"라는 진단명은 직접 언급하지 않음):

> `fixtures/bookmarks-api` 관련해서 버그 리포트가 하나 들어왔어(이 저장소는 `skill-experiment-lab`이고, 이 worktree는 `bookmarks-api-baseline-bug` 태그에서 분기돼 있어야 하는데, 혹시 `fixtures/bookmarks-api/`에 스텁 README만 있으면 먼저 `git checkout bookmarks-api-baseline-bug -- fixtures/bookmarks-api`로 복구해줘). `GET /bookmarks?sort=title`로 정렬해서 보면 순서가 이상하다고 해. 소문자로 시작하는 제목들이 알파벳순으로는 앞에 와야 할 때도 항상 대문자로 시작하는 제목들보다 뒤로 밀린대. 원인 찾아서 제대로 고쳐줄래? 다 되면 의미 있는 단위로 커밋해줘. `fixtures/bookmarks-api/` 밖은 건드리지 말고.
>
> 다 끝나면 어떤 과정으로 접근했는지(스킬을 썼다면 어떤 걸 왜 썼는지도) 간단히 알려줘.

마지막 문장("어떤 과정으로 접근했는지... 알려줘")은 아키텍처를 암시하지 않는 자연스러운 마무리 질문으로, 사후에 스킬 사용 여부를 자기보고받기 위한 것이다 — "스킬을 썼다면"이라는 조건문이라 스킬을 안 썼어도 자연스럽게 답할 수 있다.

## 조건

- **OFF**: `enabledPlugins.superpowers@claude-plugins-official: false`
- **ON**: `enabledPlugins.superpowers@claude-plugins-official: true`
- 두 조건 모두 `ponytail@ponytail: false`, `caveman@caveman: false`로 고정해 변수를 superpowers 하나로 격리한다.
- 두 조건 모두 정확히 같은 티켓 문구를 받는다 — 차이는 superpowers 유무뿐이다.

세션마다 `bookmarks-api-baseline-bug` 태그에서 분기한 격리된 git worktree(`Agent` 도구, `isolation: "worktree"`)에서 실행하고, 조건 내에서는 병렬, 조건 간에는 순차 실행한다.

## 활성화 검증 (본 실행 전 필수 — `CLAUDE.md` 절차)

ponytail 실험에서 확인된 대로 `enabledPlugins` 전역 토글만으로는 `Agent` 도구 서브에이전트에 훅 기반 룰셋이 주입되지 않을 가능성이 높다. superpowers는 여기에 SUBAGENT-STOP 문제까지 겹친다. 본 실행(6세션) 전에 진단 전용 서브에이전트(코드 작업 없음, `Agent`, worktree 격리)를 OFF/ON 각 1회 띄워, **자연스러운 1인칭 요청 프레이밍**(위 티켓과 같은 톤 — "당신은 서브에이전트다/아니다" 같은 언급 없이)으로 다음을 확인한다:

1. `using-superpowers` 룰셋 본문(카탈로그 한 줄 설명이 아니라 SUBAGENT-STOP·Rule·Skill Priority 등 실제 지침)이 컨텍스트에 주입됐는지.
2. 주입됐다면, **강요 없이** 스스로를 "파견된 서브에이전트"로 판단해 SUBAGENT-STOP에 따라 스킬 체크를 건너뛰는지, 아니면 자연스러운 1인칭 요청이라는 맥락 때문에 스스로를 그 범주에 안 넣고 정상적으로 관련 스킬(`systematic-debugging` 등)을 검토하는지. (이 판단 자체를 있는 그대로 관찰하는 게 목적이며, 어느 쪽으로도 유도하지 않는다.)
3. 주입되지 않았다면(ponytail과 같은 하네스 차원의 훅 미전달), `Skill` 도구로 `superpowers:using-superpowers`를 명시적으로 호출했을 때 로드는 되는지, 로드된 뒤에도 2번과 같은 자기 판단이 관찰되는지.
4. 분기:
   - **자연스러운 프레이밍만으로 스스로 SUBAGENT-STOP에 안 걸리고 관련 스킬을 검토·호출** → 훅이 원래 작동한다면 그대로, 안 된다면 `using-superpowers` 명시 호출만 최소한으로 더해 본 실행 진행. **이게 "superpowers 전체가 설계대로 작동하는가"를 가장 정직하게 재는 경우다.**
   - **스스로를 서브에이전트로 판단해 SUBAGENT-STOP에 따라 스킬 체크를 건너뜀** → 이건 실패가 아니라 **그 자체로 유효한 결과**다: "우리 하네스로 호출하는 방식(자연스러운 프레이밍 포함)으로는 superpowers의 자율 발동이 실질적으로 죽어있다"는 뜻이므로, 사용자에게 이 사실을 보고하고 다음 중 어떻게 할지 정한다 — (a) 여기서 실험을 접고 이 발견 자체를 결과로 기록, (b) 1차 설계로 되돌아가 "개별 스킬 강제 호출 효과"로 스코프를 축소해 진행, (c) 다른 방법(예: 실제 헤드리스 `claude -p` CLI 세션처럼 `Agent` 도구를 아예 거치지 않는 방식)을 모색.
   - **주입도 명시적 호출도 실패** → ponytail과 같은 완전한 활성화 실패. 사용자에게 보고.
5. 이 진단도 전역 설정을 건드리므로, 진단 시작 전 사용자에게 알린다.

## 표본 규모

조건당 3회, 총 6세션(활성화 검증 진단 2회는 별도, 이 표본에 포함 안 함).

## 지표

- **Primary(정성)**:
  1. **근본 원인 수정 여부** — `ORDER BY title COLLATE NOCASE`(또는 동등한 일관된 대소문자 무시 정렬)를 적용했는지. 대조 예: 특정 사례만 땜질하거나, 유니코드/공백 등 엣지케이스에서 깨지는 임시방편.
  2. **재현 테스트가 실제로 버그를 잡는지** — diff의 새 테스트 파일을 `bookmarks-api-baseline-bug`(수정 전)에 적용해 돌렸을 때 실패하는지 사후 검증.
  3. **TDD RED→GREEN 커밋 패턴 준수 여부** — `git log`에서 "실패하는 테스트 커밋 → 수정 커밋" 순서가 보이는지, 아니면 한 번에 뭉뚱그려 커밋했는지.
- **Secondary(정성, 무료)**:
  - **스킬 체인 발동 여부** — 자기보고 기준으로 어떤 스킬을(있다면) 어떤 순서로 썼는지, 그리고 스스로를 "서브에이전트"로 인지했는지에 대한 언급이 있다면 그것도. `using-superpowers` → `systematic-debugging` → `test-driven-development`로 이어지는 설계된 체인이 실제로 관찰되는지가 "superpowers 전체가 작동하는가"에 대한 직접적 증거다.
  - `tool_uses`, `duration_ms`(ponytail 실험에서 `duration_ms`가 벽시계 오염으로 신뢰 불가능했던 전례가 있어 참고용으로만 취급).

## 가설

자연스러운 요청 프레이밍에서도 `using-superpowers`의 메타 규칙이 살아있고 SUBAGENT-STOP에 걸리지 않는다면, ON 조건에서 에이전트가 스스로 `systematic-debugging`(그리고 체인을 따라 `test-driven-development`)을 호출하고, 그 결과 (1) 근본 원인 수정 비율이 높고, (2) 재현 테스트가 실제로 버그를 잡는 형태로 먼저 작성되며, (3) `git log`에 RED→GREEN 커밋 패턴이 더 자주 나타날 것으로 예상한다. OFF 조건은 증상만 고치거나, 테스트를 나중에(또는 안) 추가하거나, 커밋을 한 번에 뭉뚱그릴 가능성이 상대적으로 높을 것으로 예상한다. 다만 활성화 검증에서 SUBAGENT-STOP이 자연스러운 프레이밍에서도 발동한다는 게 확인되면, 이 가설 전체가 검증 불가 판정으로 바뀌고 활성화 검증 자체가 이 실험의 핵심 결과가 된다.

## 검증 방법

- 각 실행 후 `git log --oneline`으로 커밋 순서·개수 확인.
- 새 테스트 파일을 `bookmarks-api-baseline-bug`(미수정 상태)에 적용해 실제로 실패하는지 별도로 검증(재현 테스트의 진짜 재현력 확인).
- `git diff bookmarks-api-baseline-bug`로 실제 수정 내용을 확인해 근본 원인 수정 여부를 코드 리뷰 방식으로 판정.
- 세션 자기보고에서 스킬 호출 순서 및 자기 인식(서브에이전트 여부 언급)을 추출.
- 지표 파일이 조건당 3개씩 총 6개 쌓였는지 확인.

## 리스크 / 한계

- **전역 설정 변경**: `superpowers` on/off 토글은 `~/.claude/settings.json`을 직접 건드려 이 머신의 다른 세션에도 영향을 준다. 활성화 검증 진단과 본 실행 각각 시작 전에 알리고 진행하며, 실험 종료 후 원래 상태(`superpowers: false`, `ponytail: true`, `caveman: true`)로 복원한다.
- **worktree 스냅샷 시점**: ponytail 실험과 동일한 이슈 가능성 — 프롬프트에 복구 안내를 처음부터 포함시켜 세션마다 대응이 갈리지 않게 한다(위 티켓 원문에 이미 반영).
- **활성화 검증에서 부정적 결과가 나올 가능성이 실질적으로 있다**: 이건 한계라기보다 이 실험 설계가 안고 가는 진짜 리스크다 — SUBAGENT-STOP이 자연스러운 프레이밍에서도 발동하면 본 실행(6세션)까지 갈 필요 없이 활성화 검증 단계에서 실험이 끝난다. 이 경우도 "왜 이 하네스로는 superpowers를 못 켜는가"라는 독립적으로 보고할 가치가 있는 결과로 취급한다.
- **정성 판정의 주관성**: 근본 원인 수정 여부는 코드 리뷰로 내가 직접 판정한다 — 판정 기준(위 "지표" 절)을 결과 문서에 세션별로 명시해 재현 가능하게 남긴다.
- **자기보고의 한계**: "어떤 과정으로 접근했는지 알려줘"라는 질문에 대한 답은 에이전트의 사후 설명이지, 실제 내부 판단 과정의 완벽한 기록은 아니다. `git log`·diff 같은 객관적 산출물로 교차검증한다.
