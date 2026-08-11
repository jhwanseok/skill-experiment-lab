# CLAUDE.md — skill-experiment-lab

## 목적

이 저장소는 Claude Code 스킬/플러그인을 통제된 on/off 실험으로 검증하기 위한 재사용 가능한 하네스다. 여기서 나온 결과는 `jhwanseok.github.io`(별도 저장소)의 Projects 글로도 게시된다. **fixtures, 실행 절차, 실험 결과를 포함해 이 저장소 전체를 GitHub에 공개한다** — 로컬에만 두고 절대 올리지 않는 건 `SKILLS_BACKLOG.md`(아직 검토 전인 개인 메모)와 `experiments/PLAN.md`(비공개로 두는 실험 계획) 두 개뿐이다(둘 다 `.gitignore` 처리).

지금까지 설계됐거나 진행 중인 실험의 구체적 절차·티켓·지표는 `experiments/PLAN.md`에 있다 — 언제든 그 문서만 보고 이어서 실행할 수 있어야 한다. 단, 이 파일은 git에 올리지 않으므로 새 환경에서 이어가려면 별도로 가져와야 한다.

## 핵심 원칙 — baseline 불변성

각 fixture의 `baseline` 태그(그리고 archetype별 변형 태그, 예: `baseline-bug`)는 한 번 만들면 절대 직접 수정하지 않는다. 코드를 바꿔야 할 일이 생기면 새 태그를 만든다 — 그래야 몇 달 뒤 다른 스킬을 테스트해도 과거 실험 결과와 공정하게 비교할 수 있다.

## Archetype

새 스킬을 테스트할 때 먼저 아래 네 가지 중 어디에 해당하는지 판단한다. 대부분은 기존 archetype 중 하나로 커버되고, 정말 안 맞을 때만 `fixtures/`에 새 archetype을 추가한다.

| Archetype | baseline 특성 | 지금까지의 예 |
|---|---|---|
| 코드 생성/볼륨 | 깨끗한 CRUD 앱 + 테스트 몇 개 | ponytail |
| 디버깅/프로세스 | 같은 앱 + 시딩된 버그 태그(`baseline-bug`) | superpowers |
| 세션 간 컨텍스트 | 같은 앱, 세션 1→2 시나리오 | claude-mem |
| 구조/탐색 이해 | 모듈이 얽힌 더 큰 앱(읽기 전용) 또는 실제 코드베이스 | graphify |

## 새 스킬을 테스트하는 워크플로우

1. `SKILLS_BACKLOG.md`를 확인한다. 없으면 `/add-skill <저장소 URL>`로 추가한다.
2. 어느 archetype에 해당하는지 판단한다. 안 맞으면 `fixtures/`에 새 archetype을 추가한다.
3. 핵심 질문 하나와 그걸 답하는 주 지표(primary metric) 하나를 정한다 — 저장소 README가 제안하는 모든 축을 다 재려 하지 않는다.
4. 조건(도구 off/on)마다 baseline 태그에서 분기한 격리된 git worktree에서 세션을 실행한다.
5. `experiments/results/`에 실행별 지표를 기록하고, `experiments/INDEX.md`에 요약 행을 추가한다.
6. `SKILLS_BACKLOG.md`의 Status를 `done`으로 갱신하고 결과/아티클 링크를 남긴다.

## 지표 수집 규칙

Claude Code의 `Agent` 도구를 `isolation: "worktree"`로 호출하면 실행 후 `subagent_tokens`/`tool_uses`/`duration_ms`와 worktree 경로·브랜치가 반환된다. 이 값을 그대로 지표로 쓴다. 별도 계측 스크립트를 새로 만들지 않는다.

## 표본 규모 원칙

핵심 질문 하나에 집중하고, 조건당 최소 반복(대개 3회)으로 시작한다. 신호가 뚜렷하면 거기서 멈추고, 애매하면 반복 횟수를 늘리는 것을 다음 단계로 남겨둔다. 처음부터 과도한 표본을 모으지 않는다.

## 전역 설정을 건드리는 실험

플러그인 on/off 토글이 `~/.claude/settings.json` 같은 전역 설정을 거쳐야 하는 경우, 이 머신의 다른 Claude Code 세션에도 영향을 준다는 걸 실행 전에 반드시 알리고 진행하며, 실험이 끝나면 원래 상태로 복원한다.
