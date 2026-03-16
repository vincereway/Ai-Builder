"""
System Prompt 관리자

SQLite 기반 System Prompt CRUD 및 순서 관리를 담당합니다.
system_prompts.json은 기본 시드 공급용으로만 사용합니다.
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from ai_builder.constants.prompt_contract import strip_enhance_schema_contract
from conf.nnconf.nnconfig import nn_conf
from conf.nnconf.nnlogger import app_logger


class SystemPromptManager:
    """System Prompt CRUD + 순서 관리"""

    def __init__(self):
        self._db_path = nn_conf.settings_db_path
        self._seed_file_path = self._resolve_seed_file_path()

        self._initialize_table()
        self._bootstrap_system_prompts()

    def _resolve_seed_file_path(self) -> Path:
        """시드용 system_prompts.json 경로 결정"""
        dev_source_path = nn_conf.project_path / 'src' / 'ai_builder' / 'data' / 'system_prompts.json'
        bundled_path = nn_conf.root_path / 'ai_builder' / 'data' / 'system_prompts.json'

        if dev_source_path.exists():
            return dev_source_path
        return bundled_path

    def _connect(self) -> sqlite3.Connection:
        """System Prompt 저장용 SQLite 연결 반환"""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_table(self) -> None:
        """System Prompt 테이블 초기화"""
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS system_prompts (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        display_order INTEGER NOT NULL,
                        created_dt TEXT NOT NULL,
                        updated_dt TEXT NOT NULL
                    )
                    """
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_system_prompts_display_order ON system_prompts(display_order)"
                )
                conn.commit()
        except sqlite3.Error as e:
            app_logger.error(f"System Prompt 테이블 초기화 실패: {e}")

    def _bootstrap_system_prompts(self) -> None:
        """최초 실행 시 시드 JSON의 기본 Prompt를 DB에 보충"""
        self._ensure_seed_prompts()

    def _count_prompts(self) -> int:
        """저장된 System Prompt 개수 반환"""
        try:
            with self._connect() as conn:
                row = conn.execute("SELECT COUNT(*) AS count FROM system_prompts").fetchone()
                return int(row['count']) if row else 0
        except sqlite3.Error as e:
            app_logger.error(f"System Prompt 개수 조회 실패: {e}")
            return 0

    def _load_prompts_from_json(self, file_path: Path) -> list[dict]:
        """JSON 파일에서 System Prompt 목록 로드"""
        if not file_path.exists():
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            app_logger.error(f"System Prompt 시드 로드 실패: {file_path} - {e}")
            return []

        prompts = data.get('system_prompts', [])
        normalized_prompts = []
        for order, prompt in enumerate(prompts):
            normalized_prompts.append(
                self._normalize_prompt_record(
                    prompt,
                    fallback_order=order,
                )
            )
        normalized_prompts.sort(key=lambda item: item['order'])
        return normalized_prompts

    def _normalize_prompt_record(self, prompt: dict, fallback_order: int) -> dict:
        """DB 저장/반환용 System Prompt 레코드 정규화"""
        now = datetime.now().isoformat(timespec='seconds')
        prompt_id = str(prompt.get('id') or uuid.uuid4())

        try:
            display_order = int(prompt.get('order', fallback_order))
        except (TypeError, ValueError):
            display_order = fallback_order

        return {
            'id': prompt_id,
            'title': str(prompt.get('title') or ''),
            'content': strip_enhance_schema_contract(prompt.get('content') or ''),
            'order': display_order,
            'created_dt': str(prompt.get('created_dt') or now),
            'updated_dt': str(prompt.get('updated_dt') or now),
        }

    def _ensure_seed_prompts(self) -> None:
        """시드 JSON에 정의된 기본 Prompt가 DB에 없으면 추가"""
        seed_prompts = self._load_prompts_from_json(self._seed_file_path)
        if not seed_prompts:
            return

        for seed_prompt in seed_prompts:
            if self.get_system_prompt_by_id(seed_prompt['id']):
                continue

            next_order = self._count_prompts()
            prompt_to_insert = {
                **seed_prompt,
                'order': next_order,
            }
            self._insert_prompts([prompt_to_insert])
            app_logger.info(f"System Prompt 시드 추가: {seed_prompt['title']}")

    def _insert_prompts(self, prompts: list[dict]) -> None:
        """여러 System Prompt를 SQLite에 삽입"""
        if not prompts:
            return

        try:
            with self._connect() as conn:
                for prompt in prompts:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO system_prompts (
                            id, title, content, display_order, created_dt, updated_dt
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            prompt['id'],
                            prompt['title'],
                            prompt['content'],
                            prompt['order'],
                            prompt['created_dt'],
                            prompt['updated_dt'],
                        ),
                    )
                conn.commit()
        except sqlite3.Error as e:
            app_logger.error(f"System Prompt 삽입 실패: {e}")

    def load_system_prompts(self) -> list[dict]:
        """System Prompt 목록 로드 (order 순 정렬)"""
        try:
            with self._connect() as conn:
                rows = conn.execute(
                    """
                    SELECT id, title, content, display_order, created_dt, updated_dt
                    FROM system_prompts
                    ORDER BY display_order ASC, created_dt ASC
                    """
                ).fetchall()
        except sqlite3.Error as e:
            app_logger.error(f"System Prompt 로드 실패: {e}")
            return []

        return [
            {
                'id': row['id'],
                'title': row['title'],
                'content': row['content'],
                'order': row['display_order'],
                'created_dt': row['created_dt'],
                'updated_dt': row['updated_dt'],
            }
            for row in rows
        ]

    def _reindex_prompt_orders(self, conn: sqlite3.Connection, prompts: list[dict]) -> None:
        """목록 순서대로 display_order 재정렬"""
        for order, prompt in enumerate(prompts):
            conn.execute(
                "UPDATE system_prompts SET display_order = ? WHERE id = ?",
                (order, prompt['id']),
            )

    def create_system_prompt(self, title: str, content: str) -> dict:
        """System Prompt 신규 생성"""
        prompts = self.load_system_prompts()
        now = datetime.now().isoformat(timespec='seconds')
        new_prompt = {
            'id': str(uuid.uuid4()),
            'title': title,
            'content': strip_enhance_schema_contract(content),
            'order': len(prompts),
            'created_dt': now,
            'updated_dt': now,
        }

        self._insert_prompts([new_prompt])
        app_logger.info(f"System Prompt 생성: {title}")
        return new_prompt

    def update_system_prompt(self, system_prompt_id: str, title: str, content: str) -> dict:
        """System Prompt 수정"""
        updated_dt = datetime.now().isoformat(timespec='seconds')
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    UPDATE system_prompts
                    SET title = ?, content = ?, updated_dt = ?
                    WHERE id = ?
                    """,
                    (title, strip_enhance_schema_contract(content), updated_dt, system_prompt_id),
                )
                conn.commit()
        except sqlite3.Error as e:
            app_logger.error(f"System Prompt 수정 실패: {e}")
            return {}

        app_logger.info(f"System Prompt 수정: {title}")
        return self.get_system_prompt_by_id(system_prompt_id) or {}

    def delete_system_prompt(self, system_prompt_id: str) -> None:
        """System Prompt 삭제"""
        try:
            with self._connect() as conn:
                conn.execute("DELETE FROM system_prompts WHERE id = ?", (system_prompt_id,))
                rows = conn.execute(
                    """
                    SELECT id, display_order
                    FROM system_prompts
                    ORDER BY display_order ASC, created_dt ASC
                    """
                ).fetchall()
                self._reindex_prompt_orders(conn, [{'id': row['id'], 'order': row['display_order']} for row in rows])
                conn.commit()
        except sqlite3.Error as e:
            app_logger.error(f"System Prompt 삭제 실패: {e}")
            return

        app_logger.info(f"System Prompt 삭제: {system_prompt_id}")

    def move_up(self, system_prompt_id: str) -> None:
        """System Prompt 위로 이동"""
        prompts = self.load_system_prompts()
        for i, prompt in enumerate(prompts):
            if prompt['id'] == system_prompt_id and i > 0:
                prompts[i], prompts[i - 1] = prompts[i - 1], prompts[i]
                self._save_prompt_order(prompts)
                return

    def move_down(self, system_prompt_id: str) -> None:
        """System Prompt 아래로 이동"""
        prompts = self.load_system_prompts()
        for i, prompt in enumerate(prompts):
            if prompt['id'] == system_prompt_id and i < len(prompts) - 1:
                prompts[i], prompts[i + 1] = prompts[i + 1], prompts[i]
                self._save_prompt_order(prompts)
                return

    def _save_prompt_order(self, prompts: list[dict]) -> None:
        """현재 목록 순서대로 display_order 저장"""
        try:
            with self._connect() as conn:
                self._reindex_prompt_orders(conn, prompts)
                conn.commit()
        except sqlite3.Error as e:
            app_logger.error(f"System Prompt 순서 저장 실패: {e}")

    def get_system_prompt_by_id(self, system_prompt_id: str) -> dict | None:
        """System Prompt 1개 조회"""
        try:
            with self._connect() as conn:
                row = conn.execute(
                    """
                    SELECT id, title, content, display_order, created_dt, updated_dt
                    FROM system_prompts
                    WHERE id = ?
                    """,
                    (system_prompt_id,),
                ).fetchone()
        except sqlite3.Error as e:
            app_logger.error(f"System Prompt 단건 조회 실패: {e}")
            return None

        if not row:
            return None

        return {
            'id': row['id'],
            'title': row['title'],
            'content': row['content'],
            'order': row['display_order'],
            'created_dt': row['created_dt'],
            'updated_dt': row['updated_dt'],
        }