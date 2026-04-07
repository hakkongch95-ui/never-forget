import customtkinter as ctk
from core.models import Task
from features.countdown import format_countdown, urgency_color, seconds_left


def _card_bg(task: Task) -> str:
    """긴급도에 따라 카드 배경색 결정."""
    from features.countdown import seconds_left
    secs = seconds_left(task)
    if secs <= 0:
        return "#3a0000"   # 초과 — 어두운 빨강
    if secs <= 900:
        return "#2d1500"   # 15분 — 어두운 주황
    if secs <= 3600:
        return "#2a2000"   # 1시간 — 어두운 노랑
    return "#1e1e35"       # 여유 — 기본


class TaskListFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, on_complete=None, on_delete=None, on_edit=None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_complete = on_complete
        self.on_delete = on_delete
        self.on_edit = on_edit
        self._cards: list = []
        self._countdown_labels: list[tuple[ctk.CTkLabel, Task]] = []

    def refresh(self, tasks: list[Task]):
        for card in self._cards:
            card.destroy()
        self._cards.clear()
        self._countdown_labels.clear()

        if not tasks:
            label = ctk.CTkLabel(
                self, text="할 일 없음. 여유롭네.",
                font=("Pretendard", 14), text_color="#666666"
            )
            label.pack(pady=40)
            self._cards.append(label)
            return

        for task in tasks:
            self._add_card(task)

    def tick(self):
        """매초 카운트다운 라벨 + 카드 배경색 갱신 (카드 재생성 없음)."""
        for label, task in self._countdown_labels:
            try:
                label.configure(
                    text=format_countdown(task),
                    text_color=urgency_color(task),
                )
                # 카드 배경색도 갱신
                card = label.master.master  # label → left frame → card
                card.configure(fg_color=_card_bg(task))
            except Exception:
                pass

    def _add_card(self, task: Task):
        color = urgency_color(task)
        bg = _card_bg(task)
        card = ctk.CTkFrame(self, fg_color=bg, corner_radius=10)
        card.pack(fill="x", padx=10, pady=6)
        self._cards.append(card)

        # 긴급도 표시 바 (좌측 세로 선)
        accent = urgency_color(task)
        bar = ctk.CTkFrame(card, width=4, fg_color=accent, corner_radius=2)
        bar.pack(side="left", fill="y", padx=(6, 0), pady=8)

        # 좌측: 제목 + 카운트다운
        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        title_row = ctk.CTkFrame(left, fg_color="transparent")
        title_row.pack(anchor="w", fill="x")

        ctk.CTkLabel(
            title_row, text=task.title,
            font=("Pretendard", 15, "bold"), text_color="#FFFFFF", anchor="w"
        ).pack(side="left")

        # 마감 초과 배지
        if seconds_left(task) <= 0 and task.status == "active":
            ctk.CTkLabel(
                title_row, text=" OVERDUE ",
                font=("Pretendard", 10, "bold"),
                text_color="#FFFFFF", fg_color="#CC0000",
                corner_radius=4,
            ).pack(side="left", padx=(8, 0))

        countdown_label = ctk.CTkLabel(
            left, text=format_countdown(task),
            font=("Pretendard", 13), text_color=color, anchor="w"
        )
        countdown_label.pack(anchor="w")
        self._countdown_labels.append((countdown_label, task))

        if task.description:
            ctk.CTkLabel(
                left, text=task.description,
                font=("Pretendard", 12), text_color="#888888", anchor="w"
            ).pack(anchor="w")

        if task.status == "completed" and task.completed_at:
            ctk.CTkLabel(
                left, text=f"완료: {task.completed_at.strftime('%m/%d %H:%M')}",
                font=("Pretendard", 11), text_color="#555577", anchor="w"
            ).pack(anchor="w")

        # 우측: 버튼
        right = ctk.CTkFrame(card, fg_color="transparent")
        right.pack(side="right", padx=10, pady=10)

        if self.on_complete:
            ctk.CTkButton(
                right, text="완수", width=70, height=30,
                fg_color="#00AA55", hover_color="#008844",
                command=lambda t=task: self.on_complete(t),
            ).pack(pady=2)

        if self.on_edit:
            ctk.CTkButton(
                right, text="수정", width=70, height=30,
                fg_color="#2255AA", hover_color="#1144CC",
                command=lambda t=task: self.on_edit(t),
            ).pack(pady=2)

        if self.on_delete:
            ctk.CTkButton(
                right, text="삭제", width=70, height=30,
                fg_color="#3a3a3a", hover_color="#AA2222",
                command=lambda t=task: self._confirm_delete(t),
            ).pack(pady=2)

    def _confirm_delete(self, task: Task):
        """삭제 확인 다이얼로그."""
        top = ctk.CTkToplevel(self)
        top.title("삭제 확인")
        top.geometry("340x160")
        top.resizable(False, False)
        top.attributes("-topmost", True)
        top.grab_set()

        ctk.CTkLabel(
            top, text=f'"{task.title}" 삭제할게?',
            font=("Pretendard", 14), wraplength=300
        ).pack(pady=(30, 10))

        btn_frame = ctk.CTkFrame(top, fg_color="transparent")
        btn_frame.pack()

        def _yes():
            top.grab_release()
            top.destroy()
            self.on_delete(task)

        ctk.CTkButton(btn_frame, text="삭제", width=100, fg_color="#AA2222",
                      hover_color="#881111", command=_yes).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="취소", width=100, fg_color="#444444",
                      command=lambda: (top.grab_release(), top.destroy())).pack(side="left", padx=10)
