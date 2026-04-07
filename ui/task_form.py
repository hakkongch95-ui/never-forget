from datetime import datetime, timedelta
import customtkinter as ctk
import core.database as db
from core.models import Task


def show_task_form(parent, on_save=None):
    top = ctk.CTkToplevel(parent)
    top.title("할 일 추가")
    top.geometry("460x400")
    top.resizable(False, False)
    top.attributes("-topmost", True)
    top.grab_set()

    ctk.CTkLabel(top, text="절대 잊으면 안 되는 일", font=("Pretendard", 18, "bold")).pack(pady=(25, 5))

    ctk.CTkLabel(top, text="제목 *", anchor="w").pack(fill="x", padx=40)
    title_entry = ctk.CTkEntry(top, width=380, height=38, placeholder_text="할 일 제목")
    title_entry.pack(padx=40, pady=(2, 10))

    ctk.CTkLabel(top, text="설명 (선택)", anchor="w").pack(fill="x", padx=40)
    desc_entry = ctk.CTkEntry(top, width=380, height=38, placeholder_text="간단한 설명")
    desc_entry.pack(padx=40, pady=(2, 10))

    ctk.CTkLabel(top, text="마감 (YYYY-MM-DD HH:MM) *", anchor="w").pack(fill="x", padx=40)
    default_dl = (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")
    deadline_entry = ctk.CTkEntry(top, width=380, height=38, placeholder_text=default_dl)
    deadline_entry.pack(padx=40, pady=(2, 10))
    deadline_entry.insert(0, default_dl)

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
        top.grab_release()
        top.destroy()
        if on_save:
            on_save()

    # Enter 키로 저장
    top.bind("<Return>", _save)

    ctk.CTkButton(top, text="저장", width=160, height=42, command=_save).pack(pady=15)

    # 폼 열리면 제목 필드에 자동 포커스
    top.after(100, title_entry.focus_set)
