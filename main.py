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


#game full isnt lichess even its a board event stupid


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
    
    async def userInputLoop(state):
        while state.is_running:
            input = await ainput("> ")
            if input:
                await userInputQueue.put(input)
                print(f"User typed : {input}")            

#---------------- Wrapper for Generic Stream
    async def streamWrapper(clientTemplate : tuple,
                            queue: asyncio.Queue,
                            gameID : str = None):
        try:
            retryConnection = True

            while retryConnection:
                async for result in client.genericStream(clientTemplate, gameID=gameID):
                    if not result.ok:
                        print(f"\n***STREAM ERROR***"
                            f"\n{f"Status: {result.status}" if result.status else "No Status "}"
                            #f"\n{f"Headers: {result.headers}" if result.headers else "No Headers"}"
                            f"\nError: {str(result.error)}\n"
                        )
                        break
                        #print error and break to retry connection
                        #change to logging in gui eventually

                    elif result.ended:
                        retryConnection = False
                        print("Graceful stream shutdown")
                        break
                        #if loop ended normally

                    elif result.heartbeat:
                        continue
                        #not used right now, maybe turn into timeout checker?
                        #or just edit aiohttp config?

                    elif result.data:
                        print(f"\nData:{json.dumps(result.data, indent=4)}")
                        print(f"Model Output: \n{result.model}")
                        await queue.put(result.model)
                    else:
                        print(
                            f"Stream for URL: {clientTemplate[0]}"
                            f"\n{f"Status: {result.status}" if result.status else "No Status "}"
                            #f"\n{f"Headers: {result.headers}" if result.headers else "No Headers"}"
                        )

                await asyncio.sleep(2) # dont spam endpoint

        except asyncio.CancelledError as e:
            print("Task canceled on purpose")
            return


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
                    print(f"Lichess Event printout{lichessEvent}")
                    if lichessEvent.eventType == "gameStart": 
                        gameID = lichessEvent.gameID
                        logic = ChessLogic(lichessEvent)
                        state.is_in_game = True
                        boardStreamTask = asyncio.create_task(streamWrapper(client.BOARD_STREAM, gameEventQueue, gameID=gameID))
                        #if game started then tell client to start streaming the board of gameID                 
                        print(f"Game Started - Game ID : {gameID}")
                    if lichessEvent.eventType == "gameFinish":
                        print(f"Game Finished - Winner: {lichessEvent.winner}")
                        

            #Board Stream
            if state.is_in_game and state.want_board_stream:
                boardEvent: models.BoardEvent = await consumeQueue(gameEventQueue)
                if boardEvent:                    
                    logic.handle_game_event(boardEvent)
                    app.update_board()
                    if boardEvent.winner:
                        state.is_in_game = False
                        #do winner code in here, display to gui, etc

        
            #User Input
            if state.want_input and state.is_in_game:
                userInput = await consumeQueue(userInputQueue)
                if userInput:
                    userInput = userInput.strip().lower()
                    valid, reason = logic.validateMove(userInput)
                    if valid:
                        #send to client
                        asyncio.create_task(client.postMove(logic.gameID, userInput))
                        #state.want_input = False
                    else:
                        print(f"ERROR: \"{userInput}\" IS NOT A VALID MOVE REASON: \"{reason}\"")


            #GUI Input
            if state.want_gui:
                guiInput: models.GUIToMainEvent = await consumeQueue(guiQueue)
                if(guiInput):
                    if state.is_in_game:
                        if(guiInput.event_type == guiInput.Type.MOVE):
                            valid, reason = logic.validateMove(guiInput.move)
                            if valid:
                                #send to client
                                asyncio.create_task(client.postMove(logic.gameID, guiInput.move))
                                #state.want_input = False
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
            want_gui=True
        )       #Program state
    
    


    accountQueue = asyncio.Queue()
    lichessEventQueue = asyncio.Queue()
    gameEventQueue = asyncio.Queue()
    userInputQueue = asyncio.Queue()
    guiQueue = queue.Queue()
    #Queues for retreiving data from client

    client = LichessClient()
    logic = None
    app = App(guiToMainQueue=guiQueue)

    lichessStreamTask = asyncio.create_task(streamWrapper(client.LICHESS_STREAM, lichessEventQueue))
    boardStreamTask = None 
    #async tell client to call api and return data to queue

    #asyncio.create_task(userInputLoop(state))
    #user input

    app.start()
    asyncio.create_task(app.fake_main_loop())

    await mainControlLoop()




if __name__ == "__main__":
    asyncio.run(main())
