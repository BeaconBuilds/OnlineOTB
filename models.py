from __future__ import annotations
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

class PostModel:
    def __init__(self, url, status, data):
        self.endpoint = url
        self.ok = False
        self.error = None
        if status == 200:
            self.ok = True
        elif status == 400:
            self.error = data.get("error")
    

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
        fields = {
            "eventType": self.eventType,
            "is_game_start": self.is_game_start,
            "is_game_over": self.is_game_over,
            "fullID": self.fullID,
            "gameID": self.gameID,
            "fen": self.fen,
            "color": self.color,
            "winner": self.winner,
        }
        parts = [f"  {k}: {v}" for k, v in fields.items() if v is not None and v is not False]
        return "LichessEvent(\n" + "\n".join(parts) + "\n)"


class BoardEvent:
    def __init__(self, data, gameID):
        self.gameID = gameID
        self.json = data
        self.eventType = data.get("type")
        
        self.btime = None
        self.wtime = None        
        self.status = None      
        self.winner = None
        self.moves = None

        self.initialTime = None #Gamefull stuff
        self.wName = None
        self.wRating = None
        self.bName = None
        self.bRating = None

        self.binc = None
        self.winc = None

        self.chatUsername = None
        self.chatText = None

        state = data
        if self.eventType  in ("gameState", "gameFull"):
            if self.eventType == "gameFull":
                state = data.get("state", {})
                
                clock = data.get("clock", {})
                self.initialTime = clock.get("initial")

                white = data.get("white",{})
                self.wname = white.get("name")
                self.wrating = white.get("rating")

                black = data.get("black",{})
                self.bname = black.get("name")
                self.brating = black.get("rating")


            self.binc = state.get("binc")
            self.btime = state.get("btime")
            self.moves = state.get("moves")
            self.status = state.get("status")
            self.winc = state.get("winc")
            self.wtime = state.get("wtime")
            self.winner = state.get("winner")

        if self.eventType == "chatLine":
            self.chatUsername = state.get("username")
            self.chatText = state.get("text")
        

    def __str__(self):
        fields = {
            "gameID": self.gameID,
            "eventType": self.eventType,
            "btime": self.btime,
            "wtime": self.wtime,
            "status": self.status,
            "winner": self.winner,
            "moves": self.moves,
            "initialTime": self.initialTime,
            "wName": self.wName,
            "wRating": self.wRating,
            "bName": self.bName,
            "bRating": self.bRating,
            "binc": self.binc,
            "winc": self.winc,
            "chatUsername": self.chatUsername,
            "chatText": self.chatText,
        }
        parts = [f"  {k}: {v}" for k, v in fields.items() if v is not None]
        return "BoardEvent(\n" + "\n".join(parts) + "\n)"
    
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
        DRAW = "draw"
        EXIT_PROGRAM = "exit_program"
        CHALLENGE = "challenge"
        CHAT = "chat"

    event_type: Type

    move: Optional[str] = None
    gameID: Optional[str] = None       

    time: Optional[int] = None       
    increment: Optional[int] = None

    yesNo: Optional[str] = None
    
    challenge_data: Optional[ChallengeData] = None
    
    

@dataclass(frozen=False)
class ChallengeData:
    
    username: Optional[str] = None
    
    time_limit: Optional[int] = None
    time_increment: Optional[int] = None
    days: Optional[int] = None
    rated: Optional[bool] = False
    color: Optional[str] = "random"
    variant: Optional[str] = "standard"
    
@dataclass(frozen=False)
class ChallengeData:
    
    username: Optional[str] = None
    
    time_limit: Optional[int] = None
    time_increment: Optional[int] = None
    days: Optional[int] = None
    rated: Optional[bool] = False
    color: Optional[str] = "random"
    variant: Optional[str] = "standard"
    
    @property
    def data(self):
        return {
            "clock.limit": str(self.time_limit),
            "clock.increment": str(self.time_increment),
            "rated": str(self.rated).lower(),
            "color": self.color,
            "variant": self.variant,
        }

@dataclass(frozen=True)
class MatrixToMain:

    class Type(Enum):
        BOARD_CHANGE = "BOARD_CHANGE"
        CONFIRMED_MOVE = "CONFIRMED_MOVE"

    eventType: Type
    boardData: list[list[bool]]



    #requirements:
    #type field for type of change, either
    #confirmed move OR
    #stateChange
    #(This type will tell main what logic method to send data )
    #
    #then pass full board state to logic.
    #
    #Logic will, 1) make new image with changes
    #           2) check validity of piece( and return answer)
    #
    #main will then 1) if valid, send move to client
    #               2) tell gui to display something like move made
    #
    # 
    # for enemy moves, we will add a method for logic that creates the board image 
    # with enemy moves not yet made OTB yet (with red squares and arrows to show move)
    # 
    # we will keep track to ensure board matches lichess
    #
    # make new class similar to logic.py that tracks the matrix board, parses matrix data, and sends chess.board states to main or logic
    # 
    #  
    # matrix data will NOT be accepted to main/gui/logic UNTIL board synced (display GUI)
    # if "confiromed mve" type is sent, and board is not sync (confirmed by logic),
    #   then send GUI to blatently tell user to "Syncronize board"
    #             