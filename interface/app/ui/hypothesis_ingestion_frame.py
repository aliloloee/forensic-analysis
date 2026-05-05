import json
import tkinter as tk
from tkinter import ttk

from core import settings
from app.services.hypothesis_service import get_hypothesis
# from core.globals import context



class HypothesisIngestionFrame(ttk.LabelFrame):
    def __init__(self, parent, on_generate, on_save):
        super().__init__(parent, text="Query Design", padding=12)

        self.on_generate_callback = on_generate
        self.on_save = on_save

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        self._build_widgets()

    def _build_widgets(self):
        # Title Label and Entry in Row 0
        title_frame = ttk.Frame(self)
        title_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        title_frame.columnconfigure(0, weight=1)

        title_label = ttk.Label(title_frame, text="Title")
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(title_frame, textvariable=self.title_var)
        self.title_entry.grid(row=1, column=0, sticky="ew")

        # Hypothesis Frame in Row 1, Column 0
        hypothesis_frame = ttk.Frame(self)
        hypothesis_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

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

        # Middle Frame in Row 1, Column 1
        middle_frame = ttk.Frame(self)
        middle_frame.grid(row=1, column=1, sticky="n", padx=16, pady=16)

        # Generate button
        self.generate_button = ttk.Button(
            middle_frame,
            text="Generate Queries",
            command=self._handle_generate
        )
        self.generate_button.pack(pady=(0, 20), fill="x")

        # Label above dropdown
        model_label = ttk.Label(middle_frame, text="Model selection")
        model_label.pack(anchor="w", pady=(0, 4))

        self.model_dropdown_value = tk.StringVar()

        self.model_dropdown = ttk.Combobox(
            middle_frame,
            textvariable=self.model_dropdown_value,
            state="readonly",
            width=40   # increase this if needed
        )
        self.model_dropdown.pack(fill="x")
        self.model_dropdown.set(settings.HE_MODEL)

        def _refresh_dropdown(event=None):
            self.model_dropdown["values"] = settings.ALL_MODELS

            if self.model_dropdown_value.get() not in settings.ALL_MODELS:
                self.model_dropdown_value.set(settings.HE_MODEL)

        def _on_model_changed(event):
            selected_model = self.model_dropdown_value.get()
            settings.HE_MODEL = selected_model
            # print("Selected model:", selected_model)
            # context.add(settings.HYPOTHESIS_EXPANSION_MODEL_KEY, selected_model)

        self.model_dropdown.bind("<Button-1>", _refresh_dropdown)
        self.model_dropdown.bind("<FocusIn>", _refresh_dropdown)
        self.model_dropdown.bind("<<ComboboxSelected>>", _on_model_changed)

        # Number of Queries
        num_queries_label = ttk.Label(middle_frame, text="Number of Queries")
        num_queries_label.pack(anchor="w", pady=(10, 4))

        self.num_queries_value = tk.StringVar()
        self.num_queries_value.set(str(settings.HE_QUERIES))  # Default value
        self.num_queries_entry = ttk.Entry(middle_frame, textvariable=self.num_queries_value)
        self.num_queries_entry.pack(fill="x")

        # Queries Frame
        queries_frame = ttk.Frame(self)
        queries_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=(0, 0), pady=(10, 0))

        queries_frame.rowconfigure(0, weight=1)
        queries_frame.columnconfigure(0, weight=1)
        queries_frame.columnconfigure(1, weight=1)

        # Sparse Queries
        sparse_queries_group = ttk.LabelFrame(queries_frame, text="Sparse Queries", padding=8)
        sparse_queries_group.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

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

        # Dense Queries
        dense_queries_group = ttk.LabelFrame(queries_frame, text="Dense Queries", padding=8)
        dense_queries_group.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

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

        # Save Button Frame
        save_button_frame = ttk.Frame(self)
        save_button_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=(0, 0), pady=(10, 0))

        save_button_frame.columnconfigure(0, weight=1)
        self.save_button = ttk.Button(
            save_button_frame,
            text="Save Hypothesis",
            command=self.on_save
        )
        self.save_button.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 0))

    def _handle_generate(self):
        hypothesis  = self.get_hypothesis_text()
        num_queries = self.num_queries_value.get().strip()
        model       = self.model_dropdown_value.get().strip()
        self.on_generate_callback(hypothesis, num_queries, model)

    def get_hypothesis_text(self) -> str:
        return self.hypothesis_text.get("1.0", "end").strip()
    
    def get_title_text(self) -> str:
        return self.title_var.get().strip()
    
    def get_sparse_queries_text(self) -> str:
        return self.sparse_queries_text.get("1.0", "end").strip()
    
    def get_dense_queries_text(self) -> str:
        return self.dense_queries_text.get("1.0", "end").strip()

    def set_queries_text(self, text: str):
        self.sparse_queries_text.config(state="normal")
        self.sparse_queries_text.delete("1.0", "end")
        self.sparse_queries_text.insert("end", text)
        self.sparse_queries_text.see("end")

        self.dense_queries_text.config(state="normal")
        self.dense_queries_text.delete("1.0", "end")
        self.dense_queries_text.insert("end", text)
        self.dense_queries_text.see("end")

    def set_queries_list(self, queries):
        self.sparse_queries_text.config(state="normal")
        self.sparse_queries_text.delete("1.0", "end")

        self.dense_queries_text.config(state="normal")
        self.dense_queries_text.delete("1.0", "end")

        if isinstance(queries, str):
            self.sparse_queries_text.insert("end", queries)
            self.sparse_queries_text.see("end")
            self.dense_queries_text.insert("end", queries)
            self.dense_queries_text.see("end")
            return

        for i, query in enumerate(queries, start=1):
            self.sparse_queries_text.insert("end", f"{i}. {query}\n\n")
            self.dense_queries_text.insert("end", f"{i}. {query}\n\n")

        self.sparse_queries_text.see("end")
        self.dense_queries_text.see("end")

    def set_queries_enabled(self, enabled: bool):
        self.sparse_queries_text.config(state="normal" if enabled else "disabled")
        self.dense_queries_text.config(state="normal" if enabled else "disabled")

    def set_generate_enabled(self, enabled: bool):
        self.generate_button.config(state="normal" if enabled else "disabled")

    def set_hypothesis_enabled(self, enabled: bool):
        self.hypothesis_text.config(state="normal" if enabled else "disabled")

    def set_hhh_enabled(self, enabled: bool):
        self.hhh_entry.config(state="normal" if enabled else "disabled")