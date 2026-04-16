import tkinter 
from tkinter import ttk
import ttkbootstrap as tb
from models import GUIToMainEvent
import queue


class SearchFrame(ttk.Frame):
    def __init__(self,
                parent,
                on_play_panel=None,
                queue:queue.Queue=None):
        super().__init__(parent)

        self.on_play_panel = on_play_panel
        self.queue=queue

        self._build()

    def _build(self):
        pass
