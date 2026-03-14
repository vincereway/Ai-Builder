"""
메인 윈도우

진료 목록 조회, 프롬프트 관리, AI Enhance, 시그마차트 저장 등
전체 앱 기능을 통합 관리합니다.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QListWidgetItem

from ai_builder.ui.generated.main_window_ui import Ui_MainWindow
from ai_builder.ui.windows.settings_window import SettingsWindow
from ai_builder.services.sigma_api import SigmaApiClient
from ai_builder.services.prompt_manager import PromptManager
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
        self.current_prompt_id: str | None = None
        self.current_ai_agent: str | None = None
        self.connection_alive: bool = False

        # 편집 모드 상태
        self._prompt_edit_mode: str | None = None  # 'new' 또는 'edit'

        # 서비스
        self.prompt_manager = PromptManager()

        # 워커 참조 (GC 방지)
        self._encounter_worker: EncounterWorker | None = None
        self._enhance_worker: EnhanceWorker | None = None
        self._save_worker: SaveWorker | None = None

        # 설정 윈도우 참조
        self._settings_window: SettingsWindow | None = None

        # 초기화
        self._load_initial_state()
        self._setup_connections()

    # ── 1. 초기 상태 로드 ──

    def _load_initial_state(self):
        """conf.yml에서 초기 상태 로드"""
        self.current_server_ip = nn_conf.sigma_server_ip or None
        self.current_sigma_api_key = nn_conf.sigma_api_key or None
        self.current_ai_agent = nn_conf.selected_ai_agent or None

        # AI 콤보박스 초기화
        self._refresh_ai_agent_combo()

        # 프롬프트 목록 로드
        self._load_prompt_list()

        # 프롬프트 편집 영역 비활성화
        self._set_prompt_edit_enabled(False)

        # 앱 시작 시에는 경고창 없이 저장된 IP로 헬스체크만 수행
        self._refresh_connection_state_silently()

    # ── 2. 시그널-슬롯 연결 ──

    def _setup_connections(self):
        """모든 시그널-슬롯 연결"""
        # 상단
        self.ui.btn_open_settings.clicked.connect(self._open_settings)

        # 진료 조회
        self.ui.btn_load_encounters.clicked.connect(self._on_load_encounters_clicked)
        self.ui.btn_load_encounter_detail.clicked.connect(self._on_load_encounter_detail_clicked)

        # 프롬프트
        self.ui.list_prompts.currentRowChanged.connect(self._on_prompt_selected)
        self.ui.btn_prompt_new.clicked.connect(self._on_prompt_new_clicked)
        self.ui.btn_prompt_edit.clicked.connect(self._on_prompt_edit_clicked)
        self.ui.btn_prompt_delete.clicked.connect(self._on_prompt_delete_clicked)
        self.ui.btn_prompt_move_up.clicked.connect(self._on_prompt_move_up_clicked)
        self.ui.btn_prompt_move_down.clicked.connect(self._on_prompt_move_down_clicked)
        self.ui.btn_prompt_save.clicked.connect(self._on_prompt_save_clicked)

        # AI
        self.ui.combo_ai_agent.currentTextChanged.connect(self._on_ai_agent_changed)
        self.ui.btn_enhance.clicked.connect(self._on_enhance_clicked)
        self.ui.btn_save_to_sigma.clicked.connect(self._on_save_to_sigma_clicked)

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

    # ── 4. 프롬프트 목록 로드 ──

    def _load_prompt_list(self):
        """프롬프트 목록을 QListWidget에 렌더링"""
        self.ui.list_prompts.clear()
        prompts = self.prompt_manager.load_prompts()
        for p in prompts:
            item = QListWidgetItem(p['title'])
            item.setData(Qt.ItemDataRole.UserRole, p['id'])
            self.ui.list_prompts.addItem(item)

    # ── 5. 진료 목록 조회 ──

    def _on_load_encounters_clicked(self):
        """[목록조회] 클릭"""
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
        self.ui.btn_load_encounters.setText("목록조회")

    # ── 6. 진료 상세 조회 ──

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
        app_logger.info(f"진료 상세 조회 완료: {self.current_encounter_uuid}")

    # ── 7. 프롬프트 선택 ──

    def _on_prompt_selected(self, row: int):
        """프롬프트 목록 클릭: 내용 표시 (읽기 전용)"""
        if row < 0:
            self.current_prompt_id = None
            return

        item = self.ui.list_prompts.item(row)
        if not item:
            return

        prompt_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_prompt_id = prompt_id
        prompt = self.prompt_manager.get_prompt_by_id(prompt_id)
        if prompt:
            self.ui.edit_prompt_title.setText(prompt['title'])
            self.ui.txt_prompt_content.setPlainText(prompt['content'])

        # 편집 모드가 아닌 경우 읽기 전용
        if not self._prompt_edit_mode:
            self._set_prompt_edit_enabled(False)

    # ── 8. 프롬프트 신규 ──

    def _on_prompt_new_clicked(self):
        """[신규] 클릭: 빈 편집 영역 활성화"""
        self._prompt_edit_mode = 'new'
        self.current_prompt_id = None
        self.ui.edit_prompt_title.clear()
        self.ui.txt_prompt_content.clear()
        self._set_prompt_edit_enabled(True)
        self.ui.edit_prompt_title.setFocus()

    # ── 9. 프롬프트 수정 ──

    def _on_prompt_edit_clicked(self):
        """[수정] 클릭: 선택된 프롬프트 편집 활성화"""
        if not self.current_prompt_id:
            show_warning(self, "알림", "수정할 프롬프트를 선택해 주세요.")
            return
        self._prompt_edit_mode = 'edit'
        self._set_prompt_edit_enabled(True)
        self.ui.edit_prompt_title.setFocus()

    # ── 10. 프롬프트 삭제 ──

    def _on_prompt_delete_clicked(self):
        """[삭제] 클릭"""
        if not self.current_prompt_id:
            show_warning(self, "알림", "삭제할 프롬프트를 선택해 주세요.")
            return
        if not show_confirm(self, "삭제 확인", "선택한 프롬프트를 삭제할까요?"):
            return
        self.prompt_manager.delete_prompt(self.current_prompt_id)
        self.current_prompt_id = None
        self._load_prompt_list()
        self.ui.edit_prompt_title.clear()
        self.ui.txt_prompt_content.clear()
        self._set_prompt_edit_enabled(False)

    # ── 11. 프롬프트 위로 이동 ──

    def _on_prompt_move_up_clicked(self):
        """[▲ 위] 클릭"""
        if not self.current_prompt_id:
            return
        self.prompt_manager.move_up(self.current_prompt_id)
        self._load_prompt_list()
        self._select_prompt_by_id(self.current_prompt_id)

    # ── 12. 프롬프트 아래로 이동 ──

    def _on_prompt_move_down_clicked(self):
        """[▼ 아래] 클릭"""
        if not self.current_prompt_id:
            return
        self.prompt_manager.move_down(self.current_prompt_id)
        self._load_prompt_list()
        self._select_prompt_by_id(self.current_prompt_id)

    # ── 13. 프롬프트 저장 ──

    def _on_prompt_save_clicked(self):
        """[저장] 클릭"""
        title = self.ui.edit_prompt_title.text().strip()
        content = self.ui.txt_prompt_content.toPlainText().strip()

        if not title:
            show_warning(self, "알림", "프롬프트 제목을 입력해 주세요.")
            return
        if not content:
            show_warning(self, "알림", "프롬프트 내용을 입력해 주세요.")
            return

        if self._prompt_edit_mode == 'new':
            new_prompt = self.prompt_manager.create_prompt(title, content)
            self.current_prompt_id = new_prompt['id']
        elif self._prompt_edit_mode == 'edit' and self.current_prompt_id:
            self.prompt_manager.update_prompt(self.current_prompt_id, title, content)

        self._prompt_edit_mode = None
        self._load_prompt_list()
        self._select_prompt_by_id(self.current_prompt_id)
        self._set_prompt_edit_enabled(False)

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

        if not self.current_prompt_id:
            show_warning(self, "알림", "프롬프트를 선택해 주세요.")
            return

        # 선택된 프롬프트 가져오기
        prompt = self.prompt_manager.get_prompt_by_id(self.current_prompt_id)
        if not prompt:
            show_warning(self, "알림", "프롬프트를 선택해 주세요.")
            return

        self.ui.btn_enhance.setEnabled(False)
        self.ui.btn_enhance.setText("처리 중...")
        self.ui.txt_enhanced_result.clear()

        self._enhance_worker = EnhanceWorker(
            agent_type=self.current_ai_agent,
            prompt_text=prompt['content'],
            plain_note=self.current_plain_note,
        )
        self._enhance_worker.result.connect(self._on_enhance_result)
        self._enhance_worker.error.connect(self._on_enhance_error)
        self._enhance_worker.finished.connect(self._restore_enhance_button)
        self._enhance_worker.start()

    def _on_enhance_result(self, text: str):
        """Enhance 결과 수신"""
        self.current_enhanced_text = text
        self.ui.txt_enhanced_result.setPlainText(text)
        app_logger.info(f"Enhance 완료 (길이: {len(text)})")

    def _on_enhance_error(self, error_msg: str):
        """Enhance 오류"""
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
        self.ui.btn_save_to_sigma.setEnabled(True)
        self.ui.btn_save_to_sigma.setText("시그마차트에 저장")

    # ━━━━━━ 내부 헬퍼 ━━━━━━

    def _open_settings(self):
        """설정 다이얼로그 열기"""
        if self._settings_window and self._settings_window.isVisible():
            self._settings_window.activateWindow()
            return

        self._settings_window = SettingsWindow(self)
        self._settings_window.settings_changed.connect(self._on_settings_changed)
        self._settings_window.connection_state_changed.connect(self._on_connection_state_changed)
        self._settings_window.exec()

    def _on_settings_changed(self, data: dict):
        """설정 변경 시 반영"""
        nn_conf.load_config()  # 최신 설정 재로드
        self.current_server_ip = nn_conf.sigma_server_ip or None
        self.current_sigma_api_key = nn_conf.sigma_api_key or None
        self._refresh_ai_agent_combo()
        self._refresh_connection_state_silently()

    def _on_connection_state_changed(self, is_alive: bool):
        """설정 뷰에서 연결 상태 변경 시 메인 뷰 동기화"""
        self.connection_alive = is_alive
        self._update_connection_status(is_alive)

    def _update_connection_status(self, is_alive: bool | None):
        """메인 뷰 연결 상태 아이콘/텍스트 갱신"""
        if is_alive is None:
            icon, text = "⚪", "미설정"
        elif is_alive:
            icon, text = "🟢", "정상"
        else:
            icon, text = "🔴", "끊김"
        self.ui.lbl_connection_status_icon.setText(icon)
        self.ui.lbl_connection_status_text.setText(text)

    def _refresh_connection_state_silently(self):
        """경고창 없이 현재 설정 기준 연결 상태를 갱신"""
        if not self.current_server_ip:
            self.connection_alive = False
            self._update_connection_status(None)
            return

        client = SigmaApiClient(self.current_server_ip, self.current_sigma_api_key or '')
        self.connection_alive = client.health_check()
        self._update_connection_status(self.connection_alive)

    def _handle_sigma_connection_failure(self, error_msg: str):
        """시그마 서버 연결 실패성 오류면 상태를 끊김으로 갱신"""
        disconnect_markers = (
            '서버에 연결할 수 없습니다',
            '요청 시간이 초과되었습니다',
        )
        if any(marker in error_msg for marker in disconnect_markers):
            self.connection_alive = False
            self._update_connection_status(False)

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

    def _set_prompt_edit_enabled(self, enabled: bool):
        """프롬프트 편집 영역 활성화/비활성화"""
        self.ui.edit_prompt_title.setReadOnly(not enabled)
        self.ui.txt_prompt_content.setReadOnly(not enabled)
        self.ui.btn_prompt_save.setEnabled(enabled)

    def _select_prompt_by_id(self, prompt_id: str):
        """프롬프트 ID로 목록에서 선택"""
        for i in range(self.ui.list_prompts.count()):
            item = self.ui.list_prompts.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == prompt_id:
                self.ui.list_prompts.setCurrentRow(i)
                return
