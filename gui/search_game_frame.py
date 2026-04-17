import tkinter 
from tkinter import ttk
import ttkbootstrap as tb
from models import GUIToMainEvent, ChallengeData
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
        self.clock_int = tkinter.IntVar()
        self.inc_int = tkinter.IntVar()
        
        self.challenge_to_send = ChallengeData()
        self.is_valid_options = False
        
        
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

        self.title_button = ttk.Button(self.header_frame, bootstyle="disabled", text="Find Game", command=self._title_press)
        self.title_button.grid(row=0, column=1, ipadx=10, ipady=10, sticky='')

        self.menu_button = ttk.Button(self.header_frame, style="primary", text="Menu", command=self._side_panel_press)
        self.menu_button.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')
        self.menu_button.grid_propagate(False)

        self.bottom_frame = ttk.Frame(self, bootstyle="bg")
        self.bottom_frame.grid(row=1, column=0, sticky='nsew')
        self.bottom_frame.rowconfigure(index=0, weight=1)
        self.bottom_frame.columnconfigure(index=0, weight=3)
        self.bottom_frame.columnconfigure(index=1, weight=1)
        self.bottom_frame.columnconfigure(index=2, weight=3)
        

        self.settings_frame = ttk.Frame(self.bottom_frame, bootstyle="bg")
        self.settings_frame.grid(row=0, column=0, sticky='nsew')
        self.settings_frame.rowconfigure(index=0, weight=1)
        self.settings_frame.rowconfigure(index=1, weight=1)
        self.settings_frame.rowconfigure(index=2, weight=1)
        self.settings_frame.rowconfigure(index=3, weight=1)
        self.settings_frame.rowconfigure(index=4, weight=1)
        self.settings_frame.rowconfigure(index=5, weight=1)
        self.settings_frame.columnconfigure(index=0, weight=1)

        self.top_options_frame = ttk.Frame(self.settings_frame, bootstyle="bg")
        self.top_options_frame.grid(row=0, column=0, sticky='nsew')
        self.top_options_frame.rowconfigure(index=0, weight=1)
        self.top_options_frame.columnconfigure(index=0, weight=1)
        self.top_options_frame.columnconfigure(index=1, weight=1)
        self.top_options_frame.columnconfigure(index=2, weight=1)
        self.top_options_frame.columnconfigure(index=3, weight=1)
        
        self.second_options_frame= ttk.Frame(self.settings_frame, bootstyle="bg")
        self.second_options_frame.grid(row=1, column=0, sticky='nsew')

        self.t1_label = ttk.Label(self.top_options_frame, text="Opponent:")
        self.t1_label.grid(row=0, column=0, sticky='')

        self.opponents = ["Player", "WorstFish"]
        self.op_combobox = tb.Combobox(self.top_options_frame, values=self.opponents, state="readonly")
        self.op_combobox.set("WorstFish")
        self.op_combobox.grid(row=0, column=1, sticky='')

        self.t2_label = ttk.Label(self.top_options_frame, text="Side:")
        self.t2_label.grid(row=0, column=2, sticky='')

        self.sides = ["Random", "White", "Black"]
        self.side_combobox = tb.Combobox(self.top_options_frame, values=self.sides, state="readonly")
        self.side_combobox.set("Random")
        self.side_combobox.grid(row=0, column=3, sticky='')

        self.t3_label = ttk.Label(self.settings_frame, textvariable=self.clock_time_text)
        self.t3_label.grid(row=2, column=0, sticky='')

        self.clock_scale = ttk.Scale(self.settings_frame, from_=0, to=100, value=75, orient='horizontal', variable=self.clock_int, command=self._on_clock_slide)
        self.clock_scale.grid(row=3, column=0, padx=30, sticky='ew')

        self.t4_label = ttk.Label(self.settings_frame, textvariable=self.inc_time_text)
        self.t4_label.grid(row=4, column=0, sticky='')

        self.inc_scale = ttk.Scale(self.settings_frame, from_=0, to=100, value=75, orient='horizontal', variable=self.inc_int, command=self._on_inc_slide)
        self.inc_scale.grid(row=5, column=0, padx=30, sticky='ew')

        self.divider_frame = ttk.Frame(self.bottom_frame, bootstyle="dark")
        self.divider_frame.grid(row=0, column=1, sticky='nsew')

        self.favorite_frame = ttk.Frame(self.bottom_frame, bootstyle="bg")
        self.favorite_frame.grid(row=0, column=2, sticky='nsew')
        self.favorite_frame.rowconfigure(index=0, weight=1)
        self.favorite_frame.rowconfigure(index=1, weight=2)
        self.favorite_frame.rowconfigure(index=2, weight=2)
        self.favorite_frame.rowconfigure(index=3, weight=2)
        self.favorite_frame.columnconfigure(index=0, weight=1)

        self.fav_title_label = ttk.Label(self.favorite_frame, text="Favorites")
        self.fav_title_label.grid(row=0, column=0, sticky='')

        self.fav1_button = ttk.Button(self.favorite_frame, text="WorstChess\n10 min, 5 sec", bootstyle="primary")
        self.fav1_button.grid(row=1, column=0, padx=5, pady=10, sticky='nsew')

        self.fav2_button = ttk.Button(self.favorite_frame, text="Player\n10 min, 5 sec", bootstyle="primary")
        self.fav2_button.grid(row=2, column=0, padx=5, pady=10, sticky='nsew')

        self.fav3_button = ttk.Button(self.favorite_frame, text="Stockfish\n10 min, 5 sec", bootstyle="primary")
        self.fav3_button.grid(row=3, column=0, padx=5, pady=10, sticky='nsew')

    def _validate_options(self):
        username = self.op_combobox.get()
        self.challenge_to_send.username = username
        
        side = self.side_combobox.get().lower()
        self.challenge_to_send.color=side
        
        time = self.clock_int.get()
        self.clock_time_text.set(f"Clock time: {time} min")
        self.challenge_to_send.time_limit= time * 60 #api takes time in seconds
        
        inc = self.inc_int.get()
        self.inc_time_text.set(f"Clock time: {inc} min")
        self.challenge_to_send.time_increment = inc
        
        

    def _title_press(self):
        self._validate_options
        if self.queue:
            data = GUIToMainEvent(
                event_type = GUIToMainEvent.Type.CHALLENGE,
                challenge_data = self.challenge_to_send
            )
            self.queue.put(data)

    def _side_panel_press(self):
        if self.on_side_panel:
            self.on_side_panel()
       
    def _on_clock_slide(self, event):
        self._validate_options()
        
        #make it so first 75% is  5min to 30min, the next 24% for correspondance 1 day 2 day 3, 5, and '100' is for unlimited

    def _on_inc_slide(self, event):
        self._validate_options()
