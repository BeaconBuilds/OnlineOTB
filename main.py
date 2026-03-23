from dotenv import load_dotenv
from client import LichessClient
from logic import ChessLogic
from aioconsole import ainput
import logic
import json
import os
import requests
import asyncio
import models




async def main():


    async def consumeQueue(queue):
        try:   
            data = queue.get_nowait()
            return data
        except asyncio.QueueEmpty:
            pass
    
    async def userInputLoop(state):
        while state.is_running:
            input = await ainput("> ")
            if input:
                await userInputQueue.put(input)
                print(f"User typed : {input}")            


    state = models.LoopState(
            is_running=True,
            is_in_game=False,
            want_account=False,
            want_lichess_stream=True,
            want_board_stream=True,
            want_input=True
        )       
    #Program state

    print(state)
    
    client = LichessClient()
    logic = None

    accountQueue = asyncio.Queue()
    lichessEventQueue = asyncio.Queue()
    gameEventQueue = asyncio.Queue()
    userInputQueue = asyncio.Queue()
    #Queues for retreiving data from client

    asyncio.create_task(client.getAccount(accountQueue))
    asyncio.create_task(client.lichessStream(lichessEventQueue)) 
    #async tell client to call api and return data to queue

    asyncio.create_task(userInputLoop(state))
    #user input

#---------------------MAIN-LOOP-----------------------#
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
            lichessEvent = await consumeQueue(lichessEventQueue)
            if lichessEvent: #If didn't return None
                if lichessEvent.eventType == "gameStart": 
                    gameID = lichessEvent.gameID
                    logic = ChessLogic(lichessEvent)
                    asyncio.create_task(client.boardStateStream(gameEventQueue, gameID))
                    #if game started then tell client to start streaming the board of gameID
                    state.is_in_game = True
                    print(f"Game Started - Game ID : {gameID}")
                if lichessEvent.eventType == "gameFinish":
                    print(f"Game Finished - Winner: {lichessEvent.winner}")
                    state.is_in_game = False

        #Board Stream
        if state.is_in_game and state.want_board_stream:
            boardEvent = await consumeQueue(gameEventQueue)
            if boardEvent:
                logic.handle_game_event(boardEvent)
                print(f"Moves: {boardEvent.moves}")

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


        await asyncio.sleep(0.01) 
        # IMPORTANT - allows for coroutine to switch so client can receive/process data


if __name__ == "__main__":
    asyncio.run(main())
    print("running main")
