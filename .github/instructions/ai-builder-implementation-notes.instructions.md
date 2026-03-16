---
applyTo: "src/**/*.py"
description: "Recent implementation history and regression hotspots for Ai-Builder source files."
---

# Recent Implementation Notes

## 1. 목적

이 문서는 왜 최근 기능이 바뀌었는지와 어디서 회귀가 나기 쉬운지를 짧게 정리합니다.

## 2. 최근 큰 변경

- SQLite 중심 설정 구조 정리
- 중앙 `ConnectionStatusService` 도입
- System Prompt 저장 구조를 DB 중심으로 정리
- 결과 보기 설정 반영
- 진료별 Enhance 결과 캐시 도입
- Sigma 저장 UX 제거 후 클립보드 복사 UX로 전환
- 진료 목록을 `QTableWidget` 기반 2컬럼으로 전환
- 테이블 전환 후 상세 미표시 버그 수정
- Sigma 429 Rate Limit UX 강화
- Claude 통합 및 실호출 검증 완료

## 3. 회귀 포인트

결과 캐시:

- 서버 `external_note`가 있으면 로컬 캐시가 덮어쓰면 안 됩니다.
- 결과 보기 라벨을 바꿔도 캐시 복원이 새 라벨로 다시 렌더링되어야 합니다.

클립보드 UX:

- 현재 메인 흐름은 저장이 아니라 복사입니다.
- 저장 관련 코드가 남아 있어도 메인 UX를 되살리면 사용자 기대와 어긋납니다.

진료 목록 테이블:

- `encounter_uuid`는 0열 `UserRole`에 저장합니다.
- selection changed, cell clicked, current cell changed 세 경로가 모두 상세 요청으로 이어져야 합니다.
- 중복 상세 요청 방지 로직을 깨면 우측 영역이 비정상 갱신될 수 있습니다.

Rate Limit UX:

- 429는 일반 네트워크 오류처럼 뭉뚱그리면 안 됩니다.
- 목록 조회 중 날짜 이동/조회 버튼 비활성화가 유지되어야 합니다.

Claude:

- 모델 목록 조회 성공과 실제 Messages API 성공은 별개였습니다.
- 응답이 코드펜스로 감싸질 수 있으므로 JSON 정규화 경로를 건드릴 때 주의해야 합니다.

## 4. 관련 파일

- `src/ai_builder/ui/windows/main_window.py`
- `src/ai_builder/ui/windows/settings_window.py`
- `src/ai_builder/services/ai_service.py`
- `src/ai_builder/services/sigma_api.py`
- `src/ai_builder/services/encounter_result_cache.py`
- `src/ai_builder/services/system_prompt_manager.py`
- `src/conf/nnconf/nnconfig.py`

## 5. 변경 시 빠른 체크

1. 진료 선택 시 우측 원문/결과가 정상 갱신되는지 확인합니다.
2. 캐시 복원과 서버 `external_note` 우선 규칙이 유지되는지 확인합니다.
3. Claude 응답이 여전히 JSON 파싱 가능한지 확인합니다.
4. 429 안내 문구가 일반 오류로 퇴행하지 않았는지 확인합니다.
