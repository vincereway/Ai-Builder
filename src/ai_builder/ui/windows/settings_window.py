"""
설정 윈도우

서버 검색, Sigma/Gemini/OpenAI API 키 저장 및 검증,
연결 상태 표시와 AI 모델 선택을 담당합니다.
"""

import webbrowser
from datetime import date
import re

import requests
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QComboBox, QDialog, QLabel, QPushButton, QStyle

from ai_builder.ui.generated.settings_window_ui import Ui_SettingsWindow
from ai_builder.workers.scan_worker import ScanWorker
from ai_builder.constants.enums import (
    DEFAULT_GEMINI_MODEL,
    DEFAULT_OPENAI_MODEL,
    ENCOUNTERS_URL,
    GEMINI_API_KEYS_URL,
    GEMINI_API_URL,
    GEMINI_MODELS_URL,
    OPENAI_API_KEYS_URL,
    OPENAI_MODELS_URL,
)
from ai_builder.common.msgbox import show_error, show_info
from conf.nnconf.nnconfig import nn_conf
from conf.nnconf.nnlogger import app_logger


class SettingsWindow(QDialog):
    """설정 다이얼로그"""

    settings_changed = Signal(dict)
    connection_state_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_SettingsWindow()
        self.ui.setupUi(self)
        self._apply_visual_design()

        self.server_ip: str | None = None
        self.sigma_api_key_valid: bool = False
        self.gemini_api_key_valid: bool = False
        self.openai_api_key_valid: bool = False
        self._is_loading_gemini_models: bool = False
        self._is_loading_openai_models: bool = False

        self._scan_worker: ScanWorker | None = None

        self._load_initial_config()
        self._setup_connections()
        self._load_model_lists_if_available()

    def _load_initial_config(self):
        """conf.yml에서 기존 설정값 로드"""
        self.ui.edit_sigma_server_ip.setText(nn_conf.sigma_server_ip or '')
        self.ui.edit_sigma_api_key.setText(nn_conf.sigma_api_key or '')
        self.ui.edit_gemini_api_key.setText(nn_conf.gemini_api_key or '')
        self.ui.edit_openai_api_key.setText(nn_conf.openai_api_key or '')

        self._set_single_model_option(
            self.ui.combo_gemini_model,
            nn_conf.gemini_model_id or DEFAULT_GEMINI_MODEL,
        )
        self._set_single_model_option(
            self.ui.combo_openai_model,
            nn_conf.openai_model_id or DEFAULT_OPENAI_MODEL,
        )
        self._set_status_label(
            self.ui.lbl_gemini_model_status,
            f"현재 모델: {nn_conf.gemini_model_id or DEFAULT_GEMINI_MODEL}",
            'info',
        )
        self._set_status_label(
            self.ui.lbl_openai_model_status,
            f"현재 모델: {nn_conf.openai_model_id or DEFAULT_OPENAI_MODEL}",
            'info',
        )

        self.server_ip = nn_conf.sigma_server_ip or None
        if self.server_ip:
            self._check_server_health(self.server_ip)
        else:
            self._update_connection_status(None)

    def _setup_connections(self):
        """시그널-슬롯 연결"""
        self.ui.btn_sigma_search.clicked.connect(self._on_search_server_clicked)
        self.ui.btn_sigma_api_key_save.clicked.connect(self._on_save_sigma_api_key_clicked)
        self.ui.btn_gemini_api_key_save.clicked.connect(self._on_save_gemini_api_key_clicked)
        self.ui.btn_openai_api_key_save.clicked.connect(self._on_save_openai_api_key_clicked)
        self.ui.btn_gemini_model_refresh.clicked.connect(self._refresh_gemini_model_list)
        self.ui.btn_openai_model_refresh.clicked.connect(self._refresh_openai_model_list)
        self.ui.combo_gemini_model.currentTextChanged.connect(self._on_gemini_model_changed)
        self.ui.combo_openai_model.currentTextChanged.connect(self._on_openai_model_changed)
        self.ui.btn_open_gemini_link.clicked.connect(lambda: webbrowser.open(GEMINI_API_KEYS_URL))
        self.ui.btn_open_openai_link.clicked.connect(lambda: webbrowser.open(OPENAI_API_KEYS_URL))
        self.ui.btn_settings_close.clicked.connect(self.close)

    def _load_model_lists_if_available(self):
        """저장된 API 키가 있으면 모델 목록 자동 조회"""
        if nn_conf.gemini_api_key:
            self._refresh_gemini_model_list()
        if nn_conf.openai_api_key:
            self._refresh_openai_model_list()

    def _update_connection_status(self, is_alive: bool | None):
        """연결 상태 아이콘/텍스트 갱신"""
        if is_alive is None:
            icon = self._create_status_dot_icon('#94a3b8')
            text = "연결 상태: 미설정"
            role = 'neutral'
        elif is_alive:
            icon = self._create_status_dot_icon('#16a34a')
            text = "연결 상태: 정상"
            role = 'success'
        else:
            icon = self._create_status_dot_icon('#dc2626')
            text = "연결 상태: 끊김"
            role = 'danger'

        self.ui.lbl_settings_connection_status_icon.setPixmap(icon.pixmap(14, 14))
        self._set_status_label(self.ui.lbl_settings_connection_status_text, text, role)

        if is_alive is not None:
            self.connection_state_changed.emit(is_alive)

    def _on_search_server_clicked(self):
        """[검색하기] 클릭 — 네트워크 스캔 시작"""
        if self._scan_worker and self._scan_worker.isRunning():
            return

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

        nn_conf.save_config('SIGMA_SERVER_IP', server_ip)
        self.server_ip = server_ip

        today_str = date.today().isoformat()
        url = f"https://{server_ip}:{nn_conf.sigma_server_port}{ENCOUNTERS_URL}"
        params = {'encounter_date': today_str}
        headers = {'Authorization': f'Bearer {api_key}'}

        try:
            resp = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=nn_conf.request_timeout_seconds,
                verify=nn_conf.get_sigma_ssl_verify(),
            )
            if resp.status_code == 200:
                self.sigma_api_key_valid = True
                nn_conf.save_config('SIGMA_API_KEY', api_key)
                self._set_status_label(self.ui.lbl_sigma_api_status, "정상", 'success')
                self._update_connection_status(True)
                self._emit_settings_changed()
                app_logger.info("Sigma API 키 검증 성공")
            elif resp.status_code == 401:
                self.sigma_api_key_valid = False
                self._set_status_label(self.ui.lbl_sigma_api_status, "API 키 값이 올바르지 않습니다", 'danger')
            else:
                self.sigma_api_key_valid = False
                self._set_status_label(self.ui.lbl_sigma_api_status, f"서버 응답: {resp.status_code}", 'danger')
        except requests.ConnectionError:
            self.sigma_api_key_valid = False
            self._set_status_label(self.ui.lbl_sigma_api_status, "서버에 연결할 수 없습니다", 'danger')
            self._update_connection_status(False)
        except Exception as e:
            self.sigma_api_key_valid = False
            self._set_status_label(self.ui.lbl_sigma_api_status, str(e)[:40], 'danger')
            app_logger.error(f"Sigma API 키 검증 실패: {e}")

    def _on_save_gemini_api_key_clicked(self):
        """Gemini API 키 저장 및 검증"""
        api_key = self.ui.edit_gemini_api_key.text().strip()
        if not api_key:
            show_error(self, "설정 오류", "Gemini API 키를 입력해 주세요.")
            return

        url = GEMINI_API_URL.format(model=DEFAULT_GEMINI_MODEL)
        params = {'key': api_key}
        body = {"contents": [{"parts": [{"text": "Hi"}]}]}

        try:
            resp = requests.post(url, json=body, params=params, timeout=10)
            if resp.status_code == 200:
                self.gemini_api_key_valid = True
                nn_conf.save_config('GEMINI_API_KEY', api_key)
                self._set_status_label(self.ui.lbl_gemini_model_status, "API 키 유효함", 'success')
                self._refresh_gemini_model_list(api_key_validated=True)
                self._emit_settings_changed()
                app_logger.info("Gemini API 키 검증 성공")
            else:
                self.gemini_api_key_valid = False
                detail = ""
                try:
                    detail = resp.json().get('error', {}).get('message', '')
                except Exception:
                    pass
                self._set_status_label(self.ui.lbl_gemini_model_status, detail or str(resp.status_code), 'danger')
        except Exception as e:
            self.gemini_api_key_valid = False
            self._set_status_label(self.ui.lbl_gemini_model_status, str(e)[:40], 'danger')
            app_logger.error(f"Gemini API 키 검증 실패: {e}")

    def _on_save_openai_api_key_clicked(self):
        """OpenAI API 키 저장 및 검증"""
        api_key = self.ui.edit_openai_api_key.text().strip()
        if not api_key:
            show_error(self, "설정 오류", "OpenAI SECRET KEY를 입력해 주세요.")
            return

        headers = {'Authorization': f'Bearer {api_key}'}

        try:
            resp = requests.get(OPENAI_MODELS_URL, headers=headers, timeout=10)
            if resp.status_code == 200:
                self.openai_api_key_valid = True
                nn_conf.save_config('OPENAI_API_KEY', api_key)
                self._set_status_label(self.ui.lbl_openai_model_status, "API 키 유효함", 'success')
                self._refresh_openai_model_list(api_key_validated=True)
                self._emit_settings_changed()
                app_logger.info("OpenAI API 키 검증 성공")
            elif resp.status_code == 401:
                self.openai_api_key_valid = False
                self._set_status_label(self.ui.lbl_openai_model_status, "API 키 값이 올바르지 않습니다", 'danger')
            else:
                self.openai_api_key_valid = False
                self._set_status_label(self.ui.lbl_openai_model_status, f"서버 응답: {resp.status_code}", 'danger')
        except Exception as e:
            self.openai_api_key_valid = False
            self._set_status_label(self.ui.lbl_openai_model_status, str(e)[:40], 'danger')
            app_logger.error(f"OpenAI API 키 검증 실패: {e}")

    def _refresh_gemini_model_list(self, api_key_validated: bool = False):
        """Gemini 모델 목록 자동 조회 후 드롭다운 갱신"""
        api_key = self.ui.edit_gemini_api_key.text().strip()
        if not api_key:
            self._set_status_label(self.ui.lbl_gemini_model_status, "API 키를 먼저 저장해 주세요", 'warning')
            self._set_single_model_option(self.ui.combo_gemini_model, nn_conf.gemini_model_id or DEFAULT_GEMINI_MODEL)
            return

        self._is_loading_gemini_models = True
        self.ui.btn_gemini_model_refresh.setEnabled(False)
        self.ui.btn_gemini_model_refresh.setText("모델목록 갱신 중...")
        self._set_status_label(self.ui.lbl_gemini_model_status, "모델 목록 조회 중...", 'info')

        try:
            resp = requests.get(GEMINI_MODELS_URL, params={'key': api_key}, timeout=10)
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}")

            model_ids = []
            for model in resp.json().get('models', []):
                supported_methods = model.get('supportedGenerationMethods', [])
                name = str(model.get('name', ''))
                if 'generateContent' not in supported_methods:
                    continue
                if not name.startswith('models/'):
                    continue
                model_ids.append(name.split('/', 1)[1])

            model_ids = self._sort_gemini_model_ids(
                self._dedupe_preserve_order(model_ids)
            )
            selected_model_id = self._resolve_preferred_model(
                model_ids,
                nn_conf.gemini_model_id,
                DEFAULT_GEMINI_MODEL,
            )
            self._populate_model_combo(self.ui.combo_gemini_model, model_ids, selected_model_id)
            nn_conf.save_config('GEMINI_MODEL_ID', selected_model_id)
            status_text = f"{len(model_ids)}개 모델 조회됨, 최신순 정렬"
            if api_key_validated:
                status_text = f"API 키 유효함 · {status_text}"
            self._set_status_label(self.ui.lbl_gemini_model_status, status_text, 'success')
        except Exception as e:
            fallback_model_id = nn_conf.gemini_model_id or DEFAULT_GEMINI_MODEL
            self._set_single_model_option(self.ui.combo_gemini_model, fallback_model_id)
            status_text = f"조회 실패, 현재 모델 유지: {fallback_model_id}"
            if api_key_validated:
                status_text = f"API 키 유효함 · {status_text}"
            self._set_status_label(self.ui.lbl_gemini_model_status, status_text, 'warning')
            app_logger.error(f"Gemini 모델 목록 조회 실패: {e}")
        finally:
            self._is_loading_gemini_models = False
            self.ui.btn_gemini_model_refresh.setEnabled(True)
            self.ui.btn_gemini_model_refresh.setText("모델목록 갱신하기")

    def _refresh_openai_model_list(self, api_key_validated: bool = False):
        """OpenAI 모델 목록 자동 조회 후 드롭다운 갱신"""
        api_key = self.ui.edit_openai_api_key.text().strip()
        if not api_key:
            self._set_status_label(self.ui.lbl_openai_model_status, "API 키를 먼저 저장해 주세요", 'warning')
            self._set_single_model_option(self.ui.combo_openai_model, nn_conf.openai_model_id or DEFAULT_OPENAI_MODEL)
            return

        self._is_loading_openai_models = True
        self.ui.btn_openai_model_refresh.setEnabled(False)
        self.ui.btn_openai_model_refresh.setText("모델목록 갱신 중...")
        self._set_status_label(self.ui.lbl_openai_model_status, "모델 목록 조회 중...", 'info')

        try:
            resp = requests.get(
                OPENAI_MODELS_URL,
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=10,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}")

            model_entries = []
            for model in resp.json().get('data', []):
                model_id = str(model.get('id', ''))
                if not model_id:
                    continue
                if not self._is_supported_openai_model(model_id):
                    continue
                model_entries.append({
                    'id': model_id,
                    'created': int(model.get('created', 0) or 0),
                })

            model_ids = self._sort_openai_model_ids(model_entries)
            selected_model_id = self._resolve_preferred_model(
                model_ids,
                nn_conf.openai_model_id,
                DEFAULT_OPENAI_MODEL,
            )
            self._populate_model_combo(self.ui.combo_openai_model, model_ids, selected_model_id)
            nn_conf.save_config('OPENAI_MODEL_ID', selected_model_id)
            status_text = f"{len(model_ids)}개 모델 조회됨, 최신순 정렬"
            if api_key_validated:
                status_text = f"API 키 유효함 · {status_text}"
            self._set_status_label(self.ui.lbl_openai_model_status, status_text, 'success')
        except Exception as e:
            fallback_model_id = nn_conf.openai_model_id or DEFAULT_OPENAI_MODEL
            self._set_single_model_option(self.ui.combo_openai_model, fallback_model_id)
            status_text = f"조회 실패, 현재 모델 유지: {fallback_model_id}"
            if api_key_validated:
                status_text = f"API 키 유효함 · {status_text}"
            self._set_status_label(self.ui.lbl_openai_model_status, status_text, 'warning')
            app_logger.error(f"OpenAI 모델 목록 조회 실패: {e}")
        finally:
            self._is_loading_openai_models = False
            self.ui.btn_openai_model_refresh.setEnabled(True)
            self.ui.btn_openai_model_refresh.setText("모델목록 갱신하기")

    def _on_gemini_model_changed(self, text: str):
        """Gemini 모델 선택 즉시 저장"""
        if self._is_loading_gemini_models:
            return
        model_id = self.ui.combo_gemini_model.currentData() or text.strip()
        if not model_id:
            return
        nn_conf.save_config('GEMINI_MODEL_ID', model_id)
        self._set_status_label(self.ui.lbl_gemini_model_status, f"선택 모델 저장됨: {model_id}", 'success')
        self._emit_settings_changed()

    def _on_openai_model_changed(self, text: str):
        """OpenAI 모델 선택 즉시 저장"""
        if self._is_loading_openai_models:
            return
        model_id = self.ui.combo_openai_model.currentData() or text.strip()
        if not model_id:
            return
        nn_conf.save_config('OPENAI_MODEL_ID', model_id)
        self._set_status_label(self.ui.lbl_openai_model_status, f"선택 모델 저장됨: {model_id}", 'success')
        self._emit_settings_changed()

    def _apply_visual_design(self):
        """설정창 전용 스타일과 아이콘 적용"""
        self.setObjectName('SettingsWindow')
        self._apply_widget_roles()
        self._apply_button_icons()
        self._apply_stylesheet()
        self.ui.lbl_settings_connection_status_icon.setFixedSize(14, 14)
        self._set_status_label(self.ui.lbl_sigma_api_status, '', 'neutral')

    def _apply_widget_roles(self):
        """버튼 역할 속성 지정"""
        role_map = {
            self.ui.btn_sigma_search: 'secondary',
            self.ui.btn_sigma_api_key_save: 'primary',
            self.ui.btn_gemini_api_key_save: 'primary',
            self.ui.btn_openai_api_key_save: 'primary',
            self.ui.btn_gemini_model_refresh: 'secondary',
            self.ui.btn_openai_model_refresh: 'secondary',
            self.ui.btn_open_gemini_link: 'link',
            self.ui.btn_open_openai_link: 'link',
            self.ui.btn_settings_close: 'ghost',
        }

        for button, role in role_map.items():
            button.setProperty('role', role)
            button.setCursor(Qt.PointingHandCursor)

    def _apply_button_icons(self):
        """버튼 아이콘 적용"""
        icon_map = {
            self.ui.btn_sigma_search: QStyle.StandardPixmap.SP_DriveNetIcon,
            self.ui.btn_sigma_api_key_save: QStyle.StandardPixmap.SP_DialogSaveButton,
            self.ui.btn_gemini_api_key_save: QStyle.StandardPixmap.SP_DialogSaveButton,
            self.ui.btn_openai_api_key_save: QStyle.StandardPixmap.SP_DialogSaveButton,
            self.ui.btn_gemini_model_refresh: QStyle.StandardPixmap.SP_BrowserReload,
            self.ui.btn_openai_model_refresh: QStyle.StandardPixmap.SP_BrowserReload,
            self.ui.btn_open_gemini_link: QStyle.StandardPixmap.SP_ArrowForward,
            self.ui.btn_open_openai_link: QStyle.StandardPixmap.SP_ArrowForward,
            self.ui.btn_settings_close: QStyle.StandardPixmap.SP_DialogCloseButton,
        }

        for button, icon_type in icon_map.items():
            button.setIcon(self.style().standardIcon(icon_type))
            button.setIconSize(QSize(16, 16))

    def _apply_stylesheet(self):
        """설정창 스타일시트 적용"""
        self.setStyleSheet(
            """
            QDialog#SettingsWindow {
                background: #f3f7fb;
                color: #10233b;
            }
            QGroupBox {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #ffffff,
                    stop: 1 #f8fbff
                );
                border: 1px solid #d6e2f0;
                border-radius: 18px;
                margin-top: 14px;
                padding: 18px 18px 16px 18px;
                font-size: 14px;
                font-weight: 600;
                color: #0f172a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 8px;
                color: #0f172a;
            }
            QLabel {
                color: #334155;
                font-size: 13px;
            }
            QLabel#lbl_settings_connection_status_text {
                font-weight: 600;
                padding: 6px 12px;
                border-radius: 999px;
            }
            QLabel[role="neutral"] {
                color: #475569;
                background: #eef2f7;
                border: 1px solid #d8e0ea;
                border-radius: 10px;
                padding: 4px 10px;
            }
            QLabel[role="info"] {
                color: #1d4ed8;
                background: #e8f1ff;
                border: 1px solid #bfdbfe;
                border-radius: 10px;
                padding: 4px 10px;
            }
            QLabel[role="success"] {
                color: #166534;
                background: #e8f8ee;
                border: 1px solid #bbf7d0;
                border-radius: 10px;
                padding: 4px 10px;
            }
            QLabel[role="warning"] {
                color: #9a6700;
                background: #fff7e6;
                border: 1px solid #f8d38a;
                border-radius: 10px;
                padding: 4px 10px;
            }
            QLabel[role="danger"] {
                color: #b42318;
                background: #fff0ee;
                border: 1px solid #f3b6ad;
                border-radius: 10px;
                padding: 4px 10px;
            }
            QLabel[role="empty"] {
                background: transparent;
                border: none;
                padding: 0;
            }
            QLineEdit,
            QComboBox {
                min-height: 40px;
                padding: 0 12px;
                border: 1px solid #cbd5e1;
                border-radius: 12px;
                background: #ffffff;
                selection-background-color: #2563eb;
                selection-color: #ffffff;
                color: #0f172a;
            }
            QLineEdit:focus,
            QComboBox:focus {
                border: 2px solid #2563eb;
                padding: 0 11px;
                background: #ffffff;
            }
            QComboBox::drop-down {
                width: 34px;
                border: none;
                background: transparent;
            }
            QComboBox::down-arrow {
                width: 10px;
                height: 10px;
            }
            QPushButton {
                min-height: 40px;
                padding: 0 14px;
                border-radius: 12px;
                border: 1px solid #cbd5e1;
                background: #ffffff;
                color: #0f172a;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #f8fbff;
                border-color: #94a3b8;
            }
            QPushButton:pressed {
                background: #e5eef9;
            }
            QPushButton:disabled {
                background: #f8fafc;
                color: #94a3b8;
                border-color: #e2e8f0;
            }
            QPushButton[role="primary"] {
                background: #2563eb;
                color: #ffffff;
                border-color: #2563eb;
            }
            QPushButton[role="primary"]:hover {
                background: #1d4ed8;
                border-color: #1d4ed8;
            }
            QPushButton[role="primary"]:pressed {
                background: #1e40af;
                border-color: #1e40af;
            }
            QPushButton[role="secondary"] {
                background: #eff6ff;
                color: #1d4ed8;
                border-color: #bfdbfe;
            }
            QPushButton[role="secondary"]:hover {
                background: #dbeafe;
                border-color: #93c5fd;
            }
            QPushButton[role="link"] {
                background: #f8fbff;
                color: #1d4ed8;
                border: 1px solid #dbe7f4;
                text-align: left;
                padding: 0 14px;
            }
            QPushButton[role="link"]:hover {
                background: #eef6ff;
                border-color: #bfdbfe;
            }
            QPushButton[role="ghost"] {
                background: #ffffff;
                color: #0f172a;
                border-color: #cbd5e1;
            }
            QPushButton[role="ghost"]:hover {
                background: #f8fafc;
                border-color: #94a3b8;
            }
            """
        )

    def _set_status_label(self, label: QLabel, text: str, role: str):
        """상태 라벨 텍스트와 배지 스타일 갱신"""
        label.setText(text)
        label.setProperty('role', role if text else 'empty')
        label.style().unpolish(label)
        label.style().polish(label)
        label.update()

    def _create_status_dot_icon(self, color: str) -> QIcon:
        """연결 상태 점 아이콘 생성"""
        pixmap = QPixmap(14, 14)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(color))
        painter.drawEllipse(1, 1, 12, 12)
        painter.end()
        return QIcon(pixmap)

    def _emit_settings_changed(self):
        """메인 윈도우에 현재 설정 상태 전달"""
        data = {
            'sigma_server_ip': nn_conf.sigma_server_ip,
            'sigma_api_key': nn_conf.sigma_api_key,
            'gemini_api_key': nn_conf.gemini_api_key,
            'openai_api_key': nn_conf.openai_api_key,
            'gemini_model_id': nn_conf.gemini_model_id,
            'openai_model_id': nn_conf.openai_model_id,
            'selected_ai_agent': nn_conf.selected_ai_agent,
        }
        self.settings_changed.emit(data)

    def _check_server_health(self, ip: str):
        """저장된 IP로 즉시 Health Check"""
        url = f"https://{ip}:{nn_conf.sigma_server_port}/health/simple/"
        try:
            resp = requests.get(
                url,
                timeout=nn_conf.request_timeout_seconds,
                verify=nn_conf.get_sigma_ssl_verify(),
            )
            is_alive = resp.status_code == 200 and resp.json().get('status') == 'ok'
        except Exception:
            is_alive = False

        self._update_connection_status(is_alive)

    @staticmethod
    def _dedupe_preserve_order(values: list[str]) -> list[str]:
        """순서를 유지하며 중복 제거"""
        seen = set()
        deduped = []
        for value in values:
            if value in seen:
                continue
            seen.add(value)
            deduped.append(value)
        return deduped

    @staticmethod
    def _resolve_preferred_model(model_ids: list[str], saved_model_id: str, default_model_id: str) -> str:
        """저장값, 기본값, 첫 번째 가용 모델 순으로 선택"""
        if saved_model_id and saved_model_id in model_ids:
            return saved_model_id
        if default_model_id in model_ids:
            return default_model_id
        if model_ids:
            return model_ids[0]
        return saved_model_id or default_model_id

    @staticmethod
    def _populate_model_combo(
        combo: QComboBox,
        model_ids: list[str],
        selected_model_id: str,
    ):
        """모델 드롭다운 갱신"""
        combo.blockSignals(True)
        combo.clear()

        for model_id in model_ids:
            combo.addItem(model_id, model_id)

        if combo.count() == 0:
            combo.addItem(selected_model_id, selected_model_id)
        selected_index = combo.findData(selected_model_id)
        if selected_index < 0:
            selected_index = 0
        combo.setCurrentIndex(selected_index)
        combo.blockSignals(False)

    @staticmethod
    def _set_single_model_option(combo: QComboBox, model_id: str):
        """조회 실패 시 현재 모델만 표시"""
        combo.blockSignals(True)
        combo.clear()
        combo.addItem(model_id, model_id)
        combo.setCurrentIndex(0)
        combo.blockSignals(False)

    @staticmethod
    def _is_supported_openai_model(model_id: str) -> bool:
        """Responses API용 텍스트 생성 모델만 노출"""
        allow_prefixes = ('gpt-', 'chatgpt-', 'o1', 'o3', 'o4')
        if not model_id.startswith(allow_prefixes):
            return False

        blocked_keywords = ('image', 'audio', 'transcribe', 'tts', 'realtime', 'embedding', 'moderation')
        return not any(keyword in model_id for keyword in blocked_keywords)

    @staticmethod
    def _sort_openai_model_ids(model_entries: list[dict]) -> list[str]:
        """OpenAI 모델을 created 기준 최신순으로 정렬"""
        sorted_entries = sorted(
            model_entries,
            key=lambda item: (item.get('created', 0), item.get('id', '')),
            reverse=True,
        )
        return [entry['id'] for entry in sorted_entries]

    @staticmethod
    def _sort_gemini_model_ids(model_ids: list[str]) -> list[str]:
        """Gemini 모델명을 버전/안정성 기준으로 최신순 정렬"""
        def parse_version(model_id: str) -> tuple[int, ...]:
            match = re.search(r'gemini-(\d+)(?:\.(\d+))?', model_id)
            if not match:
                return (0, 0)
            major = int(match.group(1) or 0)
            minor = int(match.group(2) or 0)
            return (major, minor)

        def stability_rank(model_id: str) -> int:
            lowered = model_id.lower()
            if 'preview' in lowered or 'exp' in lowered or 'experimental' in lowered:
                return 0
            return 1

        def family_rank(model_id: str) -> int:
            lowered = model_id.lower()
            if 'pro' in lowered:
                return 2
            if 'flash' in lowered:
                return 1
            return 0

        return sorted(
            model_ids,
            key=lambda model_id: (
                parse_version(model_id),
                stability_rank(model_id),
                family_rank(model_id),
                model_id,
            ),
            reverse=True,
        )
