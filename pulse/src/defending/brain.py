# brain.py
import heapq
from collections import defaultdict

def hex_distance(q1, r1, q2, r2):
    x1 = q1 - (r1 - (r1 & 1)) // 2
    z1 = r1
    y1 = -x1 - z1
    
    x2 = q2 - (r2 - (r2 & 1)) // 2
    z2 = r2
    y2 = -x2 - z2
    
    return (abs(x1 - x2) + abs(y1 - y2) + abs(z1 - z2)) // 2

def get_neighbors(q, r):
    return [
        (q + 1, r),    # Восток
        (q, r - 1),    # Северо-восток
        (q - 1, r - 1),# Северо-запад
        (q - 1, r),    # Запад
        (q - 1, r + 1),# Юго-запад
        (q, r + 1)     # Юго-восток
    ]

def find_path(start, goal, max_cost, game_state, danger_cells):
    start_pos = (start['q'], start['r'])
    goal_pos = (goal['q'], goal['r'])
    
    open_set = []
    heapq.heappush(open_set, (0, start_pos))
    
    came_from = {}
    cost_so_far = {start_pos: 0}
    came_from[start_pos] = None
    
    best_node = start_pos
    best_heuristic = float('inf')
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == goal_pos:
            best_node = current
            break
        
        h_current = hex_distance(current[0], current[1], goal_pos[0], goal_pos[1])
        if h_current < best_heuristic:
            best_heuristic = h_current
            best_node = current
        
        for neighbor in get_neighbors(*current):
            cell = game_state['grid'].get(neighbor)
            if not cell or cell['cost'] >= 1000:
                continue
            
            move_cost = cell['cost']
            if neighbor in danger_cells:
                move_cost += 100  # Штраф за опасные клетки
            
            new_cost = cost_so_far[current] + move_cost
            if new_cost > max_cost:
                continue
            
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + hex_distance(neighbor[0], neighbor[1], goal_pos[0], goal_pos[1])
                heapq.heappush(open_set, (priority, neighbor))
                came_from[neighbor] = current
    
    # Восстановление пути
    path = []
    current = best_node
    while current != start_pos:
        path.append(current)
        current = came_from.get(current)
        if current is None:
            break
    path.reverse()
    
    # Всегда добавляем конечную цель в путь
    if path and path[-1] != goal_pos:
        path.append(goal_pos)
    return [{'q': q, 'r': r} for q, r in [start_pos] + path]

def decide_moves(data):
    moves = []
    danger_cells = set()
    home_spot = (data['spot']['q'], data['spot']['r'])
    home_set = {(h['q'], h['r']) for h in data['home']}
    
    # Создаем сетку гексов для быстрого доступа
    grid = {}
    for cell in data['map']:
        grid[(cell['q'], cell['r'])] = cell
        if cell['type'] == 1 and (cell['q'], cell['r']) not in home_set:
            # Помечаем опасные гексы вокруг вражеского муравейника
            for nq, nr in get_neighbors(cell['q'], cell['r']):
                danger_cells.add((nq, nr))
            danger_cells.add((cell['q'], cell['r']))
    
    # Охранные посты вокруг основного муравейника
    guard_posts = get_neighbors(*home_spot)
    occupied_guard_posts = set()
    
    # Собираем информацию о муравьях и ресурсах
    ants_by_pos = {(ant['q'], ant['r']): ant for ant in data['ants']}
    food_positions = {(f['q'], f['r']) for f in data['food']}
    
    # Словари для учета занятых целей
    claimed_resources = defaultdict(set)
    claimed_home_cells = defaultdict(set)
    
    # Обрабатываем бойцов (тип 1)
    fighter_ants = [ant for ant in data['ants'] if ant['type'] == 1]
    for ant in fighter_ants:
        current_pos = (ant['q'], ant['r'])
        
        # Если уже на посту - остаемся
        if current_pos in guard_posts:
            occupied_guard_posts.add(current_pos)
            moves.append({
                'ant': ant['id'],
                'path': [{'q': ant['q'], 'r': ant['r']}]
            })
            continue
        
        # Ищем свободный пост
        target_post = None
        for post in guard_posts:
            if post not in occupied_guard_posts:
                # Проверяем, не занята ли клетка другим бойцом
                if post in ants_by_pos:
                    other_ant = ants_by_pos[post]
                    if other_ant['type'] == 1:
                        continue
                
                target_post = {'q': post[0], 'r': post[1]}
                occupied_guard_posts.add(post)
                break
        
        if target_post:
            path = find_path(
                {'q': ant['q'], 'r': ant['r']},
                target_post,
                4,  # ОП бойца
                {'grid': grid},
                danger_cells
            )
            moves.append({'ant': ant['id'], 'path': path})
        else:
            # Атакуем врагов если нет постов
            if data['enemies']:
                closest_enemy = min(
                    data['enemies'],
                    key=lambda e: hex_distance(ant['q'], ant['r'], e['q'], e['r'])
                )
                path = find_path(
                    {'q': ant['q'], 'r': ant['r']},
                    {'q': closest_enemy['q'], 'r': closest_enemy['r']},
                    4,
                    {'grid': grid},
                    danger_cells
                )
                moves.append({'ant': ant['id'], 'path': path})
            else:
                moves.append({
                    'ant': ant['id'],
                    'path': [{'q': ant['q'], 'r': ant['r']}]
                })
    
    # Обрабатываем рабочих (0) и разведчиков (2)
    for ant in data['ants']:
        if ant['type'] == 1:
            continue  # Уже обработаны
        
        ant_type = ant['type']
        current_pos = (ant['q'], ant['r'])
        op = 5 if ant_type == 0 else 7  # ОП рабочего/разведчика
        
        # Если несет ресурс - идем в ближайший доступный дом
        if ant['food']['amount'] > 0:
            # Выбираем ближайшую свободную клетку муравейника
            target_home = None
            min_dist = float('inf')
            
            for home in data['home']:
                home_pos = (home['q'], home['r'])
                dist = hex_distance(*current_pos, *home_pos)
                
                # Проверяем, не занята ли клетка другим муравьем того же типа
                if home_pos in ants_by_pos:
                    other_ant = ants_by_pos[home_pos]
                    if other_ant['type'] == ant_type and other_ant['id'] != ant['id']:
                        continue
                
                # Проверяем, не претендует ли другой муравей на эту клетку
                if home_pos in claimed_home_cells[ant_type]:
                    continue
                
                if dist < min_dist:
                    min_dist = dist
                    target_home = home
            
            if target_home:
                claimed_home_cells[ant_type].add((target_home['q'], target_home['r']))
                path = find_path(
                    {'q': ant['q'], 'r': ant['r']},
                    target_home,
                    op,
                    {'grid': grid},
                    danger_cells
                )
                moves.append({'ant': ant['id'], 'path': path})
            else:
                # Если все дома заняты, ждем на месте
                moves.append({
                    'ant': ant['id'],
                    'path': [{'q': ant['q'], 'r': ant['r']}]
                })
                
        # Если видит ресурс и может его собрать
        elif data['food'] and ant['food']['amount'] == 0:
            # Выбираем ближайший доступный ресурс
            target_food = None
            min_dist = float('inf')
            
            for food in data['food']:
                food_pos = (food['q'], food['r'])
                dist = hex_distance(*current_pos, *food_pos)
                
                # Проверяем, не занят ли ресурс другим муравьем того же типа
                if food_pos in ants_by_pos:
                    other_ant = ants_by_pos[food_pos]
                    if other_ant['type'] == ant_type and other_ant['id'] != ant['id']:
                        continue
                
                # Проверяем, не претендует ли другой муравей на этот ресурс
                if food_pos in claimed_resources[ant_type]:
                    continue
                
                if dist < min_dist:
                    min_dist = dist
                    target_food = food
            
            if target_food:
                claimed_resources[ant_type].add((target_food['q'], target_food['r']))
                path = find_path(
                    {'q': ant['q'], 'r': ant['r']},
                    target_food,
                    op,
                    {'grid': grid},
                    danger_cells
                )
                moves.append({'ant': ant['id'], 'path': path})
            else:
                # Если ресурсов нет или все заняты, удаляемся от муравейника
                neighbors = get_neighbors(ant['q'], ant['r'])
                best_neighbor = None
                max_distance = -1
                
                for nq, nr in neighbors:
                    npos = (nq, nr)
                    if npos in ants_by_pos:
                        continue
                    cell = grid.get(npos)
                    if cell and cell['cost'] < 1000:
                        dist = hex_distance(nq, nr, home_spot[0], home_spot[1])
                        if dist > max_distance:
                            max_distance = dist
                            best_neighbor = {'q': nq, 'r': nr}
                
                if best_neighbor:
                    moves.append({
                        'ant': ant['id'],
                        'path': [
                            {'q': ant['q'], 'r': ant['r']},
                            best_neighbor
                        ]
                    })
                else:
                    moves.append({
                        'ant': ant['id'],
                        'path': [{'q': ant['q'], 'r': ant['r']}]
                    })
        else:
            # Удаляемся от муравейника
            neighbors = get_neighbors(ant['q'], ant['r'])
            best_neighbor = None
            max_distance = -1
            
            for nq, nr in neighbors:
                npos = (nq, nr)
                if npos in ants_by_pos:
                    continue
                cell = grid.get(npos)
                if cell and cell['cost'] < 1000:
                    dist = hex_distance(nq, nr, home_spot[0], home_spot[1])
                    if dist > max_distance:
                        max_distance = dist
                        best_neighbor = {'q': nq, 'r': nr}
            
            if best_neighbor:
                moves.append({
                    'ant': ant['id'],
                    'path': [
                        {'q': ant['q'], 'r': ant['r']},
                        best_neighbor
                    ]
                })
            else:
                moves.append({
                    'ant': ant['id'],
                    'path': [{'q': ant['q'], 'r': ant['r']}]
                })
    
    return moves