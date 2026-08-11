---
description: 리뷰할 Claude Code 스킬/플러그인을 SKILLS_BACKLOG.md의 todo 목록에 추가합니다
argument-hint: [저장소 URL]
---

## 1. 입력 확인

`$ARGUMENTS`로 저장소 URL이 주어졌는지 확인하세요. 없다면 사용자에게 물어보세요.

## 2. 저장소 정보 파악

WebFetch로 저장소 README를 가져와 이름, 한 줄 설명, 유형(skill/plugin), 설치 방식을 파악하세요.

## 3. 중복 확인

`SKILLS_BACKLOG.md`에 같은 저장소가 이미 있는지 확인하세요. 있다면 새로 추가하지 말고 기존 행을 사용자에게 보여주고 끝내세요.

## 4. Archetype 추정

`CLAUDE.md`의 Archetype 표를 기준으로 가장 가까운 archetype을 추정하세요. 애매하면 단정하지 말고 `미정`으로 남기세요 — 잘못된 archetype 배정은 나중에 픽스처를 잘못 고르게 만듭니다.

## 5. 백로그에 추가

`SKILLS_BACKLOG.md` 표에 새 행을 추가하세요: Name, Repo, Type, Status(`todo`), Archetype(추정치 또는 `미정`), Core Question(README에서 드러나는 핵심 주장을 바탕으로 초안 제시), Added(오늘 날짜), Notes(특이사항).

## 6. 결과 보고

추가한 행 내용을 사용자에게 보여주고, Archetype이나 Core Question이 이상하면 고쳐달라고 안내하세요.
