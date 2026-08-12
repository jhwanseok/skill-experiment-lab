# Experiments Index

실험 실행 이력 요약. 실행할 때마다 한 행씩 추가한다. 세부 지표는 `experiments/results/`의 개별 결과 파일을 참고.

| Date | Tool | Fixture | Ticket/Query | Condition | Reps | Primary Metric | Result | Notes |
|---|---|---|---|---|---|---|---|---|
| 2026-08-12 | ponytail | bookmarks-api | 티켓 A (태그+필터링) | OFF | 3 | subagent_tokens avg 52,724 | — | [design](design/ponytail.md) · [results](results/ponytail.md) |
| 2026-08-12 | ponytail | bookmarks-api | 티켓 A (태그+필터링) | ON (1세대, 무효) | 3 | subagent_tokens avg 55,374 | 활성화 검증 결과 ponytail 룰셋이 서브에이전트에 주입 안 됨 — 사실상 off vs off였음 | [design](design/ponytail.md) · [results](results/ponytail.md) |
| 2026-08-12 | ponytail | bookmarks-api | 티켓 A (태그+필터링) | ON-v2 (명시적 Skill 호출, 유효) | 3 | subagent_tokens avg 53,126 (+0.8% vs OFF) | LOC -49.2%, tool_uses -6.1%, 토큰만 거의 그대로 | [design](design/ponytail.md) · [results](results/ponytail.md) |
| 2026-08-12 | ponytail | bookmarks-api | 티켓 B (리마인드 날짜, date-picker 함정 설계) | OFF | 3 | subagent_tokens avg 49,244 | — | [design](design/ponytail.md) · [results](results/ponytail.md) |
| 2026-08-12 | ponytail | bookmarks-api | 티켓 B (리마인드 날짜, date-picker 함정 설계) | ON (1세대, 무효) | 3 | subagent_tokens avg 51,177 | 위와 동일한 활성화 실패 | [design](design/ponytail.md) · [results](results/ponytail.md) |
| 2026-08-12 | ponytail | bookmarks-api | 티켓 B (리마인드 날짜, date-picker 함정 설계) | ON-v2 (명시적 Skill 호출, 유효) | 3 | subagent_tokens avg 53,533 (+8.7% vs OFF) | LOC -34.4%, tool_uses -8.1%, 토큰은 오히려 증가(래더 추론 비용 추정) | [design](design/ponytail.md) · [results](results/ponytail.md) |
| 2026-08-12 | superpowers | bookmarks-api | 대소문자 정렬 버그(baseline-bug) | OFF | 3 | cost_usd avg 0.3416 | 근본원인 3/3 정확, RED/GREEN 분리 0/3, 스킬 없음 | [design](design/superpowers.md) · [results](results/superpowers.md) |
| 2026-08-12 | superpowers | bookmarks-api | 대소문자 정렬 버그(baseline-bug) | ON (claude -p 헤드리스, 유효) | 3 | cost_usd avg 0.4897 (+43.4% vs OFF) | 근본원인 3/3 정확(차이 없음), 2/3 자발적으로 systematic-debugging 호출, 1/3 RED/GREEN 분리 커밋, 비용/시간/토큰 30~43% 증가 | [design](design/superpowers.md) · [results](results/superpowers.md) |
| 2026-08-12 | caveman | bookmarks-api | 티켓 A(태그+필터, 큰 작업) | OFF/ON (claude -p, n=3+3) | 6 | cost_usd avg 0.8127→0.6896 (−15.1%) | 응답 길이 −37.6%, 테스트 6/6 통과 — 긴 작업에서 실제 순절감 | [design](design/caveman.md) · [results](results/caveman.md) |
| 2026-08-12 | caveman | bookmarks-api | 대소문자 정렬 버그(baseline-bug, 짧은 작업) | ON (claude -p, OFF는 superpowers 실험 재사용) | 3 | cost_usd avg 0.3416→0.3753 (+9.9%) | 응답 길이 −52.1%지만 세션 전체는 순손실 — 저자의 "터스한 작업은 손해" 주장과 일치 | [design](design/caveman.md) · [results](results/caveman.md) |
