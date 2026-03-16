# Ai-Builder 개발 문서

## 1. 문서 역할

이 문서는 현재 구현을 빠르게 파악하고 개발을 시작하기 위한 요약 문서입니다.

- 현재 동작과 운영 규칙은 먼저 `.github/` 아래 Copilot instruction 문서를 봅니다.
- 이 문서는 긴 초기 설계 문서 대신, 최신 구조와 개발 진입 정보만 남깁니다.
- 세부 검증 절차와 보안 규칙은 별도 instruction 문서로 분리했습니다.

우선 참고 순서:

1. `.github/copilot-instructions.md`
2. `.github/instructions/ai-builder-handover.instructions.md`
3. `.github/instructions/ai-builder-implementation-notes.instructions.md`
4. `.github/instructions/secrets-and-git-hygiene.instructions.md`
5. `.github/instructions/verification-runbook.instructions.md`

## 2. 현재 앱 개요

Ai-Builder는 Sigma 외부 API에서 진료 목록과 상세를 조회한 뒤, 선택한 System Prompt와 AI 모델로 진료 메모를 구조화된 JSON으로 변환하고, 사람이 읽기 쉬운 텍스트로 보여주는 PySide6 기반 Windows 데스크톱 앱입니다.

지원 AI:

- Gemini
- OpenAI GPT
- Claude

현재 사용자 흐름:

1. 설정에서 Sigma 서버와 API 키를 저장합니다.
2. 날짜를 선택해 진료 목록을 조회합니다.
3. 환자를 선택하면 우측 원문과 결과가 갱신됩니다.
4. System Prompt와 AI Agent를 선택해 Enhance를 실행합니다.
5. 결과는 `encounter_uuid` 기준으로 로컬 SQLite에 캐시됩니다.
6. 현재 결과는 Sigma 저장이 아니라 클립보드 복사로 내보냅니다.

## 3. 핵심 런타임 규칙

- 진료 목록 UI는 `QTableWidget` 기반 `No.` / `Name` 2컬럼입니다.
- 이름은 마스킹해서 표시합니다.
- 상세 조회는 selection changed, cell clicked, current cell changed 세 경로를 모두 사용합니다.
- 우측 결과는 서버 `external_note` 우선, 없으면 로컬 SQLite 캐시 fallback 정책을 사용합니다.
- 앱 설정, 모델 목록 캐시, System Prompt, 결과 캐시는 모두 `data/settings.sqlite3`를 기준으로 봅니다.
- `conf/conf.yml`은 개발 모드 기본값용이며 민감정보의 기준 저장소가 아닙니다.

## 4. 프로젝트 구조

```text
Ai-Builder/
├── main.py
├── build.bat
├── requirements.txt
├── .github/
│   ├── copilot-instructions.md
│   └── instructions/
├── scripts/
│   ├── compile_ui.py
│   └── build/
├── src/
│   ├── conf/nnconf/
│   └── ai_builder/
│       ├── app.py
│       ├── version.py
│       ├── constants/
│       ├── common/
│       ├── data/
│       ├── services/
│       ├── ui/
│       └── workers/
├── resources/
├── conf/
└── data/
```

중요 파일:

- `main.py`: 앱 진입점
- `src/ai_builder/app.py`: QApplication 생성과 앱 시작
- `src/ai_builder/ui/windows/main_window.py`: 메인 화면 상태와 사용자 흐름
- `src/ai_builder/ui/windows/settings_window.py`: 설정 저장, 모델 목록 조회
- `src/ai_builder/services/ai_service.py`: Gemini/OpenAI/Claude 호출
- `src/ai_builder/services/sigma_api.py`: Sigma API 클라이언트
- `src/ai_builder/services/system_prompt_manager.py`: System Prompt DB 관리
- `src/ai_builder/services/encounter_result_cache.py`: 진료 결과 캐시 관리
- `src/ai_builder/services/connection_status_service.py`: 중앙 연결 상태 관리
- `src/conf/nnconf/nnconfig.py`: YAML + SQLite 2계층 설정

## 5. 설정과 저장소

설정 계층:

- 개발 모드 기본값: `conf/conf.yml`
- 사용자 설정과 런타임 상태: `data/settings.sqlite3`

SQLite에 저장되는 주요 데이터:

- Sigma 서버 IP / API Key
- Gemini / OpenAI / Claude API Key
- 모델 ID와 모델 목록 캐시
- 선택 AI Agent
- 결과 보기 라벨
- System Prompt
- `encounter_result_cache`

민감정보 주의:

- `data/settings.sqlite3`는 git에 올리면 안 됩니다.
- 실제 API 키, 인증서, 내부 서버 정보는 추적 파일에 남기면 안 됩니다.

## 6. AI 및 Sigma 연동 요약

AI 공통:

- System Prompt는 DB에 원문만 저장합니다.
- 런타임에 JSON 계약 suffix를 붙여 전송합니다.
- Enhance 후 앱 레벨에서 JSON 구조를 다시 검증합니다.

Claude 주의점:

- 기본 모델은 `claude-sonnet-4-6`입니다.
- 응답이 Markdown 코드펜스로 감싸질 수 있어 `enhance_with_claude()`에서 정규화합니다.

Sigma 주의점:

- 기본 포트는 `57443`, 프로토콜은 HTTPS입니다.
- 429는 `get_encounters()`에서 1회 재시도 후 명확한 사용자 메시지로 안내합니다.

## 7. 개발 명령

개발 실행:

```powershell
d:/Github/Ai-Builder/.venv/Scripts/python.exe main.py
```

UI 컴파일:

```powershell
d:/Github/Ai-Builder/.venv/Scripts/python.exe scripts/compile_ui.py
```

빌드:

```powershell
Set-Location "d:/Github/Ai-Builder"
$env:Path = "d:/Github/Ai-Builder/.venv/Scripts;" + $env:Path
cmd /c build.bat
```

## 8. 작업 시 빠른 체크리스트

1. UI를 바꿨으면 `.ui`와 generated UI의 일치를 확인합니다.
2. 진료 선택 시 우측 원문/결과가 정상 갱신되는지 확인합니다.
3. 서버 `external_note` 우선, 로컬 캐시 fallback 규칙이 유지되는지 확인합니다.
4. Claude 응답이 여전히 JSON 파싱 가능한지 확인합니다.
5. `data/settings.sqlite3`가 git 추적 대상이 아닌지 확인합니다.

## 9. 추가 문서

- `.github/instructions/ai-builder-handover.instructions.md`: 현재 동작과 아키텍처
- `.github/instructions/ai-builder-implementation-notes.instructions.md`: 최근 변경 이유와 회귀 포인트
- `.github/instructions/secrets-and-git-hygiene.instructions.md`: 보안 및 git 위생
- `.github/instructions/verification-runbook.instructions.md`: 검증 명령과 재현 절차
