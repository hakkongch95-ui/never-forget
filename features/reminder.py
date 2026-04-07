from datetime import datetime
from core.models import Task
from features.countdown import seconds_left


def should_notify(task: Task) -> bool:
    """마지막 알림으로부터 충분한 시간이 지났는지 확인."""
    if task.status != "active":
        return False
    secs = seconds_left(task)
    if task.reminded_at is None:
        return True
    since_last = (datetime.now() - task.reminded_at).total_seconds()
    # 마감 초과: 10분마다
    if secs <= 0:
        return since_last >= 600
    # 15분 이내: 2분마다
    if secs <= 900:
        return since_last >= 120
    # 1시간 이내: 10분마다
    if secs <= 3600:
        return since_last >= 600
    # 6시간 이내: 30분마다
    if secs <= 21600:
        return since_last >= 1800
    # 24시간 이내: 2시간마다
    if secs <= 86400:
        return since_last >= 7200
    return False


def get_alert_level(task: Task) -> int:
    """0=토스트, 1=팝업+소리, 2=풀스크린 차단"""
    secs = seconds_left(task)
    if secs <= 0 or secs <= 900:
        return 2
    if secs <= 3600:
        return 1
    return 0
