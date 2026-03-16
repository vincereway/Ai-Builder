"""
UI 컴파일 스크립트

src/ai_builder/ui/forms/*.ui → src/ai_builder/ui/generated/*_ui.py
pyside6-uic 명령어를 사용하여 Qt Designer .ui 파일을 Python 코드로 변환합니다.
"""

import subprocess
import sys
from pathlib import Path


def compile_ui_files():
    """모든 .ui 파일을 Python 코드로 컴파일"""
    # 프로젝트 루트 기준 경로
    project_root = Path(__file__).resolve().parent.parent
    forms_dir = project_root / 'src' / 'ai_builder' / 'ui' / 'forms'
    generated_dir = project_root / 'src' / 'ai_builder' / 'ui' / 'generated'

    # generated 디렉토리 생성
    generated_dir.mkdir(parents=True, exist_ok=True)

    # __init__.py 보장
    init_file = generated_dir / '__init__.py'
    if not init_file.exists():
        init_file.touch()

    if not forms_dir.exists():
        print(f"UI forms 디렉토리가 없습니다: {forms_dir}")
        return 0

    ui_files = list(forms_dir.glob('*.ui'))
    if not ui_files:
        print("컴파일할 .ui 파일이 없습니다.")
        return 0

    compiled = 0
    failed = 0

    for ui_file in ui_files:
        # main_window.ui → main_window_ui.py
        output_name = ui_file.stem + '_ui.py'
        output_file = generated_dir / output_name

        try:
            result = subprocess.run(
                [sys.executable, '-m', 'PySide6.scripts.pyside_tool', 'uic',
                 '-o', str(output_file), str(ui_file)],
                capture_output=True, text=True
            )

            if result.returncode == 0:
                print(f"  ✅ {ui_file.name} → {output_name}")
                compiled += 1
            else:
                # pyside6-uic 직접 호출 시도
                result2 = subprocess.run(
                    ['pyside6-uic', '-o', str(output_file), str(ui_file)],
                    capture_output=True, text=True
                )
                if result2.returncode == 0:
                    print(f"  ✅ {ui_file.name} → {output_name}")
                    compiled += 1
                else:
                    print(f"  ❌ {ui_file.name} 컴파일 실패: {result2.stderr}")
                    failed += 1
        except Exception as e:
            print(f"  ❌ {ui_file.name} 처리 오류: {e}")
            failed += 1

    print(f"\nUI 컴파일 완료: {compiled}개 성공, {failed}개 실패")
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    print("=" * 50)
    print("UI 컴파일 시작")
    print("=" * 50)
    sys.exit(compile_ui_files())
