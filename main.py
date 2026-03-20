from dotenv import load_dotenv
from client import LichessClient
import logic
import json
import os
import requests
import asyncio


async def main():
    client = LichessClient()
    print("client ran")
    await client.getAccount()
    print("getting account")

    await client.makeSeek()
    #await client.lichessStream()



if __name__ == "__main__":
    asyncio.run(main())
    print("running main")