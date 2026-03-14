# -*- coding: utf-8 -*-
# 이 파일은 compile_ui.py에 의해 자동 생성됩니다.
# 수동 수정 시 다음 컴파일에서 덮어씌워집니다.

from PySide6.QtCore import QCoreApplication, QMetaObject, Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton, QSpacerItem,
    QSizePolicy,
)


class Ui_SettingsWindow:
    def setupUi(self, SettingsWindow):
        if not SettingsWindow.objectName():
            SettingsWindow.setObjectName("SettingsWindow")
        SettingsWindow.resize(620, 420)
        SettingsWindow.setModal(True)

        self.verticalLayout = QVBoxLayout(SettingsWindow)

        # === 상단 연결 상태 ===
        self.layout_status = QHBoxLayout()
        self.layout_status.addItem(
            QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        self.lbl_settings_connection_status_icon = QLabel(SettingsWindow)
        self.lbl_settings_connection_status_icon.setObjectName("lbl_settings_connection_status_icon")
        self.layout_status.addWidget(self.lbl_settings_connection_status_icon)

        self.lbl_settings_connection_status_text = QLabel(SettingsWindow)
        self.lbl_settings_connection_status_text.setObjectName("lbl_settings_connection_status_text")
        self.layout_status.addWidget(self.lbl_settings_connection_status_text)
        self.verticalLayout.addLayout(self.layout_status)

        # === 시그마차트 API 그룹 ===
        self.group_sigma = QGroupBox(SettingsWindow)
        self.group_sigma.setObjectName("group_sigma")
        self.grid_sigma = QGridLayout(self.group_sigma)

        self.grid_sigma.addWidget(QLabel("서버 IP:"), 0, 0)
        self.edit_sigma_server_ip = QLineEdit(self.group_sigma)
        self.edit_sigma_server_ip.setObjectName("edit_sigma_server_ip")
        self.edit_sigma_server_ip.setPlaceholderText("192.168.0.100")
        self.grid_sigma.addWidget(self.edit_sigma_server_ip, 0, 1)

        self.btn_sigma_search = QPushButton(self.group_sigma)
        self.btn_sigma_search.setObjectName("btn_sigma_search")
        self.grid_sigma.addWidget(self.btn_sigma_search, 0, 2)

        self.grid_sigma.addWidget(QLabel("API 키:"), 1, 0)
        self.edit_sigma_api_key = QLineEdit(self.group_sigma)
        self.edit_sigma_api_key.setObjectName("edit_sigma_api_key")
        self.edit_sigma_api_key.setPlaceholderText("sigma_xxxxxxxxxxxxxxxxxxxx")
        self.grid_sigma.addWidget(self.edit_sigma_api_key, 1, 1)

        self.btn_sigma_api_key_save = QPushButton(self.group_sigma)
        self.btn_sigma_api_key_save.setObjectName("btn_sigma_api_key_save")
        self.grid_sigma.addWidget(self.btn_sigma_api_key_save, 1, 2)

        self.lbl_sigma_api_status = QLabel(self.group_sigma)
        self.lbl_sigma_api_status.setObjectName("lbl_sigma_api_status")
        self.grid_sigma.addWidget(self.lbl_sigma_api_status, 1, 3)

        self.verticalLayout.addWidget(self.group_sigma)

        # === Gemini 그룹 ===
        self.group_gemini = QGroupBox(SettingsWindow)
        self.group_gemini.setObjectName("group_gemini")
        self.grid_gemini = QGridLayout(self.group_gemini)

        self.btn_open_gemini_link = QPushButton(self.group_gemini)
        self.btn_open_gemini_link.setObjectName("btn_open_gemini_link")
        self.btn_open_gemini_link.setFlat(True)
        self.btn_open_gemini_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.grid_gemini.addWidget(self.btn_open_gemini_link, 0, 0, 1, 3)

        self.grid_gemini.addWidget(QLabel("API 키:"), 1, 0)
        self.edit_gemini_api_key = QLineEdit(self.group_gemini)
        self.edit_gemini_api_key.setObjectName("edit_gemini_api_key")
        self.edit_gemini_api_key.setPlaceholderText("AIzaSy_xxxxxxxxxxxxxxxxx")
        self.grid_gemini.addWidget(self.edit_gemini_api_key, 1, 1)

        self.btn_gemini_api_key_save = QPushButton(self.group_gemini)
        self.btn_gemini_api_key_save.setObjectName("btn_gemini_api_key_save")
        self.grid_gemini.addWidget(self.btn_gemini_api_key_save, 1, 2)

        self.lbl_gemini_api_status = QLabel(self.group_gemini)
        self.lbl_gemini_api_status.setObjectName("lbl_gemini_api_status")
        self.grid_gemini.addWidget(self.lbl_gemini_api_status, 1, 3)

        self.verticalLayout.addWidget(self.group_gemini)

        # === OpenAI 그룹 ===
        self.group_openai = QGroupBox(SettingsWindow)
        self.group_openai.setObjectName("group_openai")
        self.grid_openai = QGridLayout(self.group_openai)

        self.btn_open_openai_link = QPushButton(self.group_openai)
        self.btn_open_openai_link.setObjectName("btn_open_openai_link")
        self.btn_open_openai_link.setFlat(True)
        self.btn_open_openai_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.grid_openai.addWidget(self.btn_open_openai_link, 0, 0, 1, 3)

        self.grid_openai.addWidget(QLabel("SECRET KEY:"), 1, 0)
        self.edit_openai_api_key = QLineEdit(self.group_openai)
        self.edit_openai_api_key.setObjectName("edit_openai_api_key")
        self.edit_openai_api_key.setPlaceholderText("sk-xxxxxxxxxxxxxxxxxxxx")
        self.grid_openai.addWidget(self.edit_openai_api_key, 1, 1)

        self.btn_openai_api_key_save = QPushButton(self.group_openai)
        self.btn_openai_api_key_save.setObjectName("btn_openai_api_key_save")
        self.grid_openai.addWidget(self.btn_openai_api_key_save, 1, 2)

        self.lbl_openai_api_status = QLabel(self.group_openai)
        self.lbl_openai_api_status.setObjectName("lbl_openai_api_status")
        self.grid_openai.addWidget(self.lbl_openai_api_status, 1, 3)

        self.verticalLayout.addWidget(self.group_openai)

        # === 하단 닫기 버튼 ===
        self.layout_bottom = QHBoxLayout()
        self.layout_bottom.addItem(
            QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        self.btn_settings_close = QPushButton(SettingsWindow)
        self.btn_settings_close.setObjectName("btn_settings_close")
        self.layout_bottom.addWidget(self.btn_settings_close)
        self.verticalLayout.addLayout(self.layout_bottom)

        self.retranslateUi(SettingsWindow)
        QMetaObject.connectSlotsByName(SettingsWindow)

    def retranslateUi(self, SettingsWindow):
        SettingsWindow.setWindowTitle(QCoreApplication.translate("SettingsWindow", "설정", None))
        self.lbl_settings_connection_status_icon.setText("⚪")
        self.lbl_settings_connection_status_text.setText("미설정")
        self.group_sigma.setTitle("시그마차트 API")
        self.btn_sigma_search.setText("검색하기")
        self.btn_sigma_api_key_save.setText("💾 저장")
        self.group_gemini.setTitle("Gemini (Google AI)")
        self.btn_open_gemini_link.setText("🔗 Google AI Studio로 이동하기")
        self.btn_gemini_api_key_save.setText("💾 저장")
        self.group_openai.setTitle("OpenAI GPT")
        self.btn_open_openai_link.setText("🔗 OpenAI 플랫폼 이동하기")
        self.btn_openai_api_key_save.setText("💾 저장")
        self.btn_settings_close.setText("닫기")
