"""
설정 윈도우

서버 검색, Sigma/Gemini/OpenAI API 키 저장 및 검증,
연결 상태 표시를 담당합니다.
"""

import webbrowser
from datetime import date

import requests
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog

from ai_builder.ui.generated.settings_window_ui import Ui_SettingsWindow
from ai_builder.workers.scan_worker import ScanWorker
from ai_builder.constants.enums import (
    GEMINI_API_KEYS_URL, OPENAI_API_KEYS_URL,
    GEMINI_API_URL, GEMINI_MODEL,
    OPENAI_MODELS_URL,
    ENCOUNTERS_URL,
)
from ai_builder.common.msgbox import show_info, show_error
from conf.nnconf.nnconfig import nn_conf
from conf.nnconf.nnlogger import app_logger


class SettingsWindow(QDialog):
    """설정 다이얼로그"""

    # 메인 윈도우에 설정 변경 알림
    settings_changed = Signal(dict)
    connection_state_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_SettingsWindow()
        self.ui.setupUi(self)

        # 내부 상태
        self.server_ip: str | None = None
        self.sigma_api_key_valid: bool = False
        self.gemini_api_key_valid: bool = False
        self.openai_api_key_valid: bool = False

        # 스캔 워커
        self._scan_worker: ScanWorker | None = None

        # 초기화
        self._load_initial_config()
        self._setup_connections()

    # ── 1. 초기 설정 로드 ──

    def _load_initial_config(self):
        """conf.yml에서 기존 설정값 로드"""
        self.ui.edit_sigma_server_ip.setText(nn_conf.sigma_server_ip or '')
        self.ui.edit_sigma_api_key.setText(nn_conf.sigma_api_key or '')
        self.ui.edit_gemini_api_key.setText(nn_conf.gemini_api_key or '')
        self.ui.edit_openai_api_key.setText(nn_conf.openai_api_key or '')

        self.server_ip = nn_conf.sigma_server_ip or None

        # 서버 IP가 있으면 Health Check
        if self.server_ip:
            self._check_server_health(self.server_ip)
        else:
            self._update_connection_status(None)

    # ── 2. 시그널-슬롯 연결 ──

    def _setup_connections(self):
        """시그널-슬롯 연결"""
        self.ui.btn_sigma_search.clicked.connect(self._on_search_server_clicked)
        self.ui.btn_sigma_api_key_save.clicked.connect(self._on_save_sigma_api_key_clicked)
        self.ui.btn_gemini_api_key_save.clicked.connect(self._on_save_gemini_api_key_clicked)
        self.ui.btn_openai_api_key_save.clicked.connect(self._on_save_openai_api_key_clicked)
        self.ui.btn_open_gemini_link.clicked.connect(lambda: webbrowser.open(GEMINI_API_KEYS_URL))
        self.ui.btn_open_openai_link.clicked.connect(lambda: webbrowser.open(OPENAI_API_KEYS_URL))
        self.ui.btn_settings_close.clicked.connect(self.close)

    # ── 3. 연결 상태 업데이트 ──

    def _update_connection_status(self, is_alive: bool | None):
        """연결 상태 아이콘/텍스트 갱신"""
        if is_alive is None:
            icon, text = "⚪", "미설정"
        elif is_alive:
            icon, text = "🟢", "정상"
        else:
            icon, text = "🔴", "끊김"

        self.ui.lbl_settings_connection_status_icon.setText(icon)
        self.ui.lbl_settings_connection_status_text.setText(text)

        if is_alive is not None:
            self.connection_state_changed.emit(is_alive)

    # ── 4. 서버 검색 ──

    def _on_search_server_clicked(self):
        """[검색하기] 클릭 — 네트워크 스캔 시작"""
        if self._scan_worker and self._scan_worker.isRunning():
            return  # 이미 스캔 중

        self.ui.btn_sigma_search.setEnabled(False)
        self.ui.btn_sigma_search.setText("검색 중...")

        self._scan_worker = ScanWorker()
        self._scan_worker.found.connect(self._on_server_found)
        self._scan_worker.not_found.connect(self._on_server_not_found)
        self._scan_worker.error.connect(self._on_scan_error)
        self._scan_worker.start()

    def _on_server_found(self, ip: str):
        """서버 발견"""
        self.server_ip = ip
        self.ui.edit_sigma_server_ip.setText(ip)
        nn_conf.save_config('SIGMA_SERVER_IP', ip)
        self._update_connection_status(True)
        self._restore_search_button()
        self._emit_settings_changed()
        app_logger.info(f"시그마 서버 검색 성공: {ip}")

    def _on_server_not_found(self):
        """서버 미발견"""
        self._update_connection_status(False)
        self._restore_search_button()
        show_info(self, "검색 결과", "네트워크에서 시그마차트 서버를 찾지 못했습니다.")

    def _on_scan_error(self, error_msg: str):
        """스캔 오류"""
        self._restore_search_button()
        show_error(self, "검색 오류", f"네트워크 스캔 중 오류: {error_msg}")
        app_logger.error(f"네트워크 스캔 오류: {error_msg}")

    def _restore_search_button(self):
        """검색 버튼 복원"""
        self.ui.btn_sigma_search.setEnabled(True)
        self.ui.btn_sigma_search.setText("검색하기")

    # ── 5. Sigma API 키 저장 ──

    def _on_save_sigma_api_key_clicked(self):
        """Sigma API 키 저장 및 검증"""
        api_key = self.ui.edit_sigma_api_key.text().strip()
        server_ip = self.ui.edit_sigma_server_ip.text().strip()

        if not server_ip:
            show_error(self, "설정 오류", "서버 IP를 먼저 설정해 주세요.")
            return
        if not api_key:
            show_error(self, "설정 오류", "API 키를 입력해 주세요.")
            return

        # 서버 IP 저장
        nn_conf.save_config('SIGMA_SERVER_IP', server_ip)
        self.server_ip = server_ip

        # API 키 검증: 인증이 필요한 엔드포인트 호출
        today_str = date.today().isoformat()
        url = f"https://{server_ip}:{nn_conf.sigma_server_port}{ENCOUNTERS_URL}"
        params = {'encounter_date': today_str}
        headers = {'Authorization': f'Bearer {api_key}'}

        try:
            resp = requests.get(
                url, headers=headers, params=params,
                timeout=nn_conf.request_timeout_seconds,
                verify=nn_conf.get_sigma_ssl_verify(),
            )
            if resp.status_code == 200:
                self.sigma_api_key_valid = True
                nn_conf.save_config('SIGMA_API_KEY', api_key)
                self.ui.lbl_sigma_api_status.setText("✅ 정상")
                self._update_connection_status(True)
                self._emit_settings_changed()
                app_logger.info("Sigma API 키 검증 성공")
            elif resp.status_code == 401:
                self.sigma_api_key_valid = False
                self.ui.lbl_sigma_api_status.setText("❌ API 키 값이 올바르지 않습니다")
            else:
                self.sigma_api_key_valid = False
                self.ui.lbl_sigma_api_status.setText(f"❌ 서버 응답: {resp.status_code}")
        except requests.ConnectionError:
            self.sigma_api_key_valid = False
            self.ui.lbl_sigma_api_status.setText("❌ 서버에 연결할 수 없습니다")
            self._update_connection_status(False)
        except Exception as e:
            self.sigma_api_key_valid = False
            self.ui.lbl_sigma_api_status.setText(f"❌ {str(e)[:40]}")
            app_logger.error(f"Sigma API 키 검증 실패: {e}")

    # ── 6. Gemini API 키 저장 ──

    def _on_save_gemini_api_key_clicked(self):
        """Gemini API 키 저장 및 검증"""
        api_key = self.ui.edit_gemini_api_key.text().strip()
        if not api_key:
            show_error(self, "설정 오류", "Gemini API 키를 입력해 주세요.")
            return

        # 검증: 간단한 generateContent 호출
        url = GEMINI_API_URL.format(model=GEMINI_MODEL)
        params = {'key': api_key}
        body = {"contents": [{"parts": [{"text": "Hi"}]}]}

        try:
            resp = requests.post(url, json=body, params=params, timeout=10)
            if resp.status_code == 200:
                self.gemini_api_key_valid = True
                nn_conf.save_config('GEMINI_API_KEY', api_key)
                self.ui.lbl_gemini_api_status.setText("✅ 정상")
                self._emit_settings_changed()
                app_logger.info("Gemini API 키 검증 성공")
            else:
                self.gemini_api_key_valid = False
                detail = ""
                try:
                    detail = resp.json().get('error', {}).get('message', '')
                except Exception:
                    pass
                self.ui.lbl_gemini_api_status.setText(f"❌ {detail or resp.status_code}")
        except Exception as e:
            self.gemini_api_key_valid = False
            self.ui.lbl_gemini_api_status.setText(f"❌ {str(e)[:40]}")
            app_logger.error(f"Gemini API 키 검증 실패: {e}")

    # ── 7. OpenAI API 키 저장 ──

    def _on_save_openai_api_key_clicked(self):
        """OpenAI API 키 저장 및 검증"""
        api_key = self.ui.edit_openai_api_key.text().strip()
        if not api_key:
            show_error(self, "설정 오류", "OpenAI SECRET KEY를 입력해 주세요.")
            return

        # 검증: GET /v1/models
        headers = {'Authorization': f'Bearer {api_key}'}

        try:
            resp = requests.get(OPENAI_MODELS_URL, headers=headers, timeout=10)
            if resp.status_code == 200:
                self.openai_api_key_valid = True
                nn_conf.save_config('OPENAI_API_KEY', api_key)
                self.ui.lbl_openai_api_status.setText("✅ 정상")
                self._emit_settings_changed()
                app_logger.info("OpenAI API 키 검증 성공")
            elif resp.status_code == 401:
                self.openai_api_key_valid = False
                self.ui.lbl_openai_api_status.setText("❌ API 키 값이 올바르지 않습니다")
            else:
                self.openai_api_key_valid = False
                self.ui.lbl_openai_api_status.setText(f"❌ 서버 응답: {resp.status_code}")
        except Exception as e:
            self.openai_api_key_valid = False
            self.ui.lbl_openai_api_status.setText(f"❌ {str(e)[:40]}")
            app_logger.error(f"OpenAI API 키 검증 실패: {e}")

    # ── 8. 설정 변경 알림 ──

    def _emit_settings_changed(self):
        """메인 윈도우에 현재 설정 상태 전달"""
        data = {
            'sigma_server_ip': nn_conf.sigma_server_ip,
            'sigma_api_key': nn_conf.sigma_api_key,
            'gemini_api_key': nn_conf.gemini_api_key,
            'openai_api_key': nn_conf.openai_api_key,
            'selected_ai_agent': nn_conf.selected_ai_agent,
        }
        self.settings_changed.emit(data)

    # ── 내부 헬퍼 ──

    def _check_server_health(self, ip: str):
        """저장된 IP로 즉시 Health Check"""
        url = f"https://{ip}:{nn_conf.sigma_server_port}/health/simple/"
        try:
            resp = requests.get(
                url, timeout=nn_conf.request_timeout_seconds,
                verify=nn_conf.get_sigma_ssl_verify(),
            )
            is_alive = resp.status_code == 200 and resp.json().get('status') == 'ok'
        except Exception:
            is_alive = False

        self._update_connection_status(is_alive)
