import tkinter 
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.scrolled import ScrolledFrame
from models import GUIToMainEvent
import queue
import asyncio
import time
from .menu_frame import MenuFrame
from .side_bar_frame import SideBarFrame
from .widgets import ClockFloodGuage

FG_GRAY = "#ABB6C2"
FG_RED = "#d9534f"
FG_GREEN = "#60c772"


class GameFrame(ttk.Frame):
    def __init__(self,
                parent,
                on_side_panel=None,
                queue:queue.Queue=None):
        super().__init__(parent)

        self.on_side_panel = on_side_panel
        self.queue = queue
        
        self.game_panel = GamePanel(self, on_side_panel=self.on_side_panel, queue=self.queue)
        self.board_panel = BoardPanel(self)
        self.end_panel = EndPanel(self)

        self._build()
    

    def add_chat_line(self, username: str, text: str):
        self.game_panel.add_chat_line(username, text)


    def update_board(self, game_id: str):
        self.board_panel.update_board(game_id)
        self.game_panel._set_game_id(game_id)


    def set_turn(self, is_my_turn: bool):
        self.game_panel.set_turn(is_my_turn)

    def set_op_time(self, msLeft: int, msTotal:int = None):
        self.game_panel.set_op_time(msLeft, msTotal)

    def set_my_time(self, msLeft: int, msTotal:int = None):
        self.game_panel.set_my_time(msLeft, msTotal)

    def _build(self):
        #self.game_frame = ttk.Frame(self, bootstyle = "bg")
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.rowconfigure(index=0, weight=1)
        self.columnconfigure(index=0, weight=1)
        self.columnconfigure(index=1, weight=1)

        self.game_panel.grid(row=0, column=1, sticky='nsew')
        self.board_panel.grid(row=0, column=0, sticky='nsew')


        


class GamePanel(ttk.Frame):

    def __init__(self,
                parent,
                on_side_panel=None,
                queue=None):
        super().__init__(parent)

        self.on_side_panel = on_side_panel
        self.queue = queue

        self.game_id = None
        self.myTimeLeftG = None
        self.opTimeLeftG = None
        self.lastMoveTimeG = None
        self.isMyTurnG = None

        self.game_chat_entry_text = tkinter.StringVar(value="Type Here")
        self.game_chat_text = tkinter.StringVar(value="This is chat\n")
        self.game_move_text = tkinter.StringVar(value="Dummy Text")

        self._build()

        
    

    def _build(self):


        self.game_right_frame = ttk.Frame(self, bootstyle= "bg")
        self.game_right_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.game_right_frame.columnconfigure(index=0, weight=1)
        self.game_right_frame.columnconfigure(index=1, weight=1)
        self.game_right_frame.columnconfigure(index=2, weight=6)       
        self.game_right_frame.rowconfigure(index=0, weight=1)
        self.game_right_frame.rowconfigure(index=1, weight=1)
        self.game_right_frame.rowconfigure(index=2, weight=4)
        self.game_right_frame.rowconfigure(index=3, weight=1)
        self.game_right_frame.rowconfigure(index=4, weight=2)
        self.game_right_frame.grid_propagate(False)        

        self.op_timer_label = ttk.Label(self.game_right_frame, background="#405C7C")
        self.op_timer_label.grid(row=0, column=0, columnspan=2, rowspan=2, padx=10, pady=10, sticky='nsew')
        self.op_timer_label.rowconfigure(0, weight=1)
        self.op_timer_label.columnconfigure(0, weight=1)
        self.op_timer_label.grid_propagate(False)

        self.op_floodgauge = ClockFloodGuage(self.op_timer_label, text="0:00", value=75)
        self.op_floodgauge.grid(row=0, column=0, columnspan=1, padx=4, pady=4, sticky='nsew')

        self.game_move_labelFrame = ttk.LabelFrame(self.game_right_frame, text="Moves", style="danger")
        self.game_move_labelFrame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        self.game_move_labelFrame.grid_propagate(False)
        self.game_move_labelFrame.rowconfigure(index=0, weight=1)
        self.game_move_labelFrame.columnconfigure(index=0, weight=1)

        self.game_move_label = ttk.Label(self.game_move_labelFrame, textvariable=self.game_move_text)
        self.game_move_label.grid(row=0, column=0, padx=4, pady=4)

        self.resign_button = ttk.Button(self.game_right_frame, text='Resign', style='danger', command = self._resign_press)
        self.resign_button.grid(row=3, column=0, padx=10, pady=10, sticky='nsew')   
        self.resign_button.grid_propagate(False)

        self.draw_button = ttk.Button(self.game_right_frame, text='Draw', style='danger', command = self._draw_press)
        self.draw_button.grid(row=3, column=1, padx=10, pady=10, sticky='nsew')  
        self.draw_button.grid_propagate(False)    

        self.my_timer_label = ttk.Label(self.game_right_frame, background="#405C7C")
        self.my_timer_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        self.my_timer_label.rowconfigure(0, weight=1)
        self.my_timer_label.columnconfigure(0, weight=1)
        self.my_timer_label.grid_propagate(False)

        self.my_floodgauge = ClockFloodGuage(self.my_timer_label, text="4:12", value=20)
        self.my_floodgauge.grid(row=0, column=0, columnspan=1, padx=4, pady=4, sticky='nsew')       

        self.game_top_menu_button = ttk.Button(self.game_right_frame, style="info", text="Menu", command=self._side_panel_press)
        self.game_top_menu_button.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')
        self.game_top_menu_button.grid_propagate(False)

        self.game_chat_label = ttk.Label(self.game_right_frame, background="#405C7C")
        self.game_chat_label.grid(row=1, column=2, rowspan=4, padx=10, pady=10, sticky='nsew')
        self.game_chat_label.rowconfigure(index=0, weight=10)
        self.game_chat_label.rowconfigure(index=1, weight=1)
        self.game_chat_label.columnconfigure(index=0, weight=1)
        self.game_chat_label.grid_propagate(False)

        self.game_chat_scrolledframe = ScrolledFrame(self.game_chat_label)
        self.game_chat_scrolledframe.grid(row=0, column=0, padx=4, pady=4, sticky='nsew')
        self.game_chat_scrolledframe.rowconfigure(index=0, weight=1)
        self.game_chat_scrolledframe.columnconfigure(index=0, weight=1)

        self.game_chat_scrolled_label = ttk.Label(self.game_chat_scrolledframe, wraplength=93, textvariable=self.game_chat_text)
        self.game_chat_scrolled_label.grid(row=0, column=0, sticky='nsew')
        self.game_chat_scrolledframe.yview_moveto(0.0)

        self.game_chat_entry = ttk.Entry(self.game_chat_label, textvariable=self.game_chat_entry_text)
        self.game_chat_entry.grid(row=1, column=0, padx=4, pady=4, sticky='nsew')
        self.game_chat_entry.bind("<Return>", self._chat_enter)


    def add_chat_line(self, username: str, text: str):

        chat = self.game_chat_text.get()
        line = f"{username}: {text}\n"
        chat += line
        self.game_chat_text.set(chat)


    def set_turn(self, isMyTurn: bool):
        self.isMyTurnG = isMyTurn
        self.lastMoveTimeG = time.time() * 1000
        if isMyTurn:

            self.my_floodgauge = self.my_floodgauge.set_color(FG_GREEN)
            self.op_floodgauge = self.op_floodgauge.set_color(FG_GRAY)
        else:

            self.my_floodgauge = self.my_floodgauge.set_color(FG_GRAY)           
            self.op_floodgauge = self.op_floodgauge.set_color(FG_GREEN)


    def set_op_time(self, msLeft: int, msTotal:int = None):
        
        self.opTimeLeftG = msLeft

        seconds = int((msLeft/1000)%60)
        minutes = int(msLeft/60000)

        if msTotal: self.op_floodgauge.maximum = msTotal
        self.op_floodgauge.configure(value = msLeft)
        self.op_floodgauge.configure(text=f"{int(minutes):02}:{int(seconds):02}")
 

    def set_my_time(self, msLeft: int, msTotal:int = None):
        
        self.myTimeLeftG = msLeft

        seconds = (msLeft/1000)%60
        minutes = (msLeft/60000)

        if msTotal: self.my_floodgauge.maximum = msTotal
        self.my_floodgauge.configure(value = msLeft)
        self.my_floodgauge.configure(text=f"{int(minutes):02}:{int(seconds):02}") 



    def _set_game_id(self, game_id):
        self.game_id = game_id


    def _resign_press(self):
        if self.game_id and self.queue:
            data = GUIToMainEvent(
                GUIToMainEvent.Type.RESIGN,
                gameID=self.game_id
            )
            self.queue.put(data) 

    def _draw_press(self):
        if self.game_id and self.queue:
            data = GUIToMainEvent(
                GUIToMainEvent.Type.DRAW,
                gameID=self.game_id
            )
            self.queue.put(data)     


    def _chat_enter(self, event):
        if self.queue:
            text = self.game_chat_entry_text.get()
            data = GUIToMainEvent(
                GUIToMainEvent.Type.MOVE,
                move = text.strip().lower(),
                gameID = self.game_id
            )
            self.queue.put(data)
            self.game_chat_entry_text.set('')
            

    def _side_panel_press(self):
        if self.on_side_panel:
            self.on_side_panel()
       
    def _clock_countdown(self):        
        if self.isMyTurnG != None:
            currentTime = time.time()*1000
            diff = currentTime - self.lastMoveTimeG
            
            if self.isMyTurnG:
                msLeft = self.myTimeLeftG - diff
                seconds = (msLeft/1000)%60
                minutes = (msLeft/60000)
                self.my_floodgauge.configure(value = msLeft)
                self.my_floodgauge.configure(text=f"{int(minutes):02}:{int(seconds):02}") 
            else:
                msLeft = self.opTimeLeftG - diff
                seconds = int((msLeft/1000)%60)
                minutes = int(msLeft/60000)
                self.op_floodgauge.configure(value = msLeft)
                self.op_floodgauge.configure(text=f"{int(minutes):02}:{int(seconds):02}")
 




class BoardPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self._build()


    def _build(self):

        self.game_left_frame = ttk.Frame(self, bootstyle= "bg", padding=0)
        self.game_left_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.game_left_frame.rowconfigure(index=0, weight=1)
        self.game_left_frame.columnconfigure(index=0, weight=1)
        self.game_left_frame.grid_propagate(False)

        self.png_img = tkinter.PhotoImage(file="board.png")
        self.img_label = ttk.Label(self.game_left_frame, image = self.png_img, bootstyle="secondary")
        self.img_label.grid(row=0, column=0, sticky='')    



    def update_board(self, gameID: str):
        """Reload the SVG board"""
        png_path = f"board_{gameID}.png"
        self.gameID = gameID

        try:
            self.png_img = tkinter.PhotoImage(file=png_path)
            self.img_label.config(image=self.png_img)
        except Exception as e:
            print(str(e))


class EndPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self._build()

    def _build(self):
        pass