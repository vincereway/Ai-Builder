"""
Ai-Builder 앱 설정 관리

SQLite 기반 전역 설정 로더.
conf/conf.yml은 개발모드에서만 비민감 기본값을 읽고,
API 키와 모델 관련 값은 항상 data/settings.sqlite3만 사용합니다.
"""

import json
import sqlite3
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
        self.settings_db_path: Path = self.data_path / 'settings.sqlite3'
        self.resources_path: Path = self.project_path / 'resources'
        self.certs_path: Path = self.project_path / 'certs'
        self.sigma_root_ca_path: Path = self.certs_path / 'rootCA.pem'

        # 기본값 초기화
        self.sigma_server_ip: str = ''
        self.sigma_server_port: int = 57443
        self.sigma_api_key: str = ''
        self.gemini_api_key: str = ''
        self.openai_api_key: str = ''
        self.claude_api_key: str = ''
        self.gemini_model_id: str = 'gemini-3.1-flash-lite-preview'
        self.openai_model_id: str = 'gpt-5.4'
        self.claude_model_id: str = 'claude-sonnet-4-6'
        self.gemini_model_list: list[str] = []
        self.openai_model_list: list[str] = []
        self.claude_model_list: list[str] = []
        self.selected_ai_agent: str = 'gemini'
        self.result_view_settings: dict = {
            'chief_complaint': 'C/C',
            'onset': 'O/S',
            'subjective': 'S',
            'objective': 'O',
            'assessment': 'A',
            'plan': 'P',
        }
        self.log_level: str = 'DEBUG'
        self.request_timeout_seconds: int = 10
        self.scan_timeout_ms: int = 300
        self.ssl_verify: bool = False

        # 디렉토리 생성
        self.ensure_directories()
        self._initialize_settings_db()

        # 설정 로드
        self.load_config()

    SQLITE_CONFIG_SPECS = {
        'SIGMA_SERVER_IP': ('sigma_server_ip', str, ''),
        'SIGMA_API_KEY': ('sigma_api_key', str, ''),
        'GEMINI_API_KEY': ('gemini_api_key', str, ''),
        'OPENAI_API_KEY': ('openai_api_key', str, ''),
        'CLAUDE_API_KEY': ('claude_api_key', str, ''),
        'GEMINI_MODEL_ID': ('gemini_model_id', str, 'gemini-3.1-flash-lite-preview'),
        'OPENAI_MODEL_ID': ('openai_model_id', str, 'gpt-5.4'),
        'CLAUDE_MODEL_ID': ('claude_model_id', str, 'claude-sonnet-4-6'),
        'GEMINI_MODEL_LIST': ('gemini_model_list', list, []),
        'OPENAI_MODEL_LIST': ('openai_model_list', list, []),
        'CLAUDE_MODEL_LIST': ('claude_model_list', list, []),
        'SELECTED_AI_AGENT': ('selected_ai_agent', str, 'gemini'),
        'RESULT_VIEW_SETTINGS': ('result_view_settings', dict, {
            'chief_complaint': 'C/C',
            'onset': 'O/S',
            'subjective': 'S',
            'objective': 'O',
            'assessment': 'A',
            'plan': 'P',
        }),
    }

    DEV_YAML_CONFIG_SPECS = {
        'SIGMA_SERVER_PORT': ('sigma_server_port', int, 57443),
        'LOG_LEVEL': ('log_level', str, 'DEBUG'),
        'REQUEST_TIMEOUT_SECONDS': ('request_timeout_seconds', int, 10),
        'SCAN_TIMEOUT_MS': ('scan_timeout_ms', int, 300),
        'SSL_VERIFY': ('ssl_verify', bool, False),
    }

    def load_config(self) -> None:
        """개발용 YAML 기본값과 SQLite 사용자 설정을 로드"""
        self._apply_default_values()

        if self._is_dev_mode():
            self._apply_config_values(self._load_dev_yaml_config(), self.DEV_YAML_CONFIG_SPECS)

        self._apply_config_values(self._load_sqlite_config(), self.SQLITE_CONFIG_SPECS)

    def get_sigma_ssl_verify(self):
        """Sigma 서버용 SSL 검증 옵션 반환"""
        if not self.ssl_verify:
            return False
        if self.sigma_root_ca_path.exists():
            return str(self.sigma_root_ca_path)
        return True

    def save_config(self, key: str, value) -> None:
        """개별 설정 값을 SQLite에 저장"""
        self._save_many_to_sqlite({key: value})
        self._apply_single_config_value(key, value)

    def ensure_directories(self) -> None:
        """앱 실행에 필요한 디렉토리가 없으면 생성"""
        for path in [self.logs_path, self.data_path, self.certs_path]:
            try:
                path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                print(f"디렉토리 생성 실패: {path} - {e}")

    def _initialize_settings_db(self) -> None:
        """SQLite 설정 DB 초기화"""
        try:
            with sqlite3.connect(self.settings_db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS app_config (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                    """
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"설정 DB 초기화 실패: {self.settings_db_path} - {e}")

    def _load_sqlite_config(self) -> dict:
        """SQLite에 저장된 설정 전체 로드"""
        if not self.settings_db_path.exists():
            return {}

        try:
            with sqlite3.connect(self.settings_db_path) as conn:
                rows = conn.execute("SELECT key, value FROM app_config").fetchall()
        except sqlite3.Error as e:
            print(f"설정 DB 로드 실패: {self.settings_db_path} - {e}")
            return {}

        data = {}
        for key, raw_value in rows:
            try:
                data[key] = json.loads(raw_value)
            except json.JSONDecodeError:
                data[key] = raw_value
        return data

    def _load_dev_yaml_config(self) -> dict:
        """개발모드에서 conf.yml의 비민감 기본값만 로드"""
        if not self.conf_file_path.exists():
            return {}

        try:
            with open(self.conf_file_path, encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"설정 파일 로드 실패: {self.conf_file_path} - {e}")
            return {}

        return {key: data[key] for key in self.DEV_YAML_CONFIG_SPECS if key in data}

    def _save_many_to_sqlite(self, items: dict) -> None:
        """여러 설정 값을 SQLite에 저장"""
        if not items:
            return

        try:
            with sqlite3.connect(self.settings_db_path) as conn:
                conn.executemany(
                    "INSERT OR REPLACE INTO app_config(key, value) VALUES(?, ?)",
                    [
                        (key, json.dumps(value, ensure_ascii=False))
                        for key, value in items.items()
                    ],
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"설정 DB 저장 실패: {self.settings_db_path} - {e}")

    def _apply_default_values(self) -> None:
        """전체 설정 기본값 재적용"""
        for key, (_, _, default_value) in {**self.DEV_YAML_CONFIG_SPECS, **self.SQLITE_CONFIG_SPECS}.items():
            self._apply_single_config_value(key, default_value)

    def _apply_config_values(self, data: dict, config_specs: dict) -> None:
        """로드한 설정값을 인스턴스 속성에 반영"""
        for key in config_specs:
            if key in data:
                self._apply_single_config_value(key, data[key])

    def _apply_single_config_value(self, key: str, value) -> None:
        """설정 키 하나를 인스턴스 속성에 반영"""
        spec = self.SQLITE_CONFIG_SPECS.get(key) or self.DEV_YAML_CONFIG_SPECS.get(key)
        if spec is None:
            attr_name = key.lower()
            if hasattr(self, attr_name):
                setattr(self, attr_name, value)
            return

        attr_name, expected_type, default_value = spec

        try:
            if expected_type is bool:
                normalized_value = bool(value)
            elif expected_type is int:
                normalized_value = int(value)
            elif expected_type is list:
                normalized_value = [str(item) for item in (value or []) if item]
            elif expected_type is dict:
                normalized_value = dict(value or {})
            elif expected_type is str:
                normalized_value = str(value or '')
            else:
                normalized_value = value
        except (TypeError, ValueError):
            normalized_value = default_value

        if key == 'LOG_LEVEL' and normalized_value not in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
            normalized_value = default_value

        setattr(self, attr_name, normalized_value)

    @staticmethod
    def _is_dev_mode() -> bool:
        """개발모드 여부 반환"""
        return not getattr(sys, 'frozen', False)


# 전역 Config 인스턴스
nn_conf = Config()
