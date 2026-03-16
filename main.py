"""
Ai-Builder 진입점

개발/배포 환경 모두에서 src를 Python 경로에 추가하고
ai_builder.app.main()을 실행합니다.
"""

import sys
import os
from pathlib import Path


def setup_paths():
    """src 디렉토리를 Python 경로에 추가"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 패키징 환경
        base_dir = Path(sys.executable).parent
        internal_dir = base_dir / '_internal'
        if internal_dir.exists():
            sys.path.insert(0, str(internal_dir))
    else:
        # 개발 환경
        base_dir = Path(__file__).resolve().parent
        src_dir = base_dir / 'src'
        if src_dir.exists():
            sys.path.insert(0, str(src_dir))


def main():
    """앱 실행"""
    setup_paths()

    try:
        from ai_builder.app import main as app_main
        return app_main()
    except Exception as e:
        print(f"Ai-Builder 실행 실패: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
