"""
AI Enhance 워커

AI API 호출을 QThread에서 비동기 실행합니다.
"""

from PySide6.QtCore import QThread, Signal

from ai_builder.services.ai_service import AiService


class EnhanceWorker(QThread):
    """AI Enhance 비동기 워커"""

    result = Signal(str)   # 성공 시 결과 텍스트
    error = Signal(str)    # 오류 시 에러 메시지

    def __init__(self, agent_type: str, system_prompt_text: str,
                 plain_note: str, parent=None):
        super().__init__(parent)
        self.agent_type = agent_type
        self.system_prompt_text = system_prompt_text
        self.plain_note = plain_note

    def run(self):
        try:
            text = AiService.enhance(
                self.agent_type, self.system_prompt_text, self.plain_note,
            )
            self.result.emit(text)
        except Exception as e:
            self.error.emit(str(e))
