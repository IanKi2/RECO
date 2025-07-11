import requests
import time
import multiprocessing
import queue
from algorithms.botai import BotAI
from algorithms.astar import AStarBot
from visualizator.visual_main import visualization_process


def send_command(command: dict = None, server_url: str = None) -> dict:
    """
    Отправляет команду на сервер.
    Если команда не указана, отправляет {"command": "attack"} по умолчанию.
    """

    if command is None:
        command = {"command": "attack"}
    
    while True:
        try:
            response = requests.post(server_url, json=command)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Server error: {response.status_code}, retrying...")
                time.sleep(1)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            time.sleep(1)
        except Exception as e:
            print(f"Network error: {str(e)}")
            time.sleep(1)

def parse_state(response: dict) -> dict:
    """Преобразует сырой ответ сервера в структурированное состояние"""
    return {
        "width": response["width"],  # <-- Добавляем ширину
        "height": response["height"],  # <-- Добавляем высоту
        "agent": {
            "x": response["agent"]["x"],
            "y": response["agent"]["y"]
        },
        "npcs": [(n["x"], n["y"]) for n in response["visible_entities"]["npcs"]],
        "resources": [(r["x"], r["y"]) for r in response["visible_entities"]["resources"]],
        "obstacles": [(o["x"], o["y"]) for o in response["visible_entities"]["obstacles"]],
        "score": response["score"],
        "respawns": response["respawns"]
    }

if __name__ == "__main__":
    SERVER_URL = "http://0.0.0.0:5000/command"
    VISION_RADIUS = 5
    
    # Создаем очередь для визуализации
    viz_queue = multiprocessing.Queue(maxsize=1)
    
    # Запускаем процесс визуализации
    visualizer = multiprocessing.Process(
        target=visualization_process,
        args=(viz_queue,),
        daemon=True
    )
    visualizer.start()
    print("Visualizer process started with PID:", visualizer.pid)

    # Инициализируем бота
    bot = AStarBot(config={"vision_radius": VISION_RADIUS})
    
    try:
        # Начинаем без начальной команды
        current_command = None
        
        while True:
            # Отправляем команду (по умолчанию attack) и получаем ответ
            raw_response = send_command(current_command, SERVER_URL)
            
            if not raw_response:
                print("Server unavailable, retrying...")
                time.sleep(1)
                continue
            
            # Парсим состояние
            parsed_state = parse_state(raw_response)
            
            # Добавляем радиус видимости
            parsed_state["vision_radius"] = VISION_RADIUS
            
            # Получаем решение от бота для следующего шага
            current_command, viz_data = bot.step(parsed_state)

            # Отправляем данные в визуализатор
            try:
                viz_queue.put_nowait((parsed_state, viz_data))
            except queue.Full:
                pass  # Пропускаем кадр если очередь заполнена
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nBot stopped")
    finally:
        print("Shutting down")