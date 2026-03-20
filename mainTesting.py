from dotenv import load_dotenv
from lichessClient import callbackOnEven
import json
import os
import requests


load_dotenv("../.env")

token = os.getenv("LICHESS_TOKEN")

headers = {
    "Authorization": f"Bearer {token}"
}

#response = requests.get("https://lichess.org/api/account", headers=headers)

#print(json.dumps(response.json(), indent=4))

def respondToCallback(num):
    print(f"the callback sent was {num}")

callbackOnEven(respondToCallback)