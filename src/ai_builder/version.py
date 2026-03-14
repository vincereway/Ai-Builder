"""
Ai-Builder 버전 정보

앱 이름, 버전, 설명, 제작사 정보를 중앙 관리합니다.
"""

__version__ = "0.1.0"
__app_name__ = "Ai-Builder"
__description__ = "시그마차트 진료 기록 AI Enhance 도구"
__author__ = "Ai-Builder"
__author_email__ = "contact@redacted.invalid"

# 편의 상수
APP_NAME = __app_name__
APP_VERSION = __version__
APP_DESCRIPTION = __description__
APP_AUTHOR = __author__

# 버전 비교용 튜플
VERSION_INFO = tuple(int(x) for x in __version__.split('.'))


def get_version() -> str:
    """버전 문자열 반환"""
    return __version__


def get_version_info() -> dict:
    """버전 정보 딕셔너리 반환"""
    return {
        'name': APP_NAME,
        'version': APP_VERSION,
        'description': APP_DESCRIPTION,
        'author': APP_AUTHOR,
    }
