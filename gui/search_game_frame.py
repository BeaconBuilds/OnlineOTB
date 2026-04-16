import tkinter 
from tkinter import ttk
import ttkbootstrap as tb
from models import GUIToMainEvent
import queue


class SearchFrame(ttk.Frame):
    def __init__(self,
                parent,
                on_play_panel=None,
                on_side_panel=None,
                queue:queue.Queue=None):
        super().__init__(parent)

        self.on_play_panel = on_play_panel
        self.on_side_panel = on_side_panel
        self.queue=queue

        self.clock_time_text = tkinter.StringVar(value="Clock time: 10 min")
        self.inc_time_text = tkinter.StringVar(value="Increment time: 3 sec")
        
        self._build()

    def _build(self):
        
        self.rowconfigure(index=0, weight=1)
        self.rowconfigure(index=1, weight=8)
        self.columnconfigure(index=0, weight=1)

        self.header_frame = ttk.Frame(self, bootstyle="bg")
        self.header_frame.grid(row=0, column=0, sticky='nsew')
        self.header_frame.rowconfigure(index=0, weight=1)
        self.header_frame.columnconfigure(index=0, weight=1)
        self.header_frame.columnconfigure(index=1, weight=5)
        self.header_frame.columnconfigure(index=2, weight=1)

        self.title_button = ttk.Button(self.header_frame, bootstyle="info", text="Find Game")
        self.title_button.grid(row=0, column=1, ipadx=10, ipady=10, sticky='')

        self.menu_button = ttk.Button(self.header_frame, style="info", text="Menu", command=self._side_panel_press)
        self.menu_button.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')
        self.menu_button.grid_propagate(False)

        self.bottom_frame = ttk.Frame(self, bootstyle="success")
        self.bottom_frame.grid(row=1, column=0, sticky='nsew')
        self.bottom_frame.rowconfigure(index=0, weight=1)
        self.bottom_frame.columnconfigure(index=0, weight=3)
        self.bottom_frame.columnconfigure(index=1, weight=1)

        self.settings_frame = ttk.Frame(self.bottom_frame, bootstyle="danger")
        self.settings_frame.grid(row=0, column=0, sticky='nsew')
        self.settings_frame.rowconfigure(index=0, weight=1)
        self.settings_frame.rowconfigure(index=1, weight=1)
        self.settings_frame.rowconfigure(index=2, weight=1)
        self.settings_frame.rowconfigure(index=3, weight=1)
        self.settings_frame.rowconfigure(index=4, weight=1)
        self.settings_frame.rowconfigure(index=5, weight=1)
        self.settings_frame.columnconfigure(index=0, weight=1)

        self.top_options_frame = ttk.Frame(self.settings_frame, bootstyle="dark")
        self.top_options_frame.grid(row=0, column=0, sticky='nsew')
        self.top_options_frame.rowconfigure(index=0, weight=1)
        self.top_options_frame.columnconfigure(index=0, weight=1)
        self.top_options_frame.columnconfigure(index=1, weight=1)
        self.top_options_frame.columnconfigure(index=2, weight=1)
        self.top_options_frame.columnconfigure(index=3, weight=1)
        
        self.second_options_frame= ttk.Frame(self.settings_frame, bootstyle="light")
        self.second_options_frame.grid(row=1, column=0, sticky='nsew')

        self.t1_label = ttk.Label(self.top_options_frame, text="Opponent:")
        self.t1_label.grid(row=0, column=0, sticky='')

        self.opponents = ["Player", "WorstChess"]
        self.op_combobox = tb.Combobox(self.top_options_frame, values=self.opponents, state="readonly")
        self.op_combobox.grid(row=0, column=1, sticky='')

        self.t2_label = ttk.Label(self.top_options_frame, text="Side:")
        self.t2_label.grid(row=0, column=2, sticky='')

        self.sides = ["Random", "White", "Black"]
        self.side_combobox = tb.Combobox(self.top_options_frame, values=self.sides, state="readonly")
        self.side_combobox.grid(row=0, column=3, sticky='')

        self.t3_label = ttk.Label(self.settings_frame, textvariable=self.clock_time_text)
        self.t3_label.grid(row=2, column=0, sticky='')

        self.clock_scale = ttk.Scale(self.settings_frame, from_=0, to=100, value=75, orient='horizontal')
        self.clock_scale.grid(row=3, column=0, padx=30, sticky='ew')

        self.t4_label = ttk.Label(self.settings_frame, textvariable=self.inc_time_text)
        self.t4_label.grid(row=4, column=0, sticky='')

        self.inc_scale = ttk.Scale(self.settings_frame, from_=0, to=100, value=75, orient='horizontal')
        self.inc_scale.grid(row=5, column=0, padx=30, sticky='ew')


        self.favorite_frame = ttk.Frame(self.bottom_frame, bootstyle="light")
        self.favorite_frame.grid(row=0, column=1, sticky='nsew')

        

    def _side_panel_press(self):
        if self.on_side_panel:
            self.on_side_panel()
       

