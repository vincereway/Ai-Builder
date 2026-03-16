# Ai-Builder

Ai-Builder는 Sigma 외부 API의 진료 기록을 조회하고, AI를 통해 구조화된 결과로 정리해 주는 PySide6 기반 Windows 데스크톱 앱입니다.

현재 기준의 최신 인수인계/자동 지시 문서는 아래 순서로 읽는 것이 가장 빠릅니다.

- [.github/copilot-instructions.md](.github/copilot-instructions.md): 저장소 전역 Copilot 공통 지시
- [.github/instructions/ai-builder-handover.instructions.md](.github/instructions/ai-builder-handover.instructions.md): 현재 동작, 핵심 파일, 운영 기준 요약
- [.github/instructions/ai-builder-implementation-notes.instructions.md](.github/instructions/ai-builder-implementation-notes.instructions.md): 최근 실제 구현 변경과 회귀 포인트
- [.github/instructions/verification-runbook.instructions.md](.github/instructions/verification-runbook.instructions.md): 재현 가능한 검증 절차
- [.github/instructions/secrets-and-git-hygiene.instructions.md](.github/instructions/secrets-and-git-hygiene.instructions.md): 비밀정보, 공개 저장소, git 운영 원칙
- [DEVELOPMENT.md](DEVELOPMENT.md): 초기 설계 및 상세 개발 참고 문서

중요:

- 최신 구현 기준은 `.github/` 아래 Copilot instruction 문서들입니다.
- `DEVELOPMENT.md`에는 초기 설계 기준 설명이 남아 있어 일부 내용이 현재 UI/동작과 다를 수 있습니다.
