import requests
import config

HEADERS = {
    "Accept": "application/json",
    "X-Auth-Token": config.TOKEN,
    "Content-Type": "application/json"
}

def get_arena():
    response = requests.get(
        f"{config.SERVER_URL}/api/arena",
        headers=HEADERS
    )
    return response.json()

def post_move(moves):
    formatted_moves = []
    for move in moves:
        path = [{"q": q, "r": r} for q, r in move['path']]
        formatted_moves.append({
            "ant": move['ant_id'],
            "path": path
        })
    
    response = requests.post(
        f"{config.SERVER_URL}/api/move",
        json={"moves": formatted_moves},
        headers=HEADERS
    )
    return response.json()