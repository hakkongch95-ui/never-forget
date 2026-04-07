import queue
import threading
from apscheduler.schedulers.background import BackgroundScheduler

import core.database as db
from features.reminder import should_notify, get_alert_level
from features.threat_engine import get_threat

# UI 스레드가 이 큐를 폴링해서 처리한다.
alert_queue: queue.Queue = queue.Queue()
verify_queue: queue.Queue = queue.Queue()  # 기억 검증 요청 큐

_scheduler = BackgroundScheduler()


def _check_tasks():
    tasks = db.get_active_tasks()
    for task in tasks:
        if not should_notify(task):
            continue
        level = get_alert_level(task)
        message = get_threat(task)
        alert_queue.put({
            "task": task,
            "level": level,
            "message": message,
        })
        db.update_reminded_at(task.id)
        db.log_reminder(task.id, f"level_{level}")

        # 위협 레벨이 높을수록 기억 검증도 요청
        if task.threat_level >= 2:
            verify_queue.put({"task": task})


def start():
    # 앱 시작 5초 후 첫 체크 (60초 기다리지 않음)
    _scheduler.add_job(_check_tasks, "interval", seconds=60,
                       id="task_check", next_run_time=__import__('datetime').datetime.now()
                       + __import__('datetime').timedelta(seconds=5))
    _scheduler.start()


def check_now():
    """새 할 일 추가 시 즉시 체크 트리거."""
    _scheduler.modify_job("task_check",
                          next_run_time=__import__('datetime').datetime.now()
                          + __import__('datetime').timedelta(seconds=1))


def stop():
    _scheduler.shutdown(wait=False)
