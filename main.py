from client import LichessClient
from logic import ChessLogic
from gui.app import App
from aioconsole import ainput
import queue
import asyncio
import models
import sys




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

    async def postWrapper(clientTemplate : tuple,
                          url_data: dict = None,
                          post_data: dict = None):
        try:
            maxTries = 10
            for i in range(maxTries):
                async for result in client.genericPost(clientTemplate, url_data=url_data, post_data=post_data):
                    if result.ok:
                        if i != 0:
                            print(f"Successful post Attempt {i}")
                            print(f"At endpiont {result.endpoint}")
                        return
                    elif not result.ok:
                        print(f"***Post Error attempt {i}***")
                        print(f"At endpoint {result.endpoint}")
                        print(f"Error: {result.error}")
                        if i < maxTries-1:
                            print(f"retrying...")
        except Exception as e:
            pass             

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
                            f"\nURL: {clientTemplate[0]}"
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

                        continue
                        #not used right now, maybe turn into timeout checker?
                        #or just edit aiohttp config?

                    elif result.data:
                        #print(f"\nData:{json.dumps(result.data, indent=4)}")
                        print(f"Model Output: \n{result.model}")
                        await queue.put(result.model)


                print("Stream loop exited, retrying...")
                await asyncio.sleep(7) # retry delay

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


    #write resign, draw, etc
    def processGUIEvent(guiInput: models.GUIToMainEvent):
        if state.is_in_game:
            if(guiInput.event_type == guiInput.Type.MOVE):
            
                gameID = guiInput.gameID
                userInput = guiInput.move

                valid, reason = logicDict[gameID].validateMove(userInput)
                if valid:
                    url_data = {"gameID":gameID,
                            "move":userInput}
                    asyncio.create_task(postWrapper(client.MOVE_POST, url_data=url_data))
                else:
                    print(f"ERROR: \"{userInput}\" IS NOT A VALID MOVE, REASON: \"{reason}\"")

            if(guiInput.event_type == guiInput.Type.RESIGN):
                url_data = {"gameID":guiInput.gameID,
                        "yesNo":guiInput.yesNo}
                asyncio.create_task(postWrapper(client.RESIGN_POST, url_data=url_data))

            if(guiInput.event_type == guiInput.Type.DRAW):
                daurl_datata = {"gameID":guiInput.gameID,
                        "yesNo":guiInput.yesNo}
                asyncio.create_task(postWrapper(client.DRAW_POST, url_data=url_data))
        
        if(guiInput.event_type == guiInput.Type.CHALLENGE):
            url_data = {"username":guiInput.challenge_data.username}
            post_data = guiInput.challenge_data.data
            asyncio.create_task(postWrapper(client.CHALLENGE_POST, url_data=url_data, post_data=post_data))  
        
        if(guiInput.event_type == guiInput.Type.EXIT_PROGRAM):
                sys.exit(0)

    def processBoardEvent(boardEvent: models.BoardEvent):
        #if chatline
        gameID = boardEvent.gameID

        if boardEvent.eventType in ("gameState", "gameFull"):                     
            logicDict[gameID].handle_game_event(boardEvent)
            app.game.update_board(game_id=gameID)
            if logicDict[gameID].color: #if youre white
                app.game.set_my_time(boardEvent.wtime, boardEvent.initialTime)
                app.game.set_op_time(boardEvent.btime, boardEvent.initialTime)
            elif not logicDict[gameID].color: #if youre black
                app.game.set_my_time(boardEvent.btime, boardEvent.initialTime)
                app.game.set_op_time(boardEvent.wtime, boardEvent.initialTime)
            
            app.game.set_turn(logicDict[gameID].is_my_turn)

            if boardEvent.status == "resign":
                logicDict[gameID].resign(winner = boardEvent.winner)


            if boardEvent.winner:
                state.is_in_game = False
                app.game.set_end(logicDict[gameID].win_lose_draw, logicDict[gameID].gameEndReason)
                #do winner code in here, display to gui, etc
        if boardEvent.eventType == "chatLine":
            app.game.add_chat_line(boardEvent.chatUsername, boardEvent.chatText)
            print(f"New CHATLINE: {boardEvent.chatUsername}: {boardEvent.chatText}")



    def processMatrixEvent(matrixData : models.MatrixToMain):
        if matrixData.eventType == matrixData.Type.BOARD_CHANGE:
            pass


#--------------------START-MAIN-LOOP------------------------------------------------------#
    async def mainControlLoop():

        while state.is_running:

            #Account
            if state.want_account:
                account = await consumeQueue(accountQueue)
                if account:
                    print(f"Account Grab successful: {account.username}")
                    state.want_account = False
                    #state is switched because its just a simple get not stream

            #Lichess Stream
            if state.want_lichess_stream:
                lichessEvent: models.LichessEvent = await consumeQueue(lichessEventQueue)
                if lichessEvent: #If didn't return None
                    processLichessStream(lichessEvent)

                        

            #Board Stream
            if state.is_in_game and state.want_board_stream:
                boardEvent: models.BoardEvent = await consumeQueue(gameEventQueue)
                if boardEvent:
                    processBoardEvent(boardEvent)


            #GUI Input
            if state.want_gui:
                guiInput: models.GUIToMainEvent = await consumeQueue(guiQueue)
                if(guiInput):
                    processGUIEvent(guiInput=guiInput)


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
    guiQueue = queue.Queue()
    matrixQueue = queue.Queue()
    #Queues for retreiving data from client

    client = LichessClient()
    logicDict = {}
    
    

    #Eventually add multi-game support. as of right now, it will break with 2 games.

    app = App(guiToMainQueue=guiQueue)

    asyncio.create_task(streamWrapper(client.LICHESS_STREAM, lichessEventQueue))
    #async tell client to call api and return data to queue

    app.start()
    #asyncio.create_task(app.fake_main_loop())

    await mainControlLoop()




if __name__ == "__main__":
    asyncio.run(main())
