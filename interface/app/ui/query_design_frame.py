import tkinter as tk
from tkinter import ttk

from core import settings
# from core.globals import context


class QueryDesignFrame(ttk.LabelFrame):
    def __init__(self, parent, on_generate):
        super().__init__(parent, text="Query Design", padding=12)

        self.on_generate_callback = on_generate

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)

        self._build_widgets()

    def _build_widgets(self):
        hypothesis_frame = ttk.Frame(self)
        hypothesis_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

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

        middle_frame = ttk.Frame(self)
        middle_frame.grid(row=0, column=1, sticky="n", padx=16, pady=16)

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

        queries_frame = ttk.Frame(self)
        queries_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0))

        queries_frame.rowconfigure(0, weight=1)
        queries_frame.columnconfigure(0, weight=1)

        queries_group = ttk.LabelFrame(queries_frame, text="Queries", padding=8)
        queries_group.grid(row=0, column=0, sticky="nsew")

        queries_group.rowconfigure(0, weight=1)
        queries_group.columnconfigure(0, weight=1)

        self.queries_text = tk.Text(queries_group, wrap="word")
        self.queries_text.grid(row=0, column=0, sticky="nsew")

        queries_scrollbar = ttk.Scrollbar(
            queries_group,
            orient="vertical",
            command=self.queries_text.yview
        )
        queries_scrollbar.grid(row=0, column=1, sticky="ns")
        self.queries_text.configure(yscrollcommand=queries_scrollbar.set)

    def _handle_generate(self):
        hypothesis = self.get_hypothesis_text()
        self.on_generate_callback(hypothesis)

    def get_hypothesis_text(self) -> str:
        return self.hypothesis_text.get("1.0", "end").strip()

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

    def set_generate_enabled(self, enabled: bool):
        self.generate_button.config(state="normal" if enabled else "disabled")

    def set_hypothesis_enabled(self, enabled: bool):
        self.hypothesis_text.config(state="normal" if enabled else "disabled")