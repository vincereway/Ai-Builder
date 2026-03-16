"""
Ai-Builder 로깅 시스템

sigma_agent 패턴과 동일하게 날짜별 로그 파일을 생성합니다.
- 콘솔 + 파일 핸들러 구성
- 7일 백업, 30일 초과 로그 자동 삭제
"""

import logging
import time
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timedelta

from conf.nnconf.nnconfig import nn_conf


def cleanup_old_logs(log_directories: list = None, days: int = 30, logger: logging.Logger = None):
    """
    지정된 디렉토리에서 지정 일수보다 오래된 로그 파일을 삭제합니다.

    Args:
        log_directories: 정리할 로그 디렉토리 리스트 (None이면 기본 로그 디렉토리)
        days: 삭제 기준 일수 (기본값: 30일)
        logger: 삭제 로그를 기록할 로거
    """
    if log_directories is None:
        log_directories = [nn_conf.logs_path]

    cutoff_date = datetime.now() - timedelta(days=days)

    for log_dir in log_directories:
        if not log_dir.exists():
            continue

        for log_file in log_dir.glob('*.log*'):
            try:
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_mtime < cutoff_date:
                    log_file.unlink()
                    message = f"오래된 로그 파일 삭제: {log_file}"
                    print(message)
                    if logger:
                        logger.info(message)
            except (OSError, FileNotFoundError) as e:
                error_message = f"로그 파일 삭제 실패: {log_file} - {e}"
                print(error_message)
                if logger:
                    logger.warning(error_message)


def get_logger(logger_name: str, log_level: str = 'DEBUG') -> logging.Logger:
    """
    지정된 이름으로 로거를 생성하고 반환합니다.

    Args:
        logger_name: 로거 이름 (예: 'app', 'network', 'ai')
        log_level: 로그 레벨
    """
    full_logger_name = f"ai_builder_{logger_name}"
    logger = logging.getLogger(full_logger_name)

    if logger.handlers:
        return logger  # 이미 설정된 로거 반환

    # 로그 레벨 설정
    level = getattr(logging, log_level.upper(), logging.DEBUG)
    logger.setLevel(level)
    level_name = logging.getLevelName(level).lower()

    # 로그 디렉토리 및 파일명 준비
    today = time.strftime('%Y_%m_%d')
    log_dir = nn_conf.logs_path
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f'log_{logger_name}_{level_name}_{today}.log'

    # 로그 포맷터
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | [%(filename)s:%(lineno)d] | %(message)s'
    )

    # 콘솔 핸들러
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    # 파일 회전 핸들러 (자정마다 교체, 7일 백업 유지)
    fh = TimedRotatingFileHandler(
        filename=str(log_file),
        when='midnight',
        backupCount=7,
        encoding='utf-8'
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # 30일 이상 오래된 로그 정리
    cleanup_old_logs([nn_conf.logs_path], days=30, logger=logger)

    return logger


# 용도별 로거 인스턴스
app_logger = get_logger('app', nn_conf.log_level)
network_logger = get_logger('network', nn_conf.log_level)
ai_logger = get_logger('ai', nn_conf.log_level)
