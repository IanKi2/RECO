import requests
import os
import time

SERVER_URL = "http://0.0.0.0:5000"  # Адрес сервера

def get_full_state():
    """Получение полного состояния игры"""
    try:
        response = requests.get(f"{SERVER_URL}/full-state", timeout=5)
        if response.status_code == 200:
            return response.json()
        print(f"Ошибка сервера: {response.status_code}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка соединения: {str(e)}")
        return None

def display_game(state):
    """Визуализация игрового поля с помощью emoji"""
    width = state['width']
    height = state['height']
    
    # Создаем пустое поле
    grid = [['⬜️' for _ in range(width)] for _ in range(height)]
    
    # Расставляем объекты (в порядке приоритета отображения)
    for obj in state['obstacles']:
        if 0 <= obj['x'] < width and 0 <= obj['y'] < height:
            grid[obj['y']][obj['x']] = '🧱'  # Препятствия
    
    for res in state['resources']:
        if 0 <= res['x'] < width and 0 <= res['y'] < height:
            grid[res['y']][res['x']] = '💎'  # Ресурсы
    
    for npc in state['npcs']:
        if 0 <= npc['x'] < width and 0 <= npc['y'] < height:
            grid[npc['y']][npc['x']] = '👾'  # NPC
    
    # Отображаем агента (поверх других объектов)
    agent = state['agent']
    if 0 <= agent['x'] < width and 0 <= agent['y'] < height:
        # Выбираем emoji в зависимости от направления
        direction_emoji = {
            'up': '👆',
            'down': '👇',
            'left': '👈',
            'right': '👉'
        }
        grid[agent['y']][agent['x']] = direction_emoji.get(agent['direction'], '👤')
    
    # Очищаем экран
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Рисуем поле
    print(f"\nПоле: {width}×{height} | Счет: {state['score']} | Респавны: {state['respawns']}")
    print("=" * (width * 2))
    for row in grid:
        print(''.join(row))
    print("=" * (width * 2))
    print(f"Агент: ({agent['x']}, {agent['y']}) "
          f"| NPC: {len(state['npcs'])} "
          f"| Ресурсы: {len(state['resources'])} "
          f"| Препятствия: {len(state['obstacles'])}")

def main():
    """Основной цикл визуализатора"""
    print("Запуск визуализатора игры...")
    print("Ожидание инициализации игры на сервере")
    
    while True:
        state = get_full_state()
        
        if state:
            display_game(state)
        else:
            print("Игра не инициализирована или сервер недоступен...")
        
        time.sleep(0.2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nВизуализатор остановлен")