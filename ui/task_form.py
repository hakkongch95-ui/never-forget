from datetime import datetime, timedelta
import customtkinter as ctk
import core.database as db
from core.models import Task


def show_task_form(parent, on_save=None):
    top = ctk.CTkToplevel(parent)
    top.title("할 일 추가")
    top.geometry("460x440")
    top.resizable(False, False)
    top.attributes("-topmost", True)
    top.grab_set()

    ctk.CTkLabel(top, text="절대 잊으면 안 되는 일", font=("Pretendard", 18, "bold")).pack(pady=(20, 5))

    ctk.CTkLabel(top, text="제목 *", anchor="w").pack(fill="x", padx=40)
    title_entry = ctk.CTkEntry(top, width=380, height=38, placeholder_text="할 일 제목")
    title_entry.pack(padx=40, pady=(2, 8))

    ctk.CTkLabel(top, text="설명 (선택)", anchor="w").pack(fill="x", padx=40)
    desc_entry = ctk.CTkEntry(top, width=380, height=38, placeholder_text="간단한 설명")
    desc_entry.pack(padx=40, pady=(2, 8))

    ctk.CTkLabel(top, text="마감 (YYYY-MM-DD HH:MM) *", anchor="w").pack(fill="x", padx=40)

    deadline_entry = ctk.CTkEntry(top, width=380, height=38, placeholder_text="YYYY-MM-DD HH:MM")
    deadline_entry.pack(padx=40, pady=(2, 4))

    def _set_deadline(dt: datetime):
        deadline_entry.delete(0, "end")
        deadline_entry.insert(0, dt.strftime("%Y-%m-%d %H:%M"))

    # 빠른 마감 프리셋 버튼
    preset_frame = ctk.CTkFrame(top, fg_color="transparent")
    preset_frame.pack(padx=40, pady=(0, 8), fill="x")

    now = datetime.now()
    presets = [
        ("30분", now + timedelta(minutes=30)),
        ("1시간", now + timedelta(hours=1)),
        ("오늘 자정", now.replace(hour=23, minute=59, second=0, microsecond=0)),
        ("내일", now + timedelta(days=1)),
    ]
    for label, dt in presets:
        ctk.CTkButton(
            preset_frame, text=label, width=78, height=28,
            fg_color="#2a2a50", hover_color="#3a3a70",
            font=("Pretendard", 12),
            command=lambda d=dt: _set_deadline(d),
        ).pack(side="left", padx=3)

    # 기본값: 1시간 후
    _set_deadline(now + timedelta(hours=1))

    error_label = ctk.CTkLabel(top, text="", text_color="#FF3333", font=("Pretendard", 12))
    error_label.pack()

    def _save(event=None):
        title = title_entry.get().strip()
        desc = desc_entry.get().strip()
        dl_str = deadline_entry.get().strip()
        if not title:
            error_label.configure(text="제목을 입력해.")
            return
        try:
            deadline = datetime.strptime(dl_str, "%Y-%m-%d %H:%M")
        except ValueError:
            error_label.configure(text="마감 형식이 틀렸어. YYYY-MM-DD HH:MM")
            return
        task = Task(title=title, description=desc, deadline=deadline)
        db.add_task(task)
        # 즉시 스케줄러 체크 트리거
        try:
            import core.scheduler as scheduler
            scheduler.check_now()
        except Exception:
            pass
        top.grab_release()
        top.destroy()
        if on_save:
            on_save()

    top.bind("<Return>", _save)
    ctk.CTkButton(top, text="저장", width=160, height=42, command=_save).pack(pady=10)
    top.after(100, title_entry.focus_set)
