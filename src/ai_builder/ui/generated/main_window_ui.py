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
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QPlainTextEdit, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

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
        self.btn_open_settings = QPushButton(self.centralwidget)
        self.btn_open_settings.setObjectName(u"btn_open_settings")

        self.hboxLayout.addWidget(self.btn_open_settings)

        self.spacerItem = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout.addItem(self.spacerItem)

        self.lbl_connection_status_icon = QLabel(self.centralwidget)
        self.lbl_connection_status_icon.setObjectName(u"lbl_connection_status_icon")

        self.hboxLayout.addWidget(self.lbl_connection_status_icon)

        self.lbl_connection_status_text = QLabel(self.centralwidget)
        self.lbl_connection_status_text.setObjectName(u"lbl_connection_status_text")

        self.hboxLayout.addWidget(self.lbl_connection_status_text)


        self.verticalLayout_main.addLayout(self.hboxLayout)

        self.group_encounters = QGroupBox(self.centralwidget)
        self.group_encounters.setObjectName(u"group_encounters")
        self.hboxLayout1 = QHBoxLayout(self.group_encounters)
        self.hboxLayout1.setObjectName(u"hboxLayout1")
        self.vboxLayout = QVBoxLayout()
        self.vboxLayout.setObjectName(u"vboxLayout")
        self.hboxLayout2 = QHBoxLayout()
        self.hboxLayout2.setObjectName(u"hboxLayout2")
        self.label = QLabel(self.group_encounters)
        self.label.setObjectName(u"label")

        self.hboxLayout2.addWidget(self.label)

        self.date_edit_encounter = QDateEdit(self.group_encounters)
        self.date_edit_encounter.setObjectName(u"date_edit_encounter")

        self.hboxLayout2.addWidget(self.date_edit_encounter)

        self.btn_load_encounters = QPushButton(self.group_encounters)
        self.btn_load_encounters.setObjectName(u"btn_load_encounters")

        self.hboxLayout2.addWidget(self.btn_load_encounters)


        self.vboxLayout.addLayout(self.hboxLayout2)

        self.list_encounters = QListWidget(self.group_encounters)
        self.list_encounters.setObjectName(u"list_encounters")

        self.vboxLayout.addWidget(self.list_encounters)

        self.btn_load_encounter_detail = QPushButton(self.group_encounters)
        self.btn_load_encounter_detail.setObjectName(u"btn_load_encounter_detail")

        self.vboxLayout.addWidget(self.btn_load_encounter_detail)


        self.hboxLayout1.addLayout(self.vboxLayout)

        self.vboxLayout1 = QVBoxLayout()
        self.vboxLayout1.setObjectName(u"vboxLayout1")
        self.txt_plain_note = QPlainTextEdit(self.group_encounters)
        self.txt_plain_note.setObjectName(u"txt_plain_note")
        self.txt_plain_note.setReadOnly(True)

        self.vboxLayout1.addWidget(self.txt_plain_note)

        self.txt_enhanced_result = QPlainTextEdit(self.group_encounters)
        self.txt_enhanced_result.setObjectName(u"txt_enhanced_result")

        self.vboxLayout1.addWidget(self.txt_enhanced_result)


        self.hboxLayout1.addLayout(self.vboxLayout1)


        self.verticalLayout_main.addWidget(self.group_encounters)

        self.group_ai = QGroupBox(self.centralwidget)
        self.group_ai.setObjectName(u"group_ai")
        self.hboxLayout3 = QHBoxLayout(self.group_ai)
        self.hboxLayout3.setObjectName(u"hboxLayout3")
        self.label1 = QLabel(self.group_ai)
        self.label1.setObjectName(u"label1")

        self.hboxLayout3.addWidget(self.label1)

        self.combo_ai_agent = QComboBox(self.group_ai)
        self.combo_ai_agent.setObjectName(u"combo_ai_agent")

        self.hboxLayout3.addWidget(self.combo_ai_agent)

        self.btn_enhance = QPushButton(self.group_ai)
        self.btn_enhance.setObjectName(u"btn_enhance")

        self.hboxLayout3.addWidget(self.btn_enhance)

        self.btn_save_to_sigma = QPushButton(self.group_ai)
        self.btn_save_to_sigma.setObjectName(u"btn_save_to_sigma")

        self.hboxLayout3.addWidget(self.btn_save_to_sigma)


        self.verticalLayout_main.addWidget(self.group_ai)

        self.group_prompts = QGroupBox(self.centralwidget)
        self.group_prompts.setObjectName(u"group_prompts")
        self.hboxLayout4 = QHBoxLayout(self.group_prompts)
        self.hboxLayout4.setObjectName(u"hboxLayout4")
        self.vboxLayout2 = QVBoxLayout()
        self.vboxLayout2.setObjectName(u"vboxLayout2")
        self.list_prompts = QListWidget(self.group_prompts)
        self.list_prompts.setObjectName(u"list_prompts")

        self.vboxLayout2.addWidget(self.list_prompts)

        self.hboxLayout5 = QHBoxLayout()
        self.hboxLayout5.setObjectName(u"hboxLayout5")
        self.btn_prompt_new = QPushButton(self.group_prompts)
        self.btn_prompt_new.setObjectName(u"btn_prompt_new")

        self.hboxLayout5.addWidget(self.btn_prompt_new)

        self.btn_prompt_edit = QPushButton(self.group_prompts)
        self.btn_prompt_edit.setObjectName(u"btn_prompt_edit")

        self.hboxLayout5.addWidget(self.btn_prompt_edit)

        self.btn_prompt_delete = QPushButton(self.group_prompts)
        self.btn_prompt_delete.setObjectName(u"btn_prompt_delete")

        self.hboxLayout5.addWidget(self.btn_prompt_delete)


        self.vboxLayout2.addLayout(self.hboxLayout5)

        self.hboxLayout6 = QHBoxLayout()
        self.hboxLayout6.setObjectName(u"hboxLayout6")
        self.btn_prompt_move_up = QPushButton(self.group_prompts)
        self.btn_prompt_move_up.setObjectName(u"btn_prompt_move_up")

        self.hboxLayout6.addWidget(self.btn_prompt_move_up)

        self.btn_prompt_move_down = QPushButton(self.group_prompts)
        self.btn_prompt_move_down.setObjectName(u"btn_prompt_move_down")

        self.hboxLayout6.addWidget(self.btn_prompt_move_down)


        self.vboxLayout2.addLayout(self.hboxLayout6)


        self.hboxLayout4.addLayout(self.vboxLayout2)

        self.vboxLayout3 = QVBoxLayout()
        self.vboxLayout3.setObjectName(u"vboxLayout3")
        self.hboxLayout7 = QHBoxLayout()
        self.hboxLayout7.setObjectName(u"hboxLayout7")
        self.label2 = QLabel(self.group_prompts)
        self.label2.setObjectName(u"label2")

        self.hboxLayout7.addWidget(self.label2)

        self.edit_prompt_title = QLineEdit(self.group_prompts)
        self.edit_prompt_title.setObjectName(u"edit_prompt_title")

        self.hboxLayout7.addWidget(self.edit_prompt_title)


        self.vboxLayout3.addLayout(self.hboxLayout7)

        self.label3 = QLabel(self.group_prompts)
        self.label3.setObjectName(u"label3")

        self.vboxLayout3.addWidget(self.label3)

        self.txt_prompt_content = QPlainTextEdit(self.group_prompts)
        self.txt_prompt_content.setObjectName(u"txt_prompt_content")

        self.vboxLayout3.addWidget(self.txt_prompt_content)

        self.hboxLayout8 = QHBoxLayout()
        self.hboxLayout8.setObjectName(u"hboxLayout8")
        self.spacerItem1 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout8.addItem(self.spacerItem1)

        self.btn_prompt_save = QPushButton(self.group_prompts)
        self.btn_prompt_save.setObjectName(u"btn_prompt_save")

        self.hboxLayout8.addWidget(self.btn_prompt_save)


        self.vboxLayout3.addLayout(self.hboxLayout8)


        self.hboxLayout4.addLayout(self.vboxLayout3)


        self.verticalLayout_main.addWidget(self.group_prompts)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Ai-Builder", None))
        self.btn_open_settings.setText(QCoreApplication.translate("MainWindow", u"\u2699 \uc124\uc815", None))
        self.lbl_connection_status_icon.setText(QCoreApplication.translate("MainWindow", u"\u26aa", None))
        self.lbl_connection_status_text.setText(QCoreApplication.translate("MainWindow", u"\ubbf8\uc124\uc815", None))
        self.group_encounters.setTitle(QCoreApplication.translate("MainWindow", u"\uc9c4\ub8cc \ubaa9\ub85d", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\ub0a0\uc9dc:", None))
        self.btn_load_encounters.setText(QCoreApplication.translate("MainWindow", u"\ubaa9\ub85d\uc870\ud68c", None))
        self.btn_load_encounter_detail.setText(QCoreApplication.translate("MainWindow", u"\uc870\ud68c", None))
        self.txt_plain_note.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\uc9c4\ub8cc \uae30\ub85d\uc774 \uc5ec\uae30\uc5d0 \ud45c\uc2dc\ub429\ub2c8\ub2e4", None))
        self.txt_enhanced_result.setPlaceholderText(QCoreApplication.translate("MainWindow", u"AI Enhance \uacb0\uacfc\uac00 \uc5ec\uae30\uc5d0 \ud45c\uc2dc\ub429\ub2c8\ub2e4", None))
        self.group_ai.setTitle(QCoreApplication.translate("MainWindow", u"AI Agent", None))
        self.label1.setText(QCoreApplication.translate("MainWindow", u"\ubaa8\ub378 \uc120\ud0dd:", None))
        self.btn_enhance.setText(QCoreApplication.translate("MainWindow", u"Enhance", None))
        self.btn_save_to_sigma.setText(QCoreApplication.translate("MainWindow", u"\uc2dc\uadf8\ub9c8\ucc28\ud2b8\uc5d0 \uc800\uc7a5", None))
        self.group_prompts.setTitle(QCoreApplication.translate("MainWindow", u"\ud504\ub86c\ud504\ud2b8 \uad00\ub9ac", None))
        self.btn_prompt_new.setText(QCoreApplication.translate("MainWindow", u"\uc2e0\uaddc", None))
        self.btn_prompt_edit.setText(QCoreApplication.translate("MainWindow", u"\uc218\uc815", None))
        self.btn_prompt_delete.setText(QCoreApplication.translate("MainWindow", u"\uc0ad\uc81c", None))
        self.btn_prompt_move_up.setText(QCoreApplication.translate("MainWindow", u"\u25b2 \uc704", None))
        self.btn_prompt_move_down.setText(QCoreApplication.translate("MainWindow", u"\u25bc \uc544\ub798", None))
        self.label2.setText(QCoreApplication.translate("MainWindow", u"\uc81c\ubaa9:", None))
        self.label3.setText(QCoreApplication.translate("MainWindow", u"\ub0b4\uc6a9:", None))
        self.btn_prompt_save.setText(QCoreApplication.translate("MainWindow", u"\uc800\uc7a5", None))
    # retranslateUi

