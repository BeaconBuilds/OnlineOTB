from dotenv import load_dotenv
import os
import requests

load_dotenv("../.env")

token = os.getenv("LICHESS_TOKEN")

headers = {
    "Authorization": f"Bearer {token}"
}

response = requests.get("https://lichess.org/api/account", headers=headers)

print(response.json())