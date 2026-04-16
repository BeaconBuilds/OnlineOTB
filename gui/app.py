import tkinter 
from tkinter import ttk
import ttkbootstrap as tb
from models import GUIToMainEvent
import queue
import asyncio
from .menu_frame import MenuFrame
from .game_frame import GameFrame
from .side_bar_frame import SideBarFrame
from .search_game_frame import SearchFrame

MENU_BTN_FONT = ("Segoe UI", 25, "bold")
FG_GRAY = "#ABB6C2"
FG_RED = "#d9534f"
FG_GREEN = "#60c772"


class App(tb.Window):

    def __init__(self, guiToMainQueue: queue.Queue = None):
        super().__init__()
        
        self.title("O.O.T.B.")
        self.geometry("720x360")
        #self.style.configure(".", font=("Segoe UI", 15))
        self.style.theme_use("superhero")

        self.style.configure("TButton",font=("Segoe UI", 10, "bold"))
        self.style.configure("title.dark.TButton",font=("Segoe UI", 20, "bold"))
        self.style.configure("title.success.TButton",font=("Segoe UI", 20, "bold"))

        self.style.configure("TFloodgauge", borderwidth=5)

        self.queue = guiToMainQueue
        self.root = RootFrame(self, self.queue)
        self.root.pack(fill='both', expand='yes')



        self.start = self.root.start
        self.game = self.root.game



    

class RootFrame(ttk.Frame):
    def __init__(self, parent, queue:queue.Queue=None):
        super().__init__(parent)
        
        self.parent_app = parent
        self.queue = queue
        self.visible_frame = None

        
        self.menu = MenuFrame(self,
                            on_play=self.show_game)
        
        self.side_bar = SideBarFrame(self,
                                    on_menu=self.show_menu,
                                    on_return=self.side_bar_return)
                                    
        self.game = GameFrame(self,
                            on_side_panel=self.show_side_bar,
                            queue=self.queue)
        
        self.search = SearchFrame(self,
                                    on_play_panel=self.show_game,
                                    on_side_panel=self.show_side_bar,
                                    queue=self.queue)


        self.menu.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.side_bar.place(relx=.8, rely=0, relwidth=.2, relheight=1)
        self.game.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.search.place(relx=0, rely=0, relwidth=1, relheight=1)

        
    def show_menu(self):
        self.menu.lift()
        self.visible_frame = self.menu


    def show_game(self): 
        self.game.lift()
        self.visible_frame = self.game


    def show_side_bar(self):
        self.side_bar.lift()

    def side_bar_return(self):
        self.visible_frame.lift()

    def show_search(self):
        self.search.lift()
        self.visible_frame = self.search


    def start(self):
        self.show_menu()
        self.show_search()
        self.parent_app.update()
        asyncio.create_task(self._fake_main_loop())

    async def _fake_main_loop(self):
        try:
            while self.parent_app.winfo_exists():
                self.parent_app.update()
                self.game.game_panel._clock_countdown()
                await asyncio.sleep(.05)
        except tkinter.TclError:
            self._close_program()

    def _close_program(self):
        data = GUIToMainEvent(
            event_type = GUIToMainEvent.Type.EXIT_PROGRAM
        )
        self.queue.put(data)
        
