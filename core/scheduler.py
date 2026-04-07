import queue
import threading
from apscheduler.schedulers.background import BackgroundScheduler

import core.database as db
from features.reminder import should_notify, get_alert_level
from features.threat_engine import get_threat

# UI 스레드가 이 큐를 폴링해서 알림을 처리한다.
alert_queue: queue.Queue = queue.Queue()

_scheduler = BackgroundScheduler()
_lock = threading.Lock()


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


def start():
    _scheduler.add_job(_check_tasks, "interval", seconds=60, id="task_check")
    _scheduler.start()


def stop():
    _scheduler.shutdown(wait=False)
