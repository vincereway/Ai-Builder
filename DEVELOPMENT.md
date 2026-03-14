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
│   ├── conf/
│   │   ├── __init__.py
│   │   └── nnconf/
│   │       ├── __init__.py
│   │       ├── nnconfig.py         # sigma_agent와 동일한 구조의 Config 클래스
│   │       └── nnlogger.py         # sigma_agent와 동일한 구조의 로깅 시스템
│   └── ai_builder/
│       ├── __init__.py             # 패키지 초기화 + 버전 export
│       ├── app.py                  # QApplication 생성, 메인 윈도우 실행
│       ├── version.py              # 버전 정보 중앙 관리
│       ├── constants/              # 상수 정의
│       │   ├── __init__.py
│       │   └── enums.py            # API URL, 상태 코드 등 상수
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
│       ├── services/               # 비즈니스 로직
│       │   ├── __init__.py
│       │   ├── sigma_api.py        # 시그마차트 API 클라이언트
│       │   ├── ai_service.py       # AI API 통합 (Gemini + OpenAI)
│       │   ├── prompt_manager.py   # 프롬프트 CRUD + 순서 관리
│       │   └── network_scanner.py  # IP 대역 헬스체크 스캐너
│       ├── workers/                # QThread 워커 (비동기 처리)
│       │   ├── __init__.py
│       │   ├── encounter_worker.py # 진료 목록/상세 조회 워커
│       │   ├── enhance_worker.py   # AI Enhance 워커
│       │   ├── scan_worker.py      # IP 스캔 워커
│       │   └── save_worker.py      # 시그마차트 저장 워커
│       ├── models/                 # 데이터 모델 (dataclass 또는 dict)
│       │   ├── __init__.py
│       │   └── prompt.py           # 프롬프트 데이터 모델
│       ├── common/                 # 공통 유틸리티
│       │   ├── __init__.py
│       │   └── msgbox.py           # 메시지박스 유틸리티
│       └── data/                   # 로컬 데이터 저장
│           └── prompts.json        # 프롬프트 저장 파일
│
├── logs/                           # 로그 파일 (자동 생성)
└── data/                           # 사용자 데이터 (자동 생성)
```

---

## 3. 뷰 구성

`nnconfig.py`, `nnlogger.py`는 사용자 요구사항에 맞춰 `src/conf/nnconf/`에 두고, `ai_builder` 패키지에서 공통 설정 모듈로 import하여 사용합니다.

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

**SSL 처리 참고**: sigma_server는 자체 서명 로컬 인증서를 사용하므로, 데스크톱 앱의 `requests` 호출은 `verify=False` 또는 신뢰할 CA 번들 지정이 필요합니다. sigma_agent의 기존 HTTPS 호출도 `verify=False` 패턴을 사용합니다.

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
> 참고: 외부 API는 표준 모드이므로 성공 시 `results`/`pagination` 또는 개별 필드만 반환하며 `code`, `message` 래퍼가 없습니다.

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
| 쿼리 파라미터    | `encounter_date` (필수), `limit` (기본 50, 최대 200), `cursor` (다음 페이지)       |
| 응답             | `results[]`: `patient_id`, `patient_name`, `encounter_uuid`, `encounter_date`      |
| 페이지네이션     | Cursor 방식. `has_next=true`이면 `next_cursor` 값을 `cursor` 파라미터로 전달       |
| QListWidget 표시 | `환자이름 (차트번호)` 형식으로 표시, `encounter_uuid`를 `item.data()`에 저장       |
| 비동기           | `EncounterWorker(QThread)`                                                         |

참고:

- `patient`가 없는 진료는 목록에서 제외됩니다.
- 결과 정렬은 sigma_server 구현 기준 `encounter_id` 오름차순입니다.
- 요청/응답 필드명은 모두 `snake_case`로 처리합니다.

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
  "instructions": "{선택된_프롬프트_내용}",
  "input": "{plain_note}"
}
```

> **참고**: Gemini `gemini-3.1-pro-preview`, OpenAI `gpt-5.4` 모델을 사용합니다. OpenAI는 공식 quickstart 및 GPT-5.4 가이드 기준으로 Responses API의 top-level `instructions` + `input` 형태를 사용합니다.

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

# 네트워크 설정
REQUEST_TIMEOUT_SECONDS: 10
SCAN_TIMEOUT_MS: 300
SSL_VERIFY: false
```

---

## 7. 핵심 클래스 설계

### 7.1 Config (`src/conf/nnconf/nnconfig.py`)

```python
class Config:
    """앱 설정 관리"""
    project_path: Path          # 프로젝트 루트
  root_path: Path             # 실행 루트
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
    request_timeout_seconds: int
    scan_timeout_ms: int
    ssl_verify: bool

    def save_config(key, value)  # 개별 설정 저장
    def load_config()            # YAML 전체 로드
    def ensure_directories()     # logs/, data/ 보장
```

### 7.2 SigmaApiClient (`services/sigma_api.py`)

```python
class SigmaApiClient:
    """시그마차트 서버 API 클라이언트"""
    def __init__(self, server_ip: str, api_key: str): ...

    def health_check() -> bool
    def validate_api_key() -> bool
    def get_encounters(target_date: str, cursor: str = None) -> dict
    def get_encounter_detail(encounter_uuid: str) -> dict
    def save_external_note(encounter_uuid: str, note: str) -> dict

    # server_ip, api_key는 생성자에서 주입받아 인스턴스 속성으로 사용
    # requests 호출 시 verify=False 또는 사용자 지정 CA 번들 경로 필요
```

### 7.3 AiService (`services/ai_service.py`)

```python
class AiService:
    """AI API 통합 클라이언트"""

    def enhance_with_gemini(prompt_text: str, plain_note: str) -> str
    def enhance_with_openai(prompt_text: str, plain_note: str) -> str
    def enhance(agent_type: str, prompt_text: str, plain_note: str) -> str

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
    def update_prompt(prompt_id: str, title: str, content: str) -> dict
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
  def get_base_network(ip: str) -> str
  def check_host(ip: str) -> bool
  def scan_network() -> str | None  # 발견된 서버 IP
```

### 7.6 Worker 스레드

| Worker            | 역할                | 시그널                                                         |
| ----------------- | ------------------- | -------------------------------------------------------------- |
| `ScanWorker`      | IP 대역 스캔        | `found(str)`, `not_found()`, `error(str)`                      |
| `EncounterWorker` | 진료 목록/상세 조회 | `encounters_loaded(list)`, `detail_loaded(dict)`, `error(str)` |
| `EnhanceWorker`   | AI Enhance 실행     | `result(str)`, `error(str)`                                    |
| `SaveWorker`      | 시그마차트 저장     | `success(dict)`, `error(str)`                                  |

---

## 8. API 통신 상세

### 8.0 시그마 외부 API 공통 정책

`app/external/guide_data.py` 기준으로 Ai-Builder가 따라야 할 공통 규칙은 아래와 같습니다.

- 인증은 `Authorization: Bearer <api_key>`만 지원합니다.
- Basic 인증은 지원하지 않습니다.
- 요청/응답 네이밍은 모두 `snake_case`입니다.
- 외부 API는 camelCase 자동 변환이 적용되지 않습니다.
- 성공 응답은 `code`, `message` 엔벨로프 없이 본문 데이터만 반환합니다.
- 에러 응답은 RFC7807 `application/problem+json` 형식을 사용합니다.
- 속도 제한은 API 키 단위 Token Bucket이며, 모든 외부 엔드포인트가 하나의 버킷을 공유합니다.
- 자체 서명 HTTPS 인증서를 사용하므로 Python은 `verify=False`, cURL은 `-k` 사용을 전제로 합니다.

### 8.1 시그마차트 API 엔드포인트 정리

| 용도             | Method | URL                                                      | 인증         |
| ---------------- | ------ | -------------------------------------------------------- | ------------ |
| 간단 헬스체크    | GET    | `/health/simple/`                                        | 불필요       |
| 상세 헬스체크    | GET    | `/health/`                                               | 불필요       |
| API 가이드       | GET    | `/external/v1/guide`                                     | 불필요       |
| 진료 목록        | GET    | `/external/v1/encounters?encounter_date=YYYY-MM-DD`      | Bearer Token |
| 진료 상세        | GET    | `/external/v1/encounters/{encounter_uuid}`               | Bearer Token |
| 외부 노트 조회   | GET    | `/external/v1/encounters/{encounter_uuid}/external-note` | Bearer Token |
| 외부 노트 저장   | PATCH  | `/external/v1/encounters/{encounter_uuid}/external-note` | Bearer Token |
| 외부 데이터 저장 | PATCH  | `/external/v1/encounters/{encounter_uuid}/external-data` | Bearer Token |

> 참고: Ai-Builder 현재 범위는 진료 목록, 진료 상세, 외부 노트 저장 3개 엔드포인트 중심입니다.

### 8.2 시그마차트 API 응답 형식

외부 API는 guide_data 기준으로 `표준 모드`를 사용합니다.

- 성공 응답: 데이터만 직접 반환
- 실패 응답: RFC7807 형식 반환
- `code`, `message`, `result` 래퍼 없음

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

**에러 응답 예시** (RFC7807):

```json
{
  "type": "https://api.example.com/problems/invalid-parameter",
  "title": "Invalid parameter",
  "status": 400,
  "detail": "encounter_date와 start_date/end_date/patient_id는 함께 사용할 수 없습니다.",
  "instance": "/external/v1/encounters"
}
```

### 8.3 시그마차트 인증 방식

```
Authorization: Bearer sigma_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

- 접두사: `sigma_`
- 전체 길이: 약 54자
- Bearer 헤더 누락, 유효하지 않은 키, 비활성 키, 만료 키는 모두 401 대상

### 8.4 Rate Limiting

시그마차트 API는 Token Bucket 방식의 Rate Limiting을 적용합니다. 대량 요청 시 429 응답이 올 수 있으므로, 목록 조회 시 적절한 간격(최소 100ms)을 두거나, 429 응답 시 재시도 로직을 구현합니다.

**응답 헤더**:

- `RateLimit-Limit`: 분당 최대 허용 요청 수
- `RateLimit-Remaining`: 현재 남은 요청 수
- `RateLimit-Reset`: 다음 버킷 리필까지 남은 시간(초)
- `Retry-After`: 429 응답 시 다음 요청까지 대기 시간(초)

> 참고: sigma_server의 guide_data.py 문서에는 `X-RateLimit-*` 접두사로 기재되어 있으나, 실제 구현(`rate_limit_service.py`)은 접두사 없는 `RateLimit-*`을 반환합니다. 클라이언트는 실제 응답 헤더 기준으로 구현합니다.

**구현 원칙**:

- 진료 목록, 상세, 저장 API 모두 같은 RateLimit 버킷을 공유한다고 가정합니다.
- 429 응답 시 `Retry-After`를 우선 사용합니다.
- 자동 재시도는 최대 1회까지만 허용하는 방향으로 구현 명세를 고정합니다.

### 8.5 Sigma API 클라이언트 구현 규칙

Ai-Builder의 `SigmaApiClient`는 guide_data 기준으로 아래 규칙을 지켜야 합니다.

- 모든 URL은 `https://{server_ip}:57443`를 기준으로 생성
- 외부 API 요청은 모두 `snake_case` 파라미터 사용
- `requests` 호출 시 `timeout`, `verify`, `headers`, `params/json`을 명시
- 목록 조회 성공 시 `results`, `pagination` 키 존재를 검증
- 상세/저장 성공 시 최상위 키를 직접 읽고 `result` 래퍼를 기대하지 않음
- 에러 시 JSON이 RFC7807 형식이면 `detail`을 우선 사용자 메시지로 사용
- cURL 예시가 필요할 경우 `curl -k` 패턴을 기준으로 문서화

### 8.6 Ai-Builder 사용 엔드포인트 상세 예시

Ai-Builder는 현재 범위에서 아래 3개 엔드포인트를 핵심적으로 사용합니다.

#### 8.6.1 진료 목록 조회

요청 예시:

```bash
curl -k -X GET "https://{server_host}/external/v1/encounters?encounter_date=2026-03-01&limit=10" \
  -H "Authorization: Bearer sigma_your_api_key"
```

성공 응답 예시:

```json
{
  "results": [
    {
      "patient_id": 123,
      "patient_name": "홍길동",
      "encounter_uuid": "550e8400-e29b-41d4-a716-446655440000",
      "encounter_date": "2026-03-01"
    }
  ],
  "pagination": {
    "limit": 10,
    "next_cursor": null,
    "has_next": false
  }
}
```

구현 체크 포인트:

- `results`가 비어 있어도 정상 응답으로 처리
- `pagination.next_cursor`는 `has_next=true`일 때만 사용
- `patient_name`, `patient_id`, `encounter_uuid`를 QListWidget 표시용 데이터로 저장

#### 8.6.2 진료 상세 조회

요청 예시:

```bash
curl -k -X GET "https://{server_host}/external/v1/encounters/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer sigma_your_api_key"
```

성공 응답 예시:

```json
{
  "encounter_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "encounter_date": "2026-03-01",
  "plain_note": "환자 주소: 두통, 어지러움 ...",
  "external_note": "외부 시스템에서 작성한 메모",
  "external_data": {
    "외부메모": "연동테스트"
  }
}
```

구현 체크 포인트:

- `plain_note`가 `null` 또는 빈 문자열일 수 있으므로 버튼 활성화 조건을 분리
- `external_note`는 조회용 참고값이며 저장 시 전체 교체 대상
- `external_data`는 현재 범위에서 표시 참고만 하고 수정 대상에서 제외

#### 8.6.3 외부 노트 저장

요청 예시:

```bash
curl -k -X PATCH "https://{server_host}/external/v1/encounters/550e8400-e29b-41d4-a716-446655440000/external-note" \
  -H "Authorization: Bearer sigma_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"external_note": "외부 시스템에서 작성한 메모"}'
```

성공 응답 예시:

```json
{
  "encounter_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "external_note": "외부 시스템에서 작성한 메모"
}
```

구현 체크 포인트:

- `external_note`는 병합이 아니라 전체 교체
- 빈 문자열 `""` 저장을 허용해야 함
- UTF-8 기준 100KB 초과 시 400 에러 처리
- 첫 저장 시 `EncounterExternalData`가 없으면 서버에서 자동 생성

### 8.7 Sigma API 수동 검증 체크리스트

개발자가 실제 구현 전에 Postman, cURL, 또는 임시 Python 스크립트로 아래 항목을 먼저 검증합니다.

#### 연결 및 인증

- `GET /health/simple/`가 `200`과 `{"status":"ok"}`를 반환하는지
- 잘못된 API 키로 `GET /external/v1/encounters?...` 호출 시 `401`이 발생하는지
- 유효한 API 키로 동일 호출 시 `200`이 발생하는지

#### 진료 목록

- `encounter_date` 단일 모드가 정상 동작하는지
- `start_date + end_date + patient_id` 조합이 정상 동작하는지
- 파라미터 혼합 시 `400` RFC7807이 오는지
- 결과가 0건일 때도 빈 `results`로 정상 응답하는지

#### 진료 상세

- 존재하는 `encounter_uuid` 조회 시 `plain_note`가 반환되는지
- 존재하지 않는 `encounter_uuid` 조회 시 `404` RFC7807이 오는지

#### 외부 노트 저장

- 일반 문자열 저장이 되는지
- 빈 문자열 저장으로 초기화가 되는지
- 저장 직후 상세 조회 시 `external_note` 값이 반영되는지
- 100KB 초과 데이터 전송 시 `400`이 오는지

#### 속도 제한

- 응답 헤더에 `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`이 포함되는지
- 강제로 요청을 몰아 429가 발생할 때 `Retry-After`가 내려오는지

### 8.8 Ai-Builder 예외 처리 우선순위

Sigma API 호출 실패 시 메시지 처리 우선순위는 아래와 같이 고정합니다.

1. RFC7807 JSON의 `detail`
2. 일반 JSON의 `message`
3. HTTP 상태 코드 기반 기본 메시지
4. 네트워크 예외 문자열

권장 기본 메시지:

- `400`: 요청 형식이 올바르지 않습니다.
- `401`: API 키 값이 올바르지 않습니다.
- `404`: 조회 대상 진료를 찾을 수 없습니다.
- `413`: 데이터 크기가 허용 한도를 초과했습니다.
- `429`: 요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.
- `500`: 서버 내부 오류가 발생했습니다.

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
      self.ui.btn_load_encounters.clicked.connect(self._on_load_encounters_clicked)
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
  │     └─ 192.168.x.0~255 순회 → GET /health/simple/ (verify=False)
  │           └─ 성공 IP → conf.yml 저장 + UI 업데이트
  │
  ├─ Sigma API 키 [저장] → GET /external/v1/encounters?encounter_date={오늘날짜} (Bearer 인증, verify=False)
  │     └─ 200: "정상" / 401: "API 키 올바르지 않음"
  │
  ├─ Gemini API 키 [저장] → POST generateContent (test)
  │     └─ 200: 저장 / 오류: 안내
  │
  └─ OpenAI API 키 [저장] → GET /v1/models
        └─ 200: 저장 / 오류: 안내
```

예시 cURL:

```bash
curl -k -X GET "https://{server_host}/external/v1/encounters?encounter_date=2026-03-01&limit=10" \
  -H "Authorization: Bearer sigma_your_api_key"
```

---

## 13. 에러 처리 전략

| 상황                   | 처리                                                 |
| ---------------------- | ---------------------------------------------------- |
| 서버 연결 실패         | 연결끊김 아이콘 + "서버에 연결할 수 없습니다" 메시지 |
| API 키 인증 실패 (401) | "API 키 값이 올바르지 않습니다"                      |
| 페이로드 초과 (413)    | "데이터 크기가 허용 한도를 초과했습니다"             |
| Rate Limit (429)       | "잠시 후 다시 시도해 주세요"                         |
| AI API 오류            | 구체적 에러 메시지 표시 (모델 오류, 토큰 초과 등)    |
| 네트워크 타임아웃      | "요청 시간이 초과되었습니다"                         |
| 프롬프트 미선택        | "프롬프트를 선택해 주세요"                           |
| plain_note 없음        | "먼저 진료 기록을 조회해 주세요"                     |

---

## 14. 개발 순서 (권장)

### Phase 1: 프로젝트 골격

1. 폴더 구조 생성
2. `src/conf/nnconf/nnconfig.py`, `src/conf/nnconf/nnlogger.py` 구성
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

---

## 16. 파일별 구현 명세

이 섹션은 실제 코드를 작성할 때 각 파일에 무엇을 넣어야 하는지 바로 판단할 수 있도록 책임을 고정한 명세입니다.

### 16.1 루트 파일

#### `main.py`

- 역할: 개발/배포 환경 모두에서 `src`를 Python 경로에 추가하고 `ai_builder.app.main()`을 실행
- 책임:
  - PyInstaller 환경 감지
  - `src` 경로 추가
  - 예외 발생 시 콘솔 출력
  - 종료 코드 반환
- 금지사항:
  - 비즈니스 로직 작성 금지
  - UI 위젯 생성 금지

#### `build.bat`

- 역할: 한 번에 UI 컴파일 + PyInstaller 빌드
- 책임:
  - 현재 git 브랜치 표시
  - `python scripts/compile_ui.py` 실행
  - `scripts/build/build_ai_builder.bat` 호출
  - 빌드 성공/실패 코드 반환
- 참고:
  - sigma_agent처럼 단계별 로그를 출력
  - 문서용 작업만 진행 중이므로 실제 난독화(PyArmor)는 포함하지 않음

#### `requirements.txt`

- 역할: 개발 및 빌드 의존성 고정
- 1차 권장 목록:
  - `PySide6`
  - `requests`
  - `PyYAML`
  - `PyInstaller`
- 원칙:
  - Gemini/OpenAI는 `requests` 기반 호출을 기본으로 함
  - SDK는 필요 시에만 추가

### 16.2 공통 설정 파일

#### `src/conf/nnconf/nnconfig.py`

- 역할: sigma_agent 패턴을 유지하는 전역 설정 로더
- 책임:
  - 프로젝트 루트 경로 결정
  - `conf/conf.yml` 로드/저장
  - `logs/`, `data/` 경로 보관
  - 서버 IP, 포트, API 키, 선택 AI 모델 로드
- 필수 속성:
  - `project_path`
  - `root_path`
  - `logs_path`
  - `data_path`
  - `conf_file_path`
  - `sigma_server_ip`
  - `sigma_server_port`
  - `sigma_api_key`
  - `gemini_api_key`
  - `openai_api_key`
  - `selected_ai_agent`
  - `log_level`
  - `request_timeout_seconds`
  - `scan_timeout_ms`
  - `ssl_verify`
- 필수 메서드:
  - `load_config()`
  - `save_config(key, value)`
  - `ensure_directories()`

#### `src/conf/nnconf/nnlogger.py`

- 역할: sigma_agent 패턴과 동일한 날짜별 로그 파일 생성
- 책임:
  - 콘솔 + 파일 핸들러 구성
  - 날짜별 로그 파일명 생성
  - 7일 백업, 30일 초과 로그 삭제
- 기본 로거:
  - `app_logger`
  - `network_logger`
  - `ai_logger`

### 16.3 패키지 진입 및 버전

#### `src/ai_builder/app.py`

- 역할: `QApplication` 생성 및 메인 윈도우 실행
- 책임:
  - 앱 아이콘 로드
  - 스타일시트 적용
  - `MainWindow` 생성
  - 종료 코드 반환

#### `src/ai_builder/version.py`

- 역할: 앱 이름, 버전, 설명, 제작사 정보 중앙 관리
- 권장 상수:
  - `__version__`
  - `__app_name__`
  - `__description__`
  - `__author__`

### 16.4 서비스 레이어

#### `src/ai_builder/services/sigma_api.py`

- 역할: sigma_server 외부 API 호출 전담
- 책임:
  - 생성자에서 `server_ip`, `api_key`를 주입받아 인스턴스 속성으로 보관
  - 공통 헤더 생성
  - `verify=False` 포함 HTTPS 호출
  - 타임아웃/응답 코드/예외 처리
- 필수 메서드:
  - `__init__(server_ip, api_key)` — 인스턴스 속성 설정
  - `health_check() -> bool`
  - `validate_api_key() -> bool`
  - `get_encounters(target_date, cursor=None) -> dict`
  - `get_encounter_detail(encounter_uuid) -> dict`
  - `save_external_note(encounter_uuid, note) -> dict`

#### `src/ai_builder/services/ai_service.py`

- 역할: Gemini/OpenAI API 호출 전담
- 책임:
  - 선택된 모델 분기 처리
  - 공통 에러 메시지 정규화
  - 응답 텍스트 추출
- 필수 메서드:
  - `validate_gemini_key(api_key) -> bool`
  - `validate_openai_key(api_key) -> bool`
  - `enhance_with_gemini(prompt_text, plain_note) -> str`
  - `enhance_with_openai(prompt_text, plain_note) -> str`
  - `enhance(agent_type, prompt_text, plain_note) -> str`

#### `src/ai_builder/services/prompt_manager.py`

- 역할: `prompts.json` CRUD와 정렬 관리
- 책임:
  - JSON 파일 로드/저장
  - 순서 이동 시 `order` 재정렬
  - 선택 프롬프트 1건 반환
- 필수 메서드:
  - `load_prompts() -> list[dict]`
  - `save_prompts(prompts) -> None`
  - `create_prompt(title, content) -> dict`
  - `update_prompt(prompt_id, title, content) -> dict`
  - `delete_prompt(prompt_id) -> None`
  - `move_up(prompt_id) -> None`
  - `move_down(prompt_id) -> None`
  - `get_prompt_by_id(prompt_id) -> dict | None`

#### `src/ai_builder/services/network_scanner.py`

- 역할: 로컬 IP 대역에서 sigma_server 탐색
- 책임:
  - 현재 머신의 IPv4 대역 계산
  - `/health/simple/` 병렬 호출
  - 첫 성공 IP 반환
- 필수 메서드:
  - `get_local_ip() -> str`
  - `get_base_network(ip) -> str`
  - `check_host(ip) -> bool`
  - `scan_network() -> str | None`

### 16.5 워커 레이어

#### `src/ai_builder/workers/scan_worker.py`

- 역할: 네트워크 스캔 비동기 처리
- 시그널:
  - `found(str)`
  - `not_found()`
  - `error(str)`

#### `src/ai_builder/workers/encounter_worker.py`

- 역할: 진료 목록 조회 / 상세 조회
- 모드:
  - `list`
  - `detail`
- 시그널:
  - `encounters_loaded(list)`
  - `detail_loaded(dict)`
  - `error(str)`

#### `src/ai_builder/workers/enhance_worker.py`

- 역할: AI Enhance 비동기 처리
- 입력:
  - `agent_type`
  - `prompt_text`
  - `plain_note`
- 시그널:
  - `result(str)`
  - `error(str)`

#### `src/ai_builder/workers/save_worker.py`

- 역할: `external_note` 저장 비동기 처리
- 시그널:
  - `success(dict)`
  - `error(str)`

### 16.6 UI 레이어

#### `src/ai_builder/ui/windows/main_window.py`

- 역할: 메인 화면 상태 관리 및 사용자 이벤트 처리
- 책임:
  - 날짜 조회 이벤트 처리
  - 진료 목록 렌더링
  - 프롬프트 CRUD 연동
  - AI Enhance 실행
  - 저장 버튼 처리

#### `src/ai_builder/ui/windows/settings_window.py`

- 역할: 설정 다이얼로그 상태 관리
- 책임:
  - 서버 검색
  - Sigma/Gemini/OpenAI API 키 저장
  - 상태 아이콘 갱신
  - 메인 윈도우에 설정 변경 시그널 전달

---

## 17. UI 위젯 객체명 명세

Qt Designer에서 사용할 권장 objectName을 고정합니다. 구현과 문서를 동일하게 맞추기 위해, 코드에서는 아래 이름을 그대로 사용합니다.

### 17.1 `main_window.ui`

#### 상단/공통

- `btn_open_settings`
- `lbl_connection_status_icon`
- `lbl_connection_status_text`

#### 진료 조회 영역

- `date_edit_encounter`
- `btn_load_encounters`
- `list_encounters`
- `btn_load_encounter_detail`
- `txt_plain_note`
- `txt_enhanced_result`

#### AI 영역

- `combo_ai_agent`
- `btn_enhance`
- `btn_save_to_sigma`

#### 프롬프트 영역

- `list_prompts`
- `edit_prompt_title`
- `txt_prompt_content`
- `btn_prompt_new`
- `btn_prompt_edit`
- `btn_prompt_delete`
- `btn_prompt_move_up`
- `btn_prompt_move_down`
- `btn_prompt_save`

### 17.2 `settings_window.ui`

- `lbl_settings_connection_status_icon`
- `lbl_settings_connection_status_text`
- `edit_sigma_server_ip`
- `btn_sigma_search`
- `edit_sigma_api_key`
- `btn_sigma_api_key_save`
- `lbl_sigma_api_status`
- `btn_open_gemini_link`
- `edit_gemini_api_key`
- `btn_gemini_api_key_save`
- `lbl_gemini_api_status`
- `btn_open_openai_link`
- `edit_openai_api_key`
- `btn_openai_api_key_save`
- `lbl_openai_api_status`
- `btn_settings_close`

---

## 18. 상태 관리 명세

### 18.1 MainWindow 내부 상태

`MainWindow`는 최소 아래 상태를 멤버 변수로 유지합니다.

- `self.current_server_ip: str | None`
- `self.current_sigma_api_key: str | None`
- `self.current_plain_note: str`
- `self.current_enhanced_text: str`
- `self.current_encounter_uuid: str | None`
- `self.current_prompt_id: str | None`
- `self.current_ai_agent: str | None`
- `self.connection_alive: bool`

### 18.2 SettingsWindow 내부 상태

- `self.server_ip: str | None`
- `self.sigma_api_key_valid: bool`
- `self.gemini_api_key_valid: bool`
- `self.openai_api_key_valid: bool`

### 18.3 시그널 명세

`SettingsWindow`에서 `MainWindow`로 아래 시그널을 보냅니다.

- `settings_changed(dict)`
- `connection_state_changed(bool)`

전달 데이터 예시:

```python
{
    "sigma_server_ip": "192.168.0.12",
    "sigma_api_key": "sigma_xxx",
    "gemini_api_key": "AIza...",
    "openai_api_key": "sk-...",
    "selected_ai_agent": "gemini",
}
```

---

## 19. 설정 파일 스키마 명세

`conf/conf.yml`은 아래 키를 사용합니다.

```yaml
SIGMA_SERVER_IP: "192.168.0.100"
SIGMA_SERVER_PORT: 57443
SIGMA_API_KEY: "sigma_xxx"
GEMINI_API_KEY: "AIza..."
OPENAI_API_KEY: "sk-..."
SELECTED_AI_AGENT: "gemini"
LOG_LEVEL: "DEBUG"
REQUEST_TIMEOUT_SECONDS: 10
SCAN_TIMEOUT_MS: 300
SSL_VERIFY: false
```

### 키별 규칙

- `SIGMA_SERVER_IP`: 검색 성공 시 즉시 저장
- `SIGMA_SERVER_PORT`: 기본값 `57443`, UI에서 수정하지 않음
- `SELECTED_AI_AGENT`: 콤보박스 변경 즉시 저장
- `SSL_VERIFY`: 기본값 `false`, 자체 서명 인증서 대응용

---

## 20. prompts.json 스키마 명세

```json
{
  "prompts": [
    {
      "id": "8c29f2f6-8d83-4fa5-a9a6-112233445566",
      "title": "SOAP 변환",
      "content": "아래 진료 기록을 SOAP 형식으로 정리하세요.",
      "order": 0,
      "created_dt": "2026-03-14T09:00:00",
      "updated_dt": "2026-03-14T09:00:00"
    }
  ]
}
```

### 저장 규칙

- `id`: UUID 문자열
- `title`: 빈 문자열 금지
- `content`: 빈 문자열 금지
- `order`: 0부터 시작하는 정수, 중복 금지
- 삭제 후에는 전체 항목 `order`를 재정렬

---

## 21. 메서드 단위 구현 순서

### 21.1 `SettingsWindow`

구현 순서:

1. `_load_initial_config()`
2. `_setup_connections()`
3. `_update_connection_status(is_alive)`
4. `_on_search_server_clicked()`
5. `_on_save_sigma_api_key_clicked()`
6. `_on_save_gemini_api_key_clicked()`
7. `_on_save_openai_api_key_clicked()`
8. `_emit_settings_changed()`

### 21.2 `MainWindow`

구현 순서:

1. `_load_initial_state()`
2. `_setup_connections()`
3. `_refresh_ai_agent_combo()`
4. `_load_prompt_list()`
5. `_on_load_encounters_clicked()`
6. `_on_load_encounter_detail_clicked()`
7. `_on_prompt_selected()`
8. `_on_prompt_new_clicked()`
9. `_on_prompt_edit_clicked()`
10. `_on_prompt_delete_clicked()`
11. `_on_prompt_move_up_clicked()`
12. `_on_prompt_move_down_clicked()`
13. `_on_prompt_save_clicked()`
14. `_on_ai_agent_changed()`
15. `_on_enhance_clicked()`
16. `_on_save_to_sigma_clicked()`

---

## 22. 구현 금지 사항

문서 기준으로 아래 사항은 이번 범위에서 제외합니다.

- 실제 프로젝트 파일 생성 및 코드 작성
- 아이콘 실물 제작
- 테스트 코드 작성
- sigma_server 서버 코드 수정
- 데이터베이스 직접 연동
- 프롬프트 다중 선택 기능
- 외부 노트 이외의 필드 저장 기능

이 문서는 설계와 구현 명세까지만 다룹니다.
