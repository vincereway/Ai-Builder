"""
네트워크 스캐너

로컬 IP 대역에서 시그마차트 서버를 검색합니다.
concurrent.futures.ThreadPoolExecutor로 병렬 스캔합니다.
"""

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from conf.nnconf.nnconfig import nn_conf
from conf.nnconf.nnlogger import network_logger


class NetworkScanner:
    """로컬 네트워크에서 시그마 서버 검색"""

    @staticmethod
    def get_local_ip() -> str:
        """현재 PC의 로컬 IPv4 주소 반환"""
        try:
            # UDP 소켓으로 외부 연결 시도하여 로컬 IP 확인
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception as e:
            network_logger.warning(f"로컬 IP 확인 실패: {e}")
            return "127.0.0.1"

    @staticmethod
    def get_base_network(ip: str) -> str:
        """IP 주소에서 C클래스 대역 추출 (예: '192.168.0')"""
        parts = ip.split('.')
        return '.'.join(parts[:3])

    @staticmethod
    def check_host(ip: str) -> bool:
        """
        지정 IP로 Health Check 요청

        Args:
            ip: 대상 IP 주소

        Returns:
            True이면 시그마 서버 발견
        """
        url = f"https://{ip}:{nn_conf.sigma_server_port}/health/simple/"
        timeout_sec = nn_conf.scan_timeout_ms / 1000.0
        try:
            resp = requests.get(
                url,
                timeout=timeout_sec,
                verify=nn_conf.get_sigma_ssl_verify(),
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get('status') == 'ok':
                    return True
        except Exception:
            pass
        return False

    @staticmethod
    def scan_network() -> str | None:
        """
        로컬 IP 대역(0~255)을 병렬 스캔하여 시그마 서버 IP를 반환.

        Returns:
            발견된 서버 IP 문자열 또는 None
        """
        local_ip = NetworkScanner.get_local_ip()
        base = NetworkScanner.get_base_network(local_ip)
        network_logger.info(f"네트워크 스캔 시작: {base}.0/24 (로컬 IP: {local_ip})")

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {}
            for i in range(256):
                ip = f"{base}.{i}"
                futures[executor.submit(NetworkScanner.check_host, ip)] = ip

            for future in as_completed(futures):
                ip = futures[future]
                try:
                    if future.result():
                        network_logger.info(f"시그마 서버 발견: {ip}")
                        # 나머지 작업 취소
                        for f in futures:
                            f.cancel()
                        return ip
                except Exception:
                    pass

        network_logger.info("네트워크 스캔 완료 - 서버 미발견")
        return None
