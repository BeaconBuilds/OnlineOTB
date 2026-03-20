import chess
import chess.svg
import random
import time
import webbrowser
PYTHON_CHESS_TESTING = False

class ChessLogic:
    def __init__(self, client):
        self.client = client
        self.board = None

    def handle_game_event(self, event):
        pass




if PYTHON_CHESS_TESTING:

    testBoard = chess.Board()
    print(list(testBoard.generate_legal_captures()))


    def displayBoard(b, lm):
            svg_data = chess.svg.board(b, lastmove=lm)
            with open("board.svg", "w") as f:
                f.write(svg_data)    


    foundCheckmate = False;

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


