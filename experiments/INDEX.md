# Experiments Index

실험 실행 이력 요약. 실행할 때마다 한 행씩 추가한다. 세부 지표는 `experiments/results/`의 개별 결과 파일을 참고.

| Date | Tool | Fixture | Ticket/Query | Condition | Reps | Primary Metric | Result | Notes |
|---|---|---|---|---|---|---|---|---|
| 2026-08-12 | ponytail | bookmarks-api | 티켓 A (태그+필터링) | OFF | 3 | subagent_tokens avg 52,724 | — | [design](design/ponytail.md) · [results](results/ponytail.md) |
| 2026-08-12 | ponytail | bookmarks-api | 티켓 A (태그+필터링) | ON | 3 | subagent_tokens avg 55,374 (+5.0% vs OFF) | 가설과 반대: 토큰·tool_uses·LOC 모두 ON이 더 큼. 재검토 결과 over-build trap 없는 티켓이었음 | [design](design/ponytail.md) · [results](results/ponytail.md) |
| 2026-08-12 | ponytail | bookmarks-api | 티켓 B (리마인드 날짜, date-picker 함정 설계) | OFF | 3 | subagent_tokens avg 49,244 | — | [design](design/ponytail.md) · [results](results/ponytail.md) |
| 2026-08-12 | ponytail | bookmarks-api | 티켓 B (리마인드 날짜, date-picker 함정 설계) | ON | 3 | subagent_tokens avg 51,177 (+3.9% vs OFF) | OFF도 이미 native `<input type="date">` 사용 — 함정에 아무도 안 빠짐(모델이 이미 lazy) | [design](design/ponytail.md) · [results](results/ponytail.md) |
