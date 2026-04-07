from datetime import datetime
from core.models import Task


def seconds_left(task: Task) -> float:
    return (task.deadline - datetime.now()).total_seconds()


def format_countdown(task: Task) -> str:
    secs = seconds_left(task)
    if secs <= 0:
        elapsed = -secs
        h, rem = divmod(int(elapsed), 3600)
        m, s = divmod(rem, 60)
        return f"마감 {h}시간 {m}분 {s}초 초과"
    h, rem = divmod(int(secs), 3600)
    m, s = divmod(rem, 60)
    d, h = divmod(h, 24)
    if d > 0:
        return f"D-{d}일 {h}시간 {m}분"
    if h > 0:
        return f"{h}시간 {m}분 {s}초 남음"
    return f"{m}분 {s}초 남음"


def urgency_color(task: Task) -> str:
    secs = seconds_left(task)
    if secs <= 0:
        return "#FF0000"          # 초과 — 빨간색
    if secs <= 900:               # 15분
        return "#FF4500"
    if secs <= 3600:              # 1시간
        return "#FF8C00"
    if secs <= 21600:             # 6시간
        return "#FFD700"
    return "#00CC66"              # 여유 — 초록색
