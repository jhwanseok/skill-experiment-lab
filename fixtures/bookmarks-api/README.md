# bookmarks-api

FastAPI + 정적 HTML/JS로 구성된 최소 "북마크 관리 API". CRUD 엔드포인트, SQLite 저장, 최소 리스트 뷰, 기본 테스트를 갖췄다. `bookmarks-api-baseline` 태그로 고정되어 있으며, 이 태그는 직접 수정하지 않는다 — 변경이 필요하면 새 태그를 만든다.

Archetype:
- 코드 생성/볼륨 (예: ponytail) — baseline에 신규 기능 티켓 적용
- 디버깅/프로세스 (예: superpowers) — `baseline-bug` 태그(시딩된 버그) 적용
- 세션 간 컨텍스트 (예: claude-mem) — baseline에서 세션 1→2 시나리오 진행

## 실행

```
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # Windows
.venv/bin/pip install -r requirements.txt        # macOS/Linux
.venv/Scripts/uvicorn app.main:app --reload       # http://127.0.0.1:8000
```

## 테스트

```
.venv/Scripts/python -m pytest -q
```

## 엔드포인트

- `GET /bookmarks` — 목록
- `POST /bookmarks` — 생성 (`{"url": "...", "title": "..."}`)
- `GET /bookmarks/{id}` — 단건 조회
- `DELETE /bookmarks/{id}` — 삭제
- `GET /` — 정적 리스트 뷰
