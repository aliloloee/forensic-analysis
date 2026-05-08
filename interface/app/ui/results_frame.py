import tkinter as tk
from tkinter import ttk

from core import settings
# from core.globals import context


class ResultsFrame(ttk.LabelFrame):
    def __init__(self, parent, on_retrieve_bm25, on_retrieve_dense, on_retrieve_hybrid, on_generate):
        super().__init__(parent, text="Retrieve and Generate", padding=12)

        self.on_rag_bm25 = on_retrieve_bm25
        self.on_rag_dense = on_retrieve_dense
        self.on_rag_hybrid = on_retrieve_hybrid
        self.on_rag_generate = on_generate

        # Row 0: dropdown
        # Row 1: main content
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        self._build_widgets()

    def _build_widgets(self):
        # =====================================
        # Top dropdown row
        # =====================================
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # The Model Selection Dropdown
        ttk.Label(top_frame, text="Model Selection:").grid(
            row=0, column=0, sticky="w", padx=(0, 4)
        )

        self._dropdown_value = tk.StringVar()
        self._dropdown = ttk.Combobox(
            top_frame,
            textvariable=self._dropdown_value,
            state="readonly",
            width=40,
        )
        def _refresh_dropdown(event=None):
            self._dropdown["values"] = settings.ALL_MODELS

            if self._dropdown_value.get() not in settings.ALL_MODELS:
                self._dropdown_value.set(settings.CG_MODEL)

        def _on_model_changed(event):
            selected_model = self._dropdown_value.get()
            settings.CG_MODEL = selected_model
            # print("Selected model:", selected_model)
            # context.add(settings.HYPOTHESIS_EXPANSION_MODEL_KEY, selected_model)

        self._dropdown.set(settings.CG_MODEL)

        self._dropdown.bind("<Button-1>", _refresh_dropdown)
        self._dropdown.bind("<FocusIn>", _refresh_dropdown)
        self._dropdown.bind("<<ComboboxSelected>>", _on_model_changed)

        self._dropdown.grid(row=0, column=1, sticky="w")

        # Top number of chunks Entry
        ttk.Label(top_frame, text="Number of chunks to retrieve:").grid(
            row=0, column=2, sticky="w", padx=(10, 4)
        )
        self._chunks_entry_value = tk.StringVar(value=str(settings.TOP_K_CHUNKS))
        self._chunks_entry_value.default_value = str(settings.TOP_K_CHUNKS)  # Store default value as an attribute
        self._chunks_entry = ttk.Entry(top_frame, width=15, textvariable=self._chunks_entry_value)
        self._chunks_entry.grid(row=0, column=3, sticky="w")
        # =====================================
        # Left side
        # =====================================
        left_frame = ttk.Frame(self)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)

        # BM25 Group
        bm25_group = ttk.LabelFrame(left_frame, text="BM25")
        bm25_group.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        buttons_frame = ttk.Frame(bm25_group)
        buttons_frame.grid(row=1, column=0, sticky="nw")

        self.retrieve_button_bm25 = ttk.Button(buttons_frame, text="Retrieve and Union", command=self.on_rag_bm25)
        self.generate_button_bm25 = ttk.Button(
            buttons_frame,
            text="Generate Inference for BM25 Chunks",
            command=lambda: self.on_rag_generate(method="BM25")
            )
        self.generate_button_bm25.config(state="disabled") # Initially disabled

        self.retrieve_button_bm25.grid(row=0, column=0, padx=(10, 10), pady=5)
        self.generate_button_bm25.grid(row=0, column=1, pady=5)

        # Dense Group
        dense_group = ttk.LabelFrame(left_frame, text="Dense")
        dense_group.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        buttons_frame_dense = ttk.Frame(dense_group)
        buttons_frame_dense.grid(row=1, column=0, sticky="nw")

        self.rag_button_dense = ttk.Button(buttons_frame_dense, text="Retrieve and Union", command=self.on_rag_dense)
        self.generate_button_dense = ttk.Button(
            buttons_frame_dense,
            text="Generate Inference for Dense Chunks",
            command=lambda: self.on_rag_generate(method="Dense")
            )
        self.generate_button_dense.config(state="disabled") # Initially disabled

        self.rag_button_dense.grid(row=0, column=0, padx=(10, 10), pady=5)
        self.generate_button_dense.grid(row=0, column=1, pady=5)

        # Hybrid Group
        hybrid_group = ttk.LabelFrame(left_frame, text="Hybrid")
        hybrid_group.grid(row=2, column=0, sticky="ew")

        buttons_frame_hybrid = ttk.Frame(hybrid_group)
        buttons_frame_hybrid.grid(row=1, column=0, sticky="nw")

        self.rag_button_hybrid = ttk.Button(buttons_frame_hybrid, text="Retrieve and Union", command=self.on_rag_hybrid)
        self.generate_button_hybrid = ttk.Button(
            buttons_frame_hybrid,
            text="Generate Inference for Hybrid Chunks",
            command=lambda: self.on_rag_generate(method="Hybrid")
            )
        self.generate_button_hybrid.config(state="disabled") # Initially disabled

        self.rag_button_hybrid.grid(row=0, column=0, padx=(10, 10), pady=5)
        self.generate_button_hybrid.grid(row=0, column=1, pady=5)
        # =====================================
        # Right side
        # =====================================
        right_frame = ttk.Frame(self)
        right_frame.grid(row=1, column=1, sticky="nsew")

        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        results_group = ttk.LabelFrame(right_frame, text="Results", padding=8)
        results_group.grid(row=0, column=0, sticky="nsew")

        results_group.rowconfigure(0, weight=1)
        results_group.columnconfigure(0, weight=1)

        self.results_text = tk.Text(results_group, wrap="word")
        self.results_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            results_group,
            orient="vertical",
            command=self.results_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.results_text.configure(yscrollcommand=scrollbar.set)

        self.results_text.insert("end", "Text results will appear here.\n")

    def get_selected_method(self) -> str:
        return self.selected_method.get()
    
    def get_top_k_chunks_number(self):
        return int(self._chunks_entry_value.get())

    def set_results_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.results_text.config(state=state)

    def append_result(self, text: str):
        self.results_text.config(state="normal")
        self.results_text.insert("end", text + "\n")
        self.results_text.see("end")

    def clear_results(self):
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")

    def set_results_header(self, method):
        self.clear_results()
        self.results_text.insert("end", f"Inference Results for {method} Retrieved Chunks")

    def set_results_list(self, result, index):
        self.results_text.insert("end", "\n" + ("—" * 60) + "\n\n")
        self._render_single_result(index, result)
        # self.results_text.see("1.0") # Stay at top
        self.results_text.see("end") # Go to the end after each result

    def _render_single_result(self, index, item):
        label = item.get("label")
        json_valid = item.get("json_valid", False)
        reason = item.get("reason")
        evidence_spans = item.get("evidence_spans", [])
        raw_response = item.get("raw_response", "")
        email_id = item.get(settings.EMAIL_ID)
        chunk_index = item.get(settings.CHUNK_INDEX)

        # Optional header per result
        self.results_text.insert("end", f"Result {index}", ("field_name",))
        if email_id is not None:
            self.results_text.insert("end", f" (email_id={email_id})")
        if chunk_index is not None:
            self.results_text.insert("end", f" (chunk_index={chunk_index})")
        self.results_text.insert("end", "\n\n")

        if label is not None and json_valid:
            self._insert_field("Label", str(label))
            self._insert_field("Reason", str(reason) if reason is not None else "")

            self.results_text.insert("end", "Evidence spans: ", ("field_name",))

            if evidence_spans:
                self.results_text.insert("end", "\n")
                for span in evidence_spans:
                    self.results_text.insert("end", "  • ", ())
                    self.results_text.insert("end", str(span) + "\n", ("evidence_item",))
            else:
                self.results_text.insert("end", "[]\n")

        else:
            self._insert_field("Raw response", str(raw_response) if raw_response is not None else "")

    def _insert_field(self, field_name, value):
        self.results_text.insert("end", f"{field_name}: ", ("field_name",))
        self.results_text.insert("end", f"{value}\n")