import json

import tkinter as tk
from tkinter import ttk

from core import settings
from app.services.hypothesis_service import get_hypothesis
# from core.globals import context


class QueryDesignFrame(ttk.LabelFrame):
    def __init__(self, parent, on_generate):
        super().__init__(parent, text="Query Design", padding=12)

        self.on_generate_callback = on_generate

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self._build_widgets()

    def _build_widgets(self):
        # Row 0: Hypothesis Selection Dropdown
        hypothesis_selection_frame = ttk.Frame(self)
        hypothesis_selection_frame.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        hypothesis_selection_frame.columnconfigure(0, weight=0)
        
        hypothesis_label = ttk.Label(hypothesis_selection_frame, text="Hypothesis selection")
        hypothesis_label.pack(anchor="w", pady=(0, 4))
        
        self.hypothesis_dropdown_value = tk.StringVar()
        self.hypothesis_dropdown = ttk.Combobox(
            hypothesis_selection_frame,
            textvariable=self.hypothesis_dropdown_value,
            state="readonly",
            width=35
        )
        self.hypothesis_dropdown.pack()
        self.hypothesis_dropdown.set("Select:")

        def _refresh_hypothesis_dropdown(event=None):
            self.hypothesis_dropdown["values"] = list(settings.ALL_HYPOTHESES.keys())

        def _on_hypothesis_changed(event):
            selected_hypothesis = self.hypothesis_dropdown_value.get()
            selected_id = settings.ALL_HYPOTHESES[selected_hypothesis]
            hypothesis = get_hypothesis(uuid=selected_id)

            self.hypothesis_text.delete("1.0", "end")
            self.hypothesis_text.insert("end", hypothesis['hypothesis'])

            self.sparse_queries_text.delete("1.0", "end")
            self.dense_queries_text.delete("1.0", "end")
            
            # Display queries in JSON format
            sparse_queries_json = json.dumps(hypothesis['sparse_queries'], indent=2)
            self.sparse_queries_text.insert("end", sparse_queries_json)

            dense_queries_json = json.dumps(hypothesis['dense_queries'], indent=2)
            self.dense_queries_text.insert("end", dense_queries_json)

        self.hypothesis_dropdown.bind("<Button-1>", _refresh_hypothesis_dropdown)
        self.hypothesis_dropdown.bind("<FocusIn>", _refresh_hypothesis_dropdown)
        self.hypothesis_dropdown.bind("<<ComboboxSelected>>", _on_hypothesis_changed)

        # Row 1, Column 0: Hypothesis Text
        hypothesis_frame = ttk.Frame(self)
        hypothesis_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        hypothesis_frame.rowconfigure(0, weight=1)
        hypothesis_frame.columnconfigure(0, weight=1)

        hypothesis_group = ttk.LabelFrame(hypothesis_frame, text="Hypothesis", padding=8)
        hypothesis_group.grid(row=0, column=0, sticky="nsew")

        hypothesis_group.rowconfigure(0, weight=1)
        hypothesis_group.columnconfigure(0, weight=1)

        self.hypothesis_text = tk.Text(hypothesis_group, wrap="word")
        self.hypothesis_text.grid(row=0, column=0, sticky="nsew")

        hypothesis_scrollbar = ttk.Scrollbar(
            hypothesis_group,
            orient="vertical",
            command=self.hypothesis_text.yview
        )
        hypothesis_scrollbar.grid(row=0, column=1, sticky="ns")
        self.hypothesis_text.configure(yscrollcommand=hypothesis_scrollbar.set)

        # Row 1, Column 1: Sparse Queries Text
        sparse_queries_frame = ttk.Frame(self)
        sparse_queries_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 5))

        sparse_queries_frame.rowconfigure(0, weight=1)
        sparse_queries_frame.columnconfigure(0, weight=1)

        sparse_queries_group = ttk.LabelFrame(sparse_queries_frame, text="Sparse Queries", padding=8)
        sparse_queries_group.grid(row=0, column=0, sticky="nsew")

        sparse_queries_group.rowconfigure(0, weight=1)
        sparse_queries_group.columnconfigure(0, weight=1)

        self.sparse_queries_text = tk.Text(sparse_queries_group, wrap="word")
        self.sparse_queries_text.grid(row=0, column=0, sticky="nsew")

        sparse_queries_scrollbar = ttk.Scrollbar(
            sparse_queries_group,
            orient="vertical",
            command=self.sparse_queries_text.yview
        )
        sparse_queries_scrollbar.grid(row=0, column=1, sticky="ns")
        self.sparse_queries_text.configure(yscrollcommand=sparse_queries_scrollbar.set)

        # Row 1, Column 2: Dense Queries Text
        dense_queries_frame = ttk.Frame(self)
        dense_queries_frame.grid(row=1, column=2, sticky="nsew", padx=(5, 0))

        dense_queries_frame.rowconfigure(0, weight=1)
        dense_queries_frame.columnconfigure(0, weight=1)

        dense_queries_group = ttk.LabelFrame(dense_queries_frame, text="Dense Queries", padding=8)
        dense_queries_group.grid(row=0, column=0, sticky="nsew")

        dense_queries_group.rowconfigure(0, weight=1)
        dense_queries_group.columnconfigure(0, weight=1)

        self.dense_queries_text = tk.Text(dense_queries_group, wrap="word")
        self.dense_queries_text.grid(row=0, column=0, sticky="nsew")

        dense_queries_scrollbar = ttk.Scrollbar(
            dense_queries_group,
            orient="vertical",
            command=self.dense_queries_text.yview
        )
        dense_queries_scrollbar.grid(row=0, column=1, sticky="ns")
        self.dense_queries_text.configure(yscrollcommand=dense_queries_scrollbar.set)

    def get_hypothesis_text(self) -> str:
        return self.hypothesis_text.get("1.0", "end").strip()

    def set_sparse_queries(self, queries):
        self.sparse_queries_text.config(state="normal")
        self.sparse_queries_text.delete("1.0", "end")

        if isinstance(queries, str):
            self.sparse_queries_text.insert("end", queries)
        else:
            for i, query in enumerate(queries, start=1):
                self.sparse_queries_text.insert("end", f"{i}. {query}\n\n")

        self.sparse_queries_text.see("end")

    def set_dense_queries(self, queries):
        self.dense_queries_text.config(state="normal")
        self.dense_queries_text.delete("1.0", "end")

        if isinstance(queries, str):
            self.dense_queries_text.insert("end", queries)
        else:
            for i, query in enumerate(queries, start=1):
                self.dense_queries_text.insert("end", f"{i}. {query}\n\n")

        self.dense_queries_text.see("end")

    def set_generate_enabled(self, enabled: bool):
        self.generate_button.config(state="normal" if enabled else "disabled")

    def set_hypothesis_enabled(self, enabled: bool):
        self.hypothesis_text.config(state="normal" if enabled else "disabled")