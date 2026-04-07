import customtkinter as ctk
import core.database as db
import core.scheduler as scheduler
from ui.task_form import show_task_form
from ui.task_list import TaskListFrame
from ui.alert_popup import show_alert


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

        # Ctrl+N 단축키로 할 일 추가
        self.bind("<Control-n>", lambda e: self._open_form())

    def _build_ui(self):
        # 헤더
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

        # 탭
        self.tab = ctk.CTkTabview(self)
        self.tab.pack(fill="both", expand=True, padx=16, pady=(8, 16))
        self.tab.add("진행 중")
        self.tab.add("완료")

        self.active_list = TaskListFrame(
            self.tab.tab("진행 중"),
            on_complete=self._complete_task,
            on_delete=self._delete_task,
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
        """DB에서 읽어 카드 전체 재구성 — 추가/삭제/완수 시에만 호출."""
        all_tasks = db.get_all_tasks()
        active = [t for t in all_tasks if t.status == "active"]
        done = [t for t in all_tasks if t.status == "completed"]

        self.active_list.refresh(active)
        self.done_list.refresh(done)

        # 탭에 개수 표시 (현재 탭 위치 유지)
        try:
            self.tab._segmented_button.configure(
                values=[
                    f"진행 중 ({len(active)})" if active else "진행 중",
                    f"완료 ({len(done)})" if done else "완료",
                ]
            )
        except Exception:
            pass

        # 긴급 태스크 수를 윈도우 타이틀에 표시
        overdue = sum(1 for t in active if __import__('features.countdown', fromlist=['seconds_left']).seconds_left(t) <= 0)
        if overdue:
            self.title(f"⚠ NEVER FORGET — 마감 초과 {overdue}개!")
        elif active:
            self.title(f"NEVER FORGET ({len(active)}개 진행 중)")
        else:
            self.title("NEVER FORGET")

    def _tick(self):
        """매초 카운트다운 라벨만 갱신 (DB 쿼리 없음)."""
        self.active_list.tick()
        self.after(1000, self._tick)

    def _open_form(self):
        show_task_form(self, on_save=self._full_refresh)

    def _complete_task(self, task):
        db.mark_completed(task.id)
        self._full_refresh()

    def _delete_task(self, task):
        db.delete_task(task.id)
        self._full_refresh()

    def _poll_alerts(self):
        """스케줄러 큐를 폴링해서 알림 팝업 표시."""
        try:
            while True:
                alert = scheduler.alert_queue.get_nowait()
                task = alert["task"]
                level = alert["level"]
                message = alert["message"]

                def _on_close(completed=False, t=task):
                    if completed:
                        self._complete_task(t)

                show_alert(self, task, message, level, on_close=_on_close)
        except Exception:
            pass
        self.after(2000, self._poll_alerts)
