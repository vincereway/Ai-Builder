"""
Ai-Builder 앱 설정 관리

sigma_agent 패턴을 따르는 전역 설정 로더.
conf/conf.yml에서 설정을 로드/저장하고,
logs/, data/ 디렉토리 경로를 관리합니다.
"""

import sys
import yaml
from pathlib import Path


# 모듈 기준 경로: src/conf/nnconf/ → src/
BASE_PATH = Path(__file__).resolve().parent.parent.parent


class Config:
    """
    앱 설정 관리

    속성:
        project_path (Path): 프로젝트 루트 (Ai-Builder/)
        root_path (Path): 실행 루트 (개발: src/, 빌드: _internal/)
        logs_path (Path): 로그 디렉토리
        data_path (Path): 데이터 디렉토리
        conf_file_path (Path): conf.yml 경로
    """

    def __init__(self):
        # PyInstaller 환경 감지
        if getattr(sys, 'frozen', False):
            # PyInstaller 패키징 환경 - 실행 파일 위치 기준
            self.project_path = Path(sys.executable).parent
            self.root_path = self.project_path / '_internal'
        else:
            # 개발 환경 - src/ 기준으로 프로젝트 루트 결정
            self.root_path = BASE_PATH
            self.project_path = BASE_PATH.parent

        # 경로 설정
        self.logs_path: Path = self.project_path / 'logs'
        self.data_path: Path = self.project_path / 'data'
        self.conf_file_path: Path = self.project_path / 'conf' / 'conf.yml'
        self.resources_path: Path = self.project_path / 'resources'
        self.certs_path: Path = self.project_path / 'certs'
        self.sigma_root_ca_path: Path = self.certs_path / 'rootCA.pem'

        # 기본값 초기화
        self.sigma_server_ip: str = ''
        self.sigma_server_port: int = 57443
        self.sigma_api_key: str = ''
        self.gemini_api_key: str = ''
        self.openai_api_key: str = ''
        self.selected_ai_agent: str = 'gemini'
        self.log_level: str = 'DEBUG'
        self.request_timeout_seconds: int = 10
        self.scan_timeout_ms: int = 300
        self.ssl_verify: bool = False

        # YAML 설정 로드
        self.load_config()

        # 디렉토리 생성
        self.ensure_directories()

    def load_config(self) -> None:
        """conf.yml 전체 로드하여 속성에 반영"""
        if not self.conf_file_path.exists():
            return

        try:
            with open(self.conf_file_path, encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"설정 파일 로드 실패: {self.conf_file_path} - {e}")
            return

        # 각 키별 반영
        if 'SIGMA_SERVER_IP' in data:
            self.sigma_server_ip = str(data['SIGMA_SERVER_IP'] or '')
        if 'SIGMA_SERVER_PORT' in data:
            self.sigma_server_port = int(data['SIGMA_SERVER_PORT'])
        if 'SIGMA_API_KEY' in data:
            self.sigma_api_key = str(data['SIGMA_API_KEY'] or '')
        if 'GEMINI_API_KEY' in data:
            self.gemini_api_key = str(data['GEMINI_API_KEY'] or '')
        if 'OPENAI_API_KEY' in data:
            self.openai_api_key = str(data['OPENAI_API_KEY'] or '')
        if 'SELECTED_AI_AGENT' in data:
            self.selected_ai_agent = str(data['SELECTED_AI_AGENT'] or 'gemini')

        # 로그 레벨 검증
        level = data.get('LOG_LEVEL')
        if isinstance(level, str) and level.upper() in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
            self.log_level = level.upper()

        if 'REQUEST_TIMEOUT_SECONDS' in data:
            self.request_timeout_seconds = int(data['REQUEST_TIMEOUT_SECONDS'])
        if 'SCAN_TIMEOUT_MS' in data:
            self.scan_timeout_ms = int(data['SCAN_TIMEOUT_MS'])
        if 'SSL_VERIFY' in data:
            self.ssl_verify = bool(data['SSL_VERIFY'])

    def get_sigma_ssl_verify(self):
        """Sigma 서버용 SSL 검증 옵션 반환"""
        if not self.ssl_verify:
            return False
        if self.sigma_root_ca_path.exists():
            return str(self.sigma_root_ca_path)
        return True

    def save_config(self, key: str, value) -> None:
        """개별 설정 값을 conf.yml에 저장"""
        # 현재 파일 로드
        data = {}
        if self.conf_file_path.exists():
            try:
                with open(self.conf_file_path, encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
            except Exception:
                data = {}

        # 값 업데이트
        data[key] = value

        # 파일 저장
        self.conf_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.conf_file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

        # 인스턴스 속성 갱신
        attr_name = key.lower()
        if hasattr(self, attr_name):
            setattr(self, attr_name, value)

    def ensure_directories(self) -> None:
        """앱 실행에 필요한 디렉토리가 없으면 생성"""
        for path in [self.logs_path, self.data_path, self.certs_path]:
            try:
                path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                print(f"디렉토리 생성 실패: {path} - {e}")


# 전역 Config 인스턴스
nn_conf = Config()
