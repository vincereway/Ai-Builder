"""AI Enhance 출력 계약 상수 및 유틸리티"""

ENHANCE_JSON_SCHEMA_SUFFIX = """JSON Schema:
{
    \"chief_complaint\": \"string\",
    \"onset\": \"string\",
  \"subjective\": \"string\",
  \"objective\": \"string\",
  \"assessment\": \"string\",
  \"plan\": \"string\",
  \"metadata\": {
    \"primary_diagnosis\": \"string\",
    \"follow_up_needed\": true
  }
}

Return exactly one valid JSON object matching this schema."""


def strip_enhance_schema_contract(prompt_text: str) -> str:
    """저장된 System Prompt에서 강제 출력 계약 블록 제거"""
    text = str(prompt_text or '').rstrip()
    marker = '\n\nJSON Schema:\n'

    if marker in text and text.endswith(ENHANCE_JSON_SCHEMA_SUFFIX):
        return text[: text.rfind(marker)].rstrip()

    if text.endswith(ENHANCE_JSON_SCHEMA_SUFFIX):
        return text[: -len(ENHANCE_JSON_SCHEMA_SUFFIX)].rstrip()

    return text


def compose_enhance_system_prompt(prompt_text: str) -> str:
    """사용자 Prompt 뒤에 강제 출력 계약을 붙여 AI로 전송"""
    base_prompt = strip_enhance_schema_contract(prompt_text)
    if not base_prompt:
        return ENHANCE_JSON_SCHEMA_SUFFIX
    return f"{base_prompt}\n\n{ENHANCE_JSON_SCHEMA_SUFFIX}"