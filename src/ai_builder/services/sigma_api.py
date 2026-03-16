"""
시그마차트 서버 API 클라이언트

외부 API 호출 전담. verify=False, 타임아웃, 에러 처리를 포함합니다.
"""

import time

import requests
import urllib3

from ai_builder.constants.enums import (
    HEALTH_SIMPLE_URL, ENCOUNTERS_URL,
    ENCOUNTER_DETAIL_URL, EXTERNAL_NOTE_URL,
    HTTP_ERROR_MESSAGES,
)
from conf.nnconf.nnconfig import nn_conf
from conf.nnconf.nnlogger import network_logger


class SigmaApiClient:
    """시그마차트 서버 API 클라이언트"""

    def __init__(self, server_ip: str, api_key: str):
        self.server_ip = server_ip
        self.api_key = api_key
        self.base_url = f"https://{server_ip}:{nn_conf.sigma_server_port}"
        self.timeout = nn_conf.request_timeout_seconds
        self.verify = nn_conf.get_sigma_ssl_verify()
        if self.verify is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _headers(self) -> dict:
        """공통 인증 헤더"""
        return {'Authorization': f'Bearer {self.api_key}'}

    def _handle_error(self, resp: requests.Response) -> str:
        """
        에러 응답에서 사용자 메시지 추출.
        우선순위: RFC7807 detail → message → HTTP 기본 메시지 → 상태 코드
        """
        try:
            data = resp.json()
            # RFC7807 형식
            if 'detail' in data:
                return data['detail']
            if 'message' in data:
                return data['message']
        except Exception:
            pass
        return HTTP_ERROR_MESSAGES.get(resp.status_code, f"HTTP {resp.status_code}")

    def health_check(self, timeout_seconds: float | None = None) -> bool:
        """간단 헬스체크"""
        url = f"{self.base_url}{HEALTH_SIMPLE_URL}"
        try:
            timeout_value = timeout_seconds if timeout_seconds is not None else self.timeout
            resp = requests.get(url, timeout=timeout_value, verify=self.verify)
            return resp.status_code == 200 and resp.json().get('status') == 'ok'
        except Exception as e:
            network_logger.debug(f"Health Check 실패: {e}")
            return False

    def validate_api_key(self) -> bool:
        """
        API 키 유효성 검증.
        인증이 필요한 엔드포인트에 요청하여 200 여부로 판단.
        """
        from datetime import date
        url = f"{self.base_url}{ENCOUNTERS_URL}"
        params = {'encounter_date': date.today().isoformat()}
        try:
            resp = requests.get(
                url, headers=self._headers(), params=params,
                timeout=self.timeout, verify=self.verify,
            )
            return resp.status_code == 200
        except Exception:
            return False

    def get_encounters(self, target_date: str, cursor: str = None) -> dict:
        """
        진료 목록 조회

        Args:
            target_date: YYYY-MM-DD 형식 날짜
            cursor: 다음 페이지 커서 (선택)

        Returns:
            {'results': [...], 'pagination': {...}} 또는 에러 시 {'error': '...'}
        """
        url = f"{self.base_url}{ENCOUNTERS_URL}"
        params = {'encounter_date': target_date, 'limit': 200}
        if cursor:
            params['cursor'] = cursor

        try:
            resp = requests.get(
                url, headers=self._headers(), params=params,
                timeout=self.timeout, verify=self.verify,
            )
            if resp.status_code == 200:
                data = resp.json()
                if not isinstance(data, dict):
                    return {'error': '진료 목록 응답 형식이 올바르지 않습니다.'}
                if 'results' not in data or 'pagination' not in data:
                    return {'error': '진료 목록 응답에 results 또는 pagination이 없습니다.'}
                return data

            # 429 Rate Limit 처리: 1회 자동 재시도
            if resp.status_code == 429:
                retry_after = int(resp.headers.get('Retry-After', 2))
                network_logger.warning(f"Rate Limit 도달. {retry_after}초 대기 후 재시도")
                time.sleep(retry_after)
                resp = requests.get(
                    url, headers=self._headers(), params=params,
                    timeout=self.timeout, verify=self.verify,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if not isinstance(data, dict):
                        return {'error': '진료 목록 응답 형식이 올바르지 않습니다.'}
                    if 'results' not in data or 'pagination' not in data:
                        return {'error': '진료 목록 응답에 results 또는 pagination이 없습니다.'}
                    return data

                if resp.status_code == 429:
                    retry_after = int(resp.headers.get('Retry-After', retry_after))
                    return {
                        'error': (
                            '서버 요청 제한(429 Rate Limit)으로 진료 목록을 불러오지 못했습니다. '
                            f'{retry_after}초 후 다시 시도해 주세요.'
                        )
                    }

            return {'error': self._handle_error(resp)}
        except requests.ConnectionError:
            return {'error': '서버에 연결할 수 없습니다.'}
        except requests.Timeout:
            return {'error': '요청 시간이 초과되었습니다.'}
        except Exception as e:
            network_logger.error(f"진료 목록 조회 실패: {e}")
            return {'error': str(e)}

    def get_encounter_detail(self, encounter_uuid: str) -> dict:
        """
        진료 상세 조회

        Returns:
            {'encounter_uuid': ..., 'plain_note': ...} 또는 {'error': '...'}
        """
        url = f"{self.base_url}{ENCOUNTER_DETAIL_URL.format(encounter_uuid=encounter_uuid)}"
        try:
            resp = requests.get(
                url, headers=self._headers(),
                timeout=self.timeout, verify=self.verify,
            )
            if resp.status_code == 200:
                return resp.json()
            return {'error': self._handle_error(resp)}
        except requests.ConnectionError:
            return {'error': '서버에 연결할 수 없습니다.'}
        except requests.Timeout:
            return {'error': '요청 시간이 초과되었습니다.'}
        except Exception as e:
            network_logger.error(f"진료 상세 조회 실패: {e}")
            return {'error': str(e)}

    def save_external_note(self, encounter_uuid: str, note: str) -> dict:
        """
        외부 노트 저장 (전체 교체)

        Returns:
            {'encounter_uuid': ..., 'external_note': ...} 또는 {'error': '...'}
        """
        url = f"{self.base_url}{EXTERNAL_NOTE_URL.format(encounter_uuid=encounter_uuid)}"
        body = {'external_note': note}
        try:
            resp = requests.patch(
                url, headers={**self._headers(), 'Content-Type': 'application/json'},
                json=body, timeout=self.timeout, verify=self.verify,
            )
            if resp.status_code == 200:
                return resp.json()
            return {'error': self._handle_error(resp)}
        except requests.ConnectionError:
            return {'error': '서버에 연결할 수 없습니다.'}
        except requests.Timeout:
            return {'error': '요청 시간이 초과되었습니다.'}
        except Exception as e:
            network_logger.error(f"외부 노트 저장 실패: {e}")
            return {'error': str(e)}
