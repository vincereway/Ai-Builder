# Ai-Builder Copilot Instructions

이 저장소의 Copilot 기준 문서는 `.github/instructions/` 아래의 instruction 파일들입니다.

우선순위:

1. 현재 코드
2. `.github/instructions/ai-builder-handover.instructions.md`
3. `.github/instructions/ai-builder-implementation-notes.instructions.md`
4. `.github/instructions/secrets-and-git-hygiene.instructions.md`
5. `.github/instructions/verification-runbook.instructions.md`
6. `DEVELOPMENT.md`

문서 사용 방식:

- 런타임 동작, 아키텍처, 현재 UX는 handover 문서를 기준으로 판단합니다.
- 최근 변경 이유와 회귀 포인트는 implementation notes를 우선 봅니다.
- 보안, git 추적 안전성, 민감정보 규칙은 secrets 문서를 우선 봅니다.
- 검증 명령과 재현 절차는 verification runbook을 필요 시 참고합니다.
- `DEVELOPMENT.md`는 현재 구현 요약과 개발 진입용 참고 문서입니다.

항상 지킬 것:

- 현재 메인 UX는 Sigma 저장이 아니라 클립보드 복사입니다.
- 진료 상세에서는 서버 `external_note`가 로컬 캐시보다 우선합니다.
- 앱 설정, 모델 목록 캐시, System Prompt, 진료 결과 캐시는 모두 `data/settings.sqlite3`를 기준으로 봅니다.
- `conf/conf.yml`은 개발 모드 기본값용이며, 민감정보의 기준 저장소로 취급하지 않습니다.
- Claude 응답 정규화는 `enhance_with_claude()` 경로를 기준으로 판단합니다.
- 실제 API 키, SQLite DB, 인증서, 내부 서버 정보는 추적 파일에 넣지 않습니다.
