import json
import tkinter as tk
from tkinter import ttk

from core import settings
# from core.globals import context


class HypothesisIngestionFrame(ttk.Frame):
    def __init__(self, parent, on_save):
        super().__init__(parent, padding=12)

        self.on_save = on_save

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  
        self.rowconfigure(1, weight=0)  
        self.rowconfigure(2, weight=0)  
        self.rowconfigure(3, weight=1)  # Hypothesis text area
        self.rowconfigure(4, weight=0) 
        self.rowconfigure(5, weight=1)  # Queries text area
        self.rowconfigure(6, weight=0) 

        self._build_widgets()

    def _build_widgets(self):
        title_label = ttk.Label(self, text="Title")
        title_label.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))

        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(self, textvariable=self.title_var)
        self.title_entry.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 18), ipady=6)

        hypothesis_label = ttk.Label(self, text="Hypothesis")
        hypothesis_label.grid(row=2, column=0, sticky="w", padx=12, pady=(0, 6))

        hypothesis_frame = ttk.Frame(self)
        hypothesis_frame.grid(row=3, column=0, sticky="nsew", padx=12, pady=(0, 18))
        hypothesis_frame.columnconfigure(0, weight=1)
        hypothesis_frame.rowconfigure(0, weight=1)

        self.hypothesis_text = tk.Text(hypothesis_frame, wrap="word")
        self.hypothesis_text.grid(row=0, column=0, sticky="nsew")

        hypothesis_scrollbar = ttk.Scrollbar(
            hypothesis_frame,
            orient="vertical",
            command=self.hypothesis_text.yview
        )
        hypothesis_scrollbar.grid(row=0, column=1, sticky="ns")
        self.hypothesis_text.configure(yscrollcommand=hypothesis_scrollbar.set)

        queries_label = ttk.Label(self, text="Queries")
        queries_label.grid(row=4, column=0, sticky="w", padx=12, pady=(0, 6))

        queries_frame = ttk.Frame(self)
        queries_frame.grid(row=5, column=0, sticky="nsew", padx=12, pady=(0, 18))
        queries_frame.columnconfigure(0, weight=1)
        queries_frame.rowconfigure(0, weight=1)

        self.queries_text = tk.Text(queries_frame, wrap="word")
        self.queries_text.grid(row=0, column=0, sticky="nsew")

        queries_scrollbar = ttk.Scrollbar(
            queries_frame,
            orient="vertical",
            command=self.queries_text.yview
        )
        queries_scrollbar.grid(row=0, column=1, sticky="ns")
        self.queries_text.configure(yscrollcommand=queries_scrollbar.set)

        # Save button
        self.save_button = ttk.Button(
            self,
            text="Save Hypothesis",
            command=self.on_save
        )
        self.save_button.grid(row=6, column=0, sticky="w", padx=12, pady=(0, 12))

    def get_title_text(self) -> str:
        return self.title_var.get().strip()

    def get_hypothesis_text(self) -> str:
        return self.hypothesis_text.get("1.0", "end-1c").strip()

    def get_queries_text(self) -> str:
        return self.queries_text.get("1.0", "end-1c").strip()

    def set_queries_text(self, text: str):
        self.queries_text.config(state="normal")
        self.queries_text.delete("1.0", "end")
        self.queries_text.insert("end", text)
        self.queries_text.see("end")

    def set_queries_list(self, queries):
        self.queries_text.config(state="normal")
        self.queries_text.delete("1.0", "end")

        if isinstance(queries, str):
            self.queries_text.insert("end", queries)
            self.queries_text.see("end")
            return

        for i, query in enumerate(queries, start=1):
            self.queries_text.insert("end", f"{i}. {query}\n\n")

        self.queries_text.see("end")

    def set_hypothesis_enabled(self, enabled: bool):
        self.hypothesis_text.config(state="normal" if enabled else "disabled")

    def set_queries_enabled(self, enabled: bool):
        self.queries_text.config(state="normal" if enabled else "disabled")

    def set_title_enabled(self, enabled: bool):
        self.title_entry.config(state="normal" if enabled else "disabled")

    def set_save_enabled(self, enabled: bool):
        self.save_button.config(state="normal" if enabled else "disabled")