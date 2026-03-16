"""
서버 연결 확인 워커

Sigma 서버 health check를 데몬 스레드에서 비동기 실행합니다.
"""

import threading

from PySide6.QtCore import QObject, Signal

from ai_builder.services.sigma_api import SigmaApiClient


class ConnectionCheckWorker(QObject):
    """Sigma 서버 연결 상태 확인 워커"""

    checked = Signal(bool)
    error = Signal(str)
    finished = Signal()

    def __init__(self, client: SigmaApiClient, timeout_seconds: float | None = None, parent=None):
        super().__init__(parent)
        self.client = client
        self.timeout_seconds = timeout_seconds
        self._thread: threading.Thread | None = None
        self._is_running: bool = False

    def start(self):
        """백그라운드 스레드 시작"""
        if self._is_running:
            return

        self._is_running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def isRunning(self) -> bool:
        """실행 중 여부 반환"""
        return self._is_running

    def _run(self):
        try:
            self.checked.emit(self.client.health_check(timeout_seconds=self.timeout_seconds))
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self._is_running = False
            self.finished.emit()