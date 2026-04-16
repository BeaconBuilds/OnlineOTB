import tkinter 
from tkinter import ttk
import ttkbootstrap as tb

class SideBarFrame(ttk.Frame):
    def __init__(self,
                 parent,
                 on_return=None,
                 on_menu=None
                 ):
        super().__init__(parent)

        self.on_return = on_return
        self.on_menu = on_menu

        self._build()


    def _build(self):

        self.side_options_frame = ttk.Frame(self, bootstyle = "info", borderwidth=3, relief="groove")
        self.side_options_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.side_container_frame = ttk.Frame(self.side_options_frame, bootstyle = "light")
        self.side_container_frame.pack(fill="both", expand=True)
        
        self.side_container_frame.columnconfigure(index=0, weight=1)
        for i in range(6):
            self.side_container_frame.rowconfigure(index=i, weight=1)  

        self.side_return_button = ttk.Button(self.side_container_frame, text='Return', style = 'primary', command=self._return_press)
        self.side_return_button.grid(row=0, column=0, ipadx=16, ipady=10, sticky='')
    
        self.side_menu_button = ttk.Button(self.side_container_frame, text='Menu', style = 'primary', command=self._menu_press)
        self.side_menu_button.grid(row=1, column=0, ipadx=16, ipady=10, sticky='')


    def _return_press(self):
        if self.on_return:
            self.on_return()

    
    def _menu_press(self):
        if self.on_menu:
            self.on_menu()