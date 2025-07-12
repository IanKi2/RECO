from utils import get_neighbors, hex_distance, direction_score
import math

RESOURCE_VALUES = {1: 10, 2: 20, 3: 60}
UNIT_MOVEMENT_POINTS = {0: 5, 1: 4, 2: 7}
UNIT_CAPACITY = {0: 8, 1: 2, 2: 2}  # Грузоподъемность юнитов
DEFENSE_RADIUS = 1

class Bot:
    def __init__(self):
        self.defense_positions = []
        self.home_hexes = []
        self.spot = None
        self.hex_info = {}
        self.enemy_hills = []
        self.reserved_cells = set()
        self.current_resources = {}

    def update_state(self, state):
        """Обновление состояния игры"""
        self.home_hexes = [(h['q'], h['r']) for h in state['home']]
        self.spot = (state['spot']['q'], state['spot']['r'])
        self.hex_info = {}
        self.enemy_hills = []
        self.reserved_cells = set()
        self.current_resources = {}
        
        # Сохраняем информацию о гексах
        for hex_cell in state['map']:
            pos = (hex_cell['q'], hex_cell['r'])
            self.hex_info[pos] = hex_cell
            if hex_cell['type'] == 1 and pos not in self.home_hexes:
                self.enemy_hills.append(pos)
        
        # Сохраняем информацию о ресурсах
        for resource in state['food']:
            pos = (resource['q'], resource['r'])
            self.current_resources[pos] = {
                "type": resource['type'],
                "amount": resource['amount'],
                "value": RESOURCE_VALUES[resource['type']] * resource['amount']
            }
        
        # Расчет защитных позиций
        self.defense_positions = self._calculate_defense_positions()
    
    def _calculate_defense_positions(self):
        """Вычисление всех защитных позиций вокруг муравейника"""
        defense_positions = set()
        for home_hex in self.home_hexes:
            for neighbor in get_neighbors(*home_hex):
                if neighbor not in self.home_hexes:
                    defense_positions.add(neighbor)
        return list(defense_positions)

    def process_turn(self, state):
        """Обработка хода"""
        self.update_state(state)
        moves = []
        occupied = self._get_occupied_cells(state)
        
        # Обработка бойцов в первую очередь
        fighters = [ant for ant in state['ants'] if ant['type'] == 1]
        for ant in fighters:
            ant_pos = (ant['q'], ant['r'])
            path = self._defend_home(ant_pos, UNIT_MOVEMENT_POINTS[1], occupied)
            moves.append({"ant_id": ant['id'], "path": path})
            self.reserved_cells.add(path[-1])
        
        # Обработка остальных юнитов
        for ant in state['ants']:
            if ant['type'] == 1:  # Бойцы уже обработаны
                continue
                
            ant_pos = (ant['q'], ant['r'])
            ant_type = ant['type']
            move_points = UNIT_MOVEMENT_POINTS[ant_type]
            capacity = UNIT_CAPACITY[ant_type]
            
            # Юнит несет ресурсы - возвращаемся домой
            if ant['food']['amount'] > 0:
                path = self._return_home(ant_pos, move_points, occupied)
            
            # Юнит может собирать ресурсы
            else:
                path = self._collect_resources(
                    ant_pos, 
                    move_points, 
                    capacity, 
                    occupied
                )
            
            moves.append({"ant_id": ant['id'], "path": path})
            self.reserved_cells.add(path[-1])
            
        return moves

    def _get_occupied_cells(self, state):
        """Получение занятых клеток с учетом резервирования"""
        occupied = set()
        for enemy in state['enemies']:
            occupied.add((enemy['q'], enemy['r']))
        for ant in state['ants']:
            occupied.add((ant['q'], ant['r']))
        occupied.update(self.reserved_cells)
        return occupied

    def _return_home(self, start, move_points, occupied):
        """Возвращение домой с ресурсами"""
        best_goal = min(
            self.home_hexes,
            key=lambda h: hex_distance(start, h)
        )
        return self._find_path(
            start, 
            best_goal, 
            move_points, 
            occupied,
            must_reach=True
        )

    def _collect_resources(self, start, move_points, capacity, occupied):
        """Сбор ресурсов с учетом грузоподъемности"""
        # Если уже на ресурсе - остаемся для сбора
        if start in self.current_resources:
            return [start]
        
        # Выбор лучшего доступного ресурса
        best_resource = None
        best_score = -math.inf
        
        for pos, resource in self.current_resources.items():
            # Пропускаем недоступные ресурсы
            if pos in occupied:
                continue
                
            # Рассчитываем доступное количество
            available = min(capacity, resource['amount'])
            value = available * RESOURCE_VALUES[resource['type']]
            dist = hex_distance(start, pos)
            
            # Рассчитываем эффективность
            if dist == 0:
                score = value * 1000  # Максимальный приоритет
            else:
                score = value / dist
                
            if score > best_score:
                best_score = score
                best_resource = pos
        
        # Найден подходящий ресурс
        if best_resource:
            return self._find_path(
                start,
                best_resource,
                move_points,
                occupied,
                must_reach=True
            )
        
        # Ресурсов нет - исследуем территорию
        return self._explore(start, move_points, occupied)

    def _defend_home(self, start, move_points, occupied):
        """Занятие защитной позиции"""
        if start in self.defense_positions:
            return [start]
        
        free_positions = [
            p for p in self.defense_positions 
            if p not in occupied
        ]
        
        if not free_positions:
            return [start]
        
        best_pos = min(
            free_positions,
            key=lambda p: hex_distance(start, p)
        )
        
        return self._find_path(
            start,
            best_pos,
            move_points,
            occupied,
            must_reach=True
        )

    def _explore(self, start, move_points, occupied):
        """Исследование территории"""
        path = [start]
        current = start
        remaining = move_points
        
        while remaining > 0:
            neighbors = get_neighbors(*current)
            valid_moves = []
            
            for pos in neighbors:
                if pos in occupied:
                    continue
                if pos not in self.hex_info:
                    continue
                if self.hex_info[pos]['cost'] > remaining:
                    continue
                if not self._is_safe_position(pos):
                    continue
                
                valid_moves.append(pos)
            
            if not valid_moves:
                break
                
            # Выбираем направление максимального удаления от базы
            best_move = max(
                valid_moves,
                key=lambda p: hex_distance(p, self.spot)
            )
            
            path.append(best_move)
            current = best_move
            remaining -= self.hex_info[best_move]['cost']
            
        return path

    def _is_safe_position(self, pos):
        """Проверка безопасности позиции"""
        for hill in self.enemy_hills:
            if hex_distance(pos, hill) <= 2:
                return False
        return True

    def _find_path(self, start, goal, move_points, occupied, must_reach=False):
        """Поиск пути к цели с учетом стоимости перемещения"""
        path = [start]
        current = start
        remaining = move_points
        
        while current != goal and remaining > 0:
            neighbors = get_neighbors(*current)
            best_neighbor = None
            best_score = float('inf')
            
            for pos in neighbors:
                if pos in occupied:
                    continue
                if pos not in self.hex_info:
                    continue
                
                cost = self.hex_info[pos]['cost']
                if cost > remaining:
                    continue
                
                if not self._is_safe_position(pos):
                    continue
                
                # Оценка направления с учетом стоимости
                distance_score = direction_score(pos, goal)
                terrain_cost = cost * 0.1  # Учет сложности местности
                score = distance_score + terrain_cost
                
                if score < best_score:
                    best_score = score
                    best_neighbor = pos
                    best_cost = cost
            
            if best_neighbor is None:
                if must_reach:
                    # Попытка найти обходной путь
                    for pos in neighbors:
                        if pos in occupied or pos not in self.hex_info:
                            continue
                        cost = self.hex_info[pos]['cost']
                        if cost <= remaining:
                            best_neighbor = pos
                            best_cost = cost
                            break
                if best_neighbor is None:
                    break
            
            path.append(best_neighbor)
            current = best_neighbor
            remaining -= best_cost
            occupied.add(current)
            
        return path