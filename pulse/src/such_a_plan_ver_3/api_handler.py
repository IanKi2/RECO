import requests
import json

SERVER_URL = "https://games-test.datsteam.dev/"
TOKEN = "63bf8b86-1505-4f25-b160-27342aa20c58"

headers = {
    "Accept": "application/json",
    "X-Auth-Token": TOKEN,
    "Content-Type": "application/json"
}

def get_arena():
    response = requests.get(f"{SERVER_URL}/api/arena", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"GET /api/arena failed: {response.status_code}")

def post_move(moves):
    payload = {"moves": moves}
    response = requests.post(
        f"{SERVER_URL}/api/move",
        headers=headers,
        data=json.dumps(payload))
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"POST /api/move failed: {response.status_code}")