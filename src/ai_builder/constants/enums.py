"""
Ai-Builder 상수 정의

API URL, 상태 코드, AI 모델 등 상수를 정의합니다.
"""

# 시그마차트 서버 기본 포트 (HTTPS/SSL)
SIGMA_SERVER_PORT = 57443

# 시그마차트 API 엔드포인트
HEALTH_SIMPLE_URL = "/health/simple/"
HEALTH_URL = "/health/"
ENCOUNTERS_URL = "/external/v1/encounters"
ENCOUNTER_DETAIL_URL = "/external/v1/encounters/{encounter_uuid}"
EXTERNAL_NOTE_URL = "/external/v1/encounters/{encounter_uuid}/external-note"

# AI 기본 모델명
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_OPENAI_MODEL = "gpt-5.4"

# AI API 엔드포인트
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GEMINI_MODELS_URL = "https://generativelanguage.googleapis.com/v1beta/models"
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
OPENAI_MODELS_URL = "https://api.openai.com/v1/models"

# AI Agent 타입
AI_AGENT_GEMINI = "gemini"
AI_AGENT_OPENAI = "openai"

# 외부 링크
GEMINI_API_KEYS_URL = "https://aistudio.google.com/api-keys?hl=ko"
OPENAI_API_KEYS_URL = "https://platform.openai.com/settings/organization/api-keys"

# HTTP 상태 코드별 기본 에러 메시지
HTTP_ERROR_MESSAGES = {
    400: "요청 형식이 올바르지 않습니다.",
    401: "API 키 값이 올바르지 않습니다.",
    404: "조회 대상 진료를 찾을 수 없습니다.",
    413: "데이터 크기가 허용 한도를 초과했습니다.",
    429: "요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.",
    500: "서버 내부 오류가 발생했습니다.",
}

# 연결 상태
CONNECTION_OK = "ok"
CONNECTION_FAIL = "fail"
CONNECTION_UNSET = "unset"
