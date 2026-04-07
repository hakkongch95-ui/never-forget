import winsound
import customtkinter as ctk
from core.models import Task
import core.database as db


def show_alert(parent, task: Task, message: str, level: int, on_close=None):
    """
    level 0 → 일반 팝업
    level 1 → 팝업 + 경고음
    level 2 → 풀스크린 차단 (닫기 불가, 확인 전까지 잠금)
    """
    top = ctk.CTkToplevel(parent)
    top.title("⚠ NEVER FORGET")
    top.attributes("-topmost", True)

    if level == 2:
        top.attributes("-fullscreen", True)
        top.grab_set()          # 다른 창 클릭 차단
        winsound.MessageBeep(winsound.MB_ICONHAND)
    elif level == 1:
        top.geometry("480x300")
        top.resizable(False, False)
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    else:
        top.geometry("400x240")
        top.resizable(False, False)

    bg = "#1a0000" if level == 2 else "#1e1e2e"
    top.configure(fg_color=bg)

    frame = ctk.CTkFrame(top, fg_color=bg)
    frame.pack(expand=True, fill="both", padx=40, pady=40)

    # 위협 메시지
    ctk.CTkLabel(
        frame,
        text=message,
        font=("Pretendard", 28 if level == 2 else 20, "bold"),
        text_color="#FF3333",
        wraplength=600,
    ).pack(pady=(20, 10))

    # 할 일 제목
    ctk.CTkLabel(
        frame,
        text=f'"{task.title}"',
        font=("Pretendard", 18),
        text_color="#FFFFFF",
        wraplength=600,
    ).pack(pady=5)

    # 마감
    ctk.CTkLabel(
        frame,
        text=f"마감: {task.deadline.strftime('%Y-%m-%d %H:%M')}",
        font=("Pretendard", 14),
        text_color="#AAAAAA",
    ).pack(pady=5)

    def _acknowledge():
        db.escalate_threat(task.id)     # 무시할수록 위협 단계 상승
        top.grab_release()
        top.destroy()
        if on_close:
            on_close()

    def _complete():
        top.grab_release()
        top.destroy()
        # 완수 확인은 app_window가 처리
        if on_close:
            on_close(completed=True)

    btn_frame = ctk.CTkFrame(frame, fg_color=bg)
    btn_frame.pack(pady=20)

    ctk.CTkButton(
        btn_frame, text="✅ 완수했다", width=160, height=45,
        fg_color="#00AA55", hover_color="#008844",
        font=("Pretendard", 14, "bold"),
        command=_complete,
    ).pack(side="left", padx=10)

    ctk.CTkButton(
        btn_frame, text="나중에 (위협 강화)", width=180, height=45,
        fg_color="#555555", hover_color="#444444",
        font=("Pretendard", 13),
        command=_acknowledge,
    ).pack(side="left", padx=10)
