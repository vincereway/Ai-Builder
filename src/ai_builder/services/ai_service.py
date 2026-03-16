"""
AI API 통합 클라이언트

Gemini, OpenAI API를 requests로 직접 호출합니다.
"""

import requests

from ai_builder.constants.enums import (
    GEMINI_API_URL, DEFAULT_GEMINI_MODEL,
    OPENAI_RESPONSES_URL, OPENAI_MODELS_URL, DEFAULT_OPENAI_MODEL,
    CLAUDE_MESSAGES_URL, CLAUDE_MODELS_URL, CLAUDE_API_VERSION, DEFAULT_CLAUDE_MODEL,
    AI_AGENT_GEMINI, AI_AGENT_OPENAI, AI_AGENT_CLAUDE,
)
from ai_builder.constants.prompt_contract import compose_enhance_system_prompt
from conf.nnconf.nnconfig import nn_conf
from conf.nnconf.nnlogger import ai_logger


class AiService:
    """AI API 통합 클라이언트"""

    @staticmethod
    def _normalize_json_response_text(text: str) -> str:
        """코드펜스로 감싼 JSON 응답을 순수 JSON 문자열로 정규화"""
        normalized_text = (text or '').strip()
        if not normalized_text.startswith('```'):
            return normalized_text

        lines = normalized_text.splitlines()
        if not lines:
            return normalized_text

        if lines[0].startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]

        return '\n'.join(lines).strip()

    @staticmethod
    def validate_gemini_key(api_key: str) -> bool:
        """Gemini API 키 유효성 검증"""
        model_id = nn_conf.gemini_model_id or DEFAULT_GEMINI_MODEL
        url = GEMINI_API_URL.format(model=model_id)
        params = {'key': api_key}
        body = {"contents": [{"parts": [{"text": "Hi"}]}]}
        try:
            resp = requests.post(url, json=body, params=params, timeout=10)
            return resp.status_code == 200
        except Exception:
            return False

    @staticmethod
    def validate_openai_key(api_key: str) -> bool:
        """OpenAI API 키 유효성 검증"""
        headers = {'Authorization': f'Bearer {api_key}'}
        try:
            resp = requests.get(OPENAI_MODELS_URL, headers=headers, timeout=10)
            return resp.status_code == 200
        except Exception:
            return False

    @staticmethod
    def validate_claude_key(api_key: str) -> bool:
        """Claude API 키 유효성 검증"""
        headers = {
            'x-api-key': api_key,
            'anthropic-version': CLAUDE_API_VERSION,
        }
        try:
            resp = requests.get(CLAUDE_MODELS_URL, headers=headers, timeout=10)
            return resp.status_code == 200
        except Exception:
            return False

    @staticmethod
    def enhance_with_gemini(prompt_text: str, plain_note: str) -> str:
        """
        Gemini API 호출

        Args:
            prompt_text: System Prompt (선택된 System Prompt 내용)
            plain_note: 사용자 입력 (진료 기록 텍스트)

        Returns:
            AI 응답 텍스트
        """
        api_key = nn_conf.gemini_api_key
        if not api_key:
            raise RuntimeError('Gemini API 키가 설정되지 않았습니다.')

        resolved_prompt_text = compose_enhance_system_prompt(prompt_text)

        model_id = nn_conf.gemini_model_id or DEFAULT_GEMINI_MODEL
        url = GEMINI_API_URL.format(model=model_id)
        params = {'key': api_key}
        body = {
            "system_instruction": {
                "parts": [{"text": resolved_prompt_text}]
            },
            "generationConfig": {
                "responseMimeType": "application/json"
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": plain_note}]
                }
            ]
        }

        ai_logger.info(f"Gemini API 호출 시작 (모델: {model_id})")
        resp = requests.post(url, json=body, params=params, timeout=60)

        if resp.status_code != 200:
            error_msg = ""
            try:
                error_msg = resp.json().get('error', {}).get('message', '')
            except Exception:
                pass
            raise RuntimeError(error_msg or f"Gemini API 오류: HTTP {resp.status_code}")

        data = resp.json()
        # 응답 텍스트 추출
        candidates = data.get('candidates', [])
        if not candidates:
            raise RuntimeError("Gemini 응답에 결과가 없습니다.")

        parts = candidates[0].get('content', {}).get('parts', [])
        text = ''.join(p.get('text', '') for p in parts)
        ai_logger.info(f"Gemini API 응답 수신 (길이: {len(text)})")
        return text

    @staticmethod
    def enhance_with_openai(prompt_text: str, plain_note: str) -> str:
        """
        OpenAI Responses API 호출

        Args:
            prompt_text: System Prompt (instructions)
            plain_note: 사용자 입력 (input)

        Returns:
            AI 응답 텍스트
        """
        api_key = nn_conf.openai_api_key
        if not api_key:
            raise RuntimeError('OpenAI API 키가 설정되지 않았습니다.')

        resolved_prompt_text = compose_enhance_system_prompt(prompt_text)

        model_id = nn_conf.openai_model_id or DEFAULT_OPENAI_MODEL

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        body = {
            "model": model_id,
            "instructions": resolved_prompt_text,
            "input": plain_note,
        }

        ai_logger.info(f"OpenAI API 호출 시작 (모델: {model_id})")
        resp = requests.post(OPENAI_RESPONSES_URL, headers=headers, json=body, timeout=60)

        if resp.status_code != 200:
            error_msg = ""
            try:
                error_data = resp.json()
                error_msg = error_data.get('error', {}).get('message', '')
            except Exception:
                pass
            raise RuntimeError(error_msg or f"OpenAI API 오류: HTTP {resp.status_code}")

        data = resp.json()
        # Responses API 출력 추출
        output = data.get('output', [])
        text_parts = []
        for item in output:
            if item.get('type') == 'message':
                for content in item.get('content', []):
                    if content.get('type') == 'output_text':
                        text_parts.append(content.get('text', ''))
        text = ''.join(text_parts)

        if not text:
            # fallback: output_text가 최상위에 있는 경우
            text = data.get('output_text', '')

        ai_logger.info(f"OpenAI API 응답 수신 (길이: {len(text)})")
        return text

    @staticmethod
    def enhance_with_claude(prompt_text: str, plain_note: str) -> str:
        """
        Anthropic Claude Messages API 호출

        Args:
            prompt_text: System Prompt
            plain_note: 사용자 입력

        Returns:
            AI 응답 텍스트
        """
        api_key = nn_conf.claude_api_key
        if not api_key:
            raise RuntimeError('Claude API 키가 설정되지 않았습니다.')

        resolved_prompt_text = compose_enhance_system_prompt(prompt_text)
        model_id = nn_conf.claude_model_id or DEFAULT_CLAUDE_MODEL

        headers = {
            'x-api-key': api_key,
            'anthropic-version': CLAUDE_API_VERSION,
            'Content-Type': 'application/json',
        }
        body = {
            'model': model_id,
            'max_tokens': 4096,
            'system': resolved_prompt_text,
            'messages': [
                {
                    'role': 'user',
                    'content': plain_note,
                }
            ],
        }

        ai_logger.info(f"Claude API 호출 시작 (모델: {model_id})")
        resp = requests.post(CLAUDE_MESSAGES_URL, headers=headers, json=body, timeout=60)

        if resp.status_code != 200:
            error_msg = ""
            try:
                error_msg = resp.json().get('error', {}).get('message', '')
            except Exception:
                pass
            raise RuntimeError(error_msg or f"Claude API 오류: HTTP {resp.status_code}")

        data = resp.json()
        text_parts = []
        for item in data.get('content', []):
            if item.get('type') == 'text':
                text_parts.append(item.get('text', ''))
        text = ''.join(text_parts)
        if not text:
            raise RuntimeError('Claude 응답에 결과가 없습니다.')

        text = AiService._normalize_json_response_text(text)

        ai_logger.info(f"Claude API 응답 수신 (길이: {len(text)})")
        return text

    @staticmethod
    def enhance(agent_type: str, prompt_text: str, plain_note: str) -> str:
        """
        선택된 AI 모델로 Enhance 실행

        Args:
            agent_type: 'gemini' 또는 'openai'
            prompt_text: System Prompt
            plain_note: 진료 기록 텍스트

        Returns:
            AI 응답 텍스트
        """
        if agent_type == AI_AGENT_GEMINI:
            return AiService.enhance_with_gemini(prompt_text, plain_note)
        elif agent_type == AI_AGENT_OPENAI:
            return AiService.enhance_with_openai(prompt_text, plain_note)
        elif agent_type == AI_AGENT_CLAUDE:
            return AiService.enhance_with_claude(prompt_text, plain_note)
        else:
            raise ValueError(f"지원하지 않는 AI Agent: {agent_type}")
