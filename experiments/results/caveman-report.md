# 실험 보고서 — caveman은 언제 이득이고 언제 손해인가

**날짜**: 2026-08-12 · **대상**: [caveman](https://github.com/juliusbrussee/caveman) (skill) · **Archetype**: 무관(범용 응답 압축) · **픽스처**: `fixtures/bookmarks-api` (두 archetype 재사용)
**원자료**: [실험설계](../design/caveman.md) · [실행별 지표 전체](caveman.md)

## 한 줄 요약

**caveman은 "항상 이득"이 아니라 작업 크기에 따라 부호가 바뀌는 스킬이다.** 출력이 긴 작업(태그 기능 추가, 세션 출력 15,000+ 토큰)에서는 세션 전체 비용이 15.1% 줄었지만, 출력이 짧은 작업(한 줄짜리 버그 수정, 세션 출력 ~3,500토큰)에서는 오히려 9.9% 늘었다. 응답을 짧게 만드는 효과 자체는 두 경우 모두 뚜렷했다(응답 산문 37~52% 압축) — 다만 짧은 작업에서는 스킬을 로딩하는 고정비용이 그 절감분을 넘어섰다. 이건 caveman 저장소가 스스로 `docs/HONEST-NUMBERS.md`에 적어둔 경험칙과 정확히 일치하는 결과다.

## 핵심 질문과 방법

**핵심 질문**: caveman을 켰을 때 여러 archetype에 걸쳐 토큰 사용량이 실제로 줄고 품질 저하는 없는가? (`SKILLS_BACKLOG.md` 원안)

caveman은 특정 archetype에 묶이지 않는 범용 응답 압축 스킬이라, 이미 검증된 두 archetype·픽스처를 재사용했다:

- **Archetype 1(코드 생성/볼륨)**: ponytail 실험의 티켓 A(북마크 태그+필터링 기능 추가), `bookmarks-api-baseline`.
- **Archetype 2(디버깅/프로세스)**: superpowers 실험의 버그 티켓(대소문자 구분 정렬 버그 수정), `bookmarks-api-baseline-bug`.

두 archetype 모두 헤드리스 `claude -p` CLI(`--output-format json`)로 실행했다 — 이유는 아래 참고. Archetype 2의 OFF 데이터는 superpowers 실험에서 이미 `caveman: false`로 실행된 것을 그대로 재사용했다.

## 저장소 확인 — 저자가 스스로 밝힌 한계

`docs/HONEST-NUMBERS.md`("No marketing. If caveman lose for your workload, this page tell you to turn it off"으로 시작하는, 이례적으로 솔직한 문서)의 핵심:

- 출력 토큰은 평균 65%(22~87%) 준다 — 이건 진짜.
- 입력 토큰은 0% 준다 — caveman은 출력 스타일만 압축, 컨텍스트·파일은 안 건드림.
- 스킬 자체를 로딩하는 데 **턴당 ~1,000~1,500토큰의 고정비용**이 든다.
- 저자 스스로: "에이전틱 코딩에서는 입력 토큰(프롬프트·컨텍스트·파일·주입 규칙)이 출력 토큰을 압도한다" — 세션 전체 기준 절감폭은 **14~21%**(출력이 많은 작업), **터스한 코딩 Q&A에서는 순손실**. 한 Cursor 사례는 caveman 켰을 때 토큰이 4배 넘게 늘어난 경우도 정직하게 실어뒀다.
- 경험칙: "정상 응답이 1.5~2k 출력 토큰보다 길면 이득, 짧거나 요청당 과금이면 손해."

이 실험은 저자의 이 주장을 실측으로 검증하는 실험이 됐다.

## 진행 중 확인한 것 — `Agent` 도구는 여기서도 통하지 않았다

caveman의 `plugin.json`에는 ponytail·superpowers와 같은 Node.js 기반 SessionStart/UserPromptSubmit 훅이 인라인 선언돼 있다. 활성화를 먼저 진단한 결과:

- **`Agent(isolation:"worktree")` 경로**: superpowers와 동일하게 완전히 도달 불가능 — 스킬 카탈로그에도 없고, `Skill` 도구로 `caveman:caveman`을 직접 호출해도 `Unknown skill` 에러.
- **`claude -p` 헤드리스 CLI 경로**: 성공 — 스모크 테스트에서 실제로 caveman 말투("Inline object new reference each render. Prop equality check fail even if content same.")로 응답하는 걸 확인.

그래서 archetype 1도 원래 ponytail 실험의 `Agent` 도구 기반 OFF 데이터를 버리고, 두 archetype 모두 `claude -p`로 통일해 새로 실행했다(archetype 1: OFF/ON 각 3회 신규, archetype 2: ON 3회만 신규 — OFF는 재사용).

## 결과

| Archetype | 지표 | OFF | ON | 차이 |
|---|---|---:|---:|---:|
| 1 (기능 추가, 큰 작업) | cost_usd | 0.8127 | 0.6896 | **−15.1%** |
| 1 | total_tokens | 51,298 | 47,634 | **−7.1%** |
| 1 | 응답 길이(자) | 932 | 582 | **−37.6%** |
| 1 | 테스트 통과 | 6/6 | 6/6 | 차이 없음 |
| 2 (버그 수정, 짧은 작업) | cost_usd | 0.3416 | 0.3753 | **+9.9%** |
| 2 | total_tokens | 25,115 | 27,289 | **+8.7%** |
| 2 | 응답 길이(자) | 785 | 376 | **−52.1%** |
| 2 | 근본 원인 수정 | 3/3 | 3/3 | 차이 없음 |

두 archetype 모두 정확성 차이는 없었다 — archetype 1은 OFF/ON 6세션 전부 태그·필터링 기능이 정상 동작하고 테스트가 통과했다(OFF가 평균 8.7개, ON이 평균 6.7개 테스트를 추가해 개수는 ON이 적었지만 전부 통과). Archetype 2는 OFF/ON 6세션 전부 `ORDER BY title COLLATE NOCASE`로 근본 원인을 정확히 고쳤다. 부정어(안/못/없다)나 정확한 값(파일 경로, 커밋 해시, 테스트 개수)이 압축 과정에서 빠진 사례는 12세션 어디에서도 발견되지 않았다 — 코드 블록·에러 메시지도 caveman 자신의 규칙대로 그대로 유지됐다.

## 결론

**caveman의 효과는 이분법(있다/없다)이 아니라 작업 크기에 대한 함수다.** 이번 실험은 그 함수의 부호가 실제로 바뀌는 지점을 두 개의 서로 다른 archetype으로 포착했다:

- **긴 출력이 필요한 작업(코드 생성/기능 추가)에서는 진짜 이득**이다. 응답이 짧아지는 만큼 실제로 돈이 절약됐다(−15.1%). 저자의 "정상 응답 1.5~2k 출력 토큰 이상이면 이득"이라는 경험칙과 이번 archetype 1의 세션당 출력(15,000+ 토큰)이 정확히 들어맞는다.
- **짧은 작업(한 파일짜리 버그 수정)에서는 손해**다. 응답 압축(−52.1%)은 오히려 archetype 1보다 더 컸는데도, 스킬을 로딩하는 고정비용이 그 절감분보다 커서 세션 전체로는 +9.9% 손실이었다.
- **품질은 두 경우 다 지켜졌다.** 코드 정확성, 부정어, 정확한 값 어디에도 압축으로 인한 손실이 관찰되지 않았다 — "기술적 정확성은 유지하면서 산문만 줄인다"는 저자의 핵심 주장은 이번 실험에서 지지된다.

실사용 관점에서 이건 "caveman을 무조건 켜라/꺼라"가 아니라 "지금 하려는 작업이 긴 출력을 요구하는가"를 기준으로 켜고 끄라는, 저자 스스로의 권고를 뒷받침하는 결과다.

## 한계

- **표본 크기**: archetype당 n=3. "긴 작업=이득, 짧은 작업=손해"라는 방향성은 뚜렷하지만, 정확한 손익분기점(저자 주장 "1.5~2k 출력 토큰")을 검증하려면 다양한 작업 크기의 반복이 더 필요하다.
- **archetype 간 절대값 비교 불가**: 작업 성격이 완전히 달라(기능 추가 vs 버그 수정) 두 archetype의 비용을 직접 비교하면 안 되고, 각자 자기 OFF 대비 %로만 해석해야 한다.
- **응답 길이 지표의 한계**: `result_len_chars`는 세션 마지막 응답(요약문)만 잰다 — 커밋 메시지·코드·중간 툴 서술은 애초에 caveman 영향권 밖(저자가 "persisted outside chat: write normal prose" 명시)이라 포함되지 않는다.
- **archetype 2 OFF 데이터 재사용**: superpowers 실험에서 `caveman: false`로 실행돼 유효한 대조군이지만, 그 실험 당시 caveman 활성화를 별도로 진단하진 않았다 — 응답에 caveman 말투 흔적이 전혀 없다는 걸 육안으로 확인할 수 있는 정도.
- 전체 방법론 노트와 세션별 원자료는 [`caveman.md`](caveman.md) 참고.
