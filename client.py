import aiohttp
import dotenv
import os
import json
import requests
import models
TOKEN = os.getenv("LICHESS_TOKEN")


class LichessClient:
    def __init__ (self):
        self.aSession = aiohttp.ClientSession(
            headers = {"Authorization": f"Bearer {TOKEN}"}
        )
    
    async def getAccount(self, queue):
        async with self.aSession.get(
            "https://lichess.org/api/account"
        ) as response:
            data = await response.json()
            profile = models.Profile(data)
            await queue.put(profile)


    async def lichessStream(self, queue):
        async with self.aSession.get(
            "https://lichess.org/api/stream/event"
        ) as response:
            print(f"Lichess Stream Status: {response.status}")
            async for line in response.content:
                line = line.decode().strip()
                if not line:
                    continue
                data = json.loads(line)
                print(data)
                event = models.LichessEvent(data)
                await queue.put(event)

        for i in range(30): print("--------------RESETTING LICHESS STREAM ------------")
        self.lichessStream(queue)
        #call endpoint, print status, read stream lines,
        #ignore empty lines, convert to json, put data in model structure,
        #put in queue

    async def boardStateStream(self, queue, gameID):
        async with self.aSession.get(
            f"https://lichess.org/api/board/game/stream/{gameID}"
        ) as response:
            print(f"Board State Stream Status: {response.status}") 
            async for line in response.content:
                line = line.decode().strip()
                if not line:
                    continue
                data = json.loads(line)
                event = models.BoardEvent(data)
                await queue.put(event)

    #Make move
    async def postMove(self, gameID, move, offerdraw = False, queue = None):
        async with self.aSession.post(
            url = f"https://lichess.org/api/board/game/{gameID}/move/{move}"
        ) as response:
            print(f"Send Move Status: {response.status}")
