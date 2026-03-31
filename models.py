from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union
from models import *

class Profile:
    def __init__(self, data):
        self.json = data
        self.id = data.get("id")
        self.url = data.get("url")
        self.username = data.get("username")
        self.rapidRating = data.get("perfs", {}).get("rapid", {}).get("rating")
        #Safely chain get calls by providing {} as default of key isn't in json

    def __str__(self):
        return (f"ID: {self.id}\n"
                f"URL: {self.url}\n"
                f"Username: {self.username}\n"
                f"Rapid Rating: {self.rapidRating}\n"
                )
    

class LichessEvent:
    def __init__(self, data):
        self.json = data
        self.eventType = data.get("type")
        self.is_game_start = False
        self.is_game_over = False
        self.fullID = None
        self.gameID = None
        self.fen = None
        self.color = None
        self.winner = None
        if self.eventType in ("gameStart", "gameFinish"):   
            game = data.get("game", {})         
            self.fullID = game.get("fullId")
            self.gameID = game.get("gameId")
            self.fen = game.get("fen")
            self.color = game.get("color")
            if self.eventType == "gameStart":
                self.is_game_start = True
            elif self.eventType == "gameFinish":
                self.is_game_over = True
                self.winner = game.get("winner")

    def __str__(self):
        return (f"LichessEvent Printout\n"
                f"Event Type: {self.eventType}\n"
                f"Is Game Start: {self.is_game_start}\n"
                f"Is Game Over: {self.is_game_over}\n"
                f"Full ID: {self.fullID}\n"
                f"Game ID: {self.gameID}\n"
                f"FEN: {self.fen}\n"
                f"Color: {self.color}\n"
                f"Winner: {self.winner}\n"
                #f"Board State: {self.boardState}\n"
                )


class BoardEvent:
    def __init__(self, data):
        self.json = data
        self.eventType = data.get("type")
        self.binc = None
        self.btime = None
        self.moves = None
        self.status = None
        self.winc = None
        self.wtime = None
        self.winner = None
        state = data
        if self.eventType  in ("gameState", "gameFull"):
            if self.eventType == "gameFull":
                state = data.get("state", {})

            self.binc = state.get("binc")
            self.btime = state.get("btime")
            self.moves = state.get("moves")
            self.status = state.get("status")
            self.winc = state.get("winc")
            self.wtime = state.get("wtime")
            self.winner = state.get("winner")
        

    def __str__(self):
        return (f"BoardEvent Printout\n"
                f"Event Type: {self.eventType}\n"
                f"Black Increment: {self.binc}\n"
                f"Black Time: {self.btime}\n"
                f"Moves: {self.moves}\n"
                f"Status: {self.status}\n"
                f"White Increment: {self.winc}\n"
                f"White Time: {self.wtime}\n"
                f"Winner: {self.winner}\n"
            )    
    
@dataclass (frozen=True)
class StreamModel:
    status: Optional[str] = None
    headers: Optional[str] = None
    data: Optional[str] = None
    model: Optional[Union[LichessEvent, BoardEvent]] = None
    error: Optional[Exception] = None
    ok: Optional[bool] = True
    heartbeat: Optional[bool] = False
    ended: Optional[bool] = False


@dataclass
class LoopState:
    is_running: bool = True
    is_in_game: bool = False
    want_account: bool = False
    want_lichess_stream: bool = True
    want_board_stream: bool = True
    want_input: bool = True
    want_gui: bool = True



@dataclass (frozen=True)
class ClientEvent:
    class Status(Enum):
        ACTIVE = "active"
        FAILED = "failed"
        ENDED = "ended:"

    source: str      
    state: Status   
    info: str = "" #error messages



@dataclass(frozen=True)
class MainToGUIEvent:

    class Type(Enum):
        MOVE = "move"                 
        BOARD_UPDATE = "board_update" 
        LICHESS_STATE = "game_state"  
        LOG = "log"                   
        ERROR = "error"               

    event_type: Type

    boardEventData : Optional[BoardEvent] = None
    lichessEventData : Optional[LichessEvent] = None

    move: Optional[str] = None     
    # log/errors
    message: Optional[str] = None



@dataclass(frozen=True)
class GUIToMainEvent:

    class Type(Enum):
        FIND_GAME = "find_game"
        MOVE = "move"
        RESIGN = "resign"
        DRAW_REQUEST = "draw_request"

    event_type: Type

    move: Optional[str] = None       

    time: Optional[int] = None       
    increment: Optional[int] = None