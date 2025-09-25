"""Desktop application that fetches and displays trending topics."""

from __future__ import annotations

import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk
from typing import Iterable

from .collectors import BaiduHotSearchCollector
from .models import TrendingTopic
from .ranking import rank_topics


class HotTopicsApp:
    """Tkinter based application to browse realtime hot topics."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("网络热点排行")
        self.root.geometry("860x480")

        self.collector = BaiduHotSearchCollector()
        self._topics: list[TrendingTopic] = []

        self.limit_var = tk.IntVar(value=20)
        self.status_var = tk.StringVar(value="点击“刷新”获取最新话题")
        self.description_var = tk.StringVar(value="")

        self._build_widgets()

    # ------------------------------------------------------------------ UI
    def _build_widgets(self) -> None:
        control_frame = ttk.Frame(self.root, padding=(12, 12))
        control_frame.pack(fill=tk.X)

        ttk.Label(control_frame, text="显示数量：").pack(side=tk.LEFT)
        spinbox = ttk.Spinbox(
            control_frame,
            from_=5,
            to=50,
            increment=5,
            textvariable=self.limit_var,
            width=5,
        )
        spinbox.pack(side=tk.LEFT)

        self.refresh_button = ttk.Button(
            control_frame,
            text="刷新热点",
            command=self.refresh_topics,
        )
        self.refresh_button.pack(side=tk.LEFT, padx=(8, 0))

        ttk.Label(control_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=16)

        table_frame = ttk.Frame(self.root, padding=(12, 0, 12, 0))
        table_frame.pack(fill=tk.BOTH, expand=True)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("rank", "title", "traffic", "source", "url"),
            show="headings",
            height=16,
        )
        self.tree.heading("rank", text="排名")
        self.tree.heading("title", text="话题")
        self.tree.heading("traffic", text="热度")
        self.tree.heading("source", text="来源")
        self.tree.heading("url", text="链接")

        self.tree.column("rank", width=60, anchor=tk.CENTER)
        self.tree.column("title", width=260)
        self.tree.column("traffic", width=100, anchor=tk.CENTER)
        self.tree.column("source", width=140)
        self.tree.column("url", width=240)

        self.tree.tag_configure("even", background="#f6f6f6")
        self.tree.tag_configure("odd", background="white")

        y_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=y_scroll.set, xscroll=x_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<<TreeviewSelect>>", self._on_select_topic)
        self.tree.bind("<Double-1>", self._on_open_link)

        desc_frame = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        desc_frame.pack(fill=tk.X)
        ttk.Label(desc_frame, text="话题简介：").pack(anchor=tk.W)
        self.desc_label = ttk.Label(
            desc_frame,
            textvariable=self.description_var,
            wraplength=820,
            justify=tk.LEFT,
        )
        self.desc_label.pack(fill=tk.X)

    # ---------------------------------------------------------------- events
    def refresh_topics(self) -> None:
        self.refresh_button.state(["disabled"])
        self.status_var.set("正在获取热点...")
        self.description_var.set("")
        thread = threading.Thread(target=self._fetch_topics, daemon=True)
        thread.start()

    def _fetch_topics(self) -> None:
        try:
            limit = max(1, int(self.limit_var.get()))
        except (TypeError, tk.TclError, ValueError):
            limit = 20
        try:
            topics = rank_topics(self.collector.fetch(limit=limit))
        except Exception as exc:  # pragma: no cover - UI feedback
            self.root.after(0, self._handle_error, exc)
        else:
            self.root.after(0, self._update_topic_table, topics)

    def _handle_error(self, exc: Exception) -> None:  # pragma: no cover - UI feedback
        self.status_var.set("获取失败")
        self._topics = []
        self.refresh_button.state(["!disabled"])
        messagebox.showerror("抓取失败", f"无法获取热点数据：{exc}")

    def _update_topic_table(self, topics: Iterable[TrendingTopic]) -> None:
        self._topics = list(topics)
        for item in self.tree.get_children():
            self.tree.delete(item)

        for index, topic in enumerate(self._topics, start=1):
            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(index, topic.title, topic.traffic, topic.source, topic.url or ""),
                tags=("even" if index % 2 == 0 else "odd",),
            )

        self.status_var.set(f"已加载 {len(self._topics)} 条热点")

        if self._topics:
            first_item = self.tree.get_children()
            if first_item:
                self.tree.selection_set(first_item[0])
                self.tree.focus(first_item[0])
                self._on_select_topic()
        else:
            self.description_var.set("")

        self.refresh_button.state(["!disabled"])

    def _on_select_topic(self, event: tk.Event | None = None) -> None:
        selection = self.tree.selection()
        if not selection:
            self.description_var.set("")
            return

        # The iid corresponds to the rank we inserted above.
        item_id = selection[0]
        try:
            index = int(item_id) - 1
        except ValueError:
            self.description_var.set("")
            return

        if not hasattr(self, "_topics") or index >= len(self._topics):
            self.description_var.set("")
            return

        topic = self._topics[index]
        self.description_var.set(topic.description or "暂无简介")

    def _on_open_link(self, event: tk.Event) -> None:  # pragma: no cover - user interaction
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        try:
            index = int(item_id) - 1
        except ValueError:
            return

        if index < 0 or index >= len(self._topics):
            return

        topic = self._topics[index]
        if topic.url:
            webbrowser.open_new_tab(topic.url)


def run() -> None:
    """Start the hot topic application."""

    root = tk.Tk()
    app = HotTopicsApp(root)
    app.refresh_topics()
    root.mainloop()


if __name__ == "__main__":  # pragma: no cover - manual run only
    run()
