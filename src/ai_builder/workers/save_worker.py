"""
시그마차트 저장 워커

external_note 저장을 QThread에서 비동기 실행합니다.
"""

from PySide6.QtCore import QThread, Signal

from ai_builder.services.sigma_api import SigmaApiClient


class SaveWorker(QThread):
    """시그마차트 external_note 저장 워커"""

    success = Signal(dict)   # 성공 시 응답 데이터
    error = Signal(str)      # 오류 시 에러 메시지

    def __init__(self, client: SigmaApiClient, encounter_uuid: str,
                 note: str, parent=None):
        super().__init__(parent)
        self.client = client
        self.encounter_uuid = encounter_uuid
        self.note = note

    def run(self):
        try:
            result = self.client.save_external_note(self.encounter_uuid, self.note)
            if 'error' in result:
                self.error.emit(result['error'])
            else:
                self.success.emit(result)
        except Exception as e:
            self.error.emit(str(e))
