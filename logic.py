import chess
import chess.svg
import random
import time
import webbrowser
import models
PYTHON_CHESS_TESTING = False

class ChessLogic:
    def __init__(self, lichessEvent):
        self.board = chess.Board()
        self.moves = []
        self.makeSVG()
        self.color = chess.WHITE if lichessEvent.color == "white" else chess.BLACK 
        self.turn = chess.WHITE
        self.is_my_turn = True if self.color == self.turn else False
        self.gameID = lichessEvent.gameID
        
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
        if chess.Move.from_uci(moveStr) not in legalList:
            reason = f"{moveStr} not in legal set of moves: {legalList}"
            return (is_Valid, reason)
        
        is_Valid = True
        reason = f"{moveStr} is a valid move"
        return is_Valid, reason



    def handle_game_event(self, boardEvent):
        print(self.board)
        if boardEvent.eventType == "gameState" and boardEvent.moves is not None:
            self.updateMoves(boardEvent.moves.split(" "))
        #make moves

        self.turn = self.board.turn
        if self.turn == self.color:
            self.is_my_turn = True
        else:
            self.is_my_turn = False

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

        self.makeSVG()
    


    def updateMoves(self, newMoves):
        newMovesNum = len(newMoves)
        currentMoveNum = len(self.moves)
        
        print(f"we in the handle if\nCurrent MOve nUM: {currentMoveNum}\nnewmovesnum: {newMovesNum}")
        if currentMoveNum > newMovesNum:
            self.moves = []
            self.board = chess.Board()
            currentMoveNum = len(self.moves)
            #if logic moves are greater than lichess moves (should never happen during same game) restart board

        if currentMoveNum < newMovesNum:
            movesToPush = newMoves[currentMoveNum:]
            for move in movesToPush:
                print(f"pushing move: {move}")
                self.board.push_uci(move)
        self.moves = newMoves

    def makeSVG(self):
        lastMove = None
        if len(self.moves) != 0:
            lastMove = chess.Move.from_uci(self.moves[len(self.moves)-1])
        svg = chess.svg.board(board = self.board, lastmove = lastMove)
        with open("board.svg", "w", encoding="utf-8") as f:
            f.write(svg)

    def setMoves():
        pass




if PYTHON_CHESS_TESTING:

    testBoard = chess.Board()
    print(list(testBoard.generate_legal_captures()))


    def displayBoard(b, lm):
            svg_data = chess.svg.board(b, lastmove=lm)
            with open("board.svg", "w") as f:
                f.write(svg_data)    


    foundCheckmate = False

    while not foundCheckmate:
        time.sleep(2)
        board = chess.Board()
        for i in range(100):
            time.sleep(0)
            #print(f"Turn: {board.fullmove_number}\tSide: {board.turn}\n")
            #print(board)
            if(board.is_game_over()):
                print("FINAL MOVE")
                print(f"Turn: {board.fullmove_number}\tSide: {"White" if board.turn==chess.WHITE else "Black"}\n" + f"{board}")
                print(f"Checkmate: {str(board.is_checkmate())}\n"
                    f"Stalemate: {str(board.is_stalemate())}\n"
                    f"Game Over: {str(board.is_game_over())}\n"
                    f"5-Fold: {str(board.is_fivefold_repetition())}\n"
                    f"50-Moves: {str(board.is_fifty_moves())}\n"
                    f"Legal Move Count: {board.legal_moves.count()}\n"
                    f"Winning Side: {"White" if board.turn==chess.BLACK else "Black"}")
                
                if(board.is_checkmate() or board.is_stalemate()):
                    foundCheckmate = False
                    displayBoard(board, move)

                break

            capturingMoves = list(board.generate_legal_captures())
            legalMoves = list(board.legal_moves)

            if board.turn == chess.WHITE:
                if capturingMoves: #if list is not empty
                    move = random.choice(capturingMoves)
                else:
                    move = random.choice(list(board.legal_moves))

            else:
                cowardMoves = [m for m in legalMoves if m not in capturingMoves]
                if cowardMoves:
                    move = random.choice(cowardMoves)
                else:
                    move = random.choice(legalMoves)

                
            print(f"Turn: {board.fullmove_number}\tSide: {"White" if board.turn==chess.WHITE else "Black"}\n" + f"{board}" + "\n\n\n" + f"Previous Move Made: {move}", end="/r")
            board.push(move)
    #        displayBoard(board)


