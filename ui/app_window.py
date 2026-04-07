import customtkinter as ctk
import core.database as db
import core.scheduler as scheduler
from features.countdown import seconds_left
from ui.task_form import show_task_form
from ui.task_list import TaskListFrame
from ui.alert_popup import show_alert
from ui.verify_popup import show_verify


class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("NEVER FORGET")
        self.geometry("700x560")
        self.minsize(600, 480)

        self._build_ui()
        self._full_refresh()
        self._tick()
        self._poll_alerts()
        self._poll_verify()

        self.bind("<Control-n>", lambda e: self._open_form())

    def _build_ui(self):
        header = ctk.CTkFrame(self, height=60, fg_color="#12122a")
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="NEVER FORGET",
            font=("Pretendard", 22, "bold"), text_color="#FF3333"
        ).pack(side="left", padx=20, pady=10)

        ctk.CTkButton(
            header, text="+ 할 일 추가  (Ctrl+N)", width=180, height=36,
            command=self._open_form,
        ).pack(side="right", padx=20, pady=10)

        self.tab = ctk.CTkTabview(self)
        self.tab.pack(fill="both", expand=True, padx=16, pady=(8, 16))
        self.tab.add("진행 중")
        self.tab.add("완료")

        self.active_list = TaskListFrame(
            self.tab.tab("진행 중"),
            on_complete=self._complete_task,
            on_delete=self._delete_task,
            on_edit=self._edit_task,
            fg_color="transparent",
        )
        self.active_list.pack(fill="both", expand=True)

        self.done_list = TaskListFrame(
            self.tab.tab("완료"),
            on_delete=self._delete_task,
            fg_color="transparent",
        )
        self.done_list.pack(fill="both", expand=True)

    def _full_refresh(self):
        all_tasks = db.get_all_tasks()
        active = [t for t in all_tasks if t.status == "active"]
        done = [t for t in all_tasks if t.status == "completed"]

        self.active_list.refresh(active)
        self.done_list.refresh(done)

        try:
            self.tab._segmented_button.configure(
                values=[
                    f"진행 중 ({len(active)})" if active else "진행 중",
                    f"완료 ({len(done)})" if done else "완료",
                ]
            )
        except Exception:
            pass

        overdue = sum(1 for t in active if seconds_left(t) <= 0)
        if overdue:
            self.title(f"⚠ NEVER FORGET — 마감 초과 {overdue}개!")
        elif active:
            self.title(f"NEVER FORGET ({len(active)}개 진행 중)")
        else:
            self.title("NEVER FORGET")

    def _tick(self):
        self.active_list.tick()
        # 마감 초과 발생 시 타이틀도 갱신
        all_tasks = db.get_active_tasks()
        overdue = sum(1 for t in all_tasks if seconds_left(t) <= 0)
        if overdue:
            self.title(f"⚠ NEVER FORGET — 마감 초과 {overdue}개!")
        self.after(1000, self._tick)

    def _open_form(self):
        show_task_form(self, on_save=self._full_refresh)

    def _complete_task(self, task):
        db.mark_completed(task.id)
        self._full_refresh()

    def _edit_task(self, task):
        show_task_form(self, on_save=self._full_refresh, edit_task=task)

    def _delete_task(self, task):
        db.delete_task(task.id)
        self._full_refresh()

    def _poll_alerts(self):
        """알림 큐 폴링 — level 0은 OS 토스트, level 1/2는 팝업."""
        try:
            while True:
                alert = scheduler.alert_queue.get_nowait()
                task = alert["task"]
                level = alert["level"]
                message = alert["message"]

                if level == 0:
                    # OS 시스템 토스트 (방해 최소화)
                    try:
                        from plyer import notification
                        notification.notify(
                            title="NEVER FORGET",
                            message=f"{task.title}\n{message}",
                            app_name="Never Forget",
                            timeout=5,
                        )
                    except Exception:
                        pass
                else:
                    def _on_close(completed=False, t=task):
                        if completed:
                            self._complete_task(t)
                    show_alert(self, task, message, level, on_close=_on_close)
        except Exception:
            pass
        self.after(2000, self._poll_alerts)

    def _poll_verify(self):
        """기억 검증 큐 폴링."""
        try:
            item = scheduler.verify_queue.get_nowait()
            task = item["task"]
            # 아직 다른 팝업이 없을 때만 검증 팝업 표시
            show_verify(self, task)
        except Exception:
            pass
        self.after(5000, self._poll_verify)
