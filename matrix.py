import sys
import time
import RPi.GPIO as g
import queue
from models import MatrixToMain
#import asyncio

print("START")

COLUMN = [4, 17, 27, 22, 5, 6, 13, 26] #todo: switch 17 and 27 ( unswitched )
#OUTPUT   A   B   C  D   E  F  G    H       WHITE 

ROW = [14, 18, 23, 24, 25, 12, 16, 20] #21
#INPUT   1   2    3   4   5  6   7   8   --  ORANGE

ROW_INCREMENT = .05 #In seconds
SECONDS_MOVE_CONFIRM = 3
#seconds the matrix will spend before sending a "confirmed move" to queue
#I dont like matrix being smart - delete this confirmed move stuff, just send all changed data no matter what

class Matrix:
    def __init__(self, q: queue.Queue):
        self.q = q
        self.scans_since_last_change = 0
        self.move_confirm_count = SECONDS_MOVE_CONFIRM / (ROW_INCREMENT*8)
        self.last_board_change = None

        g.setwarnings(False)
        g.setmode(g.BCM)

        g.setup(COLUMN, g.OUT, initial= g.HIGH)
        g.output(COLUMN, g.HIGH)

        g.setup(ROW, g.IN, pull_up_down=g.PUD_UP)

        print("setup complete")


    def run(self):


        try:
            print("in try block")
            while True:
                boardScan = []
                for scanPin in COLUMN:
                    
                    g.output(scanPin, g.LOW)
                    print(f"Setting {scanPin} LOW")
                    time.sleep(0.01)

                    colData = []
                    for r in ROW:
                        value = int(not g.input(r))
                        print(f"Input pin {r} is {value}")
                        colData.append(value)

                    boardScan.append(colData)
                    g.output(scanPin, g.HIGH)

                    time.sleep(ROW_INCREMENT)

                ######## AFTER WHOLE SCAN ######

                self.scans_since_last_change += 1
                

                if self.last_board_change != boardScan:
                    self.scans_since_last_change = 0
                    self.last_board_change = boardScan
                    event = MatrixToMain(
                        eventType=MatrixToMain.Type.BOARD_CHANGE,
                        boardData=self.last_board_change
                        )
                    print("MATRIX.PY: sending any move change")
                    self.sendData(event)
                    

                if self.scans_since_last_change > self.move_confirm_count:
                    MatrixToMain(
                        eventType=MatrixToMain.Type.CONFIRMED_MOVE,
                        boardData=self.last_board_change
                        )
                    print("MATRIX.PY: sending confirmed move")
                    self.sendData(event)



                print("\n\nCOLUMN DATA:")
                for r in range(len(ROW)):
                    for c in range(len(COLUMN)):
                        print(f"{boardScan[c][r]}\t", end="")
                    print()


        except KeyboardInterrupt:
            g.cleanup()

    def sendData(self, event):
        self.q.put(event)

if __name__ == "__main__":
    matrix = Matrix()
    matrix.run()