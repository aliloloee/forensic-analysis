import tkinter as tk
from tkinter import ttk


class StatusBar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.status_var = tk.StringVar(value="Ready")

        self.label = ttk.Label(
            self,
            textvariable=self.status_var,
            anchor="w",
            relief="sunken",
            padding=(8, 4)
        )
        self.label.pack(fill="x")

    def set_status(self, text: str):
        self.status_var.set(text)