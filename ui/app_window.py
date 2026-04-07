import winsound
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

        self._alert_open = False  # 팝업 중복 방지 플래그

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
            empty_text="아직 완수한 일이 없어. 뭐 하고 있어?",
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

        overdue_count = sum(1 for t in active if seconds_left(t) <= 0)
        if overdue_count:
            self.title(f"⚠ NEVER FORGET — 마감 초과 {overdue_count}개!")
        elif active:
            self.title(f"NEVER FORGET ({len(active)}개 진행 중)")
        else:
            self.title("NEVER FORGET")

        # 할 일이 하나도 없을 때 환영 힌트 표시
        if not active and not done:
            self._show_welcome()

    def _tick(self):
        overdue = self.active_list.tick()
        if overdue:
            self.title(f"⚠ NEVER FORGET — 마감 초과 {overdue}개!")
        self.after(1000, self._tick)

    def _open_form(self):
        show_task_form(self, on_save=self._full_refresh)

    def _show_welcome(self):
        """최초 실행 시 툴팁 형태의 힌트 (한 번만)."""
        if getattr(self, "_welcome_shown", False):
            return
        self._welcome_shown = True
        top = ctk.CTkToplevel(self)
        top.title("NEVER FORGET")
        top.geometry("380x180")
        top.resizable(False, False)
        top.attributes("-topmost", True)
        ctk.CTkLabel(
            top,
            text="잊으면 안 되는 일을 추가해.\n\nCtrl+N 또는 '+ 할 일 추가' 버튼으로 시작해.",
            font=("Pretendard", 14),
            justify="center",
        ).pack(expand=True)
        ctk.CTkButton(top, text="알겠어", width=120,
                      command=top.destroy).pack(pady=(0, 20))

    def _complete_task(self, task):
        db.mark_completed(task.id)
        # 완수 효과음
        try:
            winsound.MessageBeep(winsound.MB_OK)
        except Exception:
            pass
        self._full_refresh()

    def _edit_task(self, task):
        show_task_form(self, on_save=self._full_refresh, edit_task=task)

    def _delete_task(self, task):
        db.delete_task(task.id)
        self._full_refresh()

    def _poll_alerts(self):
        """알림 큐 폴링 — level 0은 OS 토스트, level 1/2는 팝업 (중복 방지)."""
        try:
            while True:
                alert = scheduler.alert_queue.get_nowait()
                task = alert["task"]
                level = alert["level"]
                message = alert["message"]

                if level == 0:
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
                elif not self._alert_open:
                    self._alert_open = True

                    def _on_close(completed=False, t=task):
                        self._alert_open = False
                        if completed:
                            self._complete_task(t)

                    show_alert(self, task, message, level, on_close=_on_close)
                    break  # 한 번에 팝업 하나만
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
