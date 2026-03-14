# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_window.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_SettingsWindow(object):
    def setupUi(self, SettingsWindow):
        if not SettingsWindow.objectName():
            SettingsWindow.setObjectName(u"SettingsWindow")
        SettingsWindow.resize(620, 420)
        SettingsWindow.setModal(True)
        self.verticalLayout = QVBoxLayout(SettingsWindow)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.hboxLayout = QHBoxLayout()
        self.hboxLayout.setObjectName(u"hboxLayout")
        self.spacerItem = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout.addItem(self.spacerItem)

        self.lbl_settings_connection_status_icon = QLabel(SettingsWindow)
        self.lbl_settings_connection_status_icon.setObjectName(u"lbl_settings_connection_status_icon")

        self.hboxLayout.addWidget(self.lbl_settings_connection_status_icon)

        self.lbl_settings_connection_status_text = QLabel(SettingsWindow)
        self.lbl_settings_connection_status_text.setObjectName(u"lbl_settings_connection_status_text")

        self.hboxLayout.addWidget(self.lbl_settings_connection_status_text)


        self.verticalLayout.addLayout(self.hboxLayout)

        self.group_sigma = QGroupBox(SettingsWindow)
        self.group_sigma.setObjectName(u"group_sigma")
        self.gridLayout = QGridLayout(self.group_sigma)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.group_sigma)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.edit_sigma_server_ip = QLineEdit(self.group_sigma)
        self.edit_sigma_server_ip.setObjectName(u"edit_sigma_server_ip")

        self.gridLayout.addWidget(self.edit_sigma_server_ip, 0, 1, 1, 1)

        self.btn_sigma_search = QPushButton(self.group_sigma)
        self.btn_sigma_search.setObjectName(u"btn_sigma_search")

        self.gridLayout.addWidget(self.btn_sigma_search, 0, 2, 1, 1)

        self.label1 = QLabel(self.group_sigma)
        self.label1.setObjectName(u"label1")

        self.gridLayout.addWidget(self.label1, 1, 0, 1, 1)

        self.edit_sigma_api_key = QLineEdit(self.group_sigma)
        self.edit_sigma_api_key.setObjectName(u"edit_sigma_api_key")

        self.gridLayout.addWidget(self.edit_sigma_api_key, 1, 1, 1, 1)

        self.btn_sigma_api_key_save = QPushButton(self.group_sigma)
        self.btn_sigma_api_key_save.setObjectName(u"btn_sigma_api_key_save")

        self.gridLayout.addWidget(self.btn_sigma_api_key_save, 1, 2, 1, 1)

        self.lbl_sigma_api_status = QLabel(self.group_sigma)
        self.lbl_sigma_api_status.setObjectName(u"lbl_sigma_api_status")

        self.gridLayout.addWidget(self.lbl_sigma_api_status, 1, 3, 1, 1)


        self.verticalLayout.addWidget(self.group_sigma)

        self.group_gemini = QGroupBox(SettingsWindow)
        self.group_gemini.setObjectName(u"group_gemini")
        self.gridLayout1 = QGridLayout(self.group_gemini)
        self.gridLayout1.setObjectName(u"gridLayout1")
        self.btn_open_gemini_link = QPushButton(self.group_gemini)
        self.btn_open_gemini_link.setObjectName(u"btn_open_gemini_link")
        self.btn_open_gemini_link.setFlat(True)
        self.btn_open_gemini_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.gridLayout1.addWidget(self.btn_open_gemini_link, 0, 0, 1, 3)

        self.label2 = QLabel(self.group_gemini)
        self.label2.setObjectName(u"label2")

        self.gridLayout1.addWidget(self.label2, 1, 0, 1, 1)

        self.edit_gemini_api_key = QLineEdit(self.group_gemini)
        self.edit_gemini_api_key.setObjectName(u"edit_gemini_api_key")

        self.gridLayout1.addWidget(self.edit_gemini_api_key, 1, 1, 1, 1)

        self.btn_gemini_api_key_save = QPushButton(self.group_gemini)
        self.btn_gemini_api_key_save.setObjectName(u"btn_gemini_api_key_save")

        self.gridLayout1.addWidget(self.btn_gemini_api_key_save, 1, 2, 1, 1)

        self.lbl_gemini_api_status = QLabel(self.group_gemini)
        self.lbl_gemini_api_status.setObjectName(u"lbl_gemini_api_status")

        self.gridLayout1.addWidget(self.lbl_gemini_api_status, 1, 3, 1, 1)


        self.verticalLayout.addWidget(self.group_gemini)

        self.group_openai = QGroupBox(SettingsWindow)
        self.group_openai.setObjectName(u"group_openai")
        self.gridLayout2 = QGridLayout(self.group_openai)
        self.gridLayout2.setObjectName(u"gridLayout2")
        self.btn_open_openai_link = QPushButton(self.group_openai)
        self.btn_open_openai_link.setObjectName(u"btn_open_openai_link")
        self.btn_open_openai_link.setFlat(True)
        self.btn_open_openai_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.gridLayout2.addWidget(self.btn_open_openai_link, 0, 0, 1, 3)

        self.label3 = QLabel(self.group_openai)
        self.label3.setObjectName(u"label3")

        self.gridLayout2.addWidget(self.label3, 1, 0, 1, 1)

        self.edit_openai_api_key = QLineEdit(self.group_openai)
        self.edit_openai_api_key.setObjectName(u"edit_openai_api_key")

        self.gridLayout2.addWidget(self.edit_openai_api_key, 1, 1, 1, 1)

        self.btn_openai_api_key_save = QPushButton(self.group_openai)
        self.btn_openai_api_key_save.setObjectName(u"btn_openai_api_key_save")

        self.gridLayout2.addWidget(self.btn_openai_api_key_save, 1, 2, 1, 1)

        self.lbl_openai_api_status = QLabel(self.group_openai)
        self.lbl_openai_api_status.setObjectName(u"lbl_openai_api_status")

        self.gridLayout2.addWidget(self.lbl_openai_api_status, 1, 3, 1, 1)


        self.verticalLayout.addWidget(self.group_openai)

        self.hboxLayout1 = QHBoxLayout()
        self.hboxLayout1.setObjectName(u"hboxLayout1")
        self.spacerItem1 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout1.addItem(self.spacerItem1)

        self.btn_settings_close = QPushButton(SettingsWindow)
        self.btn_settings_close.setObjectName(u"btn_settings_close")

        self.hboxLayout1.addWidget(self.btn_settings_close)


        self.verticalLayout.addLayout(self.hboxLayout1)


        self.retranslateUi(SettingsWindow)

        QMetaObject.connectSlotsByName(SettingsWindow)
    # setupUi

    def retranslateUi(self, SettingsWindow):
        SettingsWindow.setWindowTitle(QCoreApplication.translate("SettingsWindow", u"\uc124\uc815", None))
        self.lbl_settings_connection_status_icon.setText(QCoreApplication.translate("SettingsWindow", u"\u26aa", None))
        self.lbl_settings_connection_status_text.setText(QCoreApplication.translate("SettingsWindow", u"\ubbf8\uc124\uc815", None))
        self.group_sigma.setTitle(QCoreApplication.translate("SettingsWindow", u"\uc2dc\uadf8\ub9c8\ucc28\ud2b8 API", None))
        self.label.setText(QCoreApplication.translate("SettingsWindow", u"\uc11c\ubc84 IP:", None))
        self.edit_sigma_server_ip.setPlaceholderText(QCoreApplication.translate("SettingsWindow", u"192.168.0.100", None))
        self.btn_sigma_search.setText(QCoreApplication.translate("SettingsWindow", u"\uac80\uc0c9\ud558\uae30", None))
        self.label1.setText(QCoreApplication.translate("SettingsWindow", u"API \ud0a4:", None))
        self.edit_sigma_api_key.setPlaceholderText(QCoreApplication.translate("SettingsWindow", u"sigma_xxxxxxxxxxxxxxxxxxxx", None))
        self.btn_sigma_api_key_save.setText(QCoreApplication.translate("SettingsWindow", u"\U0001f4be \U0000c800\U0000c7a5", None))
        self.lbl_sigma_api_status.setText("")
        self.group_gemini.setTitle(QCoreApplication.translate("SettingsWindow", u"Gemini (Google AI)", None))
        self.btn_open_gemini_link.setText(QCoreApplication.translate("SettingsWindow", u"\U0001f517 Google AI Studio\U0000b85c \U0000c774\U0000b3d9\U0000d558\U0000ae30", None))
        self.label2.setText(QCoreApplication.translate("SettingsWindow", u"API \ud0a4:", None))
        self.edit_gemini_api_key.setPlaceholderText(QCoreApplication.translate("SettingsWindow", u"AIzaSy_xxxxxxxxxxxxxxxxx", None))
        self.btn_gemini_api_key_save.setText(QCoreApplication.translate("SettingsWindow", u"\U0001f4be \U0000c800\U0000c7a5", None))
        self.lbl_gemini_api_status.setText("")
        self.group_openai.setTitle(QCoreApplication.translate("SettingsWindow", u"OpenAI GPT", None))
        self.btn_open_openai_link.setText(QCoreApplication.translate("SettingsWindow", u"\U0001f517 OpenAI \U0000d50c\U0000b7ab\U0000d3fc \U0000c774\U0000b3d9\U0000d558\U0000ae30", None))
        self.label3.setText(QCoreApplication.translate("SettingsWindow", u"SECRET KEY:", None))
        self.edit_openai_api_key.setPlaceholderText(QCoreApplication.translate("SettingsWindow", u"sk-xxxxxxxxxxxxxxxxxxxx", None))
        self.btn_openai_api_key_save.setText(QCoreApplication.translate("SettingsWindow", u"\U0001f4be \U0000c800\U0000c7a5", None))
        self.lbl_openai_api_status.setText("")
        self.btn_settings_close.setText(QCoreApplication.translate("SettingsWindow", u"\ub2eb\uae30", None))
    # retranslateUi

