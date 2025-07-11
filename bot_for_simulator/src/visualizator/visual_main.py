import os
import time
import multiprocessing
import queue

def visualization_process(viz_queue: multiprocessing.Queue):
    """Процесс визуализации игрового состояния с помощью emoji"""
    print("Emoji visualizer started")
    last_state = None
    
    while True:
        try:
            state, viz_data = viz_queue.get(timeout=0.1)
            last_state = state
        except queue.Empty:
            pass
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Visualizer error: {str(e)}")
            continue
        
        if last_state:
            display_game(last_state, viz_data)
        
        time.sleep(1)

def display_game(state: dict, viz_data: dict):
    """Визуализация игрового поля с помощью emoji"""
    # Динамически определяем размеры мира
    width = state.get('width', 50)
    height = state.get('height', 50)
    
    # Создаем пустое поле
    grid = [['⬜️' for _ in range(width)] for _ in range(height)]
    
    # Добавляем маршрут (если есть)
    path = viz_data.get('path', [])
    for x, y in path:
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = '🟢'  # Зеленая точка для маршрута
    
    # Расставляем объекты (перекрывают маршрут)
    for x, y in state.get('obstacles', []):
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = '🧱'  # Препятствие
    
    for x, y in state.get('resources', []):
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = '💎'  # Ресурс
    
    for x, y in state.get('npcs', []):
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = '👾'  # NPC
    
    # Отображаем агента (перекрывает все)
    agent = state['agent']
    ax, ay = agent['x'], agent['y']
    if 0 <= ax < width and 0 <= ay < height:
        grid[ay][ax] = '🤖'  # Агент
    
    # Очищаем экран
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Выводим информацию
    print(f"\nМир: {width}×{height} | Счет: {state['score']} | Респавны: {state['respawns']}")
    print(f"Агент: ({ax}, {ay}) | Маршрут: {len(path)} точек")
    print("=" * (width * 2))
    
    start_x = 0
    end_x = width
    start_y = 0
    end_y = height
    
    for y in range(start_y, end_y):
        row = grid[y][start_x:end_x]
        print(''.join(row))
    
    print("=" * (width * 2))
    print(f"NPC: {len(state.get('npcs', []))} "
          f"| Ресурсы: {len(state.get('resources', []))} "
          f"| Препятствия: {len(state.get('obstacles', []))}")