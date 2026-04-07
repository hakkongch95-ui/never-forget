import customtkinter as ctk
from core.models import Task
import core.database as db


def show_verify(parent, task: Task, on_done=None):
    """사용자가 할 일 내용을 기억하는지 직접 타이핑으로 확인."""
    top = ctk.CTkToplevel(parent)
    top.title("기억 검증")
    top.geometry("500x320")
    top.resizable(False, False)
    top.attributes("-topmost", True)
    top.grab_set()

    ctk.CTkLabel(
        top,
        text="이 할 일의 내용을 직접 입력해봐.",
        font=("Pretendard", 16, "bold"),
        text_color="#FFD700",
    ).pack(pady=(30, 5))

    ctk.CTkLabel(
        top,
        text=f'"{task.title}"',
        font=("Pretendard", 14),
        text_color="#AAAAAA",
    ).pack(pady=5)

    entry = ctk.CTkEntry(top, width=400, height=40, placeholder_text="여기에 입력...")
    entry.pack(pady=15)

    result_label = ctk.CTkLabel(top, text="", font=("Pretendard", 13))
    result_label.pack(pady=5)

    def _check():
        answer = entry.get().strip()
        # 제목의 핵심 단어가 포함되어 있으면 통과
        keywords = [w for w in task.title.split() if len(w) > 1]
        passed = any(k in answer for k in keywords) or answer == task.title
        if passed:
            result_label.configure(text="통과. 기억하고 있군.", text_color="#00CC66")
            top.after(1000, lambda: _close(True))
        else:
            db.escalate_threat(task.id)
            result_label.configure(
                text="틀렸어. 위협 단계 상승.", text_color="#FF3333"
            )

    def _close(passed=False):
        top.grab_release()
        top.destroy()
        if on_done:
            on_done(passed)

    top.bind("<Return>", lambda e: _check())
    ctk.CTkButton(
        top, text="확인", width=160, height=40,
        command=_check,
    ).pack(pady=10)
    top.after(100, entry.focus_set)
