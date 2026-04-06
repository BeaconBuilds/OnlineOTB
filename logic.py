import chess
import chess.svg
import random
import time
import webbrowser
import models
import subprocess
import os

class ChessLogic:
    def __init__(self, lichessEvent):
        self.board = chess.Board()
        self.moves = []
        self.color = chess.WHITE if lichessEvent.color == "white" else chess.BLACK 
        self.turn = chess.WHITE
        self.is_my_turn = True if self.color == self.turn else False
        self.gameID = lichessEvent.gameID
        
        self.makeSVG()

    #make userMove def that checks validity of move and then gives ti back to main to give to client


    def validateMove(self, moveStr):
        moveStr = moveStr.strip().lower()
        is_Valid = False
        reason = "no reason given"

        if self.color != self.turn:
            reason = f"It is {self.turn}'s move, you are {self.color}."
            return (is_Valid, reason)
        
        if len(moveStr) not in (4, 5):
            reason = f"Move Length needs to be either 4 or 5. Length : {len(moveStr)}"
            return (is_Valid, reason)
        
        legalList = list(self.board.generate_legal_moves())
        try:
            if chess.Move.from_uci(moveStr) not in legalList:
                reason = f"{moveStr} not in legal set of moves: {legalList}"
                return (is_Valid, reason)
        except Exception as e:
            reason = f"{moveStr} threw exception in python-chess: {str(e)}"
            return (is_Valid, reason)
        
        is_Valid = True
        reason = f"{moveStr} is a valid move"
        return is_Valid, reason



    def handle_game_event(self, boardEvent):
        if boardEvent.eventType in ("gameState", "gameFull") and boardEvent.moves is not None:
            self.updateMoves(boardEvent.moves.split(" "))
        #make moves

        self.turn = self.board.turn
        if self.turn == self.color:
            self.is_my_turn = True
        else:
            self.is_my_turn = False

        self.makeSVG()
    
    def printState(self):
        print(
            f"""
            --- GAME STATE ---
            Game ID     : {self.gameID}
            Color       : {"White" if self.color else "Black"}
            Turn        : {"White" if self.turn else "Black"}
            Your Turn   : {self.is_my_turn}
            Moves       : {len(self.moves)} moves
            -------------------
            """
        )        
    

    def updateMoves(self, newMoves):
        newMovesNum = len(newMoves)
        currentMoveNum = len(self.moves)
        
        if currentMoveNum > newMovesNum:
            self.moves = []
            self.board = chess.Board()
            currentMoveNum = len(self.moves)
            #if logic moves are greater than lichess moves (should never happen during same game) restart board

        if currentMoveNum < newMovesNum:
            movesToPush = newMoves[currentMoveNum:]
            for move in movesToPush:
                self.board.push_uci(move)
        self.moves = newMoves



    def makeSVG(self):
        lastMove = None

        if len(self.moves) != 0:
            lastMove = chess.Move.from_uci(self.moves[len(self.moves)-1])
        svg = chess.svg.board(board = self.board, lastmove = lastMove, orientation=self.color)
        with open("board.svg", "w", encoding="utf-8") as f:
            f.write(svg)
        self.svg_to_png()



    def svg_to_png(self, svg_path="board.svg", png_path="board.png", width=340, height=340):
        rsvg_path = r"C:\msys64\mingw64\bin\rsvg-convert.exe"

        subprocess.run([
            rsvg_path,
            "-w", str(width),
            "-h", str(height),
            "-o", os.path.abspath(png_path),
            os.path.abspath(svg_path)
        ], check=True)
