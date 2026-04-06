from dotenv import load_dotenv
from client import LichessClient
from logic import ChessLogic
from gui import App
from aioconsole import ainput
import queue
import json
import os
import requests
import asyncio
import models




async def main():



    async def consumeQueue(q):
        if isinstance(q, asyncio.Queue):
            try:   
                data = q.get_nowait()
                return data
            except asyncio.QueueEmpty:
                pass
        elif isinstance(q, queue.Queue):
            if not q.empty():
                data = q.get()
                print(data)
                return data
               

#---------------- Wrapper for Generic Stream
    async def streamWrapper(clientTemplate : tuple,
                            queue: asyncio.Queue,
                            gameID : str = None):
        
        try:
            while True: #retry connection
                async for result in client.genericStream(clientTemplate, gameID=gameID):

                    statusText = f"Status: {result.status}" if result.status else "No Status"

                    if not result.ok:
                        print(
                            f"\n***STREAM ERROR***"
                            f"\n{statusText}"
                            f"\nError: {result.error}\n"
                            f"\nData: {result.data}\n"
                        )
                        break
                        #print error and break to retry connection
                        #change to logging in gui eventually

                    elif result.ended:
                        print("Graceful stream shutdown")
                        return
                        #if loop ended normally

                    elif result.heartbeat:
                        continue
                        #not used right now, maybe turn into timeout checker?
                        #or just edit aiohttp config?

                    elif result.data:
                        print(f"\nData:{json.dumps(result.data, indent=4)}")
                        print(f"Model Output: \n{result.model}")
                        await queue.put(result.model)


                print("Stream loop exited, retrying...")
                await asyncio.sleep(2) # 2 second retry delay

        except asyncio.CancelledError as e:
            print("Task canceled on purpose")


    def processLichessStream(lichessEvent : models.LichessEvent):

        if lichessEvent.eventType == "gameStart": 
            gameID = lichessEvent.gameID
            logicDict[gameID] = ChessLogic(lichessEvent)
            state.is_in_game = True

            asyncio.create_task(streamWrapper(client.BOARD_STREAM, gameEventQueue, gameID=gameID))
            #if game started then tell client to start streaming the board of gameID                
            
        if lichessEvent.eventType == "gameFinish":
            print(f"Game Finished - Winner: {lichessEvent.winner}")  
                  

#--------------------START-MAIN-LOOP------------------------------------------------------#
    async def mainControlLoop():

        while state.is_running:

            #Account
            if state.want_account:
                account = await consumeQueue(accountQueue)
                if account:
                    print(f"Account Grab successful: {account.username}")
                    state.want_account = False
                    #state is switched because its jsut a simple get not stream


            #Lichess Stream
            if state.want_lichess_stream:
                lichessEvent: models.LichessEvent = await consumeQueue(lichessEventQueue)
                if lichessEvent: #If didn't return None
                    processLichessStream(lichessEvent)

                        

            #Board Stream
            if state.is_in_game and state.want_board_stream:
                boardEvent: models.BoardEvent = await consumeQueue(gameEventQueue)
                if boardEvent:
                    gameID = boardEvent.gameID                    
                    logicDict[gameID].handle_game_event(boardEvent)
                    app.update_board()
                    if boardEvent.winner:
                        state.is_in_game = False
                        #do winner code in here, display to gui, etc


            #GUI Input
            if state.want_gui:
                guiInput: models.GUIToMainEvent = await consumeQueue(guiQueue)
                if(guiInput):
                    if state.is_in_game:
                        if(guiInput.event_type == guiInput.Type.MOVE):
                            
                            gameID = list(logicDict.keys())[0] #Horribly jank - add game selector
                            #let gui save gameID key to pass during moves
                            userInput = guiInput.move

                            valid, reason = logicDict[gameID].validateMove(userInput)
                            if valid:
                                #send to client
                                asyncio.create_task(client.postMove(gameID, userInput))
                            else:
                                print(f"ERROR: \"{userInput}\" IS NOT A VALID MOVE REASON: \"{reason}\"")




            await asyncio.sleep(0.01) 
            # IMPORTANT - allows for coroutine to switch so client can receive/process data
#----------------------------------------- END MAIN CONTROL LOOP ---------------------------------

    state = models.LoopState(
            is_running=True,
            is_in_game=False,
            want_account=False,
            want_lichess_stream=True,
            want_board_stream=True,
            want_input=True,
            want_gui=True,
        )       #Program state
    
    


    accountQueue = asyncio.Queue()
    lichessEventQueue = asyncio.Queue()
    gameEventQueue = asyncio.Queue()
    userInputQueue = asyncio.Queue()
    guiQueue = queue.Queue()
    #Queues for retreiving data from client

    client = LichessClient()
    logicDict = {}
    #Eventually add multi-game support. as of right now, it will break with 2 games.

    app = App(guiToMainQueue=guiQueue)

    asyncio.create_task(streamWrapper(client.LICHESS_STREAM, lichessEventQueue))
    boardStreamTask = None 
    #async tell client to call api and return data to queue

    app.start()
    asyncio.create_task(app.fake_main_loop())

    await mainControlLoop()




if __name__ == "__main__":
    asyncio.run(main())
