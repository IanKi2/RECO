import requests
import json

SERVER_URL = "https://games-test.datsteam.dev/"
TOKEN = "63bf8b86-1505-4f25-b160-27342aa20c58"

def get_arena():
    url = SERVER_URL + "api/arena"
    headers = {
        "Accept": "application/json",
        "X-Auth-Token": TOKEN
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при запросе состояния арены: {response.status_code}")
        return None

def post_move(moves):
    url = SERVER_URL + "api/move"
    headers = {
        "Accept": "application/json",
        "X-Auth-Token": TOKEN,
        "Content-Type": "application/json"
    }
    data = json.dumps({"moves": moves})
    response = requests.post(url, headers=headers, data=data)
    return response.status_code, response.text