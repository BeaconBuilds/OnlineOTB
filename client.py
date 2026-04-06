import aiohttp
import dotenv
import os
import json
import requests
import models
import typing
TOKEN = os.getenv("LICHESS_TOKEN")


class LichessClient:

    ACCOUNT_GET = "https://lichess.org/api/account", models.Profile
    LICHESS_STREAM = "https://lichess.org/api/stream/event", models.LichessEvent
    BOARD_STREAM = "https://lichess.org/api/board/game/stream/{gameID}", models.BoardEvent

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

    async def genericStream(self,
                            template: tuple, 
                            gameID: str | None = None
                            ) -> typing.AsyncGenerator[models.StreamModel, None]:

        url, modelClass = template
        if template == self.BOARD_STREAM:
            if not gameID:
                print("ERROR: no gameID found")
                return
            url = url.format(gameID = gameID)

        try:
            async with self.aSession.get(url) as response:
                response.raise_for_status()
                initialRes = models.StreamModel(
                    status=response.status,
                    headers=response.headers
                )
                yield initialRes
                async for line in response.content:
                    line = line.decode().strip()
                    if not line:
                        heartbeatRes = models.StreamModel(heartbeat=True)
                        yield heartbeatRes
                        continue

                    jsonData = json.loads(line)
                    event = modelClass(jsonData)

                    if template == self.BOARD_STREAM:
                        event = modelClass(jsonData, gameID)      

                    newRes = models.StreamModel(
                        data=jsonData,
                        model=event
                    )     
                    yield newRes

                ended = models.StreamModel(
                    ended=True
                )
                yield ended

        except aiohttp.ClientResponseError as e:
            error = models.StreamModel(
                status=e.status,
                headers=e.headers,
                error = e,
                ok = False
            )
            yield error
            return

        except Exception as e:
            error = models.StreamModel(
                status=response.status,
                headers=response.headers,
                error = e,
                ok = False
            )
            yield error
            return


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
