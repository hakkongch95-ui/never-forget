import json
import random
from pathlib import Path
from core.models import Task
from features.countdown import seconds_left

_THREATS_PATH = Path(__file__).parent.parent / "assets" / "threats.json"
_threats: dict = {}


def _load():
    global _threats
    if not _threats:
        with open(_THREATS_PATH, encoding="utf-8") as f:
            _threats = json.load(f)


def get_threat(task: Task) -> str:
    _load()
    secs = seconds_left(task)
    if secs <= 0:
        pool = _threats.get("overdue", [])
    else:
        level_key = f"level_{min(task.threat_level, 4)}"
        pool = _threats.get(level_key, [])
    return random.choice(pool) if pool else "지금 해."
