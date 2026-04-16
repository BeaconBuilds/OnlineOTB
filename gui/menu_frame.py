import tkinter 
from tkinter import ttk
import ttkbootstrap as tb

class MenuFrame(ttk.Frame):
    def __init__(self,
                parent,
                on_play=None,
                on_history=None,
                on_settings=None
                ):
        super().__init__(parent)
        
        self.on_play = on_play
        self.on_history = on_history
        self.on_settings = on_settings

        self._build()
    
    
    def _build(self):
        self.menu_frame = ttk.Frame(self, bootstyle = "bg")
        self.menu_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        for i in range(3):
            self.menu_frame.rowconfigure(index=i, weight= 0)
        self.menu_frame.rowconfigure(index=3, weight= 2)
        self.menu_frame.rowconfigure(index=4, weight= 1)
        self.menu_frame.rowconfigure(index=5, weight= 2)


        #for r in range(2):
        #    self.menu_frame.rowconfigure(index=r, weight= 1)
        for c in range(9):
            self.menu_frame.columnconfigure(index=c, weight= 1)

        self.title_img = tkinter.PhotoImage(file="title.png")
        self.title_img_label = ttk.Label(self.menu_frame, image = self.title_img, bootstyle="bg")
        self.title_img_label.grid(row=0, column=0, columnspan=9, rowspan=3, padx=0, pady=0, sticky='nsew')            

        self.menu_history_button = tb.Button(self.menu_frame, text=' Game\nHistory', style="title.dark.TButton", command = self._history_press)
        self.menu_history_button.grid(row=4, column=1, ipadx=30, ipady=10, sticky='nsew')

        self.menu_play_button = ttk.Button(self.menu_frame, text= 'Play', style="title.success.TButton",  command = self._play_press)
        self.menu_play_button.grid(row=4, column=4, ipadx=30, ipady=10, sticky='nsew')

        self.menu_settings_button = ttk.Button(self.menu_frame, text= 'Settings', style="title.dark.TButton",  command = self._settings_press)
        self.menu_settings_button.grid(row=4, column=7, ipadx=30, ipady=10, sticky='nsew')
           
        
    def _play_press(self):
        if self.on_play:
            self.on_play()
        #application handles navigation


    def _history_press(self):
        if self.on_history:
            self.on_history()


    def _settings_press(self):
        if self.on_settings:
            self.on_settings()