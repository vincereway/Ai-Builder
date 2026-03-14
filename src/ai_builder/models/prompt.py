"""
프롬프트 데이터 모델
"""

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Prompt:
    """프롬프트 항목"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    order: int = 0
    created_dt: str = field(default_factory=lambda: datetime.now().isoformat(timespec='seconds'))
    updated_dt: str = field(default_factory=lambda: datetime.now().isoformat(timespec='seconds'))

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'order': self.order,
            'created_dt': self.created_dt,
            'updated_dt': self.updated_dt,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Prompt':
        """딕셔너리에서 생성"""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            title=data.get('title', ''),
            content=data.get('content', ''),
            order=data.get('order', 0),
            created_dt=data.get('created_dt', datetime.now().isoformat(timespec='seconds')),
            updated_dt=data.get('updated_dt', datetime.now().isoformat(timespec='seconds')),
        )
