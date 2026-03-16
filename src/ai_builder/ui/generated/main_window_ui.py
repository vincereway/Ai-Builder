# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QPlainTextEdit,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1000, 750)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_main = QVBoxLayout(self.centralwidget)
        self.verticalLayout_main.setObjectName(u"verticalLayout_main")
        self.hboxLayout = QHBoxLayout()
        self.hboxLayout.setObjectName(u"hboxLayout")
        self.lbl_connection_status_icon = QLabel(self.centralwidget)
        self.lbl_connection_status_icon.setObjectName(u"lbl_connection_status_icon")

        self.hboxLayout.addWidget(self.lbl_connection_status_icon)

        self.lbl_connection_status_text = QLabel(self.centralwidget)
        self.lbl_connection_status_text.setObjectName(u"lbl_connection_status_text")

        self.hboxLayout.addWidget(self.lbl_connection_status_text)

        self.spacerItem = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout.addItem(self.spacerItem)

        self.btn_open_settings = QPushButton(self.centralwidget)
        self.btn_open_settings.setObjectName(u"btn_open_settings")

        self.hboxLayout.addWidget(self.btn_open_settings)


        self.verticalLayout_main.addLayout(self.hboxLayout)

        self.group_encounters = QGroupBox(self.centralwidget)
        self.group_encounters.setObjectName(u"group_encounters")
        self.hboxLayout1 = QHBoxLayout(self.group_encounters)
        self.hboxLayout1.setObjectName(u"hboxLayout1")
        self.vboxLayout = QVBoxLayout()
        self.vboxLayout.setObjectName(u"vboxLayout")
        self.gridLayout_encounter_date_controls = QGridLayout()
        self.gridLayout_encounter_date_controls.setObjectName(u"gridLayout_encounter_date_controls")
        self.lbl_encounter_date = QLabel(self.group_encounters)
        self.lbl_encounter_date.setObjectName(u"lbl_encounter_date")

        self.gridLayout_encounter_date_controls.addWidget(self.lbl_encounter_date, 0, 1, 2, 1)

        self.btn_prev_date = QPushButton(self.group_encounters)
        self.btn_prev_date.setObjectName(u"btn_prev_date")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_prev_date.sizePolicy().hasHeightForWidth())
        self.btn_prev_date.setSizePolicy(sizePolicy)

        self.gridLayout_encounter_date_controls.addWidget(self.btn_prev_date, 0, 2, 2, 1)

        self.date_edit_encounter = QDateEdit(self.group_encounters)
        self.date_edit_encounter.setObjectName(u"date_edit_encounter")
        self.date_edit_encounter.setCalendarPopup(True)

        self.gridLayout_encounter_date_controls.addWidget(self.date_edit_encounter, 0, 3, 1, 1)

        self.btn_next_date = QPushButton(self.group_encounters)
        self.btn_next_date.setObjectName(u"btn_next_date")
        sizePolicy.setHeightForWidth(self.btn_next_date.sizePolicy().hasHeightForWidth())
        self.btn_next_date.setSizePolicy(sizePolicy)

        self.gridLayout_encounter_date_controls.addWidget(self.btn_next_date, 0, 4, 2, 1)

        self.btn_load_encounters = QPushButton(self.group_encounters)
        self.btn_load_encounters.setObjectName(u"btn_load_encounters")
        sizePolicy.setHeightForWidth(self.btn_load_encounters.sizePolicy().hasHeightForWidth())
        self.btn_load_encounters.setSizePolicy(sizePolicy)

        self.gridLayout_encounter_date_controls.addWidget(self.btn_load_encounters, 0, 5, 2, 1)

        self.btn_go_today = QPushButton(self.group_encounters)
        self.btn_go_today.setObjectName(u"btn_go_today")

        self.gridLayout_encounter_date_controls.addWidget(self.btn_go_today, 1, 3, 1, 1)


        self.vboxLayout.addLayout(self.gridLayout_encounter_date_controls)

        self.list_encounters = QListWidget(self.group_encounters)
        self.list_encounters.setObjectName(u"list_encounters")

        self.vboxLayout.addWidget(self.list_encounters)


        self.hboxLayout1.addLayout(self.vboxLayout)

        self.vboxLayout1 = QVBoxLayout()
        self.vboxLayout1.setObjectName(u"vboxLayout1")
        self.txt_plain_note = QPlainTextEdit(self.group_encounters)
        self.txt_plain_note.setObjectName(u"txt_plain_note")

        self.vboxLayout1.addWidget(self.txt_plain_note)

        self.btn_enhance = QPushButton(self.group_encounters)
        self.btn_enhance.setObjectName(u"btn_enhance")

        self.vboxLayout1.addWidget(self.btn_enhance)

        self.txt_enhanced_result = QPlainTextEdit(self.group_encounters)
        self.txt_enhanced_result.setObjectName(u"txt_enhanced_result")

        self.vboxLayout1.addWidget(self.txt_enhanced_result)

        self.btn_save_to_sigma = QPushButton(self.group_encounters)
        self.btn_save_to_sigma.setObjectName(u"btn_save_to_sigma")

        self.vboxLayout1.addWidget(self.btn_save_to_sigma)

        self.lbl_enhanced_result_status = QLabel(self.group_encounters)
        self.lbl_enhanced_result_status.setObjectName(u"lbl_enhanced_result_status")

        self.vboxLayout1.addWidget(self.lbl_enhanced_result_status)


        self.hboxLayout1.addLayout(self.vboxLayout1)


        self.verticalLayout_main.addWidget(self.group_encounters)

        self.group_system_prompts = QGroupBox(self.centralwidget)
        self.group_system_prompts.setObjectName(u"group_system_prompts")
        self.hboxLayout2 = QHBoxLayout(self.group_system_prompts)
        self.hboxLayout2.setObjectName(u"hboxLayout2")
        self.vboxLayout2 = QVBoxLayout()
        self.vboxLayout2.setObjectName(u"vboxLayout2")
        self.horizontalLayout_ai_agent_selector = QHBoxLayout()
        self.horizontalLayout_ai_agent_selector.setObjectName(u"horizontalLayout_ai_agent_selector")
        self.label_ai_agent = QLabel(self.group_system_prompts)
        self.label_ai_agent.setObjectName(u"label_ai_agent")

        self.horizontalLayout_ai_agent_selector.addWidget(self.label_ai_agent)

        self.combo_ai_agent = QComboBox(self.group_system_prompts)
        self.combo_ai_agent.setObjectName(u"combo_ai_agent")

        self.horizontalLayout_ai_agent_selector.addWidget(self.combo_ai_agent)


        self.vboxLayout2.addLayout(self.horizontalLayout_ai_agent_selector)

        self.horizontalLayout_system_prompt_header = QHBoxLayout()
        self.horizontalLayout_system_prompt_header.setObjectName(u"horizontalLayout_system_prompt_header")
        self.label_system_prompt_list = QLabel(self.group_system_prompts)
        self.label_system_prompt_list.setObjectName(u"label_system_prompt_list")

        self.horizontalLayout_system_prompt_header.addWidget(self.label_system_prompt_list)

        self.spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_system_prompt_header.addItem(self.spacerItem1)

        self.btn_sp_new = QPushButton(self.group_system_prompts)
        self.btn_sp_new.setObjectName(u"btn_sp_new")

        self.horizontalLayout_system_prompt_header.addWidget(self.btn_sp_new)

        self.btn_sp_delete = QPushButton(self.group_system_prompts)
        self.btn_sp_delete.setObjectName(u"btn_sp_delete")

        self.horizontalLayout_system_prompt_header.addWidget(self.btn_sp_delete)


        self.vboxLayout2.addLayout(self.horizontalLayout_system_prompt_header)

        self.horizontalLayout_system_prompt_list_area = QHBoxLayout()
        self.horizontalLayout_system_prompt_list_area.setObjectName(u"horizontalLayout_system_prompt_list_area")
        self.list_system_prompts = QListWidget(self.group_system_prompts)
        self.list_system_prompts.setObjectName(u"list_system_prompts")

        self.horizontalLayout_system_prompt_list_area.addWidget(self.list_system_prompts)

        self.verticalLayout_system_prompt_move_buttons = QVBoxLayout()
        self.verticalLayout_system_prompt_move_buttons.setObjectName(u"verticalLayout_system_prompt_move_buttons")
        self.spacerItem2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_system_prompt_move_buttons.addItem(self.spacerItem2)

        self.btn_sp_move_up = QPushButton(self.group_system_prompts)
        self.btn_sp_move_up.setObjectName(u"btn_sp_move_up")

        self.verticalLayout_system_prompt_move_buttons.addWidget(self.btn_sp_move_up)

        self.btn_sp_move_down = QPushButton(self.group_system_prompts)
        self.btn_sp_move_down.setObjectName(u"btn_sp_move_down")

        self.verticalLayout_system_prompt_move_buttons.addWidget(self.btn_sp_move_down)

        self.spacerItem3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_system_prompt_move_buttons.addItem(self.spacerItem3)


        self.horizontalLayout_system_prompt_list_area.addLayout(self.verticalLayout_system_prompt_move_buttons)


        self.vboxLayout2.addLayout(self.horizontalLayout_system_prompt_list_area)


        self.hboxLayout2.addLayout(self.vboxLayout2)

        self.vboxLayout3 = QVBoxLayout()
        self.vboxLayout3.setObjectName(u"vboxLayout3")
        self.hboxLayout3 = QHBoxLayout()
        self.hboxLayout3.setObjectName(u"hboxLayout3")
        self.label = QLabel(self.group_system_prompts)
        self.label.setObjectName(u"label")

        self.hboxLayout3.addWidget(self.label)

        self.edit_sp_title = QLineEdit(self.group_system_prompts)
        self.edit_sp_title.setObjectName(u"edit_sp_title")

        self.hboxLayout3.addWidget(self.edit_sp_title)


        self.vboxLayout3.addLayout(self.hboxLayout3)

        self.label1 = QLabel(self.group_system_prompts)
        self.label1.setObjectName(u"label1")

        self.vboxLayout3.addWidget(self.label1)

        self.horizontalLayout_sp_content_area = QHBoxLayout()
        self.horizontalLayout_sp_content_area.setObjectName(u"horizontalLayout_sp_content_area")
        self.txt_sp_content = QPlainTextEdit(self.group_system_prompts)
        self.txt_sp_content.setObjectName(u"txt_sp_content")

        self.horizontalLayout_sp_content_area.addWidget(self.txt_sp_content)

        self.verticalLayout_sp_action_buttons = QVBoxLayout()
        self.verticalLayout_sp_action_buttons.setObjectName(u"verticalLayout_sp_action_buttons")
        self.btn_sp_edit = QPushButton(self.group_system_prompts)
        self.btn_sp_edit.setObjectName(u"btn_sp_edit")
        self.btn_sp_edit.setMinimumSize(QSize(96, 0))

        self.verticalLayout_sp_action_buttons.addWidget(self.btn_sp_edit)

        self.btn_sp_cancel = QPushButton(self.group_system_prompts)
        self.btn_sp_cancel.setObjectName(u"btn_sp_cancel")
        self.btn_sp_cancel.setMinimumSize(QSize(96, 0))

        self.verticalLayout_sp_action_buttons.addWidget(self.btn_sp_cancel)

        self.btn_sp_save = QPushButton(self.group_system_prompts)
        self.btn_sp_save.setObjectName(u"btn_sp_save")
        self.btn_sp_save.setMinimumSize(QSize(96, 0))

        self.verticalLayout_sp_action_buttons.addWidget(self.btn_sp_save)

        self.spacerItem4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_sp_action_buttons.addItem(self.spacerItem4)


        self.horizontalLayout_sp_content_area.addLayout(self.verticalLayout_sp_action_buttons)


        self.vboxLayout3.addLayout(self.horizontalLayout_sp_content_area)


        self.hboxLayout2.addLayout(self.vboxLayout3)


        self.verticalLayout_main.addWidget(self.group_system_prompts)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Ai-Builder", None))
        self.lbl_connection_status_icon.setText(QCoreApplication.translate("MainWindow", u"\u26aa", None))
        self.lbl_connection_status_text.setText(QCoreApplication.translate("MainWindow", u"\ubbf8\uc124\uc815", None))
        self.btn_open_settings.setText(QCoreApplication.translate("MainWindow", u"\u2699 API \ud0a4 \uc124\uc815", None))
        self.group_encounters.setTitle(QCoreApplication.translate("MainWindow", u"\uc9c4\ub8cc \ubaa9\ub85d", None))
        self.lbl_encounter_date.setText(QCoreApplication.translate("MainWindow", u"\ub0a0\uc9dc:", None))
        self.btn_prev_date.setText(QCoreApplication.translate("MainWindow", u"\u25c0", None))
        self.date_edit_encounter.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy-MM-dd", None))
        self.btn_next_date.setText(QCoreApplication.translate("MainWindow", u"\u25b6", None))
        self.btn_load_encounters.setText(QCoreApplication.translate("MainWindow", u"\uc870\ud68c", None))
        self.btn_go_today.setText(QCoreApplication.translate("MainWindow", u"\uc624\ub298\ub85c \uc774\ub3d9", None))
        self.txt_plain_note.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\ubcf4\uac15\ud560 \ubb38\uc11c\ub97c \ub123\uc5b4\uc8fc\uc138\uc694.", None))
        self.btn_enhance.setText(QCoreApplication.translate("MainWindow", u"Enhance", None))
        self.txt_enhanced_result.setPlaceholderText(QCoreApplication.translate("MainWindow", u"AI Enhance \uacb0\uacfc\uac00 \uc5ec\uae30\uc5d0 \ud45c\uc2dc\ub429\ub2c8\ub2e4", None))
        self.btn_save_to_sigma.setText(QCoreApplication.translate("MainWindow", u"\ucc28\ud2b8\uc5d0 \uc800\uc7a5", None))
        self.lbl_enhanced_result_status.setText(QCoreApplication.translate("MainWindow", u"\uc800\uc7a5\ud560 Enhance \uacb0\uacfc\uac00 \uc5c6\uc2b5\ub2c8\ub2e4.", None))
        self.group_system_prompts.setTitle(QCoreApplication.translate("MainWindow", u"AI Agent", None))
        self.label_ai_agent.setText(QCoreApplication.translate("MainWindow", u"\ubaa8\ub378 \uc120\ud0dd:", None))
        self.label_system_prompt_list.setText(QCoreApplication.translate("MainWindow", u"System Prompt", None))
        self.btn_sp_new.setText(QCoreApplication.translate("MainWindow", u"\uc0c8\ub85c \ub9cc\ub4e4\uae30", None))
        self.btn_sp_delete.setText(QCoreApplication.translate("MainWindow", u"\uc0ad\uc81c", None))
        self.btn_sp_move_up.setText(QCoreApplication.translate("MainWindow", u"\u25b2 \uc704\ub85c", None))
        self.btn_sp_move_down.setText(QCoreApplication.translate("MainWindow", u"\u25bc \uc544\ub798\ub85c", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\uc81c\ubaa9:", None))
        self.label1.setText(QCoreApplication.translate("MainWindow", u"\ub0b4\uc6a9:", None))
        self.btn_sp_edit.setText(QCoreApplication.translate("MainWindow", u"\uc218\uc815", None))
        self.btn_sp_cancel.setText(QCoreApplication.translate("MainWindow", u"\ucde8\uc18c", None))
        self.btn_sp_save.setText(QCoreApplication.translate("MainWindow", u"\uc800\uc7a5", None))
    # retranslateUi

