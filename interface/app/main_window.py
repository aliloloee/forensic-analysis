import threading
import time
import json
import requests
import tkinter as tk
from tkinter import ttk

import pandas as pd
import numpy as np
import json

from app.ui.query_design_frame import QueryDesignFrame
from app.ui.results_frame import ResultsFrame
from app.ui.status_bar import StatusBar
from app.ui.hypothesis_ingestion_frame import HypothesisIngestionFrame
from app.ui.data_ingestion_frame import DataIngestionFrame
from app.services.query_service import generate_queries
from app.services.retrieve_service import bm25_retrieve, dense_retrieve
from app.services.hypothesis_service import add_hypothesis
from app.services.hypothesis_service import get_all_hypotheses
from app.services.data_service import ingest_data

from core import settings
from core.globals import context

from retrieval.hybrid import rrf_hybrid
from generation.chunk_analysis import process_chunk, build_prompt

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

        self._load_hypotheses()

    def _build_layout(self):
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.columnconfigure(0, weight=1)

        # Top tab bar
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=12, pady=(12, 0))

        # Tabs
        self.home_tab = ttk.Frame(self.notebook)
        self.database_tab = ttk.Frame(self.notebook)
        self.hypothesis_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.home_tab, text="Home")
        self.notebook.add(self.database_tab, text="Database")
        self.notebook.add(self.hypothesis_tab, text="Hypothesis")
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # Make Home tab expandable
        self.home_tab.rowconfigure(0, weight=1)
        self.home_tab.rowconfigure(1, weight=1)
        self.home_tab.columnconfigure(0, weight=1)

        # Put your current Home content inside home_tab instead of self
        self.query_frame = QueryDesignFrame(
            self.home_tab,
            on_generate=self.handle_generate,
        )
        self.query_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=(12, 6))

        self.results_frame = ResultsFrame(
            self.home_tab,
            on_retrieve_bm25=self.handle_retrieve_bm25,
            on_retrieve_dense=self.handle_retrieve_dense,
            on_retrieve_hybrid=self.handle_retrieve_hybrid,
            on_generate=self.handle_generate_inference
        )
        self.results_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=6)

        # Status bar stays below tabs
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=1, column=0, sticky="ew", padx=12, pady=(6, 12))

        # Make Hypothesis tab expandable
        self.hypothesis_tab.rowconfigure(0, weight=1)
        self.hypothesis_tab.columnconfigure(0, weight=1)

        # Optional placeholder content for Hypothesis tab
        self.hypothesis_ingestion_frame = HypothesisIngestionFrame(
            self.hypothesis_tab,
            on_generate=self.handle_generate,
            on_save=self.handle_hypothesis_saving,
        )
        self.hypothesis_ingestion_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=(12, 6))

        # ttk.Label(self.hypothesis_tab, text="Hypothesis tab content goes here").pack(
        #     padx=20, pady=20, anchor="nw"
        # )


        # Make Database tab expandable
        self.database_tab.rowconfigure(0, weight=1)
        self.database_tab.columnconfigure(0, weight=1)

        # Optional placeholder content for Hypothesis tab
        self.data_ingestion_frame = DataIngestionFrame(
            self.database_tab,
            on_save=self.handle_data_ingestion,
        )
        self.data_ingestion_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=(12, 6))

    # =========================================================
    # TAB CHANGING
    # =========================================================
    def _on_tab_changed(self, event):
        # self.update_idletasks()
        # self.geometry("")
        selected_tab = event.widget.tab(event.widget.select(), "text")

        if selected_tab in ["Home", "Hypothesis"]:
            self.geometry("1150x650")

        elif selected_tab == "Database":
            self.geometry("550x650")

    # =========================================================
    # SAVE HYPOTHESIS
    # =========================================================
    def handle_hypothesis_saving(self):
        title = self.hypothesis_ingestion_frame.get_title_text()
        hypothesis = self.hypothesis_ingestion_frame.get_hypothesis_text()
        sparse_queries_raw = self.hypothesis_ingestion_frame.get_sparse_queries_text()
        dense_queries_raw = self.hypothesis_ingestion_frame.get_dense_queries_text()

        if not title or not hypothesis:
            self.status_bar.set_status(f"Title or Hypothesis can not be Empty.")
            return

        try:
            sparse_queries = json.loads(sparse_queries_raw)
            if not isinstance(sparse_queries, list):
                self.status_bar.set_status(f"Sparse queries must be a valid JSON list. Example:['query 1', 'query 2']")
                return
            
            dense_queries = json.loads(dense_queries_raw)
            if not isinstance(dense_queries, list):
                self.status_bar.set_status(f"Dense queries must be a valid JSON list. Example:['query 1', 'query 2']")
                return

        except Exception:
            self.status_bar.set_status(f"Queries must be a valid JSON list. Example:['query 1', 'query 2']")
            return
        
        add_hypothesis (title, hypothesis, sparse_queries, dense_queries)
        self.status_bar.set_status(f"Hypothesis added successfully.")

    # =========================================================
    # DATA INGESTION
    # =========================================================
    def handle_data_ingestion(self):
        emails_file = self.data_ingestion_frame.emails_file
        chunks_file = self.data_ingestion_frame.chunks_file
        embedding1_file = self.data_ingestion_frame.embedding1_file
        embedding2_file = self.data_ingestion_frame.embedding2_file

        # Check if all files are selected
        if not all([emails_file, chunks_file, embedding1_file]):
            self.status_bar.set_status("Please select all files before adding to database.")
            return

        try:
            emails_data = pd.read_csv(emails_file)
            chunks_data = pd.read_csv(chunks_file)
            embedding1_data = np.load(embedding1_file)
            if embedding2_file:
                embedding2_data = np.load(embedding2_file)

            self.status_bar.set_status("Files read successfully. Ready to add to database.")

        except Exception as e:
            self.status_bar.set_status(f"Error reading files: {str(e)}")

        ingest_data(emails_data, chunks_data, embedding1_data, embedding2_data if embedding2_file else None)
        self.status_bar.set_status("Data ingestion process completed. Check console for details.")

    # =========================================================
    # QUERY GENERATION
    # =========================================================
    def handle_generate(self, hypothesis: str, num_queries: str, model: str = settings.HE_MODEL):
        if self._query_task_running:
            return

        if not hypothesis.strip():
            self.hypothesis_ingestion_frame.set_queries_text("Please enter a hypothesis first.")
            self.status_bar.set_status("No hypothesis entered")
            return

        self._query_task_running = True
        self._query_start_time = time.time()

        self.hypothesis_ingestion_frame.set_generate_enabled(False)
        self.hypothesis_ingestion_frame.set_hypothesis_enabled(False)
        self.hypothesis_ingestion_frame.set_queries_text("Generating queries...\nPlease wait.")

        self._update_query_elapsed_time()

        thread = threading.Thread(
            target=self._run_generate_background,
            args=(hypothesis, num_queries, model),
            daemon=True,
        )
        thread.start()

    def _run_generate_background(self, hypothesis: str, num_queries: str, model: str = settings.HE_MODEL):
        try:
            queries = generate_queries(hypothesis, num_queries, model, template_path=settings.HE_PROMPT_TEMPLATE_SPARSE)
            self.after(0, self._on_sparse_generate_finished, queries)
        except Exception as exc:
            self.after(0, self._on_generate_failed, str(exc))

        try:
            queries = generate_queries(hypothesis, num_queries, model, template_path=settings.HE_PROMPT_TEMPLATE_DENSE)
            self.after(0, self._on_dense_generate_finished, queries)
        except Exception as exc:
            self.after(0, self._on_generate_failed, str(exc))

    def _on_sparse_generate_finished(self, queries):
        self._set_sparse_queries(queries)

    def _on_dense_generate_finished(self, queries):
        self._set_dense_queries(queries)
        self._query_task_running = False

        if self._query_timer_job is not None:
            self.after_cancel(self._query_timer_job)
            self._query_timer_job = None

        self.hypothesis_ingestion_frame.set_generate_enabled(True)
        self.hypothesis_ingestion_frame.set_hypothesis_enabled(True)

        elapsed = int(time.time() - self._query_start_time)
        self.status_bar.set_status(f"Queries generated in {self._format_seconds(elapsed)}")

        self._query_start_time = None

    def _set_sparse_queries(self, queries):
        self.hypothesis_ingestion_frame.sparse_queries_text.config(state="normal")
        self.hypothesis_ingestion_frame.sparse_queries_text.delete("1.0", "end")

        if isinstance(queries, str):
            self.hypothesis_ingestion_frame.sparse_queries_text.insert("end", queries)
        else:
            for i, query in enumerate(queries, start=1):
                self.hypothesis_ingestion_frame.sparse_queries_text.insert("end", f"{i}. {query}\n\n")

        self.hypothesis_ingestion_frame.sparse_queries_text.see("end")

    def _set_dense_queries(self, queries):
        self.hypothesis_ingestion_frame.dense_queries_text.config(state="normal")
        self.hypothesis_ingestion_frame.dense_queries_text.delete("1.0", "end")

        if isinstance(queries, str):
            self.hypothesis_ingestion_frame.dense_queries_text.insert("end", queries)
        else:
            for i, query in enumerate(queries, start=1):
                self.hypothesis_ingestion_frame.dense_queries_text.insert("end", f"{i}. {query}\n\n")

        self.hypothesis_ingestion_frame.dense_queries_text.see("end")

    def _on_generate_finished(self, queries):
        self._query_task_running = False

        if self._query_timer_job is not None:
            self.after_cancel(self._query_timer_job)
            self._query_timer_job = None

        self.hypothesis_ingestion_frame.set_queries_list(queries)
        self.hypothesis_ingestion_frame.set_generate_enabled(True)
        self.hypothesis_ingestion_frame.set_hypothesis_enabled(True)

        elapsed = int(time.time() - self._query_start_time)
        self.status_bar.set_status(f"Queries generated in {self._format_seconds(elapsed)}")

        self._query_start_time = None

    def _on_generate_failed(self, error_message: str):
        self._query_task_running = False

        if self._query_timer_job is not None:
            self.after_cancel(self._query_timer_job)
            self._query_timer_job = None

        self.hypothesis_ingestion_frame.set_queries_text(f"Query generation failed:\n{error_message}")
        self.hypothesis_ingestion_frame.set_generate_enabled(True)
        self.hypothesis_ingestion_frame.set_hypothesis_enabled(True)
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
    def handle_retrieve_bm25(self):
        if self._rag_task_running:
            return

        self._rag_task_running = True
        self._rag_start_time = time.time()

        self.results_frame.generate_button_bm25.config(state="disabled")

        self._update_rag_elapsed_time()

        thread = threading.Thread(target=self._run_retrieve_bm25_background, daemon=True)
        thread.start()

    def _run_retrieve_bm25_background(self):
        try:
            # hypothesis = self.query_frame.hypothesis_text.get("1.0", "end-1c").strip()
            queries = json.loads(self.query_frame.sparse_queries_text.get("1.0", "end-1c").strip())
            top_k = 2*self.results_frame.get_top_k_chunks_number()
            results = bm25_retrieve(
                    # hypothesis=hypothesis, 
                    queris=queries,
                    top_k=top_k
                    )
            self.after(0, self._on_retrieval_finished, results, "BM25")
        except Exception as exc:
            self.after(0, self._on_retrieval_failed, str(exc))

        # try:
        #     hypothesis = self.query_frame.hypothesis_text.get("1.0", "end-1c").strip()
        #     queries = json.loads(self.query_frame.sparse_queries_text.get("1.0", "end-1c").strip())
        #     top_k = 2*self.results_frame.get_top_k_chunks_number()
        #     results = bm25_retrieve(
        #             hypothesis=hypothesis, 
        #             queris=queries,
        #             top_k=settings.PER_QUERY_TOP_K
        #             )
        #     self.after(0, self._on_rag_finished, results)
        # except Exception as exc:
        #     self.after(0, self._on_rag_failed, str(exc))

    def handle_retrieve_dense(self):
        if self._rag_task_running:
            return

        self._rag_task_running = True
        self._rag_start_time = time.time()

        self.results_frame.generate_button_dense.config(state="disabled")

        self._update_rag_elapsed_time()

        thread = threading.Thread(target=self._run_retrieve_dense_background, daemon=True)
        thread.start()

    def _run_retrieve_dense_background(self):
        try:
            # hypothesis = self.query_frame.hypothesis_text.get("1.0", "end-1c").strip()
            queries = json.loads(self.query_frame.dense_queries_text.get("1.0", "end-1c").strip())
            top_k = 2*self.results_frame.get_top_k_chunks_number()
            results = dense_retrieve(
                    # hypothesis=hypothesis, 
                    queris=queries,
                    top_k=top_k
                    )
            self.after(0, self._on_retrieval_finished, results, "Dense")
        except Exception as exc:
            self.after(0, self._on_retrieval_failed, str(exc))

    def handle_retrieve_hybrid(self):
        if self._rag_task_running:
            return

        self._rag_task_running = True
        self._rag_start_time = time.time()

        self.results_frame.generate_button_hybrid.config(state="disabled")

        self._update_rag_elapsed_time()

        thread = threading.Thread(target=self._run_retrieve_hybrid_background, daemon=True)
        thread.start()

    def _run_retrieve_hybrid_background(self):
        try:
            # hypothesis = self.query_frame.hypothesis_text.get("1.0", "end-1c").strip()
            sparse_queries = json.loads(self.query_frame.sparse_queries_text.get("1.0", "end-1c").strip())
            dense_queries = json.loads(self.query_frame.dense_queries_text.get("1.0", "end-1c").strip())
            top_k = 2*self.results_frame.get_top_k_chunks_number()
            bm25_results = bm25_retrieve(
                    # hypothesis=hypothesis, 
                    queris=sparse_queries,
                    top_k=top_k
                    )
            dense_results = dense_retrieve(
                    # hypothesis=hypothesis, 
                    queris=dense_queries,
                    top_k=top_k
                    )
            
            results = rrf_hybrid(bm25_results, dense_results)
            # print(results)
            results.to_csv(
                settings.BASE_DIR/ 'hybrid_retrieval_results.csv',
                index=False,
                encoding="utf-8",
            )

            self.after(0, self._on_retrieval_finished, results, "Hybrid")
        except Exception as exc:
            self.after(0, self._on_retrieval_failed, str(exc))

    def _on_retrieval_finished(self, results, method):
        self._rag_task_running = False

        if self._rag_timer_job is not None:
            self.after_cancel(self._rag_timer_job)
            self._rag_timer_job = None

        if method == "BM25":
            self.results_frame.generate_button_bm25.config(state="normal")
            context.add(settings.BM25_RETRIEVED_CHUNKS_KEY, results)  # "results" is Pandas Dataframe
        elif method == "Dense":
            self.results_frame.generate_button_dense.config(state="normal")
            context.add(settings.DENSE_RETRIEVED_CHUNKS_KEY, results)
        elif method == "Hybrid":
            self.results_frame.generate_button_hybrid.config(state="normal")
            context.add(settings.DENSE_RETRIEVED_CHUNKS_KEY, results)

        elapsed = int(time.time() - self._rag_start_time)
        self.status_bar.set_status(f"Retrieval completed with {len(results)} hits in {self._format_seconds(elapsed)} for {method}")

        self._rag_start_time = None

    def _on_retrieval_failed(self, error_message: str):
        self._rag_task_running = False

        if self._rag_timer_job is not None:
            self.after_cancel(self._rag_timer_job)
            self._rag_timer_job = None

        print(f"Retrieval failed: {error_message}")
        self.status_bar.set_status("Retrieval failed")

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

    def handle_generate_inference(self, method):
        if self._rag_task_running:
            return

        self._rag_task_running = True
        self._rag_start_time = time.time()

        top_k = self.results_frame.get_top_k_chunks_number()

        hypothesis = self.query_frame.hypothesis_text.get("1.0", "end-1c").strip()
        if hypothesis.strip() == "":
            self.status_bar.set_status(f"No hypothesis found")
            return

        if method == "BM25":
            # need to save only top_k
            results = context.get(settings.BM25_RETRIEVED_CHUNKS_KEY)
        elif method == "Dense":
            # need to save only top_k
            results = context.get(settings.DENSE_RETRIEVED_CHUNKS_KEY)
        elif method == "Hybrid":
            # need to save only top_k
            results = context.get(settings.DENSE_RETRIEVED_CHUNKS_KEY)

        self._update_rag_elapsed_time()

        thread = threading.Thread(
            target=self._run_generate_inference,
            kwargs={'results': results, 'hypothesis': hypothesis, 'limit':int(top_k), 'method': method},
            daemon=True
            )
        thread.start()

    def _run_generate_inference(self, **kwargs):
        df = kwargs.get("results")
        hypothesis = kwargs.get("hypothesis")
        limit = kwargs.get("limit", None)
        method = kwargs.get("method")

        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")

        required_cols = {settings.EMAIL_ID, settings.CHUNK_INDEX, settings.CHUNK_TEXT_SPARSE}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"DataFrame is missing required columns: {missing}")
        
        # Set header in results text frame
        self.results_frame.set_results_header(method)

        results = []
        rows = df if limit is None else df.head(limit)

        for i, row in rows.iterrows():
            email_id = row[settings.EMAIL_ID]
            chunk_index = row[settings.CHUNK_INDEX]
            chunk_text = row[settings.CHUNK_TEXT_SPARSE]

            prompt = build_prompt(hypothesis, chunk_text)
            try:
                llm_result = process_chunk(prompt)
            except Exception as exc:
                print(f"Inference faild for chunk {chunk_index} due to {exc}")
                continue

            llm_result[settings.EMAIL_ID] = email_id
            llm_result[settings.CHUNK_INDEX] = chunk_index
            # llm_result["chunk"] = chunk_text
            
            results.append(llm_result)
            self.results_frame.set_results_list(llm_result, index=i+1)
        
        self.after(0, self._on_rag_finished, results, "Hybrid")

    def _on_rag_finished(self, results, method):
        self._rag_task_running = False

        if self._rag_timer_job is not None:
            self.after_cancel(self._rag_timer_job)
            self._rag_timer_job = None

        with open(settings.BASE_DIR / f'{method}_inference_results.json', 'w') as f:
            json.dump(results, f)

        elapsed = int(time.time() - self._rag_start_time)
        self.status_bar.set_status(f"Inference generated in {self._format_seconds(elapsed)}")

        self._rag_start_time = None

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
    # LOAD HYPOTHESES
    # =========================================================
    def _load_hypotheses(self):
        thread = threading.Thread(target=self._fetch_hypotheses_values, daemon=True)
        thread.start()
    
    def _fetch_hypotheses_values(self):
        try:
            hypotheses = get_all_hypotheses()
            self.after(0, self._update_hypotheses_settings, hypotheses)

        except Exception as e:
            print(f"Error fetching hypotheses: {e}")

    def _update_hypotheses_settings(self, hypotheses):
        settings.ALL_HYPOTHESES = hypotheses
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