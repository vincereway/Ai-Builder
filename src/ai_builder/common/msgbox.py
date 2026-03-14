"""
메시지박스 유틸리티

sigma_agent 패턴에 맞춰 parent를 반드시 전달합니다.
"""

from PySide6.QtWidgets import QMessageBox, QWidget


def show_info(parent: QWidget, title: str, message: str) -> None:
    """정보 메시지박스"""
    QMessageBox.information(parent, title, message)


def show_warning(parent: QWidget, title: str, message: str) -> None:
    """경고 메시지박스"""
    QMessageBox.warning(parent, title, message)


def show_error(parent: QWidget, title: str, message: str) -> None:
    """에러 메시지박스"""
    QMessageBox.critical(parent, title, message)


def show_confirm(parent: QWidget, title: str, message: str) -> bool:
    """확인/취소 메시지박스, 확인 선택 시 True 반환"""
    reply = QMessageBox.question(
        parent, title, message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
    return reply == QMessageBox.StandardButton.Yes
