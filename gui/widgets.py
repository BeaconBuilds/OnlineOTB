import tkinter 
from tkinter import ttk
import ttkbootstrap as tb

FG_GRAY = "#ABB6C2"
FG_RED = "#d9534f"
FG_GREEN = "#60c772"

class ClockFloodGuage(tb.Floodgauge):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.bar_color = FG_GRAY
        self.trough_color = FG_RED

    
    def set_color(self, color: str):
        text = self.cget("text")
        value = self.cget("value")
        maxi = self.cget("maximum")
        gridInfo = self.grid_info()
        parent = self.master

        self.destroy()

        new = ClockFloodGuage(parent, text = text, value = value, maximum = maxi)
        new.bar_color = color
        new.trough_color = FG_RED
        new.grid(**gridInfo)

        return new

