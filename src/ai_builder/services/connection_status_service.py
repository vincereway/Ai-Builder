"""
연결 상태 서비스

Sigma 서버 연결 상태를 단일 소스에서 비동기 관리하고,
메인/설정 창은 이 상태를 구독만 합니다.
"""

from PySide6.QtCore import QObject, Signal

from ai_builder.services.sigma_api import SigmaApiClient
from ai_builder.workers.connection_check_worker import ConnectionCheckWorker
from conf.nnconf.nnconfig import nn_conf
from conf.nnconf.nnlogger import app_logger


class ConnectionStatusService(QObject):
    """Sigma 연결 상태 단일 관리자"""

    status_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._status: bool | str | None = None
        self._worker: ConnectionCheckWorker | None = None
        self._refresh_requested_while_running: bool = False
        self._check_timeout_seconds: float = 3.0

    @property
    def status(self) -> bool | str | None:
        """현재 연결 상태 반환"""
        return self._status

    def refresh(self):
        """현재 설정 기준으로 연결 상태 새로 확인"""
        server_ip = nn_conf.sigma_server_ip or ''
        api_key = nn_conf.sigma_api_key or ''

        if not server_ip:
            self.set_status(None)
            return

        if self._worker and self._worker.isRunning():
            self._refresh_requested_while_running = True
            return

        self._refresh_requested_while_running = False
        self.set_status('checking')

        client = SigmaApiClient(server_ip, api_key)
        self._worker = ConnectionCheckWorker(
            client,
            timeout_seconds=min(self._check_timeout_seconds, float(nn_conf.request_timeout_seconds)),
            parent=self,
        )
        self._worker.checked.connect(self._on_checked)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def set_status(self, status: bool | str | None):
        """현재 연결 상태를 즉시 갱신 후 방송"""
        self._status = status
        self.status_changed.emit(status)

    def _on_checked(self, is_alive: bool):
        """연결 확인 성공 처리"""
        self.set_status(is_alive)

    def _on_error(self, error_msg: str):
        """연결 확인 실패 처리"""
        self.set_status(False)
        app_logger.warning(f"중앙 연결 상태 확인 실패: {error_msg}")

    def _on_finished(self):
        """워커 종료 후 후속 새로고침 처리"""
        self._worker = None
        if self._refresh_requested_while_running:
            self._refresh_requested_while_running = False
            self.refresh()


_connection_status_service: ConnectionStatusService | None = None


def get_connection_status_service() -> ConnectionStatusService:
    """전역 연결 상태 서비스 반환"""
    global _connection_status_service
    if _connection_status_service is None:
        _connection_status_service = ConnectionStatusService()
    return _connection_status_service