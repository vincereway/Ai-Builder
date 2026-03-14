# -*- coding: utf-8 -*-
# 이 파일은 compile_ui.py에 의해 자동 생성됩니다.
# 수동 수정 시 다음 컴파일에서 덮어씌워집니다.

from PySide6.QtCore import QCoreApplication, QDate, QMetaObject, Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QPushButton, QDateEdit,
    QListWidget, QPlainTextEdit, QComboBox, QLineEdit,
    QSpacerItem, QSizePolicy,
)


class Ui_MainWindow:
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 750)

        self.centralwidget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)
        self.verticalLayout_main = QVBoxLayout(self.centralwidget)

        # === 상단 바 ===
        self.layout_top = QHBoxLayout()
        self.btn_open_settings = QPushButton(self.centralwidget)
        self.btn_open_settings.setObjectName("btn_open_settings")
        self.layout_top.addWidget(self.btn_open_settings)

        self.layout_top.addItem(
            QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )

        self.lbl_connection_status_icon = QLabel(self.centralwidget)
        self.lbl_connection_status_icon.setObjectName("lbl_connection_status_icon")
        self.layout_top.addWidget(self.lbl_connection_status_icon)

        self.lbl_connection_status_text = QLabel(self.centralwidget)
        self.lbl_connection_status_text.setObjectName("lbl_connection_status_text")
        self.layout_top.addWidget(self.lbl_connection_status_text)

        self.verticalLayout_main.addLayout(self.layout_top)

        # === 진료 목록 그룹 ===
        self.group_encounters = QGroupBox(self.centralwidget)
        self.group_encounters.setObjectName("group_encounters")
        self.layout_encounters = QHBoxLayout(self.group_encounters)

        # 좌측: 날짜 + 목록
        self.layout_enc_left = QVBoxLayout()

        self.layout_date = QHBoxLayout()
        self.layout_date.addWidget(QLabel("날짜:"))
        self.date_edit_encounter = QDateEdit(self.group_encounters)
        self.date_edit_encounter.setObjectName("date_edit_encounter")
        self.date_edit_encounter.setCalendarPopup(True)
        self.date_edit_encounter.setDate(QDate.currentDate())
        self.layout_date.addWidget(self.date_edit_encounter)

        self.btn_load_encounters = QPushButton(self.group_encounters)
        self.btn_load_encounters.setObjectName("btn_load_encounters")
        self.layout_date.addWidget(self.btn_load_encounters)
        self.layout_enc_left.addLayout(self.layout_date)

        self.list_encounters = QListWidget(self.group_encounters)
        self.list_encounters.setObjectName("list_encounters")
        self.layout_enc_left.addWidget(self.list_encounters)

        self.btn_load_encounter_detail = QPushButton(self.group_encounters)
        self.btn_load_encounter_detail.setObjectName("btn_load_encounter_detail")
        self.layout_enc_left.addWidget(self.btn_load_encounter_detail)

        self.layout_encounters.addLayout(self.layout_enc_left)

        # 우측: plain_note + enhanced_result
        self.layout_enc_right = QVBoxLayout()

        self.txt_plain_note = QPlainTextEdit(self.group_encounters)
        self.txt_plain_note.setObjectName("txt_plain_note")
        self.txt_plain_note.setReadOnly(True)
        self.txt_plain_note.setPlaceholderText("진료 기록이 여기에 표시됩니다")
        self.layout_enc_right.addWidget(self.txt_plain_note)

        self.txt_enhanced_result = QPlainTextEdit(self.group_encounters)
        self.txt_enhanced_result.setObjectName("txt_enhanced_result")
        self.txt_enhanced_result.setPlaceholderText("AI Enhance 결과가 여기에 표시됩니다")
        self.layout_enc_right.addWidget(self.txt_enhanced_result)

        self.layout_encounters.addLayout(self.layout_enc_right)
        self.verticalLayout_main.addWidget(self.group_encounters)

        # === AI Agent 그룹 ===
        self.group_ai = QGroupBox(self.centralwidget)
        self.group_ai.setObjectName("group_ai")
        self.layout_ai = QHBoxLayout(self.group_ai)

        self.layout_ai.addWidget(QLabel("모델 선택:"))
        self.combo_ai_agent = QComboBox(self.group_ai)
        self.combo_ai_agent.setObjectName("combo_ai_agent")
        self.layout_ai.addWidget(self.combo_ai_agent)

        self.btn_enhance = QPushButton(self.group_ai)
        self.btn_enhance.setObjectName("btn_enhance")
        self.layout_ai.addWidget(self.btn_enhance)

        self.btn_save_to_sigma = QPushButton(self.group_ai)
        self.btn_save_to_sigma.setObjectName("btn_save_to_sigma")
        self.layout_ai.addWidget(self.btn_save_to_sigma)

        self.verticalLayout_main.addWidget(self.group_ai)

        # === 프롬프트 관리 그룹 ===
        self.group_prompts = QGroupBox(self.centralwidget)
        self.group_prompts.setObjectName("group_prompts")
        self.layout_prompts = QHBoxLayout(self.group_prompts)

        # 좌측: 프롬프트 목록 + 버튼
        self.layout_prompt_left = QVBoxLayout()
        self.list_prompts = QListWidget(self.group_prompts)
        self.list_prompts.setObjectName("list_prompts")
        self.layout_prompt_left.addWidget(self.list_prompts)

        self.layout_prompt_crud = QHBoxLayout()
        self.btn_prompt_new = QPushButton(self.group_prompts)
        self.btn_prompt_new.setObjectName("btn_prompt_new")
        self.layout_prompt_crud.addWidget(self.btn_prompt_new)
        self.btn_prompt_edit = QPushButton(self.group_prompts)
        self.btn_prompt_edit.setObjectName("btn_prompt_edit")
        self.layout_prompt_crud.addWidget(self.btn_prompt_edit)
        self.btn_prompt_delete = QPushButton(self.group_prompts)
        self.btn_prompt_delete.setObjectName("btn_prompt_delete")
        self.layout_prompt_crud.addWidget(self.btn_prompt_delete)
        self.layout_prompt_left.addLayout(self.layout_prompt_crud)

        self.layout_prompt_order = QHBoxLayout()
        self.btn_prompt_move_up = QPushButton(self.group_prompts)
        self.btn_prompt_move_up.setObjectName("btn_prompt_move_up")
        self.layout_prompt_order.addWidget(self.btn_prompt_move_up)
        self.btn_prompt_move_down = QPushButton(self.group_prompts)
        self.btn_prompt_move_down.setObjectName("btn_prompt_move_down")
        self.layout_prompt_order.addWidget(self.btn_prompt_move_down)
        self.layout_prompt_left.addLayout(self.layout_prompt_order)

        self.layout_prompts.addLayout(self.layout_prompt_left)

        # 우측: 프롬프트 편집
        self.layout_prompt_right = QVBoxLayout()

        self.layout_prompt_title = QHBoxLayout()
        self.layout_prompt_title.addWidget(QLabel("제목:"))
        self.edit_prompt_title = QLineEdit(self.group_prompts)
        self.edit_prompt_title.setObjectName("edit_prompt_title")
        self.layout_prompt_title.addWidget(self.edit_prompt_title)
        self.layout_prompt_right.addLayout(self.layout_prompt_title)

        self.layout_prompt_right.addWidget(QLabel("내용:"))
        self.txt_prompt_content = QPlainTextEdit(self.group_prompts)
        self.txt_prompt_content.setObjectName("txt_prompt_content")
        self.layout_prompt_right.addWidget(self.txt_prompt_content)

        self.layout_prompt_save = QHBoxLayout()
        self.layout_prompt_save.addItem(
            QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        self.btn_prompt_save = QPushButton(self.group_prompts)
        self.btn_prompt_save.setObjectName("btn_prompt_save")
        self.layout_prompt_save.addWidget(self.btn_prompt_save)
        self.layout_prompt_right.addLayout(self.layout_prompt_save)

        self.layout_prompts.addLayout(self.layout_prompt_right)
        self.verticalLayout_main.addWidget(self.group_prompts)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "Ai-Builder", None))
        self.btn_open_settings.setText("⚙ 설정")
        self.lbl_connection_status_icon.setText("⚪")
        self.lbl_connection_status_text.setText("미설정")
        self.group_encounters.setTitle("진료 목록")
        self.btn_load_encounters.setText("목록조회")
        self.btn_load_encounter_detail.setText("조회")
        self.group_ai.setTitle("AI Agent")
        self.btn_enhance.setText("Enhance")
        self.btn_save_to_sigma.setText("시그마차트에 저장")
        self.group_prompts.setTitle("프롬프트 관리")
        self.btn_prompt_new.setText("신규")
        self.btn_prompt_edit.setText("수정")
        self.btn_prompt_delete.setText("삭제")
        self.btn_prompt_move_up.setText("▲ 위")
        self.btn_prompt_move_down.setText("▼ 아래")
        self.btn_prompt_save.setText("저장")
