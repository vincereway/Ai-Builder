"""
Enhance 결과 캐시 관리자

encounter_uuid를 키로 AI Enhance 결과를 SQLite에 저장하고 조회합니다.
"""

import sqlite3
from datetime import datetime

from conf.nnconf.nnconfig import nn_conf
from conf.nnconf.nnlogger import app_logger


class EncounterResultCacheManager:
    """진료별 Enhance 결과 캐시 관리자"""

    def __init__(self):
        self._db_path = nn_conf.settings_db_path
        self._initialize_table()

    def _connect(self) -> sqlite3.Connection:
        """캐시 저장용 SQLite 연결 반환"""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_table(self) -> None:
        """진료 결과 캐시 테이블 초기화"""
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS encounter_result_cache (
                        encounter_uuid TEXT PRIMARY KEY,
                        raw_result TEXT,
                        formatted_result TEXT,
                        updated_dt TEXT NOT NULL
                    )
                    """
                )
                conn.commit()
        except sqlite3.Error as e:
            app_logger.error(f"Enhance 결과 캐시 테이블 초기화 실패: {e}")

    def save_result(self, encounter_uuid: str, raw_result: str, formatted_result: str) -> None:
        """진료별 Enhance 결과 저장"""
        if not encounter_uuid:
            return

        updated_dt = datetime.now().isoformat(timespec='seconds')
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO encounter_result_cache (
                        encounter_uuid, raw_result, formatted_result, updated_dt
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (encounter_uuid, raw_result, formatted_result, updated_dt),
                )
                conn.commit()
        except sqlite3.Error as e:
            app_logger.error(f"Enhance 결과 캐시 저장 실패: {encounter_uuid} - {e}")

    def get_result(self, encounter_uuid: str) -> dict | None:
        """진료별 Enhance 결과 조회"""
        if not encounter_uuid:
            return None

        try:
            with self._connect() as conn:
                row = conn.execute(
                    """
                    SELECT encounter_uuid, raw_result, formatted_result, updated_dt
                    FROM encounter_result_cache
                    WHERE encounter_uuid = ?
                    """,
                    (encounter_uuid,),
                ).fetchone()
        except sqlite3.Error as e:
            app_logger.error(f"Enhance 결과 캐시 조회 실패: {encounter_uuid} - {e}")
            return None

        if not row:
            return None

        return {
            'encounter_uuid': row['encounter_uuid'],
            'raw_result': row['raw_result'] or '',
            'formatted_result': row['formatted_result'] or '',
            'updated_dt': row['updated_dt'],
        }