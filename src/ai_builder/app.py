"""
Ai-Builder 애플리케이션

QApplication 생성 및 메인 윈도우를 실행합니다.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from conf.nnconf.nnconfig import nn_conf
from conf.nnconf.nnlogger import app_logger
from ai_builder.version import __app_name__, __version__


def main() -> int:
    """
    메인 함수

    Returns:
        int: 종료 코드 (0: 정상, 1: 오류)
    """
    app_logger.info(f"{__app_name__} v{__version__} 시작")

    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setApplicationVersion(__version__)

    # 앱 아이콘 설정
    icon_path = nn_conf.resources_path / 'icon.ico'
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # 메인 윈도우 생성
    from ai_builder.ui.windows.main_window import MainWindow
    window = MainWindow()
    window.show()

    app_logger.info("메인 윈도우 표시 완료")
    return app.exec()
