import tkinter 
from tkinter import ttk
from ttkbootstrap import Style
from models import GUIToMainEvent
import queue
import asyncio


class App(tkinter.Tk):

    def __init__(self, guiToMainQueue: queue.Queue = None):
        super().__init__()
        
        self.title("O.O.T.B.")
        self.geometry("720x360")
        self.style = Style("superhero")
        self.queue = guiToMainQueue
        self.application = Application(self)
        self.application.pack(fill='both', expand='yes')


        self.start = self.application.start
        self.fake_main_loop = self.application.fake_main_loop
        self.update_board = self.application.update_board
        self.update_State = self.application.update_State
        self.update_Status = self.application.update_Status

      # schedule the async task
    

class Application(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.parent_app = parent
        self.queue = self.parent_app.queue
    #variables
        self.status_text = tkinter.StringVar(value="Example Status")
        self.state_text = tkinter.StringVar(value="Example State")
        self.user_move = tkinter.StringVar()
        



    #frames
        self.main_frame = ttk.Frame(self, bootstyle = "bg")
        self.main_frame.pack(fill='both', expand=True)
        self.main_frame.rowconfigure(index=0, weight=1)
        self.main_frame.columnconfigure(index=0, weight=1)
        self.main_frame.columnconfigure(index=1, weight=1)

        self.left_frame = ttk.Frame(self.main_frame, bootstyle= "bg", padding=0)
        self.left_frame.grid(row=0, column=0, sticky='nsew')
        self.left_frame.grid_propagate(False)
        
        self.left_frame.rowconfigure(index=0, weight=1)
        self.left_frame.columnconfigure(index=0, weight=1)


        self.right_frame = ttk.Frame(self.main_frame, bootstyle= "bg")
        self.right_frame.grid(row=0, column=1, sticky='nsew')
        
        for col in range(2):
            self.right_frame.columnconfigure(index=col, weight=1)
        self.right_frame.rowconfigure(index=0, weight=1)
        self.right_frame.rowconfigure(index=1, weight=1)
        self.right_frame.rowconfigure(index=2, weight=1)
        self.right_frame.grid_propagate(False)

        self.text_label_frame = ttk.Labelframe(self.right_frame, text= " Enter Move ", bootstyle="light")
        self.text_label_frame.grid(row=2, column=1, padx=5, pady=5, sticky='nsew')

        self.state_label_frame = ttk.Labelframe(self.right_frame, text= " Current State ", bootstyle="light")
        self.state_label_frame.grid(row=0, column=0, columnspan=2, padx=15, pady=15, sticky='nsew')

        self.status_label_frame = ttk.Labelframe(self.right_frame, text= " Current Status ", bootstyle="light")
        self.status_label_frame.grid(row=1, column=0, columnspan=2, padx=15, pady=15, sticky='nsew')

    

    #labels

        self.png_img = tkinter.PhotoImage(file="board.png")
        self.img_label = ttk.Label(self.left_frame, image = self.png_img, bootstyle="secondary")
        self.img_label.grid(row=0, column=0, sticky='')    


        self.state_label = ttk.Label(self.state_label_frame, font='-size 20', anchor='center', textvariable=self.state_text, bootstyle = 'danger')
        self.state_label.pack(fill=None, expand=True, anchor = 'center', padx=5, pady=5)


        self.status_label = ttk.Label(self.status_label_frame, font='-size 20', anchor='center', textvariable=self.state_text, bootstyle = 'danger')
        self.status_label.pack(fill=None, expand=True, anchor = 'center', padx=5, pady=5)

        self.resign_button = ttk.Button(self.right_frame, text='Resign', style='info', command = self.resign)
        self.resign_button.grid(row=2, column=0, padx=0, pady=0, sticky='')

        #self.resign_button = ttk.Button(self.right_frame, text='Draw', style='info.TButton', command = self.draw)
        #self.resign_button.grid(row=2, column=1, padx=0, pady=0, sticky='')
        #-------------------put button back eventually---------------

        self.move_entry = ttk.Entry(self.text_label_frame, style='primary', textvariable=self.user_move)
        self.move_entry.bind("<Return>", self.moveEnter)
        self.move_entry.pack(fill=None, expand=True, anchor = 'center', padx=5, pady=5)
    #buttons

    #methods
    def resign(self):
        pass
    
    def draw(self):
        pass

    def update_State(self, newState: str):
        self.state_text.set(newState)

    def update_Status(self, newStatus: str):
        self.status_text.set(newStatus)

    def moveEnter(self, event):

        text = self.user_move.get()
        data = GUIToMainEvent(
            GUIToMainEvent.Type.MOVE,
            move = text.strip().lower()
        )
        self.produceQueue(data)

        self.user_move.set('')
        pass

    def update_board(self, png_path="board.png"):
        """Reload the SVG board"""
        try:
            self.png_img = tkinter.PhotoImage(file=png_path)
            self.img_label.config(image=self.png_img)
        except Exception as e:
            print(str(e))


    def produceQueue(self, communication: GUIToMainEvent):
        self.queue.put(communication)

    def start(self):
        self.parent_app.update()

    async def fake_main_loop(self):
        while self.parent_app.winfo_exists:
            self.parent_app.update()
            await asyncio.sleep(.01)

#use tkbootstrafp