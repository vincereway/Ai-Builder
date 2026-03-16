---
applyTo: "src/**/*.py"
description: "Current Ai-Builder runtime behavior, architecture, UX rules, and key files."
---

# Ai-Builder Agent Handover

## 1. 문서 역할

이 문서는 현재 구현을 가장 빠르게 이해하기 위한 요약 인수인계 문서입니다.

- 실제 동작 판단은 현재 코드가 최우선입니다.
- 이 문서는 현재 UX와 설계 의도를 짧게 고정합니다.
- 과거 설계 서술은 `DEVELOPMENT.md`보다 이 문서를 우선합니다.

## 2. 현재 앱 요약

Ai-Builder는 Sigma 외부 API에서 진료 목록과 상세를 가져오고, 선택한 System Prompt와 AI 모델로 진료 메모를 구조화된 JSON으로 변환해 사람이 읽기 쉬운 텍스트로 보여주는 Windows 데스크톱 앱입니다.

지원 AI:

- Gemini
- OpenAI GPT
- Claude

핵심 흐름:

1. 설정에서 Sigma 서버와 API 키를 저장합니다.
2. 날짜별 진료 목록을 조회합니다.
3. 환자를 선택하면 우측 원문과 결과 영역이 갱신됩니다.
4. System Prompt와 AI Agent를 선택해 Enhance를 실행합니다.
5. 결과는 `encounter_uuid` 기준으로 로컬 SQLite에 캐시됩니다.
6. 현재 화면의 결과는 Sigma 저장이 아니라 클립보드 복사로 내보냅니다.

## 3. 현재 구현의 고정 규칙

- 진료 목록은 `QTableWidget` 기반이며 컬럼은 `No.` / `Name`입니다.
- 환자명은 마스킹해서 표시합니다.
- 상세 조회 트리거는 selection changed, cell clicked, current cell changed 세 경로 모두 사용합니다.
- 우측 결과는 서버 `external_note` 우선, 없으면 로컬 SQLite 캐시 fallback 정책을 사용합니다.
- 결과 복사 버튼은 현재 화면에 보이는 결과 텍스트가 있을 때만 의미가 있습니다.
- 메인 UX에서 Sigma `external_note` 저장 버튼은 제거된 상태입니다.

## 4. 저장 구조

주요 로컬 저장소:

- `data/settings.sqlite3`

이 DB에 저장되는 핵심 데이터:

- Sigma 서버 IP / API Key
- Gemini / OpenAI / Claude API Key
- 선택 AI Agent
- 각 AI의 선택 모델 ID와 모델 목록 캐시
- 결과 보기 라벨 설정
- System Prompt
- `encounter_result_cache`

캐시 규칙:

- Enhance 성공 직후 `raw_result`와 `formatted_result`를 함께 저장합니다.
- 복원 시 `raw_result`가 있으면 현재 라벨 설정으로 다시 렌더링합니다.
- 재파싱이 실패하면 저장된 `formatted_result`를 fallback으로 씁니다.

## 5. 핵심 파일

진입점:

- `main.py`
- `src/ai_builder/app.py`

메인 UI:

- `src/ai_builder/ui/windows/main_window.py`
- `src/ai_builder/ui/forms/main_window.ui`
- `src/ai_builder/ui/generated/main_window_ui.py`

설정 UI:

- `src/ai_builder/ui/windows/settings_window.py`
- `src/ai_builder/ui/forms/settings_window.ui`
- `src/ai_builder/ui/generated/settings_window_ui.py`

연동/설정:

- `src/ai_builder/services/ai_service.py`
- `src/ai_builder/services/sigma_api.py`
- `src/ai_builder/services/network_scanner.py`
- `src/ai_builder/services/connection_status_service.py`
- `src/ai_builder/services/system_prompt_manager.py`
- `src/ai_builder/services/encounter_result_cache.py`
- `src/conf/nnconf/nnconfig.py`
- `src/ai_builder/constants/enums.py`
- `src/ai_builder/constants/prompt_contract.py`

## 6. AI / Sigma 구현 메모

AI 공통 규칙:

- System Prompt는 저장 시 원문만 저장합니다.
- 런타임에 `compose_enhance_system_prompt()`로 JSON 계약 suffix를 붙입니다.
- Enhance 성공 후 앱 레벨에서 JSON 구조를 다시 검증합니다.

Claude 주의점:

- 기본 모델은 `claude-sonnet-4-6`입니다.
- Claude는 Markdown 코드펜스 형태로 JSON을 돌려줄 수 있습니다.
- `AiService._normalize_json_response_text()`가 이를 제거합니다.
- 이 정규화는 현재 `enhance_with_claude()` 경로를 기준으로 판단합니다.

Sigma 주의점:

- 기본 포트는 `57443`, 프로토콜은 HTTPS입니다.
- `get_encounters()`만 429 자동 재시도를 1회 수행합니다.
- 메인 화면은 429 문구를 감지하면 일반 네트워크 오류와 구분해서 안내합니다.

## 7. 작업 전에 확인할 것

1. Agent 콤보에 Gemini, GPT, Claude가 모두 정상 반영되는지 확인합니다.
2. 진료 선택 시 우측 원문과 결과가 기대한 우선순위로 갱신되는지 확인합니다.
3. `external_note`가 비어 있을 때 로컬 캐시가 복원되는지 확인합니다.
4. 결과 복사 버튼이 현재 UX와 맞게 동작하는지 확인합니다.
5. `data/settings.sqlite3`가 git 추적 대상이 아닌지 확인합니다.
