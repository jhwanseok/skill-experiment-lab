# Experiments Index

실험 실행 이력 요약. 실행할 때마다 한 행씩 추가한다. 세부 지표는 `experiments/results/`의 개별 결과 파일을 참고.

| Date | Tool | Fixture | Ticket/Query | Condition | Reps | Primary Metric | Result | Notes |
|---|---|---|---|---|---|---|---|---|
| 2026-08-12 | ponytail | bookmarks-api | 티켓 A (태그+필터링) | OFF | 3 | subagent_tokens avg 52,724 | — | [design](design/ponytail.md) · [results](results/ponytail.md) |
| 2026-08-12 | ponytail | bookmarks-api | 티켓 A (태그+필터링) | ON | 3 | subagent_tokens avg 55,374 (+5.0% vs OFF) | 가설과 반대: 토큰·tool_uses·LOC 모두 ON이 더 큼 | [design](design/ponytail.md) · [results](results/ponytail.md) |
