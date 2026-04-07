import customtkinter as ctk
from core.models import Task
from features.countdown import format_countdown, urgency_color
import core.database as db


class TaskListFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, on_complete=None, on_delete=None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_complete = on_complete
        self.on_delete = on_delete
        self._cards: list[ctk.CTkFrame] = []

    def refresh(self, tasks: list[Task]):
        for card in self._cards:
            card.destroy()
        self._cards.clear()

        if not tasks:
            ctk.CTkLabel(
                self, text="할 일 없음. 여유롭네.",
                font=("Pretendard", 14), text_color="#666666"
            ).pack(pady=40)
            return

        for task in tasks:
            self._add_card(task)

    def _add_card(self, task: Task):
        color = urgency_color(task)
        card = ctk.CTkFrame(self, fg_color="#2a2a3e", corner_radius=10)
        card.pack(fill="x", padx=10, pady=6)
        self._cards.append(card)

        # 좌측: 제목 + 카운트다운
        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=14, pady=10)

        ctk.CTkLabel(
            left, text=task.title,
            font=("Pretendard", 15, "bold"), text_color="#FFFFFF", anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            left, text=format_countdown(task),
            font=("Pretendard", 13), text_color=color, anchor="w"
        ).pack(anchor="w")

        if task.description:
            ctk.CTkLabel(
                left, text=task.description,
                font=("Pretendard", 12), text_color="#888888", anchor="w"
            ).pack(anchor="w")

        # 우측: 버튼
        right = ctk.CTkFrame(card, fg_color="transparent")
        right.pack(side="right", padx=10, pady=10)

        ctk.CTkButton(
            right, text="완수", width=70, height=32,
            fg_color="#00AA55", hover_color="#008844",
            command=lambda t=task: self.on_complete and self.on_complete(t),
        ).pack(pady=2)

        ctk.CTkButton(
            right, text="삭제", width=70, height=32,
            fg_color="#AA2222", hover_color="#881111",
            command=lambda t=task: self.on_delete and self.on_delete(t),
        ).pack(pady=2)
