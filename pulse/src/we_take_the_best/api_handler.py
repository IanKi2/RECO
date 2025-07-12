import requests

SERVER_URL = "https://games-test.datsteam.dev/"
TOKEN = "63bf8b86-1505-4f25-b160-27342aa20c58"

HEADERS = {
    "Accept": "application/json",
    "X-Auth-Token": TOKEN,
    "Content-Type": "application/json"
}

def get_arena():
    """Получение состояния арены"""
    response = requests.get(
        f"{SERVER_URL}/api/arena",
        headers=HEADERS
    )
    return response.json()

def post_move(moves):
    """Отправка движений юнитов"""
    formatted_moves = []
    for move in moves:
        path = [{"q": q, "r": r} for q, r in move['path']]
        formatted_moves.append({
            "ant": move['ant_id'],
            "path": path
        })
    
    response = requests.post(
        f"{SERVER_URL}/api/move",
        json={"moves": formatted_moves},
        headers=HEADERS
    )
    return response.json()