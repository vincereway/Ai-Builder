"""
프롬프트 관리자

prompts.json CRUD 및 순서 관리를 담당합니다.
"""

import json
import shutil
import sys
import uuid
from datetime import datetime
from pathlib import Path

from conf.nnconf.nnconfig import nn_conf
from conf.nnconf.nnlogger import app_logger


class PromptManager:
    """프롬프트 CRUD + 순서 관리"""

    def __init__(self):
        # 데이터 파일 경로: src/ai_builder/data/prompts.json (개발)
        # 또는 프로젝트 경로 기준
        self._file_path = self._resolve_prompts_path()

    def _resolve_prompts_path(self) -> Path:
        """prompts.json 경로 결정"""
        bundled_path = nn_conf.root_path / 'ai_builder' / 'data' / 'prompts.json'
        dev_source_path = nn_conf.project_path / 'src' / 'ai_builder' / 'data' / 'prompts.json'

        # 개발 환경은 문서 명세대로 src 내부 파일을 사용
        if not getattr(sys, 'frozen', False) and dev_source_path.exists():
            return dev_source_path

        # 배포 환경은 사용자 데이터 경로를 사용하되, 초기 파일은 번들에서 복사
        runtime_path = nn_conf.data_path / 'prompts.json'
        if not runtime_path.exists() and bundled_path.exists():
            runtime_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(bundled_path, runtime_path)
        return runtime_path

    def load_prompts(self) -> list[dict]:
        """프롬프트 목록 로드 (order 순 정렬)"""
        if not self._file_path.exists():
            return []
        try:
            with open(self._file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            prompts = data.get('prompts', [])
            prompts.sort(key=lambda p: p.get('order', 0))
            return prompts
        except Exception as e:
            app_logger.error(f"프롬프트 로드 실패: {e}")
            return []

    def save_prompts(self, prompts: list[dict]) -> None:
        """프롬프트 목록 저장"""
        # order 재정렬
        for i, p in enumerate(prompts):
            p['order'] = i

        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump({'prompts': prompts}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            app_logger.error(f"프롬프트 저장 실패: {e}")

    def create_prompt(self, title: str, content: str) -> dict:
        """프롬프트 신규 생성"""
        prompts = self.load_prompts()
        now = datetime.now().isoformat(timespec='seconds')
        new_prompt = {
            'id': str(uuid.uuid4()),
            'title': title,
            'content': content,
            'order': len(prompts),
            'created_dt': now,
            'updated_dt': now,
        }
        prompts.append(new_prompt)
        self.save_prompts(prompts)
        app_logger.info(f"프롬프트 생성: {title}")
        return new_prompt

    def update_prompt(self, prompt_id: str, title: str, content: str) -> dict:
        """프롬프트 수정"""
        prompts = self.load_prompts()
        for p in prompts:
            if p['id'] == prompt_id:
                p['title'] = title
                p['content'] = content
                p['updated_dt'] = datetime.now().isoformat(timespec='seconds')
                self.save_prompts(prompts)
                app_logger.info(f"프롬프트 수정: {title}")
                return p
        return {}

    def delete_prompt(self, prompt_id: str) -> None:
        """프롬프트 삭제"""
        prompts = self.load_prompts()
        prompts = [p for p in prompts if p['id'] != prompt_id]
        self.save_prompts(prompts)
        app_logger.info(f"프롬프트 삭제: {prompt_id}")

    def move_up(self, prompt_id: str) -> None:
        """프롬프트 위로 이동"""
        prompts = self.load_prompts()
        for i, p in enumerate(prompts):
            if p['id'] == prompt_id and i > 0:
                prompts[i], prompts[i - 1] = prompts[i - 1], prompts[i]
                self.save_prompts(prompts)
                return

    def move_down(self, prompt_id: str) -> None:
        """프롬프트 아래로 이동"""
        prompts = self.load_prompts()
        for i, p in enumerate(prompts):
            if p['id'] == prompt_id and i < len(prompts) - 1:
                prompts[i], prompts[i + 1] = prompts[i + 1], prompts[i]
                self.save_prompts(prompts)
                return

    def get_prompt_by_id(self, prompt_id: str) -> dict | None:
        """프롬프트 1개 조회"""
        prompts = self.load_prompts()
        for p in prompts:
            if p['id'] == prompt_id:
                return p
        return None
