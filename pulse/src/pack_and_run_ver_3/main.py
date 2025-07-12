import time
from api_handler import get_arena, post_move
from brain import decide_ant_move, hex_distance

def trim_path_to_mp(path, grid_info, max_mp):
    if len(path) <= 1:
        return path
    
    current_mp = 0
    trimmed_path = [path[0]]
    
    for i in range(1, len(path)):
        current = path[i-1]
        next_hex = path[i]
        
        # Получаем стоимость перехода
        cost = grid_info.get(next_hex, {}).get('cost', 1)
        if cost >= 1000:  # Непроходимая клетка
            break
        
        # Проверяем, хватит ли ОП
        if current_mp + cost > max_mp:
            break
            
        current_mp += cost
        trimmed_path.append(next_hex)
        
        # Если достигли лимита ОП - выходим
        if current_mp >= max_mp:
            break
    
    return trimmed_path

def main():
    while True:
        start_time = time.time()
        state = get_arena()
        if not state:
            time.sleep(0.1)
            continue
        
        grid_info = {}
        for cell in state['map']:
            grid_info[(cell['q'], cell['r'])] = cell
        
        # Определяем вражеские муравейники
        our_home_hexes = set((h['q'], h['r']) for h in state['home'])
        enemy_anthills = []
        for cell in state['map']:
            if cell['type'] == 1:  # тип муравейника
                coord = (cell['q'], cell['r'])
                if coord not in our_home_hexes:
                    enemy_anthills.append(coord)
        
        moves = []
        occupied = set()
        
        # Сначала собираем все занятые клетки
        for enemy in state.get('enemies', []):
            occupied.add((enemy['q'], enemy['r']))
        for other in state['ants']:
            occupied.add((other['q'], other['r']))
        
        for ant in state['ants']:
            ant_type = ant['type']
            if ant_type == 0:  # Рабочий
                max_mp = 5
            elif ant_type == 1:  # Боец
                max_mp = 4
            elif ant_type == 2:  # Разведчик
                max_mp = 7
            else:
                continue
            
            # Временно освобождаем текущую позицию муравья
            current_pos = (ant['q'], ant['r'])
            if current_pos in occupied:
                occupied.remove(current_pos)
            
            path = decide_ant_move(
                ant,
                grid_info,
                occupied,
                state.get('food', []),
                state['home'],
                state['spot'],
                max_mp,
                enemy_anthills
            )
            
            # Обрезаем путь по доступным ОП
            trimmed_path = trim_path_to_mp(path, grid_info, max_mp)
            
            # Убираем стартовую позицию
            final_path = trimmed_path[1:] if len(trimmed_path) > 1 else []
            
            # Если путь ведет к цели - резервируем конечную позицию
            if final_path:
                occupied.add(final_path[-1])
            
            moves.append({
                "ant": ant['id'],
                "path": [{"q": q, "r": r} for q, r in final_path]
            })
            
            # Возвращаем текущую позицию в занятые
            occupied.add(current_pos)
        
        status, response = post_move({"moves": moves})
        print(f"Move status: {status}, Response: {response}")
        
        elapsed = time.time() - start_time
        sleep_time = state['nextTurnIn'] / 1000.0 - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

if __name__ == "__main__":
    main()