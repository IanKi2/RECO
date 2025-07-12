import requests

SERVER_URL = "https://games-test.datsteam.dev/"
TOKEN = "63bf8b86-1505-4f25-b160-27342aa20c58"

def get_arena():
    url = f"{SERVER_URL}api/arena"
    headers = {
        "Accept": "application/json",
        "X-Auth-Token": TOKEN
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"GET /api/arena failed: {response.status_code}")

def post_move(moves):
    url = f"{SERVER_URL}api/move"
    headers = {
        "Accept": "application/json",
        "X-Auth-Token": TOKEN,
        "Content-Type": "application/json"
    }
    payload = {"moves": moves}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"POST /api/move failed: {response.status_code}")