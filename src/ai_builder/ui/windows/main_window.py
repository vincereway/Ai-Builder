"""
메인 윈도우

진료 목록 조회, System Prompt 관리, AI Enhance, 시그마차트 저장 등
전체 앱 기능을 통합 관리합니다.
"""

import json

from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtWidgets import QMainWindow, QListWidgetItem

from ai_builder.ui.generated.main_window_ui import Ui_MainWindow
from ai_builder.ui.windows.settings_window import SettingsWindow
from ai_builder.services.connection_status_service import get_connection_status_service
from ai_builder.services.sigma_api import SigmaApiClient
from ai_builder.services.system_prompt_manager import SystemPromptManager
from ai_builder.workers.encounter_worker import EncounterWorker
from ai_builder.workers.enhance_worker import EnhanceWorker
from ai_builder.workers.save_worker import SaveWorker
from ai_builder.constants.enums import AI_AGENT_GEMINI, AI_AGENT_OPENAI
from ai_builder.common.msgbox import show_info, show_warning, show_error, show_confirm
from ai_builder.version import __app_name__, __version__
from conf.nnconf.nnconfig import nn_conf
from conf.nnconf.nnlogger import app_logger


class MainWindow(QMainWindow):
    """메인 윈도우"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # UI 설정
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(f"{__app_name__} v{__version__}")

        # 내부 상태 (§18.1)
        self.current_server_ip: str | None = None
        self.current_sigma_api_key: str | None = None
        self.current_plain_note: str = ''
        self.current_enhanced_text: str = ''
        self.current_encounter_uuid: str | None = None
        self.current_sp_id: str | None = None
        self.current_ai_agent: str | None = None
        self.connection_alive: bool = False

        # 편집 모드 상태
        self._sp_edit_mode: str | None = None  # 'new' 또는 'edit'
        self._sp_dirty: bool = False

        # 서비스
        self.sp_manager = SystemPromptManager()

        # 워커 참조 (GC 방지)
        self._encounter_worker: EncounterWorker | None = None
        self._enhance_worker: EnhanceWorker | None = None
        self._save_worker: SaveWorker | None = None

        # 설정 윈도우 참조
        self._settings_window: SettingsWindow | None = None
        self._initial_connection_check_pending: bool = True
        self._connection_status_service = get_connection_status_service()

        # 초기화
        self._load_initial_state()
        self._setup_connections()
        self._connection_status_service.status_changed.connect(self._on_connection_status_changed)
        self._sync_initial_sp_selection()
        QTimer.singleShot(0, self._connection_status_service.refresh)

    # ── 1. 초기 상태 로드 ──

    def _load_initial_state(self):
        """conf.yml에서 초기 상태 로드"""
        self.current_server_ip = nn_conf.sigma_server_ip or None
        self.current_sigma_api_key = nn_conf.sigma_api_key or None
        self.current_ai_agent = nn_conf.selected_ai_agent or None

        # 날짜 기본값은 오늘
        self.ui.date_edit_encounter.setDate(QDate.currentDate())
        self.ui.date_edit_encounter.setCalendarPopup(True)

        # AI 콤보박스 초기화
        self._refresh_ai_agent_combo()

        # System Prompt 목록 로드
        self._load_sp_list()

        # System Prompt 편집 영역 비활성화
        self._set_sp_edit_enabled(False)
        self._update_sp_editor_actions()

        # Enhance 결과 저장 버튼은 유효한 JSON이 있을 때만 활성화
        self._update_save_button_state()

        # 앱 시작 시 연결 상태는 중앙 서비스 값 사용
        initial_status = self._connection_status_service.status
        if initial_status is None and self.current_server_ip:
            initial_status = 'checking'
        self._update_connection_status(initial_status)

    # ── 2. 시그널-슬롯 연결 ──

    def _setup_connections(self):
        """모든 시그널-슬롯 연결"""
        # 상단
        self.ui.btn_open_settings.clicked.connect(self._open_settings)

        # 진료 조회
        self.ui.btn_load_encounters.clicked.connect(self._on_load_encounters_clicked)
        self.ui.btn_prev_date.clicked.connect(self._on_prev_date_clicked)
        self.ui.btn_next_date.clicked.connect(self._on_next_date_clicked)
        self.ui.btn_go_today.clicked.connect(self._on_go_today_clicked)
        self.ui.list_encounters.currentItemChanged.connect(self._on_encounter_item_clicked)

        # System Prompt
        self.ui.list_system_prompts.currentRowChanged.connect(self._on_sp_selected)
        self.ui.btn_sp_new.clicked.connect(self._on_sp_new_clicked)
        self.ui.btn_sp_edit.clicked.connect(self._on_sp_edit_clicked)
        self.ui.btn_sp_delete.clicked.connect(self._on_sp_delete_clicked)
        self.ui.btn_sp_move_up.clicked.connect(self._on_sp_move_up_clicked)
        self.ui.btn_sp_move_down.clicked.connect(self._on_sp_move_down_clicked)
        self.ui.btn_sp_cancel.clicked.connect(self._on_sp_cancel_clicked)
        self.ui.btn_sp_save.clicked.connect(self._on_sp_save_clicked)
        self.ui.edit_sp_title.textChanged.connect(self._on_sp_content_changed)
        self.ui.txt_sp_content.textChanged.connect(self._on_sp_content_changed)

        # AI
        self.ui.combo_ai_agent.currentTextChanged.connect(self._on_ai_agent_changed)
        self.ui.btn_enhance.clicked.connect(self._on_enhance_clicked)
        self.ui.btn_save_to_sigma.clicked.connect(self._on_save_to_sigma_clicked)
        self.ui.txt_enhanced_result.textChanged.connect(self._on_enhanced_text_changed)

    # ── 3. AI Agent 콤보박스 갱신 ──

    def _refresh_ai_agent_combo(self):
        """conf.yml에 API 키가 있는 AI만 콤보박스에 표시"""
        self.ui.combo_ai_agent.blockSignals(True)
        self.ui.combo_ai_agent.clear()

        if nn_conf.gemini_api_key:
            self.ui.combo_ai_agent.addItem("Gemini", AI_AGENT_GEMINI)
        if nn_conf.openai_api_key:
            self.ui.combo_ai_agent.addItem("GPT", AI_AGENT_OPENAI)

        # 저장된 선택값 복원
        for i in range(self.ui.combo_ai_agent.count()):
            if self.ui.combo_ai_agent.itemData(i) == nn_conf.selected_ai_agent:
                self.ui.combo_ai_agent.setCurrentIndex(i)
                break

        self.ui.combo_ai_agent.blockSignals(False)
        self.current_ai_agent = self.ui.combo_ai_agent.currentData()

    def _sync_initial_sp_selection(self):
        """초기 로드된 System Prompt 선택 상태를 시그널 연결 이후 동기화"""
        current_row = self.ui.list_system_prompts.currentRow()
        if current_row >= 0:
            self._on_sp_selected(current_row)

    # ── 4. System Prompt 목록 로드 ──

    def _load_sp_list(self):
        """System Prompt 목록을 QListWidget에 렌더링"""
        self.ui.list_system_prompts.clear()
        prompts = self.sp_manager.load_system_prompts()
        for p in prompts:
            item = QListWidgetItem(p['title'])
            item.setData(Qt.ItemDataRole.UserRole, p['id'])
            self.ui.list_system_prompts.addItem(item)

        if self.current_sp_id:
            self._select_sp_by_id(self.current_sp_id)
        elif self.ui.list_system_prompts.count() > 0:
            self.ui.list_system_prompts.setCurrentRow(0)

    # ── 5. 진료 목록 조회 ──

    def _on_load_encounters_clicked(self):
        """[조회] 클릭"""
        self._load_encounters_for_selected_date()

    def _load_encounters_for_selected_date(self):
        """현재 선택된 날짜의 진료 목록 조회"""
        client = self._create_api_client()
        if not client:
            return

        target_date = self.ui.date_edit_encounter.date().toString("yyyy-MM-dd")
        self.ui.btn_load_encounters.setEnabled(False)
        self.ui.btn_load_encounters.setText("조회 중...")

        self._encounter_worker = EncounterWorker(
            client, mode='list', target_date=target_date
        )
        self._encounter_worker.encounters_loaded.connect(self._on_encounters_loaded)
        self._encounter_worker.error.connect(self._on_encounter_error)
        self._encounter_worker.finished.connect(self._restore_encounter_button)
        self._encounter_worker.start()

    def _on_prev_date_clicked(self):
        """이전 날짜로 이동 후 자동 조회"""
        self.ui.date_edit_encounter.setDate(self.ui.date_edit_encounter.date().addDays(-1))
        self._load_encounters_for_selected_date()

    def _on_next_date_clicked(self):
        """다음 날짜로 이동 후 자동 조회"""
        self.ui.date_edit_encounter.setDate(self.ui.date_edit_encounter.date().addDays(1))
        self._load_encounters_for_selected_date()

    def _on_go_today_clicked(self):
        """오늘 날짜로 이동 후 자동 조회"""
        self.ui.date_edit_encounter.setDate(QDate.currentDate())
        self._load_encounters_for_selected_date()

    def _on_encounters_loaded(self, encounters: list):
        """진료 목록 수신"""
        self.ui.list_encounters.clear()
        self.ui.txt_plain_note.clear()
        self.ui.txt_enhanced_result.clear()
        self.current_encounter_uuid = None

        for enc in encounters:
            name = enc.get('patient_name', '(이름없음)')
            pid = enc.get('patient_id', '')
            uuid_val = enc.get('encounter_uuid', '')
            item = QListWidgetItem(f"{name} ({pid})")
            item.setData(Qt.ItemDataRole.UserRole, uuid_val)
            self.ui.list_encounters.addItem(item)

        app_logger.info(f"진료 목록 조회 완료: {len(encounters)}건")

    def _on_encounter_error(self, error_msg: str):
        """진료 조회 오류"""
        self._handle_sigma_connection_failure(error_msg)
        show_error(self, "조회 오류", error_msg)
        app_logger.error(f"진료 조회 오류: {error_msg}")

    def _restore_encounter_button(self):
        """목록조회 버튼 복원"""
        self.ui.btn_load_encounters.setEnabled(True)
        self.ui.btn_load_encounters.setText("조회")

    # ── 6. 진료 상세 조회 ──

    def _on_encounter_item_clicked(self, current, previous):
        """환자 목록에서 항목 클릭 시 자동 상세 조회"""
        if not current:
            return

        client = self._create_api_client()
        if not client:
            return

        encounter_uuid = current.data(Qt.ItemDataRole.UserRole)
        self.current_encounter_uuid = encounter_uuid

        self._encounter_worker = EncounterWorker(
            client, mode='detail', encounter_uuid=encounter_uuid
        )
        self._encounter_worker.detail_loaded.connect(self._on_detail_loaded)
        self._encounter_worker.error.connect(self._on_encounter_error)
        self._encounter_worker.start()

    def _on_load_encounter_detail_clicked(self):
        """[조회] 클릭"""
        current_item = self.ui.list_encounters.currentItem()
        if not current_item:
            show_warning(self, "알림", "진료 목록에서 환자를 선택해 주세요.")
            return

        client = self._create_api_client()
        if not client:
            return

        encounter_uuid = current_item.data(Qt.ItemDataRole.UserRole)
        self.current_encounter_uuid = encounter_uuid

        self._encounter_worker = EncounterWorker(
            client, mode='detail', encounter_uuid=encounter_uuid
        )
        self._encounter_worker.detail_loaded.connect(self._on_detail_loaded)
        self._encounter_worker.error.connect(self._on_encounter_error)
        self._encounter_worker.start()

    def _on_detail_loaded(self, data: dict):
        """진료 상세 수신"""
        plain_note = data.get('plain_note', '') or ''
        self.current_plain_note = plain_note
        self.ui.txt_plain_note.setPlainText(plain_note)
        self.ui.txt_enhanced_result.clear()
        self.current_enhanced_text = ''
        self._update_save_button_state()
        app_logger.info(f"진료 상세 조회 완료: {self.current_encounter_uuid}")

    # ── 7. System Prompt 선택 ──

    def _on_sp_selected(self, row: int):
        """System Prompt 목록 클릭: 내용 표시 (읽기 전용)"""
        if row < 0:
            self.current_sp_id = None
            return

        item = self.ui.list_system_prompts.item(row)
        if not item:
            return

        sp_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_sp_id = sp_id
        sp = self.sp_manager.get_system_prompt_by_id(sp_id)
        if sp:
            self.ui.edit_sp_title.setText(sp['title'])
            self.ui.txt_sp_content.setPlainText(sp['content'])
            self._sp_dirty = False

        # 편집 모드가 아닌 경우 읽기 전용
        if not self._sp_edit_mode:
            self._set_sp_edit_enabled(False)
        self._update_sp_editor_actions()

    # ── 8. System Prompt 신규 ──

    def _on_sp_new_clicked(self):
        """[신규] 클릭: 빈 편집 영역 활성화"""
        self._sp_edit_mode = 'new'
        self.current_sp_id = None
        self.ui.edit_sp_title.clear()
        self.ui.txt_sp_content.clear()
        self._sp_dirty = False
        self._set_sp_edit_enabled(True)
        self.ui.edit_sp_title.setFocus()
        self._update_sp_editor_actions()

    # ── 9. System Prompt 수정 ──

    def _on_sp_edit_clicked(self):
        """[수정] 클릭: 선택된 System Prompt 편집 활성화"""
        if not self.current_sp_id:
            show_warning(self, "알림", "수정할 System Prompt를 선택해 주세요.")
            return
        self._sp_edit_mode = 'edit'
        self._sp_dirty = False
        self._set_sp_edit_enabled(True)
        self.ui.edit_sp_title.setFocus()
        self._update_sp_editor_actions()

    def _on_sp_cancel_clicked(self):
        """[취소] 클릭: 편집 내용 폐기 후 읽기 전용 복귀"""
        self._sp_edit_mode = None
        self._sp_dirty = False

        if self.current_sp_id:
            sp = self.sp_manager.get_system_prompt_by_id(self.current_sp_id)
            if sp:
                self.ui.edit_sp_title.setText(sp['title'])
                self.ui.txt_sp_content.setPlainText(sp['content'])
        else:
            self.ui.edit_sp_title.clear()
            self.ui.txt_sp_content.clear()

        self._set_sp_edit_enabled(False)
        self._update_sp_editor_actions()

    # ── 10. System Prompt 삭제 ──

    def _on_sp_delete_clicked(self):
        """[삭제] 클릭"""
        if not self.current_sp_id:
            show_warning(self, "알림", "삭제할 System Prompt를 선택해 주세요.")
            return
        if not show_confirm(self, "삭제 확인", "선택한 System Prompt를 삭제할까요?"):
            return
        self.sp_manager.delete_system_prompt(self.current_sp_id)
        self.current_sp_id = None
        self._load_sp_list()
        self.ui.edit_sp_title.clear()
        self.ui.txt_sp_content.clear()
        self._sp_edit_mode = None
        self._sp_dirty = False
        self._set_sp_edit_enabled(False)
        self._update_sp_editor_actions()

    # ── 11. System Prompt 위로 이동 ──

    def _on_sp_move_up_clicked(self):
        """[▲ 위] 클릭"""
        if not self.current_sp_id:
            return
        self.sp_manager.move_up(self.current_sp_id)
        self._load_sp_list()
        self._select_sp_by_id(self.current_sp_id)

    # ── 12. System Prompt 아래로 이동 ──

    def _on_sp_move_down_clicked(self):
        """[▼ 아래] 클릭"""
        if not self.current_sp_id:
            return
        self.sp_manager.move_down(self.current_sp_id)
        self._load_sp_list()
        self._select_sp_by_id(self.current_sp_id)

    # ── 13. System Prompt 저장 ──

    def _on_sp_save_clicked(self):
        """[저장] 클릭"""
        title = self.ui.edit_sp_title.text().strip()
        content = self.ui.txt_sp_content.toPlainText().strip()

        if not title:
            show_warning(self, "알림", "System Prompt 제목을 입력해 주세요.")
            return
        if not content:
            show_warning(self, "알림", "System Prompt 내용을 입력해 주세요.")
            return

        if self._sp_edit_mode == 'new':
            new_sp = self.sp_manager.create_system_prompt(title, content)
            self.current_sp_id = new_sp['id']
        elif self._sp_edit_mode == 'edit' and self.current_sp_id:
            self.sp_manager.update_system_prompt(self.current_sp_id, title, content)

        self._sp_edit_mode = None
        self._sp_dirty = False
        self._load_sp_list()
        self._select_sp_by_id(self.current_sp_id)
        self._set_sp_edit_enabled(False)
        self._update_sp_editor_actions()

    def _on_sp_content_changed(self):
        """System Prompt 편집 내용 변경 감지"""
        if not self._sp_edit_mode:
            return
        self._sp_dirty = True
        self._update_sp_editor_actions()

    # ── 14. AI Agent 변경 ──

    def _on_ai_agent_changed(self, text: str):
        """AI 콤보박스 변경 시 즉시 저장"""
        agent_type = self.ui.combo_ai_agent.currentData()
        if agent_type:
            self.current_ai_agent = agent_type
            nn_conf.save_config('SELECTED_AI_AGENT', agent_type)

    # ── 15. AI Enhance ──

    def _on_enhance_clicked(self):
        """[Enhance] 클릭"""
        # 사전 검증
        if not self.current_ai_agent:
            show_warning(self, "알림", "AI Agent를 선택해 주세요.")
            return

        api_key = self._get_current_ai_key()
        if not api_key:
            show_warning(self, "알림", "선택된 AI의 API 키가 설정되지 않았습니다.\n설정에서 API 키를 입력해 주세요.")
            return

        if not self.current_sigma_api_key:
            show_warning(self, "알림", "Sigma API 키가 설정되지 않았습니다.")
            return

        if not self.connection_alive:
            show_warning(self, "알림", "시그마차트 서버에 연결되어 있지 않습니다.")
            return

        if not self.current_plain_note:
            show_warning(self, "알림", "먼저 진료 기록을 조회해 주세요.")
            return

        if not self.current_sp_id:
            show_warning(self, "알림", "System Prompt를 선택해 주세요.")
            return

        # 선택된 System Prompt 가져오기
        sp = self.sp_manager.get_system_prompt_by_id(self.current_sp_id)
        if not sp:
            show_warning(self, "알림", "System Prompt를 선택해 주세요.")
            return

        self.ui.btn_enhance.setEnabled(False)
        self.ui.btn_enhance.setText("처리 중...")
        self.ui.txt_enhanced_result.clear()

        self._enhance_worker = EnhanceWorker(
            agent_type=self.current_ai_agent,
            system_prompt_text=sp['content'],
            plain_note=self.current_plain_note,
        )
        self._enhance_worker.result.connect(self._on_enhance_result)
        self._enhance_worker.error.connect(self._on_enhance_error)
        self._enhance_worker.finished.connect(self._restore_enhance_button)
        self._enhance_worker.start()

    def _on_enhance_result(self, text: str):
        """Enhance 결과 수신"""
        try:
            normalized_text = self._validate_and_normalize_enhance_json(text)
        except ValueError as e:
            self.current_enhanced_text = ''
            self.ui.txt_enhanced_result.clear()
            show_error(self, "AI Enhance 오류", str(e))
            app_logger.error(f"Enhance 결과 검증 실패: {e}")
            return

        self.current_enhanced_text = normalized_text
        self.ui.txt_enhanced_result.setPlainText(normalized_text)
        app_logger.info(f"Enhance 완료 (길이: {len(normalized_text)})")

    def _on_enhance_error(self, error_msg: str):
        """Enhance 오류"""
        self._update_save_button_state()
        show_error(self, "AI Enhance 오류", error_msg)
        app_logger.error(f"Enhance 오류: {error_msg}")

    def _restore_enhance_button(self):
        """Enhance 버튼 복원"""
        self.ui.btn_enhance.setEnabled(True)
        self.ui.btn_enhance.setText("Enhance")

    # ── 16. 시그마차트에 저장 ──

    def _on_save_to_sigma_clicked(self):
        """[시그마차트에 저장] 클릭"""
        enhanced_text = self.ui.txt_enhanced_result.toPlainText().strip()
        if not enhanced_text:
            show_warning(self, "알림", "저장할 Enhance 결과가 없습니다.")
            return

        try:
            enhanced_text = self._validate_and_normalize_enhance_json(enhanced_text)
        except ValueError as e:
            show_error(self, "저장 오류", f"Enhance 결과 JSON 형식이 올바르지 않습니다.\n{e}")
            app_logger.error(f"저장 전 Enhance JSON 검증 실패: {e}")
            return

        self.ui.txt_enhanced_result.setPlainText(enhanced_text)
        self.current_enhanced_text = enhanced_text

        if not self.current_encounter_uuid:
            show_warning(self, "알림", "진료를 먼저 선택해 주세요.")
            return

        client = self._create_api_client()
        if not client:
            return

        self.ui.btn_save_to_sigma.setEnabled(False)
        self.ui.btn_save_to_sigma.setText("저장 중...")

        self._save_worker = SaveWorker(
            client, self.current_encounter_uuid, enhanced_text
        )
        self._save_worker.success.connect(self._on_save_success)
        self._save_worker.error.connect(self._on_save_error)
        self._save_worker.finished.connect(self._restore_save_button)
        self._save_worker.start()

    def _on_save_success(self, data: dict):
        """저장 성공"""
        show_info(self, "저장 완료", "시그마차트에 저장되었습니다.")
        app_logger.info(f"external_note 저장 완료: {self.current_encounter_uuid}")

    def _on_save_error(self, error_msg: str):
        """저장 오류"""
        self._handle_sigma_connection_failure(error_msg)
        show_error(self, "저장 오류", error_msg)
        app_logger.error(f"저장 오류: {error_msg}")

    def _restore_save_button(self):
        """저장 버튼 복원"""
        self.ui.btn_save_to_sigma.setText("시그마차트에 저장")
        self._update_save_button_state()

    def _on_enhanced_text_changed(self):
        """Enhance 결과 편집 시 저장 가능 상태 갱신"""
        self._update_save_button_state()

    # ━━━━━━ 내부 헬퍼 ━━━━━━

    def _open_settings(self):
        """설정 다이얼로그 열기"""
        if self._settings_window and self._settings_window.isVisible():
            self._settings_window.activateWindow()
            return

        self._settings_window = SettingsWindow(self)
        self._settings_window.settings_changed.connect(self._on_settings_changed)
        self._settings_window.exec()

    def _on_settings_changed(self, data: dict):
        """설정 변경 시 반영"""
        nn_conf.load_config()  # 최신 설정 재로드
        self.current_server_ip = nn_conf.sigma_server_ip or None
        self.current_sigma_api_key = nn_conf.sigma_api_key or None
        self._refresh_ai_agent_combo()
        self._connection_status_service.refresh()

    def _on_connection_status_changed(self, status: bool | str | None):
        """중앙 연결 상태 변경 시 메인 뷰 동기화"""
        self.connection_alive = bool(status is True)
        self._update_connection_status(status)

        if self._initial_connection_check_pending and status != 'checking':
            self._initial_connection_check_pending = False
            if status is True:
                self._load_initial_encounters_if_available()

    def _update_connection_status(self, is_alive: bool | str | None):
        """메인 뷰 연결 상태 아이콘/텍스트 갱신"""
        if is_alive is None:
            icon, text = "⚪", "미설정"
        elif is_alive == 'checking':
            icon, text = "🟡", "확인 중"
        elif is_alive:
            icon, text = "🟢", "정상"
        else:
            icon, text = "🔴", "끊김"
        self.ui.lbl_connection_status_icon.setText(icon)
        self.ui.lbl_connection_status_text.setText(text)

    def _load_initial_encounters_if_available(self):
        """앱 시작 직후 오늘 날짜 진료 목록 자동 조회"""
        if not self.current_server_ip or not self.current_sigma_api_key:
            return
        if not self.connection_alive:
            return
        self._load_encounters_for_selected_date()

    def _handle_sigma_connection_failure(self, error_msg: str):
        """시그마 서버 연결 실패성 오류면 상태를 끊김으로 갱신"""
        disconnect_markers = (
            '서버에 연결할 수 없습니다',
            '요청 시간이 초과되었습니다',
        )
        if any(marker in error_msg for marker in disconnect_markers):
            self.connection_alive = False
            self._connection_status_service.set_status(False)

    def _create_api_client(self) -> SigmaApiClient | None:
        """현재 설정으로 SigmaApiClient 생성"""
        if not self.current_server_ip:
            show_warning(self, "알림", "서버 IP가 설정되지 않았습니다.\n설정에서 서버를 검색해 주세요.")
            return None
        if not self.current_sigma_api_key:
            show_warning(self, "알림", "Sigma API 키가 설정되지 않았습니다.\n설정에서 API 키를 입력해 주세요.")
            return None
        return SigmaApiClient(self.current_server_ip, self.current_sigma_api_key)

    def _get_current_ai_key(self) -> str | None:
        """현재 선택된 AI의 API 키 반환"""
        if self.current_ai_agent == AI_AGENT_GEMINI:
            return nn_conf.gemini_api_key or None
        elif self.current_ai_agent == AI_AGENT_OPENAI:
            return nn_conf.openai_api_key or None
        return None

    def _validate_and_normalize_enhance_json(self, text: str) -> str:
        """Enhance 결과가 요구된 JSON 스키마인지 검증 후 정규화"""
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 실패: {e.msg}") from e

        if not isinstance(data, dict):
            raise ValueError("최상위 결과는 JSON 객체여야 합니다.")

        required_keys = ['subjective', 'objective', 'assessment', 'plan', 'metadata']
        for key in required_keys:
            if key not in data:
                raise ValueError(f"필수 키 누락: {key}")

        for key in ['subjective', 'objective', 'assessment', 'plan']:
            if not isinstance(data[key], str):
                raise ValueError(f"{key} 값은 문자열이어야 합니다.")

        metadata = data['metadata']
        if not isinstance(metadata, dict):
            raise ValueError("metadata 값은 객체여야 합니다.")

        if 'primary_diagnosis' not in metadata:
            raise ValueError("metadata.primary_diagnosis 키가 필요합니다.")
        if 'follow_up_needed' not in metadata:
            raise ValueError("metadata.follow_up_needed 키가 필요합니다.")

        if not isinstance(metadata['primary_diagnosis'], str):
            raise ValueError("metadata.primary_diagnosis 값은 문자열이어야 합니다.")
        if not isinstance(metadata['follow_up_needed'], bool):
            raise ValueError("metadata.follow_up_needed 값은 boolean이어야 합니다.")

        normalized = {
            'subjective': data['subjective'],
            'objective': data['objective'],
            'assessment': data['assessment'],
            'plan': data['plan'],
            'metadata': {
                'primary_diagnosis': metadata['primary_diagnosis'],
                'follow_up_needed': metadata['follow_up_needed'],
            },
        }
        return json.dumps(normalized, ensure_ascii=False, indent=2)

    def _update_save_button_state(self):
        """Enhance 결과 JSON 유효성에 따라 저장 버튼 상태 갱신"""
        button = self.ui.btn_save_to_sigma
        status_label = self.ui.lbl_enhanced_result_status
        enhanced_text = self.ui.txt_enhanced_result.toPlainText().strip()

        if self._save_worker is not None and self._save_worker.isRunning():
            button.setEnabled(False)
            button.setToolTip("저장 중입니다.")
            status_label.setText("저장 중입니다.")
            status_label.setStyleSheet("color: #8a6d3b;")
            return

        if not enhanced_text:
            button.setEnabled(False)
            button.setToolTip("저장할 Enhance 결과가 없습니다.")
            status_label.setText("저장할 Enhance 결과가 없습니다.")
            status_label.setStyleSheet("color: #666666;")
            return

        try:
            self._validate_and_normalize_enhance_json(enhanced_text)
        except ValueError as e:
            button.setEnabled(False)
            button.setToolTip(f"유효하지 않은 JSON: {e}")
            status_label.setText(f"JSON 검증 실패: {e}")
            status_label.setStyleSheet("color: #c62828;")
            return

        button.setEnabled(True)
        button.setToolTip("")
        status_label.setText("유효한 JSON입니다. 저장할 수 있습니다.")
        status_label.setStyleSheet("color: #2e7d32;")

    def _set_sp_edit_enabled(self, enabled: bool):
        """System Prompt 편집 영역 활성화/비활성화"""
        self.ui.edit_sp_title.setReadOnly(not enabled)
        self.ui.txt_sp_content.setReadOnly(not enabled)
        self.ui.btn_sp_cancel.setVisible(enabled)
        self.ui.btn_sp_cancel.setEnabled(enabled)
        self.ui.btn_sp_save.setVisible(enabled)

        # 편집 중에는 좌측 목록/버튼 비활성화
        self.ui.list_system_prompts.setEnabled(not enabled)
        self.ui.btn_sp_new.setEnabled(not enabled)
        self.ui.btn_sp_edit.setEnabled(not enabled)
        self.ui.btn_sp_delete.setEnabled(not enabled)
        self.ui.btn_sp_move_up.setEnabled(not enabled)
        self.ui.btn_sp_move_down.setEnabled(not enabled)

    def _update_sp_editor_actions(self):
        """System Prompt 편집 상태에 따라 액션 버튼과 상태 텍스트 갱신"""
        is_editing = bool(self._sp_edit_mode)
        is_dirty = self._sp_dirty

        self.ui.btn_sp_save.setEnabled(is_editing and is_dirty)
        self.ui.btn_sp_save.setVisible(is_editing)
        self.ui.btn_sp_cancel.setEnabled(is_editing)
        self.ui.btn_sp_cancel.setVisible(is_editing)
        self.ui.btn_sp_save.setDefault(is_editing)
        self.ui.btn_sp_save.setAutoDefault(is_editing)

        if self._sp_edit_mode == 'new':
            status_text = '새 System Prompt 작성 중'
        elif self._sp_edit_mode == 'edit' and is_dirty:
            status_text = '편집 중, 저장되지 않은 변경 사항 있음'
        elif self._sp_edit_mode == 'edit':
            status_text = '편집 중'
        else:
            status_text = '읽기 전용'

        self.ui.lbl_sp_editor_status.setText(status_text)

    def _select_sp_by_id(self, sp_id: str):
        """System Prompt ID로 목록에서 선택"""
        for i in range(self.ui.list_system_prompts.count()):
            item = self.ui.list_system_prompts.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == sp_id:
                self.ui.list_system_prompts.setCurrentRow(i)
                return
