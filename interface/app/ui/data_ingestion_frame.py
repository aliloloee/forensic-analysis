import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


class DataIngestionFrame(ttk.Frame):
    def __init__(self, parent, on_save):
        super().__init__(parent, padding=12)

        self.on_save = on_save

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=0)
        self.rowconfigure(5, weight=1)
        
        self.emails_file = None
        self.chunks_file = None
        self.embedding1_file = None
        self.embedding2_file = None
        
        self._build_widgets()
    
    def _build_widgets(self):
        # Emails import button
        emails_label = ttk.Label(self, text="Emails", font=("Arial", 10, "bold"))
        emails_label.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))
        
        self.emails_button = ttk.Button(
            self,
            text="Import Emails File",
            command=self._import_emails
        )
        self.emails_button.grid(row=0, column=1, sticky="w", padx=12, pady=(12, 6))
        
        self.emails_status = ttk.Label(self, text="No file selected", foreground="gray")
        self.emails_status.grid(row=0, column=2, sticky="w", padx=12, pady=(12, 6))
        
        # Chunks import button
        chunks_label = ttk.Label(self, text="Chunks", font=("Arial", 10, "bold"))
        chunks_label.grid(row=1, column=0, sticky="w", padx=12, pady=6)
        
        self.chunks_button = ttk.Button(
            self,
            text="Import Chunks File",
            command=self._import_chunks
        )
        self.chunks_button.grid(row=1, column=1, sticky="w", padx=12, pady=6)
        
        self.chunks_status = ttk.Label(self, text="No file selected", foreground="gray")
        self.chunks_status.grid(row=1, column=2, sticky="w", padx=12, pady=6)
        
        # Embedding1 import button
        embedding1_label = ttk.Label(self, text="Embedding1", font=("Arial", 10, "bold"))
        embedding1_label.grid(row=2, column=0, sticky="w", padx=12, pady=6)
        
        self.embedding1_button = ttk.Button(
            self,
            text="Import Embedding1 File",
            command=self._import_embedding1
        )
        self.embedding1_button.grid(row=2, column=1, sticky="w", padx=12, pady=6)
        
        self.embedding1_status = ttk.Label(self, text="No file selected", foreground="gray")
        self.embedding1_status.grid(row=2, column=2, sticky="w", padx=12, pady=6)
        
        # Embedding2 import button
        embedding2_label = ttk.Label(self, text="Embedding2", font=("Arial", 10, "bold"))
        embedding2_label.grid(row=3, column=0, sticky="w", padx=12, pady=6)
        
        self.embedding2_button = ttk.Button(
            self,
            text="Import Embedding2 File",
            command=self._import_embedding2
        )
        self.embedding2_button.grid(row=3, column=1, sticky="w", padx=12, pady=6)
        
        self.embedding2_status = ttk.Label(self, text="No file selected", foreground="gray")
        self.embedding2_status.grid(row=3, column=2, sticky="w", padx=12, pady=6)
        
        # Add Data to DB button
        self.add_data_button = ttk.Button(
            self,
            text="Add Data to DB",
            command=self.on_save
        )
        self.add_data_button.grid(row=4, column=0, columnspan=3, sticky="ew", padx=12, pady=(18, 0))
    
    def _import_emails(self):
        file_path = filedialog.askopenfilename(
            title="Select Emails File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.emails_file = file_path
            self.emails_status.config(text=file_path.split("/")[-1], foreground="green")
    
    def _import_chunks(self):
        file_path = filedialog.askopenfilename(
            title="Select Chunks File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.chunks_file = file_path
            self.chunks_status.config(text=file_path.split("/")[-1], foreground="green")
    
    def _import_embedding1(self):
        file_path = filedialog.askopenfilename(
            title="Select Embedding1 File",
            filetypes=[("NPY files", "*.npy"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.embedding1_file = file_path
            self.embedding1_status.config(text=file_path.split("/")[-1], foreground="green")
    
    def _import_embedding2(self):
        file_path = filedialog.askopenfilename(
            title="Select Embedding2 File",
            filetypes=[("NPY files", "*.npy"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.embedding2_file = file_path
            self.embedding2_status.config(text=file_path.split("/")[-1], foreground="green")