import threading
import time
import json
import requests
import tkinter as tk
from tkinter import ttk

from app.ui.query_design_frame import QueryDesignFrame
from app.ui.results_frame import ResultsFrame
from app.ui.status_bar import StatusBar
from app.services.query_service import generate_queries
from app.services.rag_service import bm25_rag

from core import settings


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Hypothesis-driven analysis of Enron utlizing RAG")
        self.geometry("1150x650")
        self.resizable(False, False)

        self._query_task_running = False
        self._query_start_time = None
        self._query_timer_job = None

        self._rag_task_running = False
        self._rag_start_time = None
        self._rag_timer_job = None

        self._build_layout()

        if not settings.DEBUG:
            self._load_models()

    def _build_layout(self):
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.query_frame = QueryDesignFrame(
            self,
            on_generate=self.handle_generate,
        )
        self.query_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=(12, 6))

        self.results_frame = ResultsFrame(
            self,
            on_rag=self.handle_rag,
            # on_show=self.handle_show,
            on_extract=self.handle_extract,
        )
        self.results_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=6)

        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))

    # =========================================================
    # QUERY GENERATION
    # =========================================================
    def handle_generate(self, hypothesis: str):
        if self._query_task_running:
            return

        if not hypothesis.strip():
            self.query_frame.set_queries_text("Please enter a hypothesis first.")
            self.status_bar.set_status("No hypothesis entered")
            return

        self._query_task_running = True
        self._query_start_time = time.time()

        self.query_frame.set_generate_enabled(False)
        self.query_frame.set_hypothesis_enabled(False)
        self.query_frame.set_queries_text("Generating queries...\nPlease wait.")

        self._update_query_elapsed_time()

        thread = threading.Thread(
            target=self._run_generate_background,
            args=(hypothesis,),
            daemon=True,
        )
        thread.start()

    def _run_generate_background(self, hypothesis: str):
        try:
            queries = generate_queries(hypothesis)
            self.after(0, self._on_generate_finished, queries)
        except Exception as exc:
            self.after(0, self._on_generate_failed, str(exc))

    def _on_generate_finished(self, queries):
        self._query_task_running = False

        if self._query_timer_job is not None:
            self.after_cancel(self._query_timer_job)
            self._query_timer_job = None

        self.query_frame.set_queries_list(queries)
        self.query_frame.set_generate_enabled(True)
        self.query_frame.set_hypothesis_enabled(True)

        elapsed = int(time.time() - self._query_start_time)
        self.status_bar.set_status(f"Queries generated in {self._format_seconds(elapsed)}")

        self._query_start_time = None

    def _on_generate_failed(self, error_message: str):
        self._query_task_running = False

        if self._query_timer_job is not None:
            self.after_cancel(self._query_timer_job)
            self._query_timer_job = None

        self.query_frame.set_queries_text(f"Query generation failed:\n{error_message}")
        self.query_frame.set_generate_enabled(True)
        self.query_frame.set_hypothesis_enabled(True)
        self.status_bar.set_status("Query generation failed")

        self._query_start_time = None

    def _update_query_elapsed_time(self):
        if not self._query_task_running or self._query_start_time is None:
            return

        elapsed = int(time.time() - self._query_start_time)
        self.status_bar.set_status(f"Generating queries... elapsed: {self._format_seconds(elapsed)}")

        self._query_timer_job = self.after(1000, self._update_query_elapsed_time)

    # =========================================================
    # RAG
    # =========================================================
    def handle_rag(self):
        if self._rag_task_running:
            return

        self._rag_task_running = True
        self._rag_start_time = time.time()

        self.results_frame.set_controls_enabled(False)
        self.results_frame.set_results_enabled(False)

        self._update_rag_elapsed_time()

        thread = threading.Thread(target=self._run_rag_background, daemon=True)
        thread.start()

    def _run_rag_background(self):
        try:
            hypothesis = self.query_frame.hypothesis_text.get("1.0", "end-1c").strip()
            queries = json.loads(self.query_frame.queries_text.get("1.0", "end-1c").strip())
            results = bm25_rag(
                    hypothesis=hypothesis, 
                    queris=queries,
                    top_k=settings.PER_QUERY_TOP_K
                    )
            self.after(0, self._on_rag_finished, results)
        except Exception as exc:
            self.after(0, self._on_rag_failed, str(exc))

    def _on_rag_finished(self, results):
        self._rag_task_running = False

        if self._rag_timer_job is not None:
            self.after_cancel(self._rag_timer_job)
            self._rag_timer_job = None

        self.results_frame.set_results_list(results)
        self.results_frame.set_results_enabled(True)
        self.results_frame.set_controls_enabled(True)

        elapsed = int(time.time() - self._rag_start_time)
        self.status_bar.set_status(f"Results retrieved in {self._format_seconds(elapsed)}")

        self._rag_start_time = None

    def _on_rag_failed(self, error_message: str):
        self._rag_task_running = False

        if self._rag_timer_job is not None:
            self.after_cancel(self._rag_timer_job)
            self._rag_timer_job = None

        self.results_frame.set_results_enabled(True)
        self.results_frame.set_controls_enabled(True)
        self.results_frame.set_results_list([f"RAG failed: {error_message}"])
        self.status_bar.set_status("RAG failed")

        self._rag_start_time = None

    def _update_rag_elapsed_time(self):
        if not self._rag_task_running or self._rag_start_time is None:
            return

        elapsed = int(time.time() - self._rag_start_time)
        self.status_bar.set_status(f"Processing... elapsed: {self._format_seconds(elapsed)}")

        self._rag_timer_job = self.after(1000, self._update_rag_elapsed_time)

    # =========================================================
    # LOAD MODELS
    # =========================================================
    def _load_models(self):
        thread = threading.Thread(target=self._fetch_dropdown_values, daemon=True)
        thread.start()
    
    def _fetch_dropdown_values(self):
        """
        Fetch available models from the server and update the settings.ALL_MODELS list
        """
        try:
            r = requests.get(settings.TAG_URL, timeout=30)
            r.raise_for_status()
            data = r.json()
            models = [m["name"] for m in data.get("models", [])]

            self.after(0, self._update_settings, models)

        except Exception as e:
            print(f"Error fetching models: {e}")

    def _update_settings(self, models):
        settings.ALL_MODELS = models
        # self.combo["values"] = values
        # if values:
        #     self.combo.current(0)
        # self.status.config(text="Loaded")
        # self.load_button.config(state="normal")

    # =========================================================
    # OTHER ACTIONS
    # =========================================================
    # def handle_show(self):
    #     self.results_frame.append_result("Show button pressed: placeholder function executed.")
    #     self.status_bar.set_status("Show action executed")

    def handle_extract(self):
        self.results_frame.append_result("Extract button pressed: placeholder function executed.")
        self.status_bar.set_status("Extract action executed")

    # =========================================================
    # UTILS
    # =========================================================
    @staticmethod
    def _format_seconds(total_seconds: int) -> str:
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"