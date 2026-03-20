import aiohttp
import dotenv
import os
import json
import requests
TOKEN = os.getenv("LICHESS_TOKEN")

class LichessClient:
    def __init__ (self):
        self.aSession = aiohttp.ClientSession(
            headers = {"Authorization": f"Bearer {TOKEN}"}
        )
    
    async def makeSeek(self, rated = False, variant = "standard", ratingRange = "", time = 1, increment = 0, color = ""):
        headers = self.aSession.headers.copy()
        headers.update({"Content-Type": "application/x-www-form-urlencoded"})
        async with self.aSession.post(
            url = "https://lichess.org/api/board/seek",
            headers=headers,
            data={
                "rated" : str(rated).lower(),
                "variant" : variant,
                "ratingRange" : ratingRange,
                "time" : str(time),
                "increment" : str(increment),
                "color" : color
            }
        ) as response:
            line = await response.text()
            print(f"MAKE SEEK FUNCTION RESPONE: {line}")

    async def getAccount(self):
        async with self.aSession.get(
            "https://lichess.org/api/account"
        ) as response:
            data = await response.json()
        print(json.dumps(data, indent=4))


    async def lichessStream(self):
        async with self.aSession.get(
            "https://lichess.org/api/stream/event"
        ) as response:
            async for line in response.content:
                print(line)


    async def gameStream (self, gameID: str):
        async with self.aSession.get(
            f"https://lichess.org/api/board/game/stream/{gameID}"
        ) as response:
            async for line in response.content:
                print(line)

    async def seekGame():
        pass




#def callbackOnEven(callback):
#    for i in range(10):
#        if i%2 == 0:
#            callback(i)