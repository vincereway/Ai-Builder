"""
네트워크 스캐너

현재 PC가 가진 IPv4 대역 전체에서 시그마차트 서버를 검색합니다.
우선순위:
1. 127.0.0.1
2. 로컬 NIC의 각 IPv4가 속한 C클래스 대역(예: 192.168.0.1~255)
대역은 순차적으로 진행하고, 각 대역 내부는 병렬 스캔합니다.
"""

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from conf.nnconf.nnconfig import nn_conf
from conf.nnconf.nnlogger import network_logger


class NetworkScanner:
    """로컬 네트워크에서 시그마 서버 검색"""

    @staticmethod
    def get_local_ips() -> list[str]:
        """현재 PC가 가진 IPv4 주소 목록 반환"""
        ip_list: list[str] = []

        try:
            hostname = socket.gethostname()
            for info in socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_STREAM):
                ip = info[4][0]
                if ip:
                    ip_list.append(ip)
        except Exception as e:
            network_logger.warning(f"호스트명 기반 로컬 IP 확인 실패: {e}")

        try:
            # 기본 NIC의 로컬 IP를 추가 확보
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ip_list.append(s.getsockname()[0])
        except Exception as e:
            network_logger.warning(f"UDP 기반 로컬 IP 확인 실패: {e}")

        filtered_ips = []
        seen = set()
        for ip in ip_list:
            if not NetworkScanner._is_scannable_ipv4(ip):
                continue
            if ip in seen:
                continue
            seen.add(ip)
            filtered_ips.append(ip)

        return filtered_ips

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
        localhost 우선, 이후 현재 PC가 가진 모든 IPv4 대역을 순차 스캔하여
        시그마 서버 IP를 반환.

        Returns:
            발견된 서버 IP 문자열 또는 None
        """
        network_logger.info("네트워크 스캔 시작")

        if NetworkScanner.check_host('127.0.0.1'):
            network_logger.info("시그마 서버 발견: 127.0.0.1")
            return '127.0.0.1'

        local_ips = NetworkScanner.get_local_ips()
        if not local_ips:
            network_logger.info("스캔 가능한 로컬 IPv4가 없어 localhost만 확인함")
            return None

        base_networks = []
        seen_bases = set()
        for ip in local_ips:
            base = NetworkScanner.get_base_network(ip)
            if base in seen_bases:
                continue
            seen_bases.add(base)
            base_networks.append(base)

        for base in base_networks:
            found_ip = NetworkScanner._scan_base_network(base)
            if found_ip:
                return found_ip

        network_logger.info("네트워크 스캔 완료 - 서버 미발견")
        return None

    @staticmethod
    def _scan_base_network(base: str) -> str | None:
        """지정 대역의 1~255 호스트를 병렬 스캔"""
        network_logger.info(f"네트워크 스캔 진행: {base}.1~255")

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {}
            for i in range(1, 256):
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

        return None

    @staticmethod
    def _is_scannable_ipv4(ip: str) -> bool:
        """스캔 대상이 될 수 있는 IPv4인지 확인"""
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        try:
            octets = [int(part) for part in parts]
        except ValueError:
            return False

        if any(octet < 0 or octet > 255 for octet in octets):
            return False
        if ip.startswith('127.'):
            return False
        if ip.startswith('169.254.'):
            return False
        return True
