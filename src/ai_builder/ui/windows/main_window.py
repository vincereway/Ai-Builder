"""
메인 윈도우

진료 목록 조회, System Prompt 관리, AI Enhance, 시그마차트 저장 등
전체 앱 기능을 통합 관리합니다.
"""

import json
import time

from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QPlainTextEdit,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ai_builder.ui.generated.main_window_ui import Ui_MainWindow
from ai_builder.ui.windows.settings_window import SettingsWindow
from ai_builder.services.connection_status_service import get_connection_status_service
from ai_builder.services.encounter_result_cache import EncounterResultCacheManager
from ai_builder.services.sigma_api import SigmaApiClient
from ai_builder.services.system_prompt_manager import SystemPromptManager
from ai_builder.workers.encounter_worker import EncounterWorker
from ai_builder.workers.enhance_worker import EnhanceWorker
from ai_builder.constants.enums import AI_AGENT_GEMINI, AI_AGENT_OPENAI
from ai_builder.common.msgbox import show_info, show_warning, show_error, show_confirm
from ai_builder.version import __app_name__, __version__
from conf.nnconf.nnconfig import nn_conf
from conf.nnconf.nnlogger import app_logger


class EnhanceRequestDialog(QDialog):
    """Enhance 전송 확인/진행/결과 다이얼로그"""

    def __init__(self, parent: QWidget, plain_note: str, agent_name: str, model_name: str, system_prompt_title: str):
        super().__init__(parent)
        self._started_at: float | None = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_elapsed_time)

        self.setWindowTitle("AI Enhance 확인")
        self.resize(760, 640)
        self.setModal(True)

        root_layout = QVBoxLayout(self)

        summary_label = QLabel("현재 설정으로 전송합니다.")
        root_layout.addWidget(summary_label)

        self.lbl_agent = QLabel(f"선택 Agent: {agent_name}")
        self.lbl_model = QLabel(f"선택 모델: {model_name}")
        self.lbl_system_prompt = QLabel(f"System Prompt 제목: {system_prompt_title}")
        root_layout.addWidget(self.lbl_agent)
        root_layout.addWidget(self.lbl_model)
        root_layout.addWidget(self.lbl_system_prompt)

        plain_note_label = QLabel("현재 입력한 내용")
        root_layout.addWidget(plain_note_label)

        self.txt_plain_note = QPlainTextEdit()
        self.txt_plain_note.setReadOnly(True)
        self.txt_plain_note.setPlainText(plain_note)
        root_layout.addWidget(self.txt_plain_note)

        self.lbl_status = QLabel("전송할까요?")
        root_layout.addWidget(self.lbl_status)

        self.lbl_elapsed = QLabel("진행시간 0초")
        self.lbl_elapsed.setVisible(False)
        root_layout.addWidget(self.lbl_elapsed)

        result_label = QLabel("결과")
        root_layout.addWidget(result_label)

        self.txt_result = QPlainTextEdit()
        self.txt_result.setReadOnly(True)
        self.txt_result.setVisible(False)
        root_layout.addWidget(self.txt_result)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        self.btn_submit = QPushButton("전송")
        self.btn_cancel = QPushButton("취소")
        self.btn_confirm = QPushButton("확인")
        self.btn_confirm.setVisible(False)

        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_submit)
        button_layout.addWidget(self.btn_confirm)
        root_layout.addLayout(button_layout)

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_confirm.clicked.connect(self.accept)

    def start_progress(self):
        """전송 시작 상태로 전환"""
        self._started_at = time.monotonic()
        self._update_elapsed_time()
        self._timer.start(1000)
        self.lbl_elapsed.setVisible(True)
        self.btn_submit.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.lbl_status.setText("전송 중...")

    def set_progress_text(self, text: str):
        """진행 단계 텍스트 갱신"""
        self.lbl_status.setText(text)

    def show_success(self, result_text: str):
        """성공 결과 표시"""
        self._timer.stop()
        self._update_elapsed_time()
        self.lbl_status.setText("수신성공했습니다")
        self.txt_result.setPlainText(result_text)
        self.txt_result.setVisible(True)
        self.btn_cancel.setVisible(False)
        self.btn_submit.setVisible(False)
        self.btn_confirm.setVisible(True)
        self.btn_confirm.setEnabled(True)
        self.btn_confirm.setFocus()

    def show_error(self, error_text: str):
        """실패 결과 표시"""
        self._timer.stop()
        self._update_elapsed_time()
        self.lbl_status.setText("수신실패했습니다")
        self.txt_result.setPlainText(error_text)
        self.txt_result.setVisible(True)
        self.btn_cancel.setVisible(False)
        self.btn_submit.setVisible(False)
        self.btn_confirm.setVisible(True)
        self.btn_confirm.setEnabled(True)
        self.btn_confirm.setFocus()

    def _update_elapsed_time(self):
        """경과 시간 라벨 갱신"""
        if self._started_at is None:
            self.lbl_elapsed.setText("진행시간 0초")
            return

        elapsed_seconds = max(0, int(time.monotonic() - self._started_at))
        self.lbl_elapsed.setText(f"진행시간 {elapsed_seconds}초")


class ResultViewSettingsDialog(QDialog):
    """Enhance 결과 보기 형식 설정 다이얼로그"""

    FIELD_DEFINITIONS = [
        ('chief_complaint', 'chief complaint', 'C/C'),
        ('onset', 'onset', 'O/S'),
        ('subjective', 'subjective', 'S'),
        ('objective', 'objective', 'O'),
        ('assessment', 'assessment', 'A'),
        ('plan', 'plan', 'P'),
    ]

    def __init__(self, parent: QWidget, initial_values: dict):
        super().__init__(parent)
        self._inputs: dict[str, QLineEdit] = {}

        self.setWindowTitle('결과보기 설정')
        self.resize(420, 320)
        self.setModal(True)

        root_layout = QVBoxLayout(self)

        for key, label_text, default_value in self.FIELD_DEFINITIONS:
            row_layout = QHBoxLayout()
            label = QLabel(f'{label_text} 라벨 :')
            edit = QLineEdit()
            edit.setText(str(initial_values.get(key) or default_value))
            row_layout.addWidget(label)
            row_layout.addWidget(edit)
            root_layout.addLayout(row_layout)
            self._inputs[key] = edit

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        btn_cancel = QPushButton('취소')
        btn_save = QPushButton('저장')
        btn_cancel.clicked.connect(self.reject)
        btn_save.clicked.connect(self.accept)
        button_layout.addWidget(btn_cancel)
        button_layout.addWidget(btn_save)
        root_layout.addLayout(button_layout)

    def get_values(self) -> dict:
        """입력된 결과보기 라벨 설정 반환"""
        values = {}
        for key, _, default_value in self.FIELD_DEFINITIONS:
            value = self._inputs[key].text().strip() or default_value
            values[key] = value
        return values


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
        self._enhance_target_encounter_uuid: str | None = None
        self._detail_request_in_flight_uuid: str | None = None

        # 편집 모드 상태
        self._sp_edit_mode: str | None = None  # 'new' 또는 'edit'
        self._sp_dirty: bool = False

        # 서비스
        self.sp_manager = SystemPromptManager()
        self.result_cache = EncounterResultCacheManager()

        # 워커 참조 (GC 방지)
        self._encounter_worker: EncounterWorker | None = None
        self._enhance_worker: EnhanceWorker | None = None
        self._enhance_dialog: EnhanceRequestDialog | None = None

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
        self._setup_encounter_table()

        # System Prompt 편집 영역 비활성화
        self._set_sp_edit_enabled(False)
        self._update_sp_editor_actions()

        # Enhance 결과 복사 버튼 상태 초기화
        self._update_copy_button_state()

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
        self.ui.list_encounters.itemSelectionChanged.connect(self._on_encounter_selection_changed)
        self.ui.list_encounters.cellClicked.connect(self._on_encounter_cell_clicked)
        self.ui.list_encounters.currentCellChanged.connect(self._on_encounter_current_cell_changed)

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
        self.ui.btn_result_view_settings.clicked.connect(self._open_result_view_settings)
        self.ui.btn_save_to_sigma.clicked.connect(self._on_copy_result_clicked)
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

    def _setup_encounter_table(self):
        """진료 목록 테이블 기본 설정"""
        table = self.ui.list_encounters
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(['No.', 'Name'])
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setShowGrid(False)
        table.setAlternatingRowColors(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table.setColumnWidth(0, 70)

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
        self._set_encounter_list_loading_state(True)

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
        self.ui.list_encounters.clearContents()
        self.ui.list_encounters.setRowCount(0)
        self.ui.txt_plain_note.clear()
        self.ui.txt_enhanced_result.clear()
        self.current_plain_note = ''
        self.current_enhanced_text = ''
        self.current_encounter_uuid = None

        self.ui.list_encounters.blockSignals(True)
        for row, enc in enumerate(encounters):
            name = str(enc.get('patient_name', '') or '(이름없음)')
            masked_name = self._mask_patient_name(name)
            pid = str(enc.get('patient_id', '') or '')
            uuid_val = enc.get('encounter_uuid', '')

            self.ui.list_encounters.insertRow(row)

            number_item = QTableWidgetItem(pid)
            number_item.setData(Qt.ItemDataRole.UserRole, uuid_val)
            name_item = QTableWidgetItem(masked_name)

            number_item.setTextAlignment(int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter))
            name_item.setTextAlignment(int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter))

            self.ui.list_encounters.setItem(row, 0, number_item)
            self.ui.list_encounters.setItem(row, 1, name_item)
        self.ui.list_encounters.blockSignals(False)

        app_logger.info(f"진료 목록 조회 완료: {len(encounters)}건")

    def _on_encounter_error(self, error_msg: str):
        """진료 조회 오류"""
        self._handle_sigma_connection_failure(error_msg)
        if '429' in error_msg or 'Rate Limit' in error_msg or '요청 제한' in error_msg:
            show_error(self, "조회 오류", f"진료 목록 조회가 서버 요청 제한 때문에 실패했습니다.\n\n{error_msg}")
        else:
            show_error(self, "조회 오류", error_msg)
        app_logger.error(f"진료 조회 오류: {error_msg}")

    def _restore_encounter_button(self):
        """목록조회 버튼 복원"""
        self._set_encounter_list_loading_state(False)

    def _set_encounter_list_loading_state(self, is_loading: bool):
        """진료 목록 조회 중 관련 UI 활성 상태 전환"""
        self.ui.btn_load_encounters.setEnabled(not is_loading)
        self.ui.btn_prev_date.setEnabled(not is_loading)
        self.ui.btn_next_date.setEnabled(not is_loading)
        self.ui.btn_go_today.setEnabled(not is_loading)
        self.ui.date_edit_encounter.setEnabled(not is_loading)
        self.ui.btn_load_encounters.setText("조회 중..." if is_loading else "조회")

    # ── 6. 진료 상세 조회 ──

    def _on_encounter_selection_changed(self):
        """환자 목록에서 행 선택 시 자동 상세 조회"""
        encounter_uuid = self._get_selected_encounter_uuid()
        if not encounter_uuid:
            return

        self._request_encounter_detail(encounter_uuid)

    def _on_encounter_cell_clicked(self, row: int, column: int):
        """환자 목록 셀 클릭 시 상세 조회"""
        encounter_uuid = self._get_encounter_uuid_for_row(row)
        if not encounter_uuid:
            return

        self._request_encounter_detail(encounter_uuid)

    def _on_encounter_current_cell_changed(self, current_row: int, current_column: int, previous_row: int, previous_column: int):
        """현재 셀이 바뀌면 상세 조회"""
        if current_row < 0:
            return

        encounter_uuid = self._get_encounter_uuid_for_row(current_row)
        if not encounter_uuid:
            return

        self._request_encounter_detail(encounter_uuid)

    def _request_encounter_detail(self, encounter_uuid: str):
        """선택된 진료 상세 조회 워커 시작"""
        if not encounter_uuid:
            return

        if (
            self._detail_request_in_flight_uuid == encounter_uuid
            and self._encounter_worker is not None
            and self._encounter_worker.isRunning()
        ):
            return

        client = self._create_api_client()
        if not client:
            return

        self.current_encounter_uuid = encounter_uuid
        self._detail_request_in_flight_uuid = encounter_uuid

        self._encounter_worker = EncounterWorker(
            client, mode='detail', encounter_uuid=encounter_uuid
        )
        self._encounter_worker.detail_loaded.connect(self._on_detail_loaded)
        self._encounter_worker.error.connect(self._on_encounter_error)
        self._encounter_worker.finished.connect(self._on_encounter_detail_request_finished)
        self._encounter_worker.start()

    def _on_load_encounter_detail_clicked(self):
        """[조회] 클릭"""
        encounter_uuid = self._get_selected_encounter_uuid()
        if not encounter_uuid:
            show_warning(self, "알림", "진료 목록에서 환자를 선택해 주세요.")
            return

        client = self._create_api_client()
        if not client:
            return

        self.current_encounter_uuid = encounter_uuid

        self._request_encounter_detail(encounter_uuid)

    def _on_detail_loaded(self, data: dict):
        """진료 상세 수신"""
        plain_note = data.get('plain_note', '') or ''
        external_note = str(data.get('external_note') or '').strip()
        self.current_plain_note = plain_note
        self.ui.txt_plain_note.setPlainText(plain_note)

        if external_note:
            self.current_enhanced_text = ''
            self.ui.txt_enhanced_result.setPlainText(external_note)
        else:
            self._restore_cached_enhance_result(self.current_encounter_uuid)

        self._update_copy_button_state()
        app_logger.info(f"진료 상세 조회 완료: {self.current_encounter_uuid}")

    def _on_encounter_detail_request_finished(self):
        """진료 상세 조회 워커 종료 시 중복 방지 상태 해제"""
        self._detail_request_in_flight_uuid = None

    def _get_selected_encounter_uuid(self) -> str | None:
        """현재 선택된 진료의 encounter_uuid 반환"""
        row = self.ui.list_encounters.currentRow()
        if row < 0:
            return None

        return self._get_encounter_uuid_for_row(row)

    def _get_encounter_uuid_for_row(self, row: int) -> str | None:
        """주어진 행의 encounter_uuid 반환"""
        if row < 0:
            return None

        item = self.ui.list_encounters.item(row, 0)
        if not item:
            return None

        encounter_uuid = item.data(Qt.ItemDataRole.UserRole)
        return str(encounter_uuid) if encounter_uuid else None

    def _mask_patient_name(self, name: str) -> str:
        """환자 이름 중간 마스킹"""
        normalized_name = str(name or '').strip()
        if not normalized_name:
            return '(이름없음)'
        if len(normalized_name) == 1:
            return normalized_name
        if len(normalized_name) == 2:
            return f'{normalized_name[0]}*'
        middle_mask = '*' * (len(normalized_name) - 2)
        return f'{normalized_name[0]}{middle_mask}{normalized_name[-1]}'

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
        self._restore_sp_selection(self.current_sp_id)

    # ── 12. System Prompt 아래로 이동 ──

    def _on_sp_move_down_clicked(self):
        """[▼ 아래] 클릭"""
        if not self.current_sp_id:
            return
        self.sp_manager.move_down(self.current_sp_id)
        self._load_sp_list()
        self._restore_sp_selection(self.current_sp_id)

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
        plain_note = self.ui.txt_plain_note.toPlainText().strip()

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

        if not plain_note:
            show_warning(self, "알림", "보강할 문서를 입력하거나 진료 기록을 조회해 주세요.")
            return

        if not self.current_sp_id:
            show_warning(self, "알림", "System Prompt를 선택해 주세요.")
            return

        # 선택된 System Prompt 가져오기
        sp = self.sp_manager.get_system_prompt_by_id(self.current_sp_id)
        if not sp:
            show_warning(self, "알림", "System Prompt를 선택해 주세요.")
            return

        agent_name = self.ui.combo_ai_agent.currentText().strip() or "미선택"
        model_name = self._get_current_ai_model_name()
        system_prompt_title = sp.get('title', '') or "(제목 없음)"

        self._enhance_dialog = EnhanceRequestDialog(
            self,
            plain_note=plain_note,
            agent_name=agent_name,
            model_name=model_name,
            system_prompt_title=system_prompt_title,
        )
        self._enhance_dialog.btn_submit.clicked.connect(
            lambda: self._start_enhance_request(sp=sp, plain_note=plain_note)
        )

        if self._enhance_dialog.exec() != QDialog.DialogCode.Accepted:
            self._enhance_dialog = None
            return

        self._enhance_dialog = None

    def _start_enhance_request(self, sp: dict, plain_note: str):
        """Enhance 전송 실행"""
        if not self._enhance_dialog:
            return

        self._enhance_target_encounter_uuid = self.current_encounter_uuid
        self.ui.btn_enhance.setEnabled(False)
        self.ui.btn_enhance.setText("처리 중...")
        self.ui.txt_enhanced_result.clear()
        self.current_plain_note = plain_note
        self._enhance_dialog.start_progress()
        self._enhance_dialog.set_progress_text("AI 서버에 요청 전송 중...")

        self._enhance_worker = EnhanceWorker(
            agent_type=self.current_ai_agent,
            system_prompt_text=sp['content'],
            plain_note=plain_note,
        )
        self._enhance_worker.progress.connect(self._on_enhance_progress)
        self._enhance_worker.result.connect(self._on_enhance_result)
        self._enhance_worker.error.connect(self._on_enhance_error)
        self._enhance_worker.finished.connect(self._restore_enhance_button)
        self._enhance_worker.start()

    def _on_enhance_progress(self, status_text: str):
        """Enhance 진행 상태 표시"""
        if self._enhance_dialog:
            self._enhance_dialog.set_progress_text(status_text)

    def _on_enhance_result(self, text: str):
        """Enhance 결과 수신"""
        try:
            normalized_text = self._validate_and_normalize_enhance_json(text)
        except ValueError as e:
            self.current_enhanced_text = ''
            self.ui.txt_enhanced_result.clear()
            if self._enhance_dialog:
                self._enhance_dialog.show_error(str(e))
            else:
                show_error(self, "AI Enhance 오류", str(e))
            app_logger.error(f"Enhance 결과 검증 실패: {e}")
            return

        self.current_enhanced_text = normalized_text
        formatted_text = self._format_enhance_result_for_view(normalized_text)
        self.ui.txt_enhanced_result.setPlainText(formatted_text)
        self._save_enhance_result_cache(
            encounter_uuid=self._enhance_target_encounter_uuid,
            raw_result=normalized_text,
            formatted_result=formatted_text,
        )
        if self._enhance_dialog:
            self._enhance_dialog.show_success(formatted_text)
        app_logger.info(f"Enhance 완료 (길이: {len(normalized_text)})")

    def _on_enhance_error(self, error_msg: str):
        """Enhance 오류"""
        self._update_copy_button_state()
        if self._enhance_dialog:
            self._enhance_dialog.show_error(error_msg)
        else:
            show_error(self, "AI Enhance 오류", error_msg)
        app_logger.error(f"Enhance 오류: {error_msg}")

    def _restore_enhance_button(self):
        """Enhance 버튼 복원"""
        self.ui.btn_enhance.setEnabled(True)
        self.ui.btn_enhance.setText("Enhance")

    # ── 16. 결과 복사 ──

    def _on_copy_result_clicked(self):
        """[클립보드에 복사] 클릭"""
        enhanced_text = self.ui.txt_enhanced_result.toPlainText().strip()
        if not enhanced_text:
            show_warning(self, "알림", "복사할 Enhance 결과가 없습니다.")
            return

        QApplication.clipboard().setText(enhanced_text)
        show_info(self, "복사 완료", "결과를 클립보드에 복사했습니다.")
        app_logger.info("Enhance 결과를 클립보드에 복사했습니다.")

    def _on_enhanced_text_changed(self):
        """Enhance 결과 편집 시 복사 가능 상태 갱신"""
        self._update_copy_button_state()

    def _open_result_view_settings(self):
        """결과보기 설정 다이얼로그 열기"""
        dialog = ResultViewSettingsDialog(self, self._get_result_view_settings())
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        settings = dialog.get_values()
        nn_conf.save_config('RESULT_VIEW_SETTINGS', settings)

        if self.current_enhanced_text:
            self.ui.txt_enhanced_result.setPlainText(
                self._format_enhance_result_for_view(self.current_enhanced_text)
            )

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

    def _get_current_ai_model_name(self) -> str:
        """현재 선택된 AI 모델명 반환"""
        if self.current_ai_agent == AI_AGENT_GEMINI:
            return nn_conf.gemini_model_id or '미설정'
        if self.current_ai_agent == AI_AGENT_OPENAI:
            return nn_conf.openai_model_id or '미설정'
        return '미설정'

    def _get_result_view_settings(self) -> dict:
        """결과보기 라벨 설정 반환"""
        defaults = {
            'chief_complaint': 'C/C',
            'onset': 'O/S',
            'subjective': 'S',
            'objective': 'O',
            'assessment': 'A',
            'plan': 'P',
        }
        configured = getattr(nn_conf, 'result_view_settings', {}) or {}
        merged = defaults.copy()
        for key in defaults:
            value = str(configured.get(key) or '').strip()
            if value:
                merged[key] = value
        return merged

    def _format_enhance_result_for_view(self, normalized_json_text: str) -> str:
        """Enhance JSON을 결과보기 설정 형식의 텍스트로 변환"""
        data = json.loads(normalized_json_text)
        labels = self._get_result_view_settings()
        field_order = [
            'chief_complaint',
            'onset',
            'subjective',
            'objective',
            'assessment',
            'plan',
        ]
        lines = []
        for key in field_order:
            label = labels[key]
            value = str(data.get(key) or '').strip()
            lines.append(f'{label} : {value}')
        return '\n'.join(lines)

    def _save_enhance_result_cache(self, encounter_uuid: str | None, raw_result: str, formatted_result: str) -> None:
        """현재 Enhance 결과를 진료별 로컬 캐시에 저장"""
        if not encounter_uuid:
            return

        self.result_cache.save_result(
            encounter_uuid=encounter_uuid,
            raw_result=raw_result,
            formatted_result=formatted_result,
        )

    def _restore_cached_enhance_result(self, encounter_uuid: str | None) -> None:
        """서버 external_note가 비어 있으면 로컬 캐시 결과를 복원"""
        self.current_enhanced_text = ''
        self.ui.txt_enhanced_result.clear()

        if not encounter_uuid:
            return

        cached = self.result_cache.get_result(encounter_uuid)
        if not cached:
            return

        raw_result = str(cached.get('raw_result') or '').strip()
        formatted_result = str(cached.get('formatted_result') or '').strip()

        if raw_result:
            try:
                formatted_result = self._format_enhance_result_for_view(raw_result)
                self.current_enhanced_text = raw_result
            except (TypeError, ValueError, json.JSONDecodeError) as e:
                app_logger.warning(f"캐시된 Enhance raw_result 재포맷 실패: {encounter_uuid} - {e}")
                self.current_enhanced_text = ''

        if not formatted_result:
            return

        self.ui.txt_enhanced_result.setPlainText(formatted_result)
        app_logger.info(f"로컬 캐시 Enhance 결과 복원: {encounter_uuid}")

    def _validate_and_normalize_enhance_json(self, text: str) -> str:
        """Enhance 결과가 요구된 JSON 스키마인지 검증 후 정규화"""
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 실패: {e.msg}") from e

        if not isinstance(data, dict):
            raise ValueError("최상위 결과는 JSON 객체여야 합니다.")

        required_keys = ['chief_complaint', 'onset', 'subjective', 'objective', 'assessment', 'plan', 'metadata']
        for key in required_keys:
            if key not in data:
                raise ValueError(f"필수 키 누락: {key}")

        for key in ['chief_complaint', 'onset', 'subjective', 'objective', 'assessment', 'plan']:
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
            'chief_complaint': data['chief_complaint'],
            'onset': data['onset'],
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

    def _update_copy_button_state(self):
        """화면에 표시된 Enhance 결과 존재 여부에 따라 복사 버튼 상태 갱신"""
        button = self.ui.btn_save_to_sigma
        enhanced_text = self.ui.txt_enhanced_result.toPlainText().strip()

        if not enhanced_text:
            button.setEnabled(False)
            button.setToolTip("복사할 Enhance 결과가 없습니다.")
            return

        button.setEnabled(True)
        button.setToolTip("")

    def _set_sp_edit_enabled(self, enabled: bool):
        """System Prompt 편집 영역 활성화/비활성화"""
        self.ui.edit_sp_title.setReadOnly(not enabled)
        self.ui.txt_sp_content.setReadOnly(not enabled)

        # 편집 중에는 좌측 목록/버튼 비활성화
        self.ui.list_system_prompts.setEnabled(not enabled)
        self.ui.btn_sp_new.setEnabled(not enabled)
        self.ui.btn_sp_delete.setEnabled(not enabled)
        self.ui.btn_sp_move_up.setEnabled(not enabled)
        self.ui.btn_sp_move_down.setEnabled(not enabled)

    def _update_sp_editor_actions(self):
        """System Prompt 편집 상태에 따라 액션 버튼 활성 상태 갱신"""
        is_editing = bool(self._sp_edit_mode)
        is_dirty = self._sp_dirty
        has_selection = bool(self.current_sp_id)

        self.ui.btn_sp_edit.setEnabled((not is_editing) and has_selection)
        self.ui.btn_sp_save.setEnabled(is_editing and is_dirty)
        self.ui.btn_sp_cancel.setEnabled(is_editing)
        self.ui.btn_sp_save.setDefault(is_editing)
        self.ui.btn_sp_save.setAutoDefault(is_editing)

    def _select_sp_by_id(self, sp_id: str):
        """System Prompt ID로 목록에서 선택"""
        for i in range(self.ui.list_system_prompts.count()):
            item = self.ui.list_system_prompts.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == sp_id:
                self.ui.list_system_prompts.setCurrentRow(i)
                return

    def _restore_sp_selection(self, sp_id: str | None):
        """이동 후에도 현재 선택/포커스가 유지되도록 복구"""
        if not sp_id:
            return

        for i in range(self.ui.list_system_prompts.count()):
            item = self.ui.list_system_prompts.item(i)
            if not item or item.data(Qt.ItemDataRole.UserRole) != sp_id:
                continue

            self.ui.list_system_prompts.setCurrentItem(item)
            item.setSelected(True)
            self.ui.list_system_prompts.scrollToItem(item)
            self.ui.list_system_prompts.setFocus()
            self.current_sp_id = sp_id
            self._on_sp_selected(i)
            return
