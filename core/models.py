from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    title: str
    deadline: datetime
    description: str = ""
    id: Optional[int] = None
    status: str = "active"          # active | completed | dismissed
    threat_level: int = 0           # 0~4, 무시할수록 높아짐
    created_at: datetime = field(default_factory=datetime.now)
    reminded_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
