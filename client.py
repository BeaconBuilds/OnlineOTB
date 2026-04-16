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
    MOVE_POST = "https://lichess.org/api/board/game/{gameID}/move/{move}", models.PostModel
    RESIGN_POST = "https://lichess.org/api/board/game/{gameID}/resign", models.PostModel
    DRAW_POST = "https://lichess.org/api/board/game/{gameID}/draw/{yesNo}", models.PostModel
    TAKEBACK_POST = "https://lichess.org/api/board/game/{gameID}/takeback/{yesNo}", models.PostModel
    CLAIM_VICTORY_POST = "https://lichess.org/api/board/game/{gameID}/claim-victory", models.PostModel
    ABORT_POST = "https://lichess.org/api/board/game/{gameID}/abort", models.PostModel
    SEND_CHAT_POST =  "https://lichess.org/api/board/game/{gameID}/chat", models.PostModel
    FETCH_CHAT_GET = "https://lichess.org/api/board/game/{gameID}/chat"#, models.FetchChat

    def __init__ (self):
        self.aSession = aiohttp.ClientSession(
            headers = {"Authorization": f"Bearer {TOKEN}"}
        )
    

    async def genericPost(self, template: tuple,
                           gameID: str = None,
                           yesNo: str = None,
                           move:str = None):
        url, modelClass = template

        if template == self.RESIGN_POST:
            url = url.format(gameID = gameID)

        elif template == self.DRAW_POST:
            url = url.format(gameID = gameID, yesNo = yesNo)
            print(f"now trying to send draw post {url}")

        elif template == self.MOVE_POST:
            url = url.format(gameID = gameID, move = move)

        async with self.aSession.post(url) as response:
            model = models.PostModel(
                url=url,
                status= response.status(),
                data = await response.text()
            )
            yield model



    async def getAccount(self, queue):
        async with self.aSession.get(
            "https://lichess.org/api/account"
        ) as response:
            data = await response.json()
            profile = models.Profile(data)
            await queue.put(profile)




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
                    

                    if gameID:
                        event = modelClass(data = jsonData, gameID=gameID) 
                    #if gameID was passed to the stream then 
                    else:
                        event = modelClass(jsonData)

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
