from dataclasses import dataclass

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
        return (f"Event Type: {self.eventType}\n"
                f"Is Game Start: {self.is_game_start}\n"
                f"Is Game Over: {self.is_game_over}\n"
                f"Full ID: {self.fullID}\n"
                f"Game ID: {self.gameID}\n"
                f"FEN: {self.fen}\n"
                f"Color: {self.color}\n"
                f"Winner: {self.winner}\n"
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
        if self.eventType  == "gameState":
            self.binc = data.get("binc")
            self.btime = data.get("btime")
            self.moves = data.get("moves")
            self.status = data.get("status")
            self.winc = data.get("winc")
            self.wtime = data.get("wtime")
            self.winner = data.get("winner")

    def __str__(self):
        return (f"Event Type: {self.eventType}\n"
                f"Black Increment: {self.binc}\n"
                f"Black Time: {self.btime}\n"
                f"Moves: {self.moves}\n"
                f"Status: {self.status}\n"
                f"White Increment: {self.winc}\n"
                f"White Time: {self.wtime}\n"
                f"Winner: {self.winner}\n"
            )    


@dataclass
class LoopState:
    is_running: bool = True
    is_in_game: bool = False
    want_account: bool = False
    want_lichess_stream: bool = True
    want_board_stream: bool = True
    want_input: bool = True
