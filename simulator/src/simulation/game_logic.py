import random

def calculate_new_position(x, y, direction):
    if direction == 'up': return (x, y - 1)
    if direction == 'down': return (x, y + 1)
    if direction == 'left': return (x - 1, y)
    if direction == 'right': return (x + 1, y)
    return (x, y)

def process_game_tick(gameworld, command_data):
    command = command_data['command']
    agent = gameworld.agent
    
    # Обработка команды агента
    if command == 'move':
        direction = command_data['direction']
        agent.direction = direction
        
        new_x, new_y = calculate_new_position(agent.x, agent.y, direction)
        
        # Проверка выхода за границы мира
        if not (0 <= new_x < gameworld.field_size and 0 <= new_y < gameworld.field_size):
            gameworld.handle_collision()
        else:
            new_cell = gameworld.cells[new_x][new_y]
            
            # Проверка на проходимость клетки
            if new_cell.is_passable():
                # Перемещаем агента
                old_cell = gameworld.cells[agent.x][agent.y]
                old_cell.remove_entity()
                new_cell.add_entity(agent)
                agent.x, agent.y = new_x, new_y
                
                # Сбор ресурса если он есть
                if new_cell.resource:
                    gameworld.score += 5
                    gameworld.resources.remove(new_cell.resource)
                    new_cell.remove_resource()
            else:
                # Столкновение с непроходимым объектом
                gameworld.handle_collision()
    
    elif command == 'attack':
        # Координаты всех соседних клеток (не диагональных)
        neighbors = [
            (agent.x, agent.y - 1),  # вверх
            (agent.x, agent.y + 1),  # вниз
            (agent.x - 1, agent.y),  # влево
            (agent.x + 1, agent.y)   # вправо
        ]
        
        killed = 0
        
        # Проверяем все соседние клетки
        for x, y in neighbors:
            # Проверка границ мира
            if not (0 <= x < gameworld.field_size and 0 <= y < gameworld.field_size):
                continue
                
            cell = gameworld.cells[x][y]
            
            # Если в клетке NPC - уничтожаем его
            if cell.entity and cell.entity.kind == 'npc':
                gameworld.npcs.remove(cell.entity)
                cell.remove_entity()
                killed += 1
        
        # Начисляем очки: 10 за каждого убитого NPC
        gameworld.score += killed * 10
    
    # Движение NPC (если включено)
    if gameworld.npc_movement:
        # Создаем копию списка для безопасного удаления
        for npc in gameworld.npcs[:]:
            directions = ['up', 'down', 'left', 'right']
            random.shuffle(directions)
            moved = False
            
            for d in directions:
                new_x, new_y = calculate_new_position(npc.x, npc.y, d)
                
                if (0 <= new_x < gameworld.field_size and 
                    0 <= new_y < gameworld.field_size):
                    
                    new_cell = gameworld.cells[new_x][new_y]
                    
                    if new_cell.is_passable() and not new_cell.entity:
                        # Перемещаем NPC
                        old_cell = gameworld.cells[npc.x][npc.y]
                        old_cell.remove_entity()
                        new_cell.add_entity(npc)
                        npc.x, npc.y = new_x, new_y
                        moved = True
                        break
    
    # Расчет видимой области
    visible_entities = calculate_visible_entities(gameworld)
    
    # Формируем ответ
    return {
        "width": gameworld.field_size,
        "height": gameworld.field_size,
        "score": gameworld.score,
        "respawns": gameworld.respawns,
        "agent": {
            "x": agent.x,
            "y": agent.y,
            "direction": agent.direction
        },
        "visible_entities": visible_entities
    }

def calculate_visible_entities(gameworld):
    agent = gameworld.agent
    radius = gameworld.agent_vision_radius
    min_x = max(0, agent.x - radius)
    max_x = min(gameworld.field_size - 1, agent.x + radius)
    min_y = max(0, agent.y - radius)
    max_y = min(gameworld.field_size - 1, agent.y + radius)
    
    visible = {
        "npcs": [],
        "resources": [],
        "obstacles": []
    }
    
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            cell = gameworld.cells[x][y]
            
            # Проверяем сущности
            if cell.entity:
                if cell.entity.kind == "npc":
                    visible["npcs"].append({"x": x, "y": y})
                elif cell.entity.kind == "obstacle":
                    visible["obstacles"].append({"x": x, "y": y})
            
            # Проверяем ресурсы
            if cell.resource:
                visible["resources"].append({"x": x, "y": y})
    
    return visible