# skill-experiment-lab

Claude Code 스킬/플러그인을 통제된 on/off 실험으로 검증하기 위한 재사용 가능한 실험 하네스.

## 무엇을 하는 저장소인가

새로운 Claude Code 스킬이나 플러그인을 써볼 때마다 레포를 새로 만드는 대신, 여기서 archetype별 baseline 픽스처를 재사용해 "적용 전/후"를 비교한다. **fixtures, 실행 절차, 실험 결과를 포함한 이 저장소 전체를 GitHub에 공개한다** — 실험 결과가 공개 저장소에 그대로 남아, `jhwanseok.github.io` 블로그 Projects 글에서 근거(evidence)로 링크할 수 있다. 로컬에만 두고 git에 올리지 않는 건 `SKILLS_BACKLOG.md`(검토 전 개인 메모)와 `experiments/PLAN.md`(비공개로 두는 실험 계획) 두 개뿐이다(`.gitignore` 처리).

## 구조

```
fixtures/            archetype별 baseline 앱 (baseline 태그는 불변)
experiments/          실험 계획(PLAN.md, 로컬 전용), 실행 이력(INDEX.md), 실행별 지표(results/)
SKILLS_BACKLOG.md     리뷰/실험 대상 스킬·플러그인 목록 — 로컬 전용, git에 올리지 않음
CLAUDE.md             작업 시작 시 참고할 워크플로우/원칙
.claude/commands/      /add-skill 같은 커스텀 커맨드
```

자세한 워크플로우와 원칙은 `CLAUDE.md`를, 지금 진행 중/예정인 실험의 구체적 절차는 로컬의 `experiments/PLAN.md`를 참고.