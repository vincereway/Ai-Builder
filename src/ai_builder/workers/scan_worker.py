"""
네트워크 스캔 워커

NetworkScanner를 QThread에서 비동기 실행합니다.
"""

from PySide6.QtCore import QThread, Signal

from ai_builder.services.network_scanner import NetworkScanner


class ScanWorker(QThread):
    """IP 대역 스캔 워커"""

    found = Signal(str)       # 서버 발견 시 IP 전달
    not_found = Signal()      # 서버 미발견
    error = Signal(str)       # 오류 발생

    def run(self):
        try:
            ip = NetworkScanner.scan_network()
            if ip:
                self.found.emit(ip)
            else:
                self.not_found.emit()
        except Exception as e:
            self.error.emit(str(e))
