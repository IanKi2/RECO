from queue import PriorityQueue

def hex_distance(a, b):
    q1, r1 = a
    q2, r2 = b
    return (abs(q1 - q2) + abs(r1 - r2) + abs(q1 + r1 - q2 - r2)) // 2

def get_neighbors(hex_coord):
    q, r = hex_coord
    neighbors = []
    if r % 2 == 0:
        directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (0, 1), (1, 1)]
    else:
        directions = [(1, 0), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]
    
    for dq, dr in directions:
        neighbors.append((q + dq, r + dr))
    return neighbors

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

def is_safe_zone(coord, enemy_anthills, min_distance=2):
    for anthill in enemy_anthills:
        if hex_distance(coord, anthill) < min_distance:
            return False
    return True

def a_star(start, goals, max_cost, grid_info, occupied, enemy_anthills):
    goals_set = set(goals)
    if start in goals_set:
        return [start]
    
    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: min(hex_distance(start, goal) for goal in goals)}
    
    best_node = start
    best_f = f_score[start]
    best_goal = None
    
    while not open_set.empty():
        _, current = open_set.get()
        
        if current in goals_set:
            return reconstruct_path(came_from, current)
        
        if f_score.get(current, float('inf')) < best_f:
            best_node = current
            best_f = f_score[current]
            best_goal = min(goals, key=lambda g: hex_distance(current, g))
        
        for neighbor in get_neighbors(current):
            if not is_safe_zone(neighbor, enemy_anthills):
                continue
                
            if neighbor in occupied:
                continue
                
            if neighbor not in grid_info:
                continue
                
            if grid_info[neighbor]['cost'] >= 1000:
                continue
            
            cost = grid_info[neighbor]['cost']
            tentative_g = g_score[current] + cost
            if tentative_g > max_cost:
                continue
                
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + min(hex_distance(neighbor, goal) for goal in goals)
                open_set.put((f_score[neighbor], neighbor))
    
    # Если не достигли цели, но можем приблизиться к ней
    if best_goal:
        path_to_best = reconstruct_path(came_from, best_node)
        return path_to_best
    
    return [start]

def decide_ant_move(ant, grid_info, occupied, food, home, spot, max_mp, enemy_anthills):
    start = (ant['q'], ant['r'])
    home_hexes = [(h['q'], h['r']) for h in home]
    
    # Если несет ресурс - идем в муравейник
    if ant['food']['amount'] > 0:
        path = a_star(start, home_hexes, max_mp, grid_info, occupied, enemy_anthills)
        
        # Проверяем, достигли ли мы муравейника в этом ходе
        if path[-1] in home_hexes:
            return path
        
        # Если не достигли - пытаемся подойти максимально близко
        return path
    
    # Ищем ближайший безопасный ресурс
    food_hexes = [(f['q'], f['r']) for f in food]
    safe_food = [f for f in food_hexes if is_safe_zone(f, enemy_anthills)]
    targets = safe_food if safe_food else food_hexes
    
    if targets:
        path = a_star(start, targets, max_mp, grid_info, occupied, enemy_anthills)
        
        # Проверяем, достигли ли мы ресурса в этом ходе
        if path[-1] in targets:
            return path
            
        # Если не достигли - пытаемся подойти ближе
        return path
    
    # Если нет ресурсов - удаляемся от муравейника
    dq = ant['q'] - spot['q']
    dr = ant['r'] - spot['r']
    target = (ant['q'] + dq, ant['r'] + dr)
    
    # Генерируем безопасные направления
    possible_targets = []
    for direction in get_neighbors(start):
        if is_safe_zone(direction, enemy_anthills) and direction not in occupied:
            possible_targets.append(direction)
    
    if possible_targets:
        # Выбираем направление, максимально удаляющее от муравейника
        possible_targets.sort(key=lambda t: hex_distance(t, spot), reverse=True)
        return [start, possible_targets[0]]
    
    # Если нет безопасных направлений - остаемся на месте
    return [start]