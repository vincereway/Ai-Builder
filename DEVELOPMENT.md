# Ai-Builder 개발 문서

## 1. 프로젝트 개요

**Ai-Builder**는 시그마차트(SigmaChart)의 진료 기록을 AI(Gemini, OpenAI GPT)를 활용하여
자동으로 개선(Enhance)해주는 PySide6 기반 Windows 데스크톱 애플리케이션입니다.

- **Python**: 3.11.9 (64-bit)
- **UI Framework**: PySide6 (Qt Designer `.ui` → `pyside6-uic` 컴파일 → Python 코드)
- **빌드**: PyInstaller
- **OS**: Windows

---

## 2. 프로젝트 폴더 구조

sigma_agent의 구조를 참고하되, 글로벌 표준 Python 패키지 구조를 따릅니다.

```
Ai-Builder/
├── main.py                         # 진입점 (src/ai_builder/app.py 호출)
├── build.bat                       # 원클릭 빌드 스크립트
├── requirements.txt                # 의존성 패키지 목록
├── README.md                       # 프로젝트 설명
├── README.txt                      # 원본 요구사항
│
├── conf/
│   └── conf.yml                    # 런타임 설정 (YAML)
├── resources/
│   └── icon.ico                    # 앱 아이콘
│
├── scripts/
│   ├── compile_ui.py               # UI 컴파일 스크립트 (.ui → .py)
│   └── build/
│       ├── build_ai_builder.bat    # PyInstaller 빌드 스크립트
│       └── AiBuilder.spec          # PyInstaller spec 파일
│
├── src/
│   └── ai_builder/
│       ├── __init__.py             # 패키지 초기화 + 버전 export
│       ├── app.py                  # QApplication 생성, 메인 윈도우 실행
│       ├── version.py              # 버전 정보 중앙 관리
│       │
│       ├── conf/                   # 설정 관리
│       │   ├── __init__.py
│       │   ├── nnconfig.py         # Config 클래스 (경로, YAML 로드)
│       │   └── nnlogger.py         # 로깅 시스템 (날짜별 파일, 7일 백업, 30일 삭제)
│       │
│       ├── constants/              # 상수 정의
│       │   ├── __init__.py
│       │   └── enums.py            # API URL, 상태 코드 등 상수
│       │
│       ├── ui/                     # UI 시스템
│       │   ├── __init__.py
│       │   ├── forms/              # Qt Designer .ui 파일
│       │   │   ├── main_window.ui      # 메인 뷰
│       │   │   └── settings_window.ui  # 설정 뷰
│       │   ├── generated/          # 컴파일된 UI Python 파일 (자동 생성)
│       │   │   ├── __init__.py
│       │   │   ├── main_window_ui.py
│       │   │   └── settings_window_ui.py
│       │   ├── windows/            # 윈도우 클래스들
│       │   │   ├── __init__.py
│       │   │   ├── main_window.py      # 메인 윈도우 로직
│       │   │   └── settings_window.py  # 설정 윈도우 로직
│       │   └── styles.qss          # QSS 스타일시트 (선택)
│       │
│       ├── services/               # 비즈니스 로직
│       │   ├── __init__.py
│       │   ├── sigma_api.py        # 시그마차트 API 클라이언트
│       │   ├── ai_service.py       # AI API 통합 (Gemini + OpenAI)
│       │   ├── prompt_manager.py   # 프롬프트 CRUD + 순서 관리
│       │   └── network_scanner.py  # IP 대역 헬스체크 스캐너
│       │
│       ├── workers/                # QThread 워커 (비동기 처리)
│       │   ├── __init__.py
│       │   ├── encounter_worker.py # 진료 목록/상세 조회 워커
│       │   ├── enhance_worker.py   # AI Enhance 워커
│       │   ├── scan_worker.py      # IP 스캔 워커
│       │   └── save_worker.py      # 시그마차트 저장 워커
│       │
│       ├── models/                 # 데이터 모델 (dataclass 또는 dict)
│       │   ├── __init__.py
│       │   └── prompt.py           # 프롬프트 데이터 모델
│       │
│       ├── common/                 # 공통 유틸리티
│       │   ├── __init__.py
│       │   └── msgbox.py           # 메시지박스 유틸리티
│       │
│       └── data/                   # 로컬 데이터 저장
│           └── prompts.json        # 프롬프트 저장 파일
│
├── logs/                           # 로그 파일 (자동 생성)
└── data/                           # 사용자 데이터 (자동 생성)
```

---

## 3. 뷰 구성

### 3.1 메인 뷰 (`main_window.ui`)

메인 뷰는 3개 영역으로 구성됩니다.

```
┌─────────────────────────────────────────────────────────────────────┐
│ [⚙ 설정]                                    연결상태: 🟢 정상      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ▶ 진료 목록 ────────────────────────────────────────────────────── │
│ ┌───────────────────────┐  ┌──────────────────────────────────────┐│
│ │ 날짜: [2026-03-13] ▼  │  │                                      ││
│ │  [목록조회]            │  │  encounter.plain_note 표시 영역      ││
│ │                        │  │  (읽기 전용 텍스트)                   ││
│ │ ┌──────────────────┐  │  │                                      ││
│ │ │ 홍길동 (123)     │  │  │                                      ││
│ │ │ 김영희 (456)     │  │  └──────────────────────────────────────┘│
│ │ │ 박철수 (789)     │  │  ┌──────────────────────────────────────┐│
│ │ │                  │  │  │  AI Enhance 결과 표시 영역            ││
│ │ │                  │  │  │  (읽기/쓰기 가능 텍스트)              ││
│ │ └──────────────────┘  │  │                                      ││
│ │  [조회]                │  └──────────────────────────────────────┘│
│ └───────────────────────┘                                           │
│                                                                     │
│ ▶ AI Agent ─────────────────────────────────────────────────────── │
│ │ 모델 선택: [Gemini ▼]    [Enhance]    [시그마차트에 저장]       │ │
│                                                                     │
│ ▶ 프롬프트 관리 ────────────────────────────────────────────────── │
│ ┌───────────────────────┐  ┌──────────────────────────────────────┐│
│ │ ┌──────────────────┐  │  │ 제목: [                            ] ││
│ │ │ ① SOAP 변환      │  │  │                                      ││
│ │ │ ② 진료요약       │  │  │ 내용:                                ││
│ │ │ ③ 처방근거       │  │  │ ┌──────────────────────────────────┐ ││
│ │ │                  │  │  │ │ 당신은 한의학 전문 AI입니다...    │ ││
│ │ └──────────────────┘  │  │ │                                    │ ││
│ │ [신규][수정][삭제]     │  │ │                                    │ ││
│ │ [▲ 위][▼ 아래]        │  │ └──────────────────────────────────┘ ││
│ └───────────────────────┘  │                          [저장]       ││
│                             └──────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 설정 뷰 (`settings_window.ui`)

별도 다이얼로그(QDialog)로 구현합니다.

```
┌────────────────────────────────────────────────────────────┐
│ 설정                                        연결상태: 🟢   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ ▶ 시그마차트 API ──────────────────────────────────────── │
│ │ 서버 IP: [192.168.0.100   ]  [검색하기]  상태: 🟢 정상 │ │
│ │ API 키 : [sigma_xxxxxxxxx ]  [💾 저장]   상태: 🟢 정상 │ │
│                                                            │
│ ▶ Gemini (Google AI) ──────────────────────────────────── │
│ │ 🔗 Google AI Studio로 이동하기                          │ │
│ │ API 키 : [AIzaSy_xxxxxxxxx]  [💾 저장]                  │ │
│                                                            │
│ ▶ OpenAI GPT ──────────────────────────────────────────── │
│ │ 🔗 OpenAI AI플랫폼 이동하기                             │ │
│ │ SECRET KEY: [sk-xxxxxxxxxxxx]  [💾 저장]                │ │
│                                                            │
│                                              [닫기]        │
└────────────────────────────────────────────────────────────┘
```

---

## 4. 기능 상세 명세

### 4.1 설정 뷰 기능

#### 4.1.1 시그마차트 서버 검색 (`network_scanner.py`)

| 항목         | 내용                                                                             |
| ------------ | -------------------------------------------------------------------------------- |
| 트리거       | [검색하기] 버튼 클릭                                                             |
| 동작         | 현재 PC의 로컬 IP 대역을 감지 → `x.x.x.0` ~ `x.x.x.255` 전체에 Health Check 요청 |
| API          | `GET https://{ip}:57443/health/simple/`                                          |
| 성공 응답    | `{"status": "ok"}`                                                               |
| 타임아웃     | 개별 IP당 300ms (전체 약 20초 이내)                                              |
| 저장         | 응답 성공한 IP를 `conf/conf.yml` → `SIGMA_SERVER_IP`에 저장                      |
| 비동기       | `ScanWorker(QThread)` — UI 블로킹 방지                                           |
| 다음 실행 시 | 저장된 IP로 즉시 Health Check, 실패 시 연결끊김 표시                             |

**동시 연결 최적화**: `concurrent.futures.ThreadPoolExecutor(max_workers=50)`로 병렬 스캔

#### 4.1.2 시그마차트 API 키 저장 및 검증

| 항목      | 내용                                                                             |
| --------- | -------------------------------------------------------------------------------- |
| 트리거    | API 키 입력 후 [💾 저장] 클릭                                                    |
| 검증 API  | `GET https://{server_ip}:57443/external/v1/encounters?encounter_date={오늘날짜}` |
| 검증 방식 | 인증이 필요한 외부 API 엔드포인트에 Bearer 토큰을 붙여 호출하여 유효성을 확인    |
| 성공      | 상태 표시: "✅ 정상"                                                             |
| 실패      | 상태 표시: "❌ API 키 값이 올바르지 않습니다"                                    |
| 저장 위치 | `conf/conf.yml` → `SIGMA_API_KEY`                                                |

> 참고: `/health/`, `/health/simple/`은 sigma_server 구현상 인증이 없는 헬스 체크 엔드포인트이므로 API 키 검증 용도로 사용하지 않습니다.

**인증 헤더 형식**:

```
Authorization: Bearer sigma_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 4.1.3 Gemini API 키 저장

| 항목      | 내용                                                                                                                |
| --------- | ------------------------------------------------------------------------------------------------------------------- |
| 링크      | https://aistudio.google.com/api-keys?hl=ko                                                                          |
| 검증 API  | `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key={api_key}` |
| 요청 Body | `{"contents": [{"parts": [{"text": "Hi"}]}]}`                                                                       |
| 저장 위치 | `conf/conf.yml` → `GEMINI_API_KEY`                                                                                  |

#### 4.1.4 OpenAI API 키 저장

| 항목      | 내용                                                       |
| --------- | ---------------------------------------------------------- |
| 링크      | https://platform.openai.com/settings/organization/api-keys |
| 검증 API  | `GET https://api.openai.com/v1/models`                     |
| 헤더      | `Authorization: Bearer sk-xxxxxxxx`                        |
| 저장 위치 | `conf/conf.yml` → `OPENAI_API_KEY`                         |

---

### 4.2 메인 뷰 기능

#### 4.2.1 진료 목록 조회

| 항목             | 내용                                                                               |
| ---------------- | ---------------------------------------------------------------------------------- |
| 트리거           | 날짜 선택 → [목록조회] 클릭                                                        |
| API              | `GET https://{server_ip}:57443/external/v1/encounters?encounter_date={YYYY-MM-DD}` |
| 헤더             | `Authorization: Bearer {sigma_api_key}`                                            |
| 응답             | `results[]`: `patient_id`, `patient_name`, `encounter_uuid`, `encounter_date`      |
| 페이지네이션     | Cursor 방식. `has_next=true`이면 `next_cursor`로 추가 요청                         |
| QListWidget 표시 | `환자이름 (차트번호)` 형식으로 표시, `encounter_uuid`를 `item.data()`에 저장       |
| 비동기           | `EncounterWorker(QThread)`                                                         |

#### 4.2.2 진료 상세 조회 (plain_note)

| 항목      | 내용                                                                    |
| --------- | ----------------------------------------------------------------------- |
| 트리거    | 목록에서 환자 선택 → [조회] 클릭                                        |
| API       | `GET https://{server_ip}:57443/external/v1/encounters/{encounter_uuid}` |
| 헤더      | `Authorization: Bearer {sigma_api_key}`                                 |
| 응답 필드 | `plain_note` (진료 기록 텍스트)                                         |
| 표시      | 우측 상단 QPlainTextEdit (읽기 전용)                                    |
| 비동기    | `EncounterWorker(QThread)`                                              |

#### 4.2.3 프롬프트 관리 (CRUD + 순서 변경)

**데이터 모델** (`data/prompts.json`):

```json
{
  "prompts": [
    {
      "id": "uuid-string",
      "title": "SOAP 변환",
      "content": "당신은 한의학 전문 AI입니다. 아래 진료 기록을 SOAP 형식으로 변환하세요...",
      "order": 0,
      "created_dt": "2026-03-13T10:00:00",
      "updated_dt": "2026-03-13T10:00:00"
    }
  ]
}
```

| 기능          | 동작                                                                          |
| ------------- | ----------------------------------------------------------------------------- |
| **신규**      | [신규] 클릭 → 제목/내용 빈칸 활성화 → 입력 후 [저장] → prompts.json에 추가    |
| **수정**      | 목록에서 선택 → [수정] 클릭 → 내용 편집 가능 → [저장] → prompts.json 업데이트 |
| **삭제**      | 목록에서 선택 → [삭제] 클릭 → "삭제할까요?" 확인 → prompts.json에서 제거      |
| **순서**      | [▲ 위] / [▼ 아래] 버튼으로 order 값 스왑 → 리스트 재정렬                      |
| **목록 클릭** | 클릭한 프롬프트의 내용을 우측에 표시 (읽기 전용)                              |

**순서 변경 방식**: 버튼(`▲ 위` / `▼ 아래`) 방식 채택

- 마우스 드래그보다 구현이 명확하고 접근성이 좋음
- `order` 필드 기반으로 QListWidget 정렬

#### 4.2.4 AI Agent 선택 (콤보박스)

| 항목         | 내용                                                              |
| ------------ | ----------------------------------------------------------------- |
| 위치         | 프롬프트 영역 상단                                                |
| 항목         | conf.yml에 API 키가 존재하는 AI만 표시                            |
| 후보         | `Gemini` (GEMINI_API_KEY 있을 때), `GPT` (OPENAI_API_KEY 있을 때) |
| 변경 시      | 즉시 `conf/conf.yml` → `SELECTED_AI_AGENT`에 저장                 |
| 다음 실행 시 | 저장된 값으로 콤보박스 초기 설정                                  |

#### 4.2.5 AI Enhance

| 항목      | 내용                                                                                                                                  |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| 트리거    | [Enhance] 버튼 클릭                                                                                                                   |
| 사전 검증 | ① AI Agent 선택됨 ② AI API 키 존재 ③ Sigma API 키 존재 ④ Sigma 서버 Health 정상 ⑤ `plain_note` 텍스트 존재 ⑥ 프롬프트가 선택되어 있음 |
| 검증 실패 | QMessageBox로 구체적 실패 원인 안내                                                                                                   |

**Enhance 프로세스**:

```
1. 현재 선택된 프롬프트 1개의 내용을 시스템 프롬프트로 사용
2. 유저 메시지 = plain_note 텍스트
3. 선택된 AI API 호출
4. 결과를 하단 QPlainTextEdit에 표시
```

**Gemini API 호출** (`ai_service.py`):

```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key={api_key}
Content-Type: application/json

{
  "system_instruction": {
    "parts": [{"text": "{선택된_프롬프트_내용}"}]
  },
  "contents": [
    {
      "role": "user",
      "parts": [{"text": "{plain_note}"}]
    }
  ]
}
```

**OpenAI GPT API 호출** (`ai_service.py`):

```
POST https://api.openai.com/v1/responses
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "model": "gpt-5.4",
  "input": [
    {
      "role": "system",
      "content": "{선택된_프롬프트_내용}"
    },
    {
      "role": "user",
      "content": "{plain_note}"
    }
  ]
}
```

> **참고**: Gemini `gemini-3.1-pro-preview`, OpenAI `gpt-5.4` 모델을 사용합니다. OpenAI는 공식 quickstart 및 GPT-5.4 가이드 기준으로 Responses API를 사용합니다.

#### 4.2.6 시그마차트에 저장

| 항목      | 내용                                                                                    |
| --------- | --------------------------------------------------------------------------------------- |
| 트리거    | [시그마차트에 저장] 클릭                                                                |
| 사전 검증 | Enhance 결과 텍스트가 존재하는지 확인                                                   |
| API       | `PATCH https://{server_ip}:57443/external/v1/encounters/{encounter_uuid}/external-note` |
| 헤더      | `Authorization: Bearer {sigma_api_key}`, `Content-Type: application/json`               |
| 요청 Body | `{"external_note": "{결과텍스트}"}`                                                     |
| 동작      | `external_note` 텍스트 전체 교체 (최대 100KB)                                           |
| 성공      | "저장 완료" 메시지 표시                                                                 |
| 비동기    | `SaveWorker(QThread)`                                                                   |

---

## 5. 연결 상태 관리

### 5.1 상태 아이콘

| 상태   | 아이콘       | 조건                                |
| ------ | ------------ | ----------------------------------- |
| 정상   | 🟢 (녹색 원) | Health Check 성공                   |
| 끊김   | 🔴 (빨간 원) | Health Check 실패 또는 서버 IP 없음 |
| 미설정 | ⚪ (회색 원) | 서버 IP 미설정                      |

### 5.2 Health Check 타이밍

| 시점          | 동작                          |
| ------------- | ----------------------------- |
| 앱 시작       | 저장된 IP로 즉시 Health Check |
| 설정 변경     | IP/API키 변경 후 즉시 재확인  |
| API 호출 실패 | 연결끊김으로 상태 변경        |

### 5.3 메인 뷰/설정 뷰 동기화

- 연결 상태는 앱 전체에서 공유 (Config 또는 시그널)
- 설정 뷰에서 상태 변경 → 메인 뷰에도 즉시 반영
- 메인 뷰 상단 바에 상태 아이콘 표시

---

## 6. conf.yml 설정 파일 구조

```yaml
# 시그마차트 서버 설정
SIGMA_SERVER_IP: "192.168.0.100"
SIGMA_SERVER_PORT: 57443
SIGMA_API_KEY: "sigma_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# AI API 키
GEMINI_API_KEY: "AIzaSy_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
OPENAI_API_KEY: "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# AI Agent 선택 (gemini / openai)
SELECTED_AI_AGENT: "gemini"

# 로그 레벨
LOG_LEVEL: "DEBUG"
```

---

## 7. 핵심 클래스 설계

### 7.1 Config (`conf/nnconfig.py`)

```python
class Config:
    """앱 설정 관리"""
    project_path: Path          # 프로젝트 루트
    logs_path: Path             # 로그 디렉토리
    data_path: Path             # 데이터 디렉토리
    conf_file_path: Path        # conf.yml 경로

    # YAML에서 로드
    sigma_server_ip: str
    sigma_server_port: int      # 기본값 57443
    sigma_api_key: str
    gemini_api_key: str
    openai_api_key: str
    selected_ai_agent: str
    log_level: str

    def save_config(key, value)  # 개별 설정 저장
    def load_config()            # YAML 전체 로드
```

### 7.2 SigmaApiClient (`services/sigma_api.py`)

```python
class SigmaApiClient:
    """시그마차트 서버 API 클라이언트"""

    def health_check() -> bool
    def validate_api_key(api_key: str) -> bool
    def get_encounters(date: str, cursor: str = None) -> dict
    def get_encounter_detail(encounter_uuid: str) -> dict
    def save_external_note(encounter_uuid: str, note: str) -> dict
```

### 7.3 AiService (`services/ai_service.py`)

```python
class AiService:
    """AI API 통합 클라이언트"""

    def call_gemini(system_prompt: str, user_message: str) -> str
    def call_openai(system_prompt: str, user_message: str) -> str
    def enhance(agent_type: str, system_prompt: str, plain_note: str) -> str

    @staticmethod
    def validate_gemini_key(api_key: str) -> bool

    @staticmethod
    def validate_openai_key(api_key: str) -> bool
```

### 7.4 PromptManager (`services/prompt_manager.py`)

```python
class PromptManager:
    """프롬프트 CRUD + 순서 관리"""

    def load_prompts() -> list[dict]
    def save_prompts(prompts: list[dict]) -> None
    def create_prompt(title: str, content: str) -> dict
    def update_prompt(prompt_id: str, content: str) -> dict
    def delete_prompt(prompt_id: str) -> None
    def move_up(prompt_id: str) -> None
    def move_down(prompt_id: str) -> None
    def get_prompt_by_id(prompt_id: str) -> dict  # 선택된 프롬프트 1개 반환
```

### 7.5 NetworkScanner (`services/network_scanner.py`)

```python
class NetworkScanner:
    """로컬 네트워크에서 시그마 서버 검색"""

    def get_local_ip() -> str
    def scan_network(base_ip: str) -> str | None  # 발견된 서버 IP
```

### 7.6 Worker 스레드

| Worker            | 역할                | 시그널                                                         |
| ----------------- | ------------------- | -------------------------------------------------------------- |
| `ScanWorker`      | IP 대역 스캔        | `found(str)`, `not_found()`, `error(str)`                      |
| `EncounterWorker` | 진료 목록/상세 조회 | `encounters_loaded(list)`, `detail_loaded(dict)`, `error(str)` |
| `EnhanceWorker`   | AI Enhance 실행     | `result(str)`, `error(str)`                                    |
| `SaveWorker`      | 시그마차트 저장     | `success()`, `error(str)`                                      |

---

## 8. API 통신 상세

### 8.1 시그마차트 API 엔드포인트 정리

| 용도           | Method | URL                                                      | 인증         |
| -------------- | ------ | -------------------------------------------------------- | ------------ |
| 간단 헬스체크  | GET    | `/health/simple/`                                        | 불필요       |
| 상세 헬스체크  | GET    | `/health/`                                               | 불필요       |
| 진료 목록      | GET    | `/external/v1/encounters?encounter_date=YYYY-MM-DD`      | Bearer Token |
| 진료 상세      | GET    | `/external/v1/encounters/{encounter_uuid}`               | Bearer Token |
| 외부 노트 저장 | PATCH  | `/external/v1/encounters/{encounter_uuid}/external-note` | Bearer Token |

### 8.2 시그마차트 API 응답 형식

**목록 조회 응답**:

```json
{
  "results": [
    {
      "patient_id": 123,
      "patient_name": "홍길동",
      "encounter_uuid": "550e8400-e29b-41d4-a716-446655440000",
      "encounter_date": "2026-03-13"
    }
  ],
  "pagination": {
    "limit": 50,
    "next_cursor": "MQ==",
    "has_next": true
  }
}
```

**상세 조회 응답**:

```json
{
  "encounter_uuid": "550e8400-...",
  "encounter_date": "2026-03-13",
  "plain_note": "환자 주소: 두통...",
  "external_note": null,
  "external_data": null
}
```

**외부 노트 저장 응답** (PATCH):

```json
{
  "encounter_uuid": "550e8400-...",
  "external_note": "S: 환자가 두통을 호소..."
}
```

### 8.3 시그마차트 인증 방식

```
Authorization: Bearer sigma_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

- 접두사: `sigma_`
- 전체 길이: 약 54자

### 8.4 Rate Limiting

시그마차트 API는 Token Bucket 방식의 Rate Limiting을 적용합니다. 대량 요청 시 429 응답이 올 수 있으므로, 목록 조회 시 적절한 간격(최소 100ms)을 두거나, 429 응답 시 재시도 로직을 구현합니다.

---

## 9. 빌드 시스템

### 9.1 build.bat

sigma_agent의 빌드 프로세스를 참고하여 단순화합니다 (PyArmor 난독화 불필요).

```
[1/4] Git 브랜치 표시
[2/4] UI 컴파일 (scripts/compile_ui.py)
[3/4] PyInstaller 빌드
[4/4] 빌드 결과 확인
```

### 9.2 compile_ui.py

- `src/ai_builder/ui/forms/*.ui` → `src/ai_builder/ui/generated/*_ui.py`
- `pyside6-uic` 명령어 사용

### 9.3 PyInstaller 빌드 옵션

```
--onefile              # 단일 EXE
--windowed             # 콘솔 창 없음
--name AiBuilder       # 실행 파일명
--icon=resources/icon.ico  # 앱 아이콘
--add-data "conf;conf" # 설정 파일 포함
```

---

## 10. 의존성 패키지 (requirements.txt)

```
PySide6>=6.8.0
requests>=2.31.0
PyYAML>=6.0
google-generativeai>=0.8.0    # Gemini API (선택: 직접 requests 사용도 가능)
openai>=1.0.0                 # OpenAI API (선택: 직접 requests 사용도 가능)
PyInstaller>=6.0               # 빌드용
```

> **참고**: Gemini와 OpenAI 모두 REST API를 직접 `requests`로 호출하는 것이 가볍고 의존성이 적습니다. 공식 SDK 없이 `requests`만으로 구현하는 것을 권장합니다.

**최종 의존성 (SDK 미사용 시)**:

```
PySide6>=6.8.0
requests>=2.31.0
PyYAML>=6.0
PyInstaller>=6.0
```

---

## 11. UI 클래스 패턴 (PySide6)

sigma_agent 패턴을 따릅니다.

```python
# src/ai_builder/ui/windows/main_window.py
from PySide6.QtWidgets import QMainWindow
from ai_builder.ui.generated.main_window_ui import Ui_MainWindow


class MainWindow(QMainWindow):
    """메인 윈도우"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # UI 설정
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 초기화
        self._init_ui()
        self._setup_connections()

    def _init_ui(self):
        """UI 초기 상태 설정"""
        pass

    def _setup_connections(self):
        """시그널-슬롯 연결"""
        self.ui.btn_search.clicked.connect(self._on_search_clicked)
```

---

## 12. 데이터 흐름 다이어그램

### 12.1 Enhance 전체 플로우

```
[사용자]
  │
  ├─ 1. 날짜 선택 → [목록조회]
  │     └─ EncounterWorker → GET /external/v1/encounters?encounter_date=...
  │           └─ 목록 표시 (QListWidget)
  │
  ├─ 2. 환자 선택 → [조회]
  │     └─ EncounterWorker → GET /external/v1/encounters/{uuid}
  │           └─ plain_note 표시 (QPlainTextEdit, 읽기 전용)
  │
  ├─ 3. AI Agent 선택 + [Enhance]
  │     └─ 사전 검증 (AI키 + Sigma키 + Health + 프롬프트 선택됨)
  │           └─ EnhanceWorker
  │                 ├─ 선택된 프롬프트 1개를 시스템 프롬프트로 사용
  │                 ├─ Gemini 또는 OpenAI API 호출
  │                 └─ 결과 텍스트 표시 (QPlainTextEdit, 편집 가능)
  │
  └─ 4. [시그마차트에 저장]
        └─ SaveWorker → PATCH /external/v1/encounters/{uuid}/external-note
              └─ {"external_note": "결과텍스트"}
```

### 12.2 설정 뷰 플로우

```
[사용자]
  │
  ├─ [검색하기] → ScanWorker
  │     └─ 192.168.x.0~255 순회 → GET /health/simple/
  │           └─ 성공 IP → conf.yml 저장 + UI 업데이트
  │
  ├─ Sigma API 키 [저장] → GET /external/v1/encounters?encounter_date={오늘날짜} (Bearer 인증)
  │     └─ 200: "정상" / 401: "API 키 올바르지 않음"
  │
  ├─ Gemini API 키 [저장] → POST generateContent (test)
  │     └─ 200: 저장 / 오류: 안내
  │
  └─ OpenAI API 키 [저장] → GET /v1/models
        └─ 200: 저장 / 오류: 안내
```

---

## 13. 에러 처리 전략

| 상황                   | 처리                                                 |
| ---------------------- | ---------------------------------------------------- |
| 서버 연결 실패         | 연결끊김 아이콘 + "서버에 연결할 수 없습니다" 메시지 |
| API 키 인증 실패 (401) | "API 키 값이 올바르지 않습니다"                      |
| Rate Limit (429)       | "잠시 후 다시 시도해 주세요"                         |
| AI API 오류            | 구체적 에러 메시지 표시 (모델 오류, 토큰 초과 등)    |
| 네트워크 타임아웃      | "요청 시간이 초과되었습니다"                         |
| 프롬프트 미선택        | "프롬프트를 선택해 주세요"                           |
| plain_note 없음        | "먼저 진료 기록을 조회해 주세요"                     |

---

## 14. 개발 순서 (권장)

### Phase 1: 프로젝트 골격

1. 폴더 구조 생성
2. `conf/nnconfig.py`, `conf/nnlogger.py` 구성
3. `main.py` → `app.py` 진입점 구성
4. `version.py` 생성
5. `compile_ui.py`, `build.bat` 구성

### Phase 2: 설정 뷰

6. `settings_window.ui` 디자인 + 컴파일
7. `SettingsWindow` 클래스 구현
8. `NetworkScanner` + `ScanWorker` 구현
9. conf.yml 저장/로드 구현
10. API 키 검증 로직 구현

### Phase 3: 메인 뷰 - 진료 조회

11. `main_window.ui` 디자인 + 컴파일
12. `MainWindow` 클래스 구현
13. `SigmaApiClient` 구현
14. `EncounterWorker` 구현
15. 진료 목록/상세 조회 연동

### Phase 4: 프롬프트 관리

16. `PromptManager` 구현 (JSON CRUD)
17. 프롬프트 UI 영역 구현 (신규/수정/삭제/순서)

### Phase 5: AI Enhance

18. `AiService` 구현 (Gemini + OpenAI)
19. `EnhanceWorker` 구현
20. AI 콤보박스 + Enhance 버튼 연동
21. `SaveWorker` + 시그마차트 저장 구현

### Phase 6: 빌드 및 마무리

22. `build.bat` 완성
23. PyInstaller spec 파일 작성
24. 통합 테스트

---

## 15. 확정된 사항

| 항목          | 결정                                               |
| ------------- | -------------------------------------------------- |
| Q1. 서버 포트 | `57443` (HTTPS/SSL) — `app/run_ssl.py` 기준        |
| Q2. 저장 방식 | `external_note` (텍스트 전체 교체, 최대 100KB)     |
| Q3. AI 모델   | Gemini `gemini-3.1-pro-preview` / OpenAI `gpt-5.4` |
| Q4. 프롬프트  | 선택된 프롬프트 1개만 시스템 프롬프트로 사용       |
| Q5. 앱 아이콘 | `resources/icon.ico` 경로로 프로젝트에 포함        |
| Q6. 저장 필드 | `EncounterExternalData.external_note` 사용         |
