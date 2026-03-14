"""
진료 조회 워커

진료 목록/상세를 QThread에서 비동기 조회합니다.
"""

from PySide6.QtCore import QThread, Signal

from ai_builder.services.sigma_api import SigmaApiClient


class EncounterWorker(QThread):
    """진료 목록/상세 조회 워커"""

    # 목록 조회 시그널
    encounters_loaded = Signal(list)
    # 상세 조회 시그널
    detail_loaded = Signal(dict)
    # 오류
    error = Signal(str)

    def __init__(self, client: SigmaApiClient, mode: str = 'list',
                 target_date: str = '', encounter_uuid: str = '', parent=None):
        super().__init__(parent)
        self.client = client
        self.mode = mode  # 'list' 또는 'detail'
        self.target_date = target_date
        self.encounter_uuid = encounter_uuid

    def run(self):
        try:
            if self.mode == 'list':
                self._load_encounters()
            elif self.mode == 'detail':
                self._load_detail()
        except Exception as e:
            self.error.emit(str(e))

    def _load_encounters(self):
        """진료 목록 조회 (커서 기반 전체 페이지)"""
        all_results = []
        cursor = None

        while True:
            data = self.client.get_encounters(self.target_date, cursor=cursor)
            if 'error' in data:
                self.error.emit(data['error'])
                return

            results = data.get('results', [])
            all_results.extend(results)

            pagination = data.get('pagination', {})
            if pagination.get('has_next'):
                cursor = pagination.get('next_cursor')
            else:
                break

        self.encounters_loaded.emit(all_results)

    def _load_detail(self):
        """진료 상세 조회"""
        data = self.client.get_encounter_detail(self.encounter_uuid)
        if 'error' in data:
            self.error.emit(data['error'])
        else:
            self.detail_loaded.emit(data)
